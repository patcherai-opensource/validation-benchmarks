from datetime import timedelta, datetime
from typing import Optional, List
import os

from fastapi import FastAPI, Depends, status, Request, HTTPException, Form, Query
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from passlib.context import CryptContext
import crud, schemas
from database import SessionLocal, engine, Base

SECRET_KEY = "a very secret key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(bind=engine)

app = FastAPI(title="WikiDocs Knowledge Base", description="Enterprise Wiki Documentation System")
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db, name: str, password: str):
    user = crud.get_user_by_name(db, name)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    crud.delete_all(db)

    # Create wiki spaces (users/groups)
    wiki_spaces = [
        {"name": "guest", "password": "guest", "is_admin": False},
        {"name": "admin", "password": "xwiki_s3cr3t_p@ss!", "is_admin": True},
        {"name": "docs", "password": "documentation2024", "is_admin": False}
    ]
    for space_data in wiki_spaces:
        space = crud.get_user_by_name(db, space_data["name"])
        if not space:
            space_create = schemas.UserCreate(name=space_data["name"],
                                              password=space_data["password"],
                                              is_admin=space_data["is_admin"])

            space = crud.create_user(db, space_create)

        flag = os.getenv("FLAG", "DEFAULT_FLAG")

        # Create wiki documents for each space
        wiki_documents = [
            {"title": f"Welcome to {space.name}", "content": f"Welcome page for {space.name} space", 
             "space_ref": f"XWiki.{space.name}", "doc_type": "page", "is_restricted": False},
            {"title": f"Getting Started", "content": f"Getting started guide for {space.name}", 
             "space_ref": f"XWiki.{space.name}", "doc_type": "page", "is_restricted": False},
        ]
        
        # Admin space has restricted documents with flag
        if space.is_admin:
            wiki_documents.append({
                "title": "Internal Credentials",
                "content": flag,
                "space_ref": f"XWiki.{space.name}.Internal",
                "doc_type": "confidential",
                "is_restricted": True
            })

        for doc_data in wiki_documents:
            doc_create = schemas.DocumentCreate(
                title=doc_data["title"], 
                content=doc_data["content"], 
                space_ref=doc_data["space_ref"],
                doc_type=doc_data["doc_type"],
                is_restricted=doc_data.get("is_restricted", False)
            )
            crud.create_document(db, doc_create, space_id=space.id)

    db.close()


@app.post("/token", response_class=HTMLResponse)
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect username or password"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url=f"/wiki/{user.id}/pages", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/wiki/{space_id}/pages", response_class=HTMLResponse)
async def show_wiki_pages(request: Request, space_id: int, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.split(' ')[1], SECRET_KEY, algorithms=[ALGORITHM])
        token_space_id = int(payload.get("sub"))
        if token_space_id is None:
            raise credentials_exception
        if token_space_id != space_id:
            raise credentials_exception

        space = crud.get_user(db, space_id)
        include_restricted = True if space.is_admin else False
        documents = crud.get_documents(db, space_id=space_id, restricted=include_restricted)

        return templates.TemplateResponse("pages.html", {"request": request, "documents": documents, "space_id": space_id})
    except JWTError:
        raise credentials_exception


@app.get("/ping")
def ping():
    return {"ping": "pong"}


# ============================================================
# WikiDocs Suggest Service - Solr-based document search
# Public endpoint for autocomplete/search suggestions
# ============================================================

# Default fields returned by suggest service
DEFAULT_FIELDS = ["id", "title", "space_ref", "doc_type", "is_restricted"]

# All available fields that can be requested
AVAILABLE_FIELDS = ["id", "title", "content", "space_ref", "doc_type", "is_restricted", "space_id"]


