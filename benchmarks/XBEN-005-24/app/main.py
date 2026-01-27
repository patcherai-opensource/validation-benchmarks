from datetime import timedelta, datetime
from typing import Optional, List, Any
import os
import json

from fastapi import FastAPI, Depends, status, Request, HTTPException, Form, Body
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from passlib.context import CryptContext
import crud, schemas
from database import SessionLocal, engine, Base

SECRET_KEY = "aimeos_admin_secret_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Aimeos Admin Panel", description="Backend administration system")
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


def authenticate_user(db, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    crud.delete_all(db)
    
    flag = os.getenv("FLAG", "DEFAULT_FLAG")

    # Create users with different roles: super, admin, editor
    example_users = [
        {"email": "editor@example.com", "password": "editor123", "role": "editor", "display_name": "Editor User"},
        {"email": "admin@internal.local", "password": "sx92kd8fj3nxmzp1", "role": "admin", "display_name": "Admin User"},
        {"email": "super@internal.local", "password": "yt73hd9sk2mxlqw4", "role": "super", "display_name": "Super User"},
    ]
    
    for user_data in example_users:
        user = crud.get_user_by_email(db, user_data["email"])
        if not user:
            user_create = schemas.UserCreate(
                email=user_data["email"],
                password=user_data["password"],
                role=user_data["role"],
                display_name=user_data["display_name"]
            )
            user = crud.create_user(db, user_create)
    
    # Create system configurations - flag stored in super-only config
    configs = [
        {"key": "site.title", "value": "Aimeos Shop", "access_level": "editor"},
        {"key": "api.rate_limit", "value": "1000", "access_level": "admin"},
        {"key": "system.secret_key", "value": flag, "access_level": "super"},
    ]
    
    for config_data in configs:
        crud.create_config(db, config_data["key"], config_data["value"], config_data["access_level"])

    db.close()


def get_current_user_from_token(token: str, db: Session):
    """Extract user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
        user = crud.get_user(db, user_id)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


@app.post("/admin/token", response_class=HTMLResponse)
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url=f"/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/admin/login")


@app.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/admin/login")
    
    try:
        user = get_current_user_from_token(token, db)
        users = crud.get_all_users(db)
        configs = crud.get_configs_for_role(db, user.role)
        return templates.TemplateResponse("dashboard.html", {
            "request": request, 
            "user": user,
            "users": users,
            "configs": configs
        })
    except HTTPException:
        return RedirectResponse(url="/admin/login")


@app.get("/ping")
def ping():
    return {"status": "ok", "service": "aimeos-admin"}


# GraphQL-style API endpoint for managing customers/users
@app.post("/admin/graphql")
async def graphql_endpoint(request: Request, db: Session = Depends(get_db)):
    """
    GraphQL-style API for customer management.
    Supports queries and mutations for user/customer data.
    """
    token = request.cookies.get("access_token")
    auth_header = request.headers.get("Authorization")
    
    if auth_header:
        token = auth_header
    
    if not token:
        return JSONResponse(
            status_code=401,
            content={"errors": [{"message": "Authentication required"}]}
        )
    
    try:
        current_user = get_current_user_from_token(token, db)
    except HTTPException:
        return JSONResponse(
            status_code=401,
            content={"errors": [{"message": "Invalid or expired token"}]}
        )
    
    try:
        body = await request.json()
    except:
        return JSONResponse(
            status_code=400,
            content={"errors": [{"message": "Invalid JSON body"}]}
        )
    
    query = body.get("query", "")
    variables = body.get("variables", {})
    
    # Parse and execute GraphQL-style operations
    if "mutation" in query.lower():
        return handle_mutation(query, variables, current_user, db)
    elif "query" in query.lower():
        return handle_query(query, variables, current_user, db)
    else:
        return JSONResponse(
            status_code=400,
            content={"errors": [{"message": "Invalid operation. Use 'query' or 'mutation'"}]}
        )


def handle_query(query: str, variables: dict, current_user, db: Session):
    """Handle GraphQL queries"""
    if "getCustomers" in query or "customers" in query.lower():
        users = crud.get_all_users(db)
        return JSONResponse(content={
            "data": {
                "customers": [
                    {
                        "id": u.id,
                        "email": u.email,
                        "display_name": u.display_name,
                        "role": u.role
                    } for u in users
                ]
            }
        })
    
    if "getConfigs" in query or "configs" in query.lower():
        configs = crud.get_configs_for_role(db, current_user.role)
        return JSONResponse(content={
            "data": {
                "configs": [
                    {
                        "key": c.key,
                        "value": c.value,
                        "access_level": c.access_level
                    } for c in configs
                ]
            }
        })
    
    return JSONResponse(content={"data": None, "errors": [{"message": "Unknown query"}]})


def handle_mutation(query: str, variables: dict, current_user, db: Session):
    """
    Handle GraphQL mutations for customer management.
    
    VULNERABILITY: The saveCustomer mutation does not properly check if the 
    current user has permission to modify the target user's sensitive fields
    like 'role' or 'password'. An editor can escalate privileges by modifying
    an admin/super user's role or resetting their password.
    """
    if "saveCustomer" in query:
        input_data = variables.get("input", {})
        
        if not input_data:
            return JSONResponse(
                status_code=400,
                content={"errors": [{"message": "Missing input data for saveCustomer mutation"}]}
            )
        
        target_id = input_data.get("customer.id") or input_data.get("id")
        
        if not target_id:
            return JSONResponse(
                status_code=400,
                content={"errors": [{"message": "customer.id is required"}]}
            )
        
        target_user = crud.get_user(db, int(target_id))
        if not target_user:
            return JSONResponse(
                status_code=404,
                content={"errors": [{"message": f"Customer with id {target_id} not found"}]}
            )
        
        # VULNERABLE: No proper authorization check!
        # Any authenticated user (including editors) can modify any customer's data
        # including sensitive fields like role and password.
        # This should restrict role/password changes to admin/super users only.
        
        # Apply updates from input - fromArray style update
        if "customer.email" in input_data or "email" in input_data:
            target_user.email = input_data.get("customer.email") or input_data.get("email")
        
        if "customer.display_name" in input_data or "display_name" in input_data:
            target_user.display_name = input_data.get("customer.display_name") or input_data.get("display_name")
        
        # CRITICAL VULNERABILITY: Role can be changed by any user
        if "customer.role" in input_data or "role" in input_data:
            new_role = input_data.get("customer.role") or input_data.get("role")
            target_user.role = new_role
        
        # CRITICAL VULNERABILITY: Password can be reset by any user
        if "customer.password" in input_data or "password" in input_data:
            new_password = input_data.get("customer.password") or input_data.get("password")
            target_user.hashed_password = pwd_context.hash(new_password)
        
        db.add(target_user)
        db.commit()
        db.refresh(target_user)
        
        return JSONResponse(content={
            "data": {
                "saveCustomer": {
                    "id": target_user.id,
                    "email": target_user.email,
                    "display_name": target_user.display_name,
                    "role": target_user.role,
                    "success": True
                }
            }
        })
    
    return JSONResponse(
        status_code=400,
        content={"errors": [{"message": "Unknown mutation"}]}
    )


@app.get("/admin/users", response_class=HTMLResponse)
async def list_users(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/admin/login")
    
    try:
        user = get_current_user_from_token(token, db)
        users = crud.get_all_users(db)
        return templates.TemplateResponse("users.html", {
            "request": request,
            "user": user,
            "users": users
        })
    except HTTPException:
        return RedirectResponse(url="/admin/login")


@app.get("/admin/configs", response_class=HTMLResponse)
async def view_configs(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/admin/login")
    
    try:
        user = get_current_user_from_token(token, db)
        configs = crud.get_configs_for_role(db, user.role)
        return templates.TemplateResponse("configs.html", {
            "request": request,
            "user": user,
            "configs": configs
        })
    except HTTPException:
        return RedirectResponse(url="/admin/login")
