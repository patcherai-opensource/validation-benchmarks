from datetime import timedelta, datetime
from typing import Optional
import os

from fastapi import FastAPI, Depends, status, Request, HTTPException, Form, Body
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from passlib.context import CryptContext
import crud, schemas
from database import SessionLocal, engine, Base

SECRET_KEY = "netmgr_jwt_secret_2023"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NetMgr - Network Management System",
    description="Enterprise network management and monitoring platform",
    version="0.17.0"
)
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


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
    """Extract and validate user from JWT token"""
    token = request.cookies.get("access_token")
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header
    
    if not token:
        return None
        
    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
        user = crud.get_user_by_username(db, username)
        return user
    except JWTError:
        return None


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    crud.delete_all(db)

    # Create users
    users_data = [
        {"username": "guest", "password": "guest", "is_admin": False, "email": "guest@netmgr.local"},
        {"username": "netadmin", "password": "Kj8#mNp2$qLx9@vR", "is_admin": True, "email": "admin@netmgr.local"},
        {"username": "operator", "password": "op3r@t0r_s3cur3!", "is_admin": False, "email": "operator@netmgr.local"}
    ]
    
    for user_data in users_data:
        user = crud.get_user_by_username(db, user_data["username"])
        if not user:
            user_create = schemas.UserCreate(
                username=user_data["username"],
                password=user_data["password"],
                is_admin=user_data["is_admin"],
                email=user_data.get("email", "")
            )
            user = crud.create_user(db, user_create)

        flag = os.getenv("FLAG", "DEFAULT_FLAG")

        # Create network configs for each user
        configs = [
            {"name": f"{user.username}_network_1", "config_data": f"Network configuration for {user.username}", "is_private": False},
            {"name": "system_credentials", "config_data": flag, "is_private": True},
        ]

        for config_data in configs:
            config_create = schemas.NetworkConfigCreate(
                name=config_data["name"], 
                config_data=config_data["config_data"], 
                is_private=config_data.get("is_private", False)
            )
            crud.create_network_config(db, config_create, user_id=user.id)

    db.close()


# ============ WEB UI ROUTES ============

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url=f"/dashboard/{user.username}", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/dashboard/{username}", response_class=HTMLResponse)
async def show_dashboard(request: Request, username: str, db: Session = Depends(get_db)):
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    if current_user.username != username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    include_private = True if current_user.is_admin else False
    configs = crud.get_network_configs(db, user_id=current_user.id, private=include_private)

    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "configs": configs, 
        "user": current_user,
        "username": username
    })


@app.get("/settings/{username}", response_class=HTMLResponse)
async def settings_page(request: Request, username: str, db: Session = Depends(get_db)):
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    if current_user.username != username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("settings.html", {
        "request": request, 
        "user": current_user,
        "username": username
    })


# ============ API ROUTES ============

@app.post("/api/auth/login")
async def api_login(request: Request, db: Session = Depends(get_db)):
    """API endpoint for authentication"""
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


@app.get("/api/users")
async def list_users(request: Request, db: Session = Depends(get_db)):
    """List all users (admin only in production, but exposed for network enumeration)"""
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    users = crud.get_all_users(db)
    return {"users": [{"username": u.username, "email": u.email, "is_admin": u.is_admin} for u in users]}


@app.get("/api/users/{username}")
async def get_user(username: str, request: Request, db: Session = Depends(get_db)):
    """Get user details"""
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"username": user.username, "email": user.email, "is_admin": user.is_admin}


@app.put("/api/users/{username}")
async def update_user(username: str, request: Request, db: Session = Depends(get_db)):
    """
    Update user account - VULNERABLE ENDPOINT
    Missing authorization check: any authenticated user can update any user's data
    """
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # VULNERABILITY: No check that current_user.username == username or current_user.is_admin
    # Any authenticated user can modify any other user's account
    
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    target_user = crud.get_user_by_username(db, username)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update allowed fields
    if "password" in body:
        target_user.hashed_password = hash_password(body["password"])
    if "email" in body:
        target_user.email = body["email"]
    if "is_admin" in body:
        target_user.is_admin = body["is_admin"]
    
    db.add(target_user)
    db.commit()
    db.refresh(target_user)
    
    return {"message": "User updated successfully", "username": target_user.username}


@app.get("/api/networks")
async def list_networks(request: Request, db: Session = Depends(get_db)):
    """List network configurations for current user"""
    current_user = get_current_user_from_token(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    include_private = True if current_user.is_admin else False
    configs = crud.get_network_configs(db, user_id=current_user.id, private=include_private)
    
    return {"networks": [{"id": c.id, "name": c.name, "config_data": c.config_data} for c in configs]}


@app.get("/api/status")
async def system_status():
    """System health status"""
    return {
        "status": "operational",
        "version": "0.17.0",
        "services": {
            "database": "connected",
            "network_monitor": "active",
            "vpn_gateway": "standby"
        }
    }


@app.get("/api/docs")
async def api_documentation():
    """API documentation overview"""
    return {
        "api_version": "v1",
        "endpoints": [
            {"method": "POST", "path": "/api/auth/login", "description": "Authenticate user"},
            {"method": "GET", "path": "/api/users", "description": "List users"},
            {"method": "GET", "path": "/api/users/{username}", "description": "Get user details"},
            {"method": "PUT", "path": "/api/users/{username}", "description": "Update user"},
            {"method": "GET", "path": "/api/networks", "description": "List network configs"},
            {"method": "GET", "path": "/api/status", "description": "System status"}
        ]
    }


@app.get("/ping")
def ping():
    return {"status": "ok", "service": "netmgr"}
