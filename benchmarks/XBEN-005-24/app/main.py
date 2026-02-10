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

SECRET_KEY = "a very secret key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(bind=engine)

app = FastAPI()
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


def hash_password(password):
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


def authenticate_user(db, name: str, password: str):
    user = crud.get_user_by_name(db, name)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user_from_token(token: str, db: Session):
    """Extract user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = crud.get_user_by_name(db, username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    crud.delete_all(db)

    # Create users - admin has the flag in their profile
    flag = os.getenv("FLAG", "DEFAULT_FLAG")
    
    example_users = [
        {"username": "demo", "password": "demo", "is_admin": False, "bio": "Demo user account"},
        {"username": "admin", "password": "x9K#mP2$vL8@nQ5wR3tY7zA1bC4dE6fG", "is_admin": True, "bio": f"Admin account. Secret: {flag}"},
        {"username": "guest", "password": "guest123", "is_admin": False, "bio": "Guest user account"}
    ]
    
    for user_data in example_users:
        user = crud.get_user_by_name(db, user_data["username"])
        if not user:
            user_create = schemas.UserCreate(
                username=user_data["username"],
                password=user_data["password"],
                is_admin=user_data["is_admin"],
                bio=user_data.get("bio", "")
            )
            crud.create_user(db, user_create)

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
    response = RedirectResponse(url=f"/users/{user.username}/profile", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/ping")
def ping():
    return {"ping": "pong"}


# API endpoint to get user list (public usernames only)
@app.get("/api/users")
async def list_users(db: Session = Depends(get_db)):
    """List all usernames (public endpoint for user discovery)"""
    users = crud.get_all_users(db)
    return {"users": [{"username": u.username, "is_admin": u.is_admin} for u in users]}


# User profile view - HTML
@app.get("/users/{username}/profile", response_class=HTMLResponse)
async def view_profile(request: Request, username: str, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    current_user = get_current_user_from_token(token, db)
    target_user = crud.get_user_by_name(db, username)
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Only show full profile (including bio with flag) if:
    # 1. User is viewing their own profile, OR
    # 2. User is an admin
    can_view_full = (current_user.username == target_user.username) or current_user.is_admin
    
    return templates.TemplateResponse("profile.html", {
        "request": request, 
        "user": target_user, 
        "current_user": current_user,
        "can_view_full": can_view_full
    })


# VULNERABLE: IDOR in user update - CVE-2023-32078 style vulnerability
# Any authenticated user can update ANY user's data (including password)
# by specifying their username in the URL. Missing authorization check!
@app.put("/api/users/{username}")
async def update_user(username: str, request: Request, user_update: dict = Body(...), db: Session = Depends(get_db)):
    """
    Update user account data.
    VULNERABLE: Missing check to verify the authenticated user is allowed to modify this account.
    Any authenticated user can change any other user's password.
    """
    token = request.cookies.get("access_token")
    if not token:
        # Also check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = auth_header
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Verify token is valid (but NOT verifying the user has permission to modify this account!)
    current_user = get_current_user_from_token(token, db)
    
    # VULNERABILITY: We only check that the user is authenticated, 
    # but we do NOT check if current_user.username == username or if current_user.is_admin
    # This allows any authenticated user to update any other user's account
    
    target_user = crud.get_user_by_name(db, username)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Allow updating password and other fields
    if "password" in user_update:
        target_user.hashed_password = hash_password(user_update["password"])
    if "bio" in user_update:
        target_user.bio = user_update["bio"]
    
    db.add(target_user)
    db.commit()
    db.refresh(target_user)
    
    return {"message": f"User {username} updated successfully"}


# Edit profile form - HTML (properly protected)
@app.get("/users/{username}/edit", response_class=HTMLResponse)
async def edit_profile_form(request: Request, username: str, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    current_user = get_current_user_from_token(token, db)
    target_user = crud.get_user_by_name(db, username)
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Only allow editing own profile (UI is protected, but API is not!)
    if current_user.username != target_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to edit this profile")
    
    return templates.TemplateResponse("edit_profile.html", {
        "request": request, 
        "user": target_user,
        "current_user": current_user
    })
