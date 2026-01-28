from datetime import timedelta, datetime
import os

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
import crud, schemas
from database import SessionLocal, engine, Base

SECRET_KEY = "evmgr_s3cr3t_k3y_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

Base.metadata.create_all(bind=engine)

app = FastAPI(title="EventFlow - Event Management Platform", version="2.3.1")
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

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user_from_cookie(request: Request, db: Session):
    """Extract and validate user from JWT cookie"""
    token = request.cookies.get("session_token")
    if not token:
        return None
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        org_id: int = payload.get("org_id")
        if username is None:
            return None
        org = crud.get_organization_by_name(db, username)
        return org
    except JWTError:
        return None

def authenticate_organization(db, name: str, password: str):
    org = crud.get_organization_by_name(db, name)
    if not org:
        return False
    if not verify_password(password, org.hashed_password):
        return False
    return org

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    
    # Create organizations (multi-tenant setup)
    organizations = [
        {"name": "eventuser", "password": "events2024", "is_admin": False, "display_name": "Event User Organization"},
        {"name": "masteradmin", "password": "xK9$mL2#pQ7@nR4!", "is_admin": True, "display_name": "Master Admin Organization"},
        {"name": "corporate", "password": "corp123secure", "is_admin": False, "display_name": "Corporate Events Ltd"},
    ]
    
    for org_data in organizations:
        org = crud.get_organization_by_name(db, org_data["name"])
        if not org:
            org_create = schemas.OrganizationCreate(
                name=org_data["name"],
                password=org_data["password"],
                is_admin=org_data["is_admin"],
                display_name=org_data["display_name"]
            )
            org = crud.create_organization(db, org_create)
        
        # Create sample users for each organization
        sample_users = [
            {"username": f"{org.name}_operator", "email": f"operator@{org.name}.local", "role": "operator"},
            {"username": f"{org.name}_viewer", "email": f"viewer@{org.name}.local", "role": "viewer"},
        ]
        
        for user_data in sample_users:
            existing = crud.get_user_by_username(db, user_data["username"])
            if not existing:
                user_create = schemas.UserCreate(**user_data)
                crud.create_user(db, user_create, organization_id=org.id)
        
        # Store flag as sensitive config for admin organization
        if org.is_admin:
            flag = os.getenv("FLAG", "FLAG{default_flag}")
            # Store flag as a "sensitive config" entry
            existing_config = crud.get_config_by_key(db, org.id, "api_master_key")
            if not existing_config:
                config_create = schemas.ConfigCreate(key="api_master_key", value=flag, is_sensitive=True)
                crud.create_config(db, config_create, organization_id=org.id)
            
            # Also add some decoy configs
            decoy_configs = [
                {"key": "webhook_url", "value": "https://hooks.eventflow.local/callback", "is_sensitive": False},
                {"key": "rate_limit", "value": "1000", "is_sensitive": False},
            ]
            for cfg in decoy_configs:
                existing = crud.get_config_by_key(db, org.id, cfg["key"])
                if not existing:
                    crud.create_config(db, schemas.ConfigCreate(**cfg), organization_id=org.id)
        else:
            # Non-admin orgs get regular configs
            regular_configs = [
                {"key": "notification_email", "value": f"notify@{org.name}.local", "is_sensitive": False},
                {"key": "max_events", "value": "50", "is_sensitive": False},
            ]
            for cfg in regular_configs:
                existing = crud.get_config_by_key(db, org.id, cfg["key"])
                if not existing:
                    crud.create_config(db, schemas.ConfigCreate(**cfg), organization_id=org.id)
    
    db.close()


# ==================== PUBLIC ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/api/auth/login", response_class=HTMLResponse)
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    org = authenticate_organization(db, form_data.username, form_data.password)
    if not org:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": org.name, "org_id": org.id}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url=f"/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="session_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("session_token")
    return response

