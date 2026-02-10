from datetime import timedelta, datetime
import os

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
import crud, schemas
from database import SessionLocal, engine, Base

SECRET_KEY = "a very secret key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

def get_current_user(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    user = crud.get_user_by_username(db, username)
    return user

def authenticate_user(db, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    
    organizations = [
        {"name": "Acme Corp", "description": "Technology solutions provider"},
        {"name": "GlobalTech", "description": "Enterprise software company"},
        {"name": "SecureSystems", "description": "Security consulting firm"},
    ]
    
    for org_data in organizations:
        org = crud.get_organization_by_name(db, org_data["name"])
        if not org:
            org_create = schemas.OrganizationCreate(**org_data)
            org = crud.create_organization(db, org_create)
    
    users_data = [
        {"username": "alice", "password": "alice123", "email": "alice@acme.com", "organization_id": 1, "role": "operator"},
        {"username": "bob", "password": "bob456", "email": "bob@acme.com", "organization_id": 1, "role": "admin"},
        {"username": "charlie", "password": "charlie789", "email": "charlie@globaltech.com", "organization_id": 2, "role": "operator"},
        {"username": "diana", "password": "diana012", "email": "diana@globaltech.com", "organization_id": 2, "role": "admin"},
        {"username": "eve", "password": "eve345", "email": "eve@securesystems.com", "organization_id": 3, "role": "operator"},
        {"username": "frank", "password": "frank678", "email": "frank@securesystems.com", "organization_id": 3, "role": "admin"},
    ]
    
    for user_data in users_data:
        user = crud.get_user_by_username(db, user_data["username"])
        if not user:
            user_create = schemas.UserCreate(**user_data)
            crud.create_user(db, user_create)
    
    secrets_data = [
        {"organization_id": 1, "key": "api_key", "value": "acme_api_key_2024_production"},
        {"organization_id": 1, "key": "database_password", "value": "acme_db_pass_secure123"},
        {"organization_id": 2, "key": "api_key", "value": "globaltech_api_key_2024"},
        {"organization_id": 2, "key": "database_password", "value": "globaltech_db_secure456"},
        {"organization_id": 3, "key": "api_key", "value": "securesystems_api_2024"},
        {"organization_id": 3, "key": "internal_secret", "value": os.getenv("FLAG", "FLAG{default_flag}")},
    ]
    
    for secret_data in secrets_data:
        existing = crud.get_secrets_by_organization(db, secret_data["organization_id"])
        if not any(s.key == secret_data["key"] for s in existing):
            secret_create = schemas.SecretCreate(key=secret_data["key"], value=secret_data["value"])
            crud.create_secret(db, secret_create, secret_data["organization_id"])
    
    db.close()


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "org_id": user.organization_id, "role": user.role}, 
        expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/backoffice/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@app.get("/backoffice/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    org = crud.get_organization(db, user.organization_id)
    users = crud.get_users_by_organization(db, user.organization_id)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": user, 
        "organization": org,
        "users": users
    })

@app.get("/backoffice/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request, organizationId: int = None, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    org_id = organizationId if organizationId else user.organization_id
    
    users = crud.get_users_by_organization(db, org_id)
    org = crud.get_organization(db, org_id)
    
    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "user": user,
        "users": users,
        "organization": org,
        "current_org_id": org_id
    })

@app.get("/backoffice/admin/user/{user_id}", response_class=HTMLResponse)
async def admin_user_detail(request: Request, user_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    target_user = crud.get_user(db, user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return templates.TemplateResponse("user_detail.html", {
        "request": request,
        "user": current_user,
        "target_user": target_user
    })

@app.get("/backoffice/admin/secrets", response_class=HTMLResponse)
async def admin_secrets(request: Request, organizationId: int = None, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    org_id = organizationId if organizationId else user.organization_id
    
    secrets = crud.get_secrets_by_organization(db, org_id)
    org = crud.get_organization(db, org_id)
    
    return templates.TemplateResponse("admin_secrets.html", {
        "request": request,
        "user": user,
        "secrets": secrets,
        "organization": org,
        "current_org_id": org_id
    })

@app.post("/backoffice/admin/user/{user_id}/toggle", response_class=HTMLResponse)
async def toggle_user_status(request: Request, user_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    target_user = crud.get_user(db, user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    crud.toggle_user_enabled(db, user_id)
    
    return RedirectResponse(url=f"/backoffice/admin/users?organizationId={target_user.organization_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/ping")
def ping():
    return {"ping": "pong"}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error.html", {"request": request, "error": "Page not found"}, status_code=404)

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("error.html", {"request": request, "error": "Internal server error"}, status_code=500)