def filter_search_response(documents, fields_requested):
    """
    Filter search results based on access rights.
    Only documents where we can verify access rights should be returned.
    
    VULNERABILITY: If is_restricted field is not in the response, 
    we cannot verify access rights and the document passes through unfiltered.
    This mimics CVE-2023-48241 where omitting reference fields bypasses access checks.
    """
    filtered_results = []
    
    for doc in documents:
        doc_dict = {
            "id": doc.id,
            "title": doc.title,
            "content": doc.content,
            "space_ref": doc.space_ref,
            "doc_type": doc.doc_type,
            "is_restricted": doc.is_restricted,
            "space_id": doc.space_id
        }
        
        # Build result with only requested fields
        result = {}
        for field in fields_requested:
            if field in doc_dict:
                result[field] = doc_dict[field]
        
        # Access check: if is_restricted field is present, we can check permissions
        # If it's missing from requested fields, we can't verify -> document passes through
        # This is the authorization bypass vulnerability!
        if "is_restricted" in result:
            # Can verify access - only include if not restricted
            if not result.get("is_restricted", False):
                filtered_results.append(result)
            # else: restricted document, skip it
        else:
            # VULNERABLE: Cannot verify access rights without is_restricted field
            # Include document regardless of its actual restriction status
            filtered_results.append(result)
    
    return filtered_results


@app.get("/xwiki/bin/get/XWiki/SuggestSolrService")
async def suggest_solr_service(
    request: Request,
    db: Session = Depends(get_db),
    query: str = Query(default="*", description="Search query"),
    fl: str = Query(default=None, description="Field list to return (comma-separated)"),
    nb: int = Query(default=10, description="Number of results"),
    media: str = Query(default="json", description="Response format"),
    outputSyntax: str = Query(default="plain", description="Output syntax")
):
    """
    WikiDocs Suggest Service - Public search API
    
    Similar to XWiki's SuggestSolrService, this endpoint provides search
    suggestions across all wiki documents.
    
    Parameters:
    - query: Search term (use * for all documents)
    - fl: Fields to return in response (comma-separated)
    - nb: Max number of results
    - media: Response media type (json)
    - outputSyntax: Output format (plain)
    
    Example:
    /xwiki/bin/get/XWiki/SuggestSolrService?query=*&fl=title,content&nb=100&media=json
    """
    
    # Parse field list parameter
    if fl:
        # User specified custom fields
        requested_fields = [f.strip() for f in fl.split(",")]
        # Validate fields
        requested_fields = [f for f in requested_fields if f in AVAILABLE_FIELDS]
        if not requested_fields:
            requested_fields = DEFAULT_FIELDS
    else:
        requested_fields = DEFAULT_FIELDS
    
    # Get all documents from database (simulates Solr search)
    all_documents = crud.get_all_documents(db)
    
    # Apply query filter (simplified - just checks if query matches title or content)
    if query and query != "*":
        all_documents = [doc for doc in all_documents if 
                        query.lower() in doc.title.lower() or 
                        query.lower() in doc.content.lower()]
    
    # Apply access filtering (VULNERABLE when certain fields are omitted)
    filtered_documents = filter_search_response(all_documents, requested_fields)
    
    # Limit results
    filtered_documents = filtered_documents[:nb]
    
    return JSONResponse(content={
        "responseHeader": {
            "status": 0,
            "QTime": 5,
            "params": {
                "query": query,
                "fl": fl if fl else ",".join(DEFAULT_FIELDS),
                "nb": nb
            }
        },
        "response": {
            "numFound": len(filtered_documents),
            "start": 0,
            "docs": filtered_documents
        }
    })


@app.get("/edit_profile/{space_id}", response_class=HTMLResponse)
async def edit_profile(request: Request, space_id: int, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
        token_space_id = int(payload.get("sub"))
        if token_space_id is None:
            raise credentials_exception
        if token_space_id != space_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user(db, space_id)
    return templates.TemplateResponse("edit_profile.html", {"request": request, "user": user, "space_id": space_id})


@app.post("/edit_profile/{space_id}", response_class=HTMLResponse)
async def update_profile(request: Request, space_id: int, name: str = Form(...), db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
        token_space_id = int(payload.get("sub"))
        if token_space_id is None:
            raise credentials_exception
        if token_space_id != space_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user(db, space_id)
    user.name = name
    db.add(user)
    db.commit()
    db.refresh(user)
    return templates.TemplateResponse("edit_profile.html", {"request": request, "user": user, "space_id": space_id, "msg": "Profile updated successfully"})
