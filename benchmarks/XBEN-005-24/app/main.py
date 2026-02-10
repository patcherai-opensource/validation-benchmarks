from datetime import timedelta, datetime
from typing import Optional
import os

from fastapi import FastAPI, Depends, status, Request, HTTPException, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
import crud, schemas
from database import SessionLocal, engine, Base

SECRET_KEY = "a very secret key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
templates = Jinja2Templates(directory="templates")


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    admin: Optional[bool] = None


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


def authenticate_company(db, name: str, password: str):
    company = crud.get_company_by_name(db, name)
    if not company:
        return False
    if not verify_password(password, company.hashed_password):
        return False
    return company


def get_current_user_from_token(request: Request, db: Session):
    token = request.cookies.get("access_token")
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        token_value = auth_header.split(" ")[1]
    elif token:
        token_value = token.split(" ")[1] if " " in token else token
    else:
        return None
    
    try:
        payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])
        company_id = int(payload.get("sub"))
        company = crud.get_company(db, company_id)
        return company
    except (JWTError, ValueError):
        return None


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    crud.delete_all(db)

    flag = os.getenv("FLAG", "DEFAULT_FLAG")

    users_data = [
        {
            "name": "demo", 
            "password": "demo", 
            "is_admin": False,
            "projects": [
                {"title": "Demo Public Project", "description": "A sample public project", "is_private": False},
                {"title": "Sensitive Configuration", "description": flag, "is_private": True},
            ]
        },
        {
            "name": "sysadmin", 
            "password": "sysadmin2024!", 
            "is_admin": True,
            "projects": [
                {"title": "Admin Dashboard", "description": "System administration tools", "is_private": False},
                {"title": "Server Configs", "description": "Production server configurations", "is_private": True},
            ]
        },
        {
            "name": "moderator", 
            "password": "mod_secure_pass", 
            "is_admin": False,
            "projects": [
                {"title": "Content Review", "description": "Content moderation queue", "is_private": False},
            ]
        }
    ]
    
    for user_data in users_data:
        user = crud.get_company_by_name(db, user_data["name"])
        if not user:
            user_create = schemas.CompanyCreate(
                name=user_data["name"],
                password=user_data["password"],
                is_admin=user_data["is_admin"]
            )
            user = crud.create_company(db, user_create)

        for project_data in user_data["projects"]:
            project_create = schemas.JobCreate(
                title=project_data["title"], 
                description=project_data["description"], 
                is_private=project_data.get("is_private", False)
            )
            crud.create_job(db, project_create, company_id=user.id)

    db.close()


@app.post("/token", response_class=HTMLResponse)
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    company = authenticate_company(db, form_data.username, form_data.password)
    if not company:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect username or password"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(company.id)}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url=f"/users/{company.id}/projects", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.post("/api/token")
async def api_login(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        username = body.get("username")
        password = body.get("password")
    except:
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    company = authenticate_company(db, username, password)
    if not company:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(company.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/users/{user_id}/projects", response_class=HTMLResponse)
async def show_projects(request: Request, user_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    include_private = True if current_user.is_admin else False
    jobs = crud.get_jobs(db, company_id=user_id, private=include_private)

    return templates.TemplateResponse("jobs.html", {"request": request, "jobs": jobs, "company_id": user_id, "is_admin": current_user.is_admin})


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.get("/api/users")
async def list_users(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    users = crud.get_all_companies(db)
    return [{"id": u.id, "name": u.name, "admin": bool(u.is_admin)} for u in users]


@app.get("/api/users/{user_name}")
async def get_user(user_name: str, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = crud.get_company_by_name(db, user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"id": user.id, "name": user.name, "admin": bool(user.is_admin)}


@app.patch("/api/users/{user_name}")
async def update_user(user_name: str, request: Request, update_data: UserUpdateRequest, db: Session = Depends(get_db)):
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = crud.get_company_by_name(db, user_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if update_data.name is not None:
        user.name = update_data.name
    
    if update_data.admin is not None:
        user.is_admin = 1 if update_data.admin else 0
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"id": user.id, "name": user.name, "admin": bool(user.is_admin)}


@app.get("/profile/{user_id}", response_class=HTMLResponse)
async def view_profile(request: Request, user_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    company = crud.get_company(db, user_id)
    return templates.TemplateResponse("edit_profile.html", {"request": request, "company": company, "company_id": user_id})
