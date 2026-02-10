"""
Backoffice Administrative Interface - Multi-tenant User Management System
Inspired by alfio-event/alf.io administrative interface

This is a multi-tenant admin system where each organization has its own users.
Authenticated users should only be able to manage users within their organization.

VULNERABILITY: CVE-2023-2260 style IDOR
The admin API endpoints accept organizationId/userId parameters but do not validate
that the authenticated user has permission to access those resources. This allows
authenticated low-privilege users to access or modify resources belonging to other
organizations by simply changing the ID parameters.
"""

from datetime import timedelta, datetime
import os

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, Cookie
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
import crud, schemas
from database import SessionLocal, engine, Base

SECRET_KEY = "a very secret key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Backoffice Admin API",
    description="Multi-tenant administrative interface for user management"
)
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

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


def authenticate_user(db, username: str, password: str):
    """Authenticate a user and return the user object"""
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if not user.enabled:
        return False
    return user


def get_current_user_from_cookie(
    access_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db)
) -> Optional[schemas.TokenData]:
    """Extract current user from JWT cookie"""
    if not access_token:
        return None
    
    try:
        # Handle "Bearer " prefix
        token = access_token
        if token.startswith("Bearer "):
            token = token[7:]
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        organization_id: int = payload.get("organization_id")
        
        if username is None:
            return None
        
        return schemas.TokenData(username=username, user_id=user_id, organization_id=organization_id)
    except JWTError:
        return None


def require_auth(token_data: Optional[schemas.TokenData] = Depends(get_current_user_from_cookie)):
    """Require authentication - returns 401 if not authenticated"""
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


