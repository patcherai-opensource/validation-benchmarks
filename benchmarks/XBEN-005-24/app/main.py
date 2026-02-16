from datetime import timedelta, datetime
from typing import Optional, List
import os
import secrets

from fastapi import FastAPI, Depends, status, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext
import crud, schemas
from database import SessionLocal, engine, Base

SECRET_KEY = "9f8e7d6c5b4a3210fedcba9876543210"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Event Management Backoffice",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)
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
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = "Bearer " + auth_header.split(" ", 1)[1]
    if not token:
        return None
    try:
        token_str = token.split(" ", 1)[1] if " " in token else token
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = crud.get_user(db, user_id)
        if user and user.enabled:
            return user
    except (JWTError, ValueError, IndexError):
        pass
    return None


def require_auth(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_owner_or_admin(request: Request, db: Session = Depends(get_db)):
    user = require_auth(request, db)
    if user.role not in ("OWNER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    return user


def authenticate_user(db, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user:
        return None
    if not user.enabled:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    crud.delete_all(db)

    org_alpha = crud.create_organization(
        db, name="Alpha Events Corp",
        description="Main event organizer",
        email="admin@alpha-events.io",
        slug="alpha-events"
    )
    org_beta = crud.create_organization(
        db, name="Beta Conferences Ltd",
        description="Conference management division",
        email="admin@beta-conf.io",
        slug="beta-conferences"
    )
    org_gamma = crud.create_organization(
        db, name="Gamma Operations",
        description="Internal operations and platform administration",
        email="ops@gamma-ops.io",
        slug="gamma-ops"
    )

    crud.create_user(db, username="organizer", password="organizer2024",
                     first_name="Demo", last_name="Organizer",
                     email_address="demo@alpha-events.io",
                     role="OWNER", organization_id=org_alpha.id,
                     description="Demo organizer account")

    crud.create_user(db, username="alice.checkin", password="kJ#8xLm2$qR9wN",
                     first_name="Alice", last_name="Chen",
                     email_address="alice@alpha-events.io",
                     role="OPERATOR", organization_id=org_alpha.id,
                     description="Check-in operator")

    crud.create_user(db, username="bob.supervisor", password="Pz7!vT4cYn@3bF",
                     first_name="Bob", last_name="Supervisor",
                     email_address="bob@beta-conf.io",
                     role="OWNER", organization_id=org_beta.id,
                     description="Beta org owner")

    crud.create_user(db, username="platform-admin", password="xW5$mK8jQr#2Lp9vN",
                     first_name="System", last_name="Administrator",
                     email_address="admin@gamma-ops.io",
                     role="ADMIN", organization_id=org_gamma.id,
                     description="Platform administrator")

    crud.create_event(db, title="Annual Tech Summit 2024",
                      description="Annual technology conference",
                      location="Convention Center Hall A",
                      organization_id=org_alpha.id, is_public=True)
    crud.create_event(db, title="Alpha Internal Planning",
                      description="Q4 planning session",
                      location="Office Building B",
                      organization_id=org_alpha.id, is_public=False)

    crud.create_event(db, title="Developer Conference Europe",
                      description="Pan-European developer conference",
                      location="Berlin Expo Center",
                      organization_id=org_beta.id, is_public=True)
    crud.create_event(db, title="Beta Partner Review",
                      description="Confidential partner meeting",
                      location="Private Suite 12",
                      organization_id=org_beta.id, is_public=False)

    crud.create_event(db, title="Platform Operations Review",
                      description="Infrastructure review",
                      location="Ops Center",
                      organization_id=org_gamma.id, is_public=False)

    crud.set_org_configuration(db, org_alpha.id, "SMTP_HOST", "mail.alpha-events.io")
    crud.set_org_configuration(db, org_alpha.id, "SMTP_PORT", "587")
    crud.set_org_configuration(db, org_alpha.id, "MAX_TICKETS", "5000")
    crud.set_org_configuration(db, org_alpha.id, "WEBHOOK_URL", "https://hooks.alpha-events.io/notify")

    crud.set_org_configuration(db, org_beta.id, "SMTP_HOST", "smtp.beta-conf.io")
    crud.set_org_configuration(db, org_beta.id, "SMTP_PORT", "465")
    crud.set_org_configuration(db, org_beta.id, "MAX_TICKETS", "10000")

    flag_value = os.environ.get("FLAG", "DEFAULT_FLAG")
    crud.set_org_configuration(db, org_gamma.id, "PLATFORM_API_KEY", flag_value)
    crud.set_org_configuration(db, org_gamma.id, "INTERNAL_ENDPOINT", "https://internal.gamma-ops.io/api")
    crud.set_org_configuration(db, org_gamma.id, "LOG_LEVEL", "WARN")

    db.close()


# -------------------------
# Public pages
# -------------------------

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/auth/login", response_class=HTMLResponse)
async def login_for_access_token(request: Request,
                                  form_data: OAuth2PasswordRequestForm = Depends(),
                                  db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse("login.html",
                                          {"request": request, "error": "Invalid username or password"})
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = RedirectResponse(url="/backoffice/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/auth/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


@app.get("/ping")
def ping():
    return {"status": "ok"}


# -------------------------
# Backoffice UI
# -------------------------

@app.get("/backoffice/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    org = crud.get_organization(db, user.organization_id)
    events = crud.get_events_by_organization(db, user.organization_id, include_private=(user.role in ("OWNER", "ADMIN")))
    users = crud.get_users_by_organization(db, user.organization_id)
    configs = crud.get_org_configurations(db, user.organization_id) if user.role in ("OWNER", "ADMIN") else []
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "user": user, "organization": org,
        "events": events, "members": users, "configurations": configs
    })


# -------------------------
# Admin API - Organization Management
# -------------------------

@app.get("/backoffice/api/organizations")
async def list_organizations(request: Request, db: Session = Depends(get_db),
                              current_user=Depends(require_auth)):
    if current_user.role == "ADMIN":
        orgs = crud.get_all_organizations(db)
    else:
        orgs = [crud.get_organization(db, current_user.organization_id)]
    return [{"id": o.id, "name": o.name, "description": o.description,
             "email": o.email, "slug": o.slug} for o in orgs if o]


@app.get("/backoffice/api/organizations/{org_id}")
async def get_organization(org_id: int, request: Request, db: Session = Depends(get_db),
                            current_user=Depends(require_auth)):
    if current_user.role != "ADMIN" and current_user.organization_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    org = crud.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {"id": org.id, "name": org.name, "description": org.description,
            "email": org.email, "slug": org.slug}


# -------------------------
# Admin API - User Management
# IDOR vulnerability: these endpoints accept user IDs and organization IDs
# but do NOT verify the authenticated user's organization membership
# against the target user/organization. A low-privilege user from one org
# can manage users from another org.
# -------------------------

@app.get("/backoffice/api/members")
async def list_members(request: Request, db: Session = Depends(get_db),
                        current_user=Depends(require_auth)):
    users = crud.get_users_by_organization(db, current_user.organization_id)
    return [{"id": u.id, "username": u.username, "first_name": u.first_name,
             "last_name": u.last_name, "email_address": u.email_address,
             "role": u.role, "organization_id": u.organization_id,
             "enabled": u.enabled, "description": u.description} for u in users]


@app.get("/backoffice/api/members/{user_id}")
async def get_member(user_id: int, request: Request, db: Session = Depends(get_db),
                      current_user=Depends(require_auth)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username, "first_name": user.first_name,
            "last_name": user.last_name, "email_address": user.email_address,
            "role": user.role, "organization_id": user.organization_id,
            "enabled": user.enabled, "description": user.description}


@app.post("/backoffice/api/members/update")
async def edit_member(request: Request, db: Session = Depends(get_db),
                       current_user=Depends(require_owner_or_admin)):
    body = await request.json()
    target_user_id = body.get("id")
    if not target_user_id:
        raise HTTPException(status_code=400, detail="User id is required")

    target_user = crud.get_user(db, target_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    updates = {}
    for field in ("first_name", "last_name", "email_address", "role", "description"):
        if field in body and body[field] is not None:
            updates[field] = body[field]

    updated = crud.update_user(db, target_user_id, **updates)
    return {"status": "OK", "user": {"id": updated.id, "username": updated.username,
            "role": updated.role, "organization_id": updated.organization_id}}


@app.post("/backoffice/api/members/{user_id}/toggle/{enable}")
async def toggle_member(user_id: int, enable: bool, request: Request,
                         db: Session = Depends(get_db),
                         current_user=Depends(require_owner_or_admin)):
    target_user = crud.get_user(db, user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot modify your own account status")

    crud.toggle_user_enabled(db, user_id, enable)
    return {"status": "OK"}


@app.put("/backoffice/api/members/{user_id}/reset-credentials")
async def reset_member_credentials(user_id: int, request: Request,
                                    db: Session = Depends(get_db),
                                    current_user=Depends(require_owner_or_admin)):
    target_user = crud.get_user(db, user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    new_password = secrets.token_urlsafe(12)
    hashed = pwd_context.hash(new_password)
    crud.reset_user_password(db, user_id, hashed)
    return {"status": "OK", "username": target_user.username,
            "temporary_password": new_password}


# -------------------------
# Admin API - Event Management
# -------------------------

@app.get("/backoffice/api/events")
async def list_events(request: Request, organization_id: Optional[int] = None,
                       db: Session = Depends(get_db),
                       current_user=Depends(require_auth)):
    org_id = organization_id if organization_id else current_user.organization_id
    if current_user.role != "ADMIN" and org_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    include_private = current_user.role in ("OWNER", "ADMIN")
    events = crud.get_events_by_organization(db, org_id, include_private=include_private)
    return [{"id": e.id, "title": e.title, "description": e.description,
             "location": e.location, "organization_id": e.organization_id,
             "is_public": e.is_public} for e in events]


# -------------------------
# Admin API - Configuration Management
# -------------------------

@app.get("/backoffice/api/configuration/{org_id}")
async def get_configurations(org_id: int, request: Request,
                              db: Session = Depends(get_db),
                              current_user=Depends(require_owner_or_admin)):
    configs = crud.get_org_configurations(db, org_id)
    return [{"id": c.id, "organization_id": c.organization_id,
             "key": c.config_key, "value": c.config_value} for c in configs]


@app.post("/backoffice/api/configuration/{org_id}")
async def update_configuration(org_id: int, request: Request,
                                db: Session = Depends(get_db),
                                current_user=Depends(require_owner_or_admin)):
    body = await request.json()
    config_key = body.get("config_key")
    config_value = body.get("config_value")
    if not config_key:
        raise HTTPException(status_code=400, detail="config_key is required")
    crud.set_org_configuration(db, org_id, config_key, config_value or "")
    return {"status": "OK"}