# ==================== ADMIN DASHBOARD ====================

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    current_org = get_current_user_from_cookie(request, db)
    if not current_org:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "org": current_org,
        "org_id": current_org.id
    })

# ==================== USER MANAGEMENT API (IDOR VULNERABLE) ====================

@app.get("/admin/api/organization/{org_id}/users", response_class=JSONResponse)
async def list_organization_users(request: Request, org_id: int, db: Session = Depends(get_db)):
    """
    List users for an organization.
    VULNERABLE: No check that requesting user belongs to org_id
    """
    current_org = get_current_user_from_cookie(request, db)
    if not current_org:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # VULNERABILITY: Missing authorization check - should verify current_org.id == org_id
    users = crud.get_users_by_organization(db, organization_id=org_id)
    return {"organization_id": org_id, "users": [{"id": u.id, "username": u.username, "email": u.email, "role": u.role} for u in users]}

@app.get("/admin/api/organization/{org_id}/config", response_class=JSONResponse)
async def get_organization_config(request: Request, org_id: int, db: Session = Depends(get_db)):
    """
    Get configuration for an organization.
    VULNERABLE: No check that requesting user belongs to org_id - allows reading sensitive configs
    """
    current_org = get_current_user_from_cookie(request, db)
    if not current_org:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # VULNERABILITY: Missing authorization check - should verify current_org.id == org_id
    configs = crud.get_configs_by_organization(db, organization_id=org_id)
    return {
        "organization_id": org_id, 
        "configs": [{"key": c.key, "value": c.value, "is_sensitive": c.is_sensitive} for c in configs]
    }

@app.put("/admin/api/user/{user_id}/role", response_class=JSONResponse)
async def update_user_role(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
    Update a user's role.
    VULNERABLE: No check that user belongs to current organization
    """
    current_org = get_current_user_from_cookie(request, db)
    if not current_org:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    body = await request.json()
    new_role = body.get("role", "viewer")
    
    # VULNERABILITY: Missing authorization check
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    crud.update_user_role(db, user_id, new_role)
    return {"status": "success", "user_id": user_id, "new_role": new_role}

@app.post("/admin/api/user/{user_id}/reset-password", response_class=JSONResponse)
async def reset_user_password(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
    Reset a user's password (generates temporary password).
    VULNERABLE: No check that user belongs to current organization
    """
    current_org = get_current_user_from_cookie(request, db)
    if not current_org:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # VULNERABILITY: Missing authorization check
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    temp_password = f"temp_{user_id}_reset"
    return {"status": "success", "user_id": user_id, "message": "Password reset email sent"}

# ==================== EVENTS API (DECOY - PROPERLY SECURED) ====================

@app.get("/admin/api/events", response_class=JSONResponse)
async def list_events(request: Request, db: Session = Depends(get_db)):
    """List events for current organization (properly secured)"""
    current_org = get_current_user_from_cookie(request, db)
    if not current_org:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Properly secured - only returns current org's data
    return {
        "organization_id": current_org.id,
        "events": [
            {"id": 1, "name": "Tech Conference 2024", "date": "2024-06-15", "status": "upcoming"},
            {"id": 2, "name": "Product Launch", "date": "2024-07-20", "status": "planning"},
        ]
    }

@app.get("/admin/api/stats", response_class=JSONResponse)
async def get_stats(request: Request, db: Session = Depends(get_db)):
    """Get statistics (properly secured)"""
    current_org = get_current_user_from_cookie(request, db)
    if not current_org:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "organization_id": current_org.id,
        "total_events": 2,
        "total_attendees": 150,
        "revenue": "$12,500"
    }

# ==================== HEALTH CHECK ====================

@app.get("/ping")
def ping():
    return {"status": "ok", "service": "eventflow-api"}

@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.3.1"}

# ==================== API DOCUMENTATION (INFO LEAK) ====================

@app.get("/api/docs", response_class=HTMLResponse)
async def api_docs(request: Request):
    return templates.TemplateResponse("api_docs.html", {"request": request})