@app.on_event("startup")
async def startup_event():
    """Initialize the database with sample multi-tenant data"""
    db = SessionLocal()
    
    # Create organizations (tenants)
    organizations_data = [
        {"name": "Acme Corp", "description": "Public demonstration organization"},
        {"name": "SecureOrg", "description": "Internal security team organization"},
        {"name": "TestOrg", "description": "Testing organization"}
    ]
    
    for org_data in organizations_data:
        org = crud.get_organization_by_name(db, org_data["name"])
        if not org:
            org_create = schemas.OrganizationCreate(**org_data)
            crud.create_organization(db, org_create)
    
    # Get the flag from environment
    flag = os.getenv("FLAG", "FLAG{default_flag}")
    
    # Create users for each organization
    users_data = [
        # Acme Corp users (organization_id=1) - demo credentials
        {"username": "demo", "email": "demo@acme.com", "password": "demo", 
         "role": "OPERATOR", "organization_id": 1, "notes": "Demo user for testing"},
        {"username": "acme_admin", "email": "admin@acme.com", "password": "acme_admin_pass_123", 
         "role": "ADMIN", "organization_id": 1, "notes": "Acme admin user"},
        
        # SecureOrg users (organization_id=2) - contains the flag
        {"username": "secure_operator", "email": "operator@secureorg.com", "password": "s3cur3_0p_p4ss!", 
         "role": "OPERATOR", "organization_id": 2, "notes": "Regular operator"},
        {"username": "secure_admin", "email": "admin@secureorg.com", "password": "sup3r_s3cr3t_4dm1n!", 
         "role": "ADMIN", "organization_id": 2, "notes": f"CONFIDENTIAL: System secret key: {flag}"},
        
        # TestOrg users (organization_id=3)
        {"username": "tester", "email": "tester@testorg.com", "password": "test123", 
         "role": "OPERATOR", "organization_id": 3, "notes": "Test user account"},
    ]
    
    for user_data in users_data:
        user = crud.get_user_by_username(db, user_data["username"])
        if not user:
            user_create = schemas.UserCreate(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
                role=user_data["role"],
                organization_id=user_data["organization_id"]
            )
            new_user = crud.create_user(db, user_create)
            # Update notes after creation
            crud.update_user(db, new_user.id, schemas.UserUpdate(notes=user_data["notes"]))
    
    db.close()


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/token", response_class=HTMLResponse)
async def login_for_access_token(
    request: Request, 
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """Authenticate user and create session"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Incorrect username or password"
        })
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "organization_id": user.organization_id
        }, 
        expires_delta=access_token_expires
    )
    
    # Redirect to the user's organization admin panel
    response = RedirectResponse(
        url=f"/admin/api/organizations/{user.organization_id}/users", 
        status_code=status.HTTP_303_SEE_OTHER
    )
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/logout")
async def logout():
    """Log out and clear session"""
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response


# ============================================================================
# Admin API Endpoints - VULNERABLE TO IDOR (CVE-2023-2260 pattern)
# 
# These endpoints require authentication but DO NOT verify that the authenticated
# user has permission to access the requested organization/user resources.
# An attacker can tamper with organizationId or userId parameters to access
# resources outside their authorized scope.
# ============================================================================

@app.get("/admin/api/organizations/{organization_id}/users", response_class=HTMLResponse)
async def list_organization_users(
    request: Request,
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(require_auth)
):
    """
    List all users in an organization.
    
    VULNERABILITY: No check that current_user belongs to organization_id.
    Attacker can change organization_id to view users from other organizations.
    """
    # Authentication check: user must be logged in
    # MISSING: Authorization check - should verify current_user.organization_id == organization_id
    
    users = crud.get_users_by_organization(db, organization_id=organization_id)
    org = crud.get_organization(db, organization_id)
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": users,
        "organization": org,
        "current_user": current_user
    })


@app.get("/admin/api/users/{user_id}")
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(require_auth)
):
    """
    Get detailed information about a user including notes.
    
    VULNERABILITY: No check that current_user has access to user_id.
    Attacker can enumerate user IDs to access details of users from other orgs.
    The 'notes' field may contain sensitive information like the flag.
    """
    # Authentication check: user must be logged in
    # MISSING: Authorization check - should verify user belongs to current_user's organization
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "enabled": user.enabled,
        "organization_id": user.organization_id,
        "notes": user.notes  # This field contains the flag for admin users
    }


@app.put("/admin/api/users/{user_id}/enable/{enable}")
async def enable_disable_user(
    user_id: int,
    enable: bool,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(require_auth)
):
    """
    Enable or disable a user account.
    
    VULNERABILITY: No check that current_user has permission to modify user_id.
    Attacker can enable/disable users in other organizations.
    """
    # Authentication check: user must be logged in
    # MISSING: Authorization check - should verify target user belongs to current_user's org
    
    user = crud.enable_user(db, user_id, enable)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"User {user_id} {'enabled' if enable else 'disabled'}", "success": True}


@app.put("/admin/api/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    reset_data: schemas.PasswordReset,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(require_auth)
):
    """
    Trigger password reset for a user.
    
    VULNERABILITY: No check that current_user has permission to reset user_id's password.
    Attacker can trigger password resets for users in other organizations.
    """
    # Authentication check: user must be logged in
    # MISSING: Authorization check - should verify target user belongs to current_user's org
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # In a real system, this would send a password reset email
    return {
        "message": f"Password reset link sent to {user.email}",
        "base_url": reset_data.base_url,
        "success": True
    }


@app.delete("/admin/api/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(require_auth)
):
    """
    Delete a user account.
    
    VULNERABILITY: No check that current_user has permission to delete user_id.
    Attacker can delete users from other organizations.
    """
    # Authentication check: user must be logged in
    # MISSING: Authorization check - should verify target user belongs to current_user's org
    
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"User {user_id} deleted", "success": True}


@app.post("/admin/api/users")
async def create_user_in_organization(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(require_auth)
):
    """
    Create a new user in an organization.
    
    VULNERABILITY: No check that current_user can create users in user_data.organization_id.
    Attacker can create users in other organizations by changing organization_id in request body.
    """
    # Authentication check: user must be logged in
    # MISSING: Authorization check - should verify current_user can manage user_data.organization_id
    
    existing = crud.get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    org = crud.get_organization(db, user_data.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    user = crud.create_user(db, user_data)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "organization_id": user.organization_id,
        "message": "User created successfully"
    }


# ============================================================================
# Utility Endpoints
# ============================================================================

@app.get("/ping")
def ping():
    """Health check endpoint"""
    return {"ping": "pong"}


@app.get("/admin/api/organizations")
async def list_organizations(
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(require_auth)
):
    """List all organizations (for debugging/discovery)"""
    orgs = crud.get_all_organizations(db)
    return [{"id": o.id, "name": o.name, "description": o.description} for o in orgs]
