from datetime import timedelta, datetime
from typing import Optional
import os

from fastapi import FastAPI, Depends, status, Request, HTTPException, Form, Body
from fastapi.exceptions import RequestValidationError
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

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request"}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user_from_token(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header
    
    if not token:
        return None
    
    try:
        token_value = token.split(" ")[1] if " " in token else token
        payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
        user = crud.get_user_by_username(db, username)
        return user
    except JWTError:
        return None


def read_flag_from_file():
    try:
        with open("/app/flag.txt", "r") as f:
            return f.read().strip()
    except:
        return "FLAG_NOT_FOUND"


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    crud.delete_all(db)
    
    flag = read_flag_from_file()

    users = [
        {"username": "demo", "password": "demo", "is_admin": False},
        {"username": "admin", "password": "s3cr3t_adm1n_p4ssw0rd_x7k9m2", "is_admin": True},
        {"username": "user1", "password": "userpass123", "is_admin": False}
    ]
    
    for user_data in users:
        user = crud.get_user_by_username(db, user_data["username"])
        if not user:
            user_create = schemas.UserCreate(
                username=user_data["username"],
                password=user_data["password"],
                is_admin=user_data["is_admin"]
            )
            user = crud.create_user(db, user_create)
        
        if user_data["is_admin"]:
            job_create = schemas.JobCreate(
                title="Internal Configuration",
                description=flag,
                is_private=True
            )
            crud.create_job(db, job_create, user_id=user.id)
        else:
            job_create = schemas.JobCreate(
                title=f"{user.username} - Project Task",
                description=f"Standard project task for {user.username}",
                is_private=False
            )
            crud.create_job(db, job_create, user_id=user.id)

    db.close()


@app.post("/token", response_class=HTMLResponse)
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect username or password"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url=f"/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.post("/api/auth/login")
async def api_login(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        username = body.get("username")
        password = body.get("password")
    except:
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}


@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_token(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    include_private = user.is_admin
    jobs = crud.get_jobs_for_user(db, user_id=user.id, include_private=include_private)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "jobs": jobs, 
        "user": user
    })


@app.get("/api/users")
async def list_users_api(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    users = db.query(crud.User).all()
    return {"users": [{"username": u.username, "is_admin": u.is_admin, "id": u.id} for u in users]}


@app.get("/api/users/{username}")
async def get_user_api(username: str, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "username": user.username,
        "is_admin": user.is_admin,
        "id": user.id
    }


@app.put("/api/users/{username}")
async def update_user(username: str, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    if "password" in body and body["password"]:
        user.hashed_password = hash_password(body["password"])
    
    if "username" in body and body["username"]:
        existing = crud.get_user_by_username(db, body["username"])
        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = body["username"]
    
    db.commit()
    db.refresh(user)
    
    return {"message": "User updated successfully", "username": user.username}


@app.get("/api/jobs")
async def get_jobs_api(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    include_private = current_user.is_admin
    jobs = crud.get_jobs_for_user(db, user_id=current_user.id, include_private=include_private)
    
    return {"jobs": [{"id": j.id, "title": j.title, "description": j.description, "is_private": j.is_private} for j in jobs]}


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_token(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "user": user
    })


@app.post("/settings", response_class=HTMLResponse)
async def update_settings(request: Request, new_password: str = Form(None), db: Session = Depends(get_db)):
    user = get_current_user_from_token(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    if new_password:
        user.hashed_password = hash_password(new_password)
        db.commit()
        db.refresh(user)
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "user": user,
        "msg": "Settings updated successfully"
    })


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response
