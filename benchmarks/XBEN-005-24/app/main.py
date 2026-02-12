from datetime import timedelta, datetime
from typing import Optional
import os

from fastapi import FastAPI, Depends, status, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext

import crud
import schemas
from database import SessionLocal, engine, Base
from models import User, Organization

SECRET_KEY = "k8s-alfio-production-secret-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="alf.io",
    description="The open source ticket reservation system",
    version="2.0-M4-2303",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
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
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user:
        return None
    if not user.enabled:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = "Bearer " + auth_header.split(" ", 1)[1]
    if not token:
        return None
    try:
        token_value = token.split(" ", 1)[1] if " " in token else token
        payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        user = crud.get_user(db, int(user_id))
        if user is None or not user.enabled:
            return None
        return user
    except (JWTError, ValueError, IndexError):
        return None


def require_auth(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_admin_or_owner(request: Request, db: Session = Depends(get_db)):
    user = require_auth(request, db)
    if user.role not in ("ADMIN", "OWNER"):
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    return user


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    crud.delete_all(db)

    # Create organizations
    org1 = crud.create_organization(db, schemas.OrganizationCreate(
        name="Platform Operations",
        slug="platform-ops",
        description="Internal platform administration",
        email="admin@platform-ops.io",
    ))
    org2 = crud.create_organization(db, schemas.OrganizationCreate(
        name="Acme Conferences",
        slug="acme-conferences",
        description="Event management for Acme Corp",
        email="events@acme-conferences.com",
    ))
    org3 = crud.create_organization(db, schemas.OrganizationCreate(
        name="TechSummit Events",
        slug="techsummit",
        description="Technology conference organizer",
        email="info@techsummit-events.com",
    ))

    # Create users across organizations
    # Org1: Platform Ops - admin and operator
    crud.create_user(db, schemas.UserCreate(
        username="admin",
        first_name="System",
        last_name="Administrator",
        email_address="admin@platform-ops.io",
        password="Xk9#mP2$vL5nQ8",
        role="ADMIN",
        organization_id=org1.id,
    ))
    crud.create_user(db, schemas.UserCreate(
        username="ops_support",
        first_name="Support",
        last_name="Staff",
        email_address="support@platform-ops.io",
        password="sUp0rt!2024sEcure",
        role="OPERATOR",
        organization_id=org1.id,
    ))

    # Org2: Acme Conferences - owner and operator
    crud.create_user(db, schemas.UserCreate(
        username="acme_owner",
        first_name="Jane",
        last_name="Mitchell",
        email_address="jane.mitchell@acme-conferences.com",
        password="AcmE!0wner2024Sec",
        role="OWNER",
        organization_id=org2.id,
    ))
    crud.create_user(db, schemas.UserCreate(
        username="acme_operator",
        first_name="Bob",
        last_name="Wilson",
        email_address="bob.wilson@acme-conferences.com",
        password="operator",
        role="OPERATOR",
        organization_id=org2.id,
    ))

    # Org3: TechSummit - owner and operator
    crud.create_user(db, schemas.UserCreate(
        username="ts_manager",
        first_name="Alice",
        last_name="Chen",
        email_address="alice.chen@techsummit-events.com",
        password="TsMgr#SecP@ss99",
        role="OWNER",
        organization_id=org3.id,
    ))
    crud.create_user(db, schemas.UserCreate(
        username="ts_staff",
        first_name="Dave",
        last_name="Brown",
        email_address="dave.brown@techsummit-events.com",
        password="staff2024",
        role="OPERATOR",
        organization_id=org3.id,
    ))

    # Create events
    crud.create_event(db, schemas.EventCreate(
        short_name="spring-conf-2024",
        display_name="Spring Conference 2024",
        description="Annual Spring developer conference",
        location="San Francisco, CA",
        organization_id=org2.id,
    ))
    crud.create_event(db, schemas.EventCreate(
        short_name="tech-summit-q3",
        display_name="Tech Summit Q3 2024",
        description="Quarterly technology summit",
        location="Austin, TX",
        organization_id=org3.id,
    ))
    crud.create_event(db, schemas.EventCreate(
        short_name="platform-internal",
        display_name="Platform Internal Review",
        description="Internal platform review event",
        location="Virtual",
        organization_id=org1.id,
    ))

    # Configuration entries
    crud.set_configuration(db, "SMTP_HOST", "smtp.platform-ops.io", "SMTP server hostname")
    crud.set_configuration(db, "SMTP_PORT", "587", "SMTP server port")
    crud.set_configuration(db, "BASE_URL", "https://events.platform-ops.io", "Base application URL")
    crud.set_configuration(db, "MAPS_API_KEY", "gm-pk-a8f3e2d1c0b9", "Maps provider API key")

    flag = os.environ.get("FLAG", "DEFAULT_FLAG")
    crud.set_configuration(
        db,
        "PAYMENT_GATEWAY_SECRET",
        flag,
        "Stripe payment gateway secret key",
        org_id=org1.id,
    )
    crud.set_configuration(db, "WEBHOOK_SECRET", "whsec_a1b2c3d4e5f6", "Webhook signing secret", org_id=org2.id)
    crud.set_configuration(db, "ANALYTICS_KEY", "UA-12345678-1", "Analytics tracking key", org_id=org3.id)

    # Create API keys
    crud.create_api_key(db, org1.id, "Platform monitoring")
    crud.create_api_key(db, org2.id, "Acme integration")

    db.close()


# ============================================================
# Authentication endpoints
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/admin/authenticate", response_class=HTMLResponse)
async def authenticate(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Bad credentials"},
            status_code=401,
        )
    access_token = create_access_token(
        data={"sub": str(user.id), "org": user.organization_id, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    response = RedirectResponse(
        url=f"/admin/organizations/{user.organization_id}/dashboard",
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/admin/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


# ============================================================
# Dashboard / Organization views (HTML)
# ============================================================

@app.get("/admin/organizations/{org_id}/dashboard", response_class=HTMLResponse)
async def org_dashboard(
    request: Request,
    org_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if current_user.organization_id != org_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")
    org = crud.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    events = crud.get_events_by_organization(db, org_id)
    users = crud.get_users_by_organization(db, org_id)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "organization": org,
        "events": events,
        "users": users,
        "current_user": current_user,
    })


@app.get("/admin/organizations/{org_id}/users", response_class=HTMLResponse)
async def org_users_page(
    request: Request,
    org_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if current_user.organization_id != org_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")
    org = crud.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    users = crud.get_users_by_organization(db, org_id)
    return templates.TemplateResponse("users.html", {
        "request": request,
        "organization": org,
        "users": users,
        "current_user": current_user,
    })


@app.get("/admin/organizations/{org_id}/configuration", response_class=HTMLResponse)
async def org_configuration_page(
    request: Request,
    org_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if current_user.organization_id != org_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")
    org = crud.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    configs = crud.get_configurations(db, org_id=org_id)
    return templates.TemplateResponse("configuration.html", {
        "request": request,
        "organization": org,
        "configurations": configs,
        "current_user": current_user,
    })


# ============================================================
# Admin API - Organizations
# ============================================================

@app.get("/admin/api/organizations")
async def list_organizations(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if current_user.role == "ADMIN":
        return [schemas.OrganizationOut.from_orm(o) for o in crud.get_all_organizations(db)]
    org = crud.get_organization(db, current_user.organization_id)
    return [schemas.OrganizationOut.from_orm(org)] if org else []


@app.get("/admin/api/organizations/{org_id}")
async def get_organization(
    org_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if current_user.organization_id != org_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")
    org = crud.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return schemas.OrganizationOut.from_orm(org)


# ============================================================
# Admin API - Users
# ============================================================

@app.get("/admin/api/users")
async def list_users(
    organization_id: Optional[int] = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if organization_id is not None:
        users = crud.get_users_by_organization(db, organization_id)
    else:
        users = crud.get_users_by_organization(db, current_user.organization_id)
    return [schemas.UserOut.from_orm(u) for u in users]


@app.get("/admin/api/users/{user_id}")
async def get_user(
    user_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserOut.from_orm(user)


@app.post("/admin/api/users")
async def insert_user(
    user_data: schemas.UserCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if current_user.role not in ("ADMIN", "OWNER"):
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    existing = crud.get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")
    user = crud.create_user(db, user_data)
    return schemas.UserOut.from_orm(user)


@app.post("/admin/api/users/{user_id}/edit")
async def edit_user(
    user_id: int,
    update_data: schemas.UserUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    user = crud.update_user(db, user_id, update_data.dict(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserOut.from_orm(user)


@app.post("/admin/api/users/{user_id}/enable/{enable}")
async def toggle_user(
    user_id: int,
    enable: bool,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    user = crud.enable_user(db, user_id, enable)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "OK"}


@app.put("/admin/api/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    temp_password = crud.reset_password(db, user_id)
    if not temp_password:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.PasswordResetResponse(temporary_password=temp_password)


@app.delete("/admin/api/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if current_user.role not in ("ADMIN", "OWNER"):
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete own account")
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "OK"}


# ============================================================
# Admin API - Events
# ============================================================

@app.get("/admin/api/events")
async def list_events(
    organization_id: Optional[int] = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    org_id = organization_id if organization_id else current_user.organization_id
    if current_user.organization_id != org_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")
    return [schemas.EventOut.from_orm(e) for e in crud.get_events_by_organization(db, org_id)]


@app.get("/admin/api/events/{event_id}")
async def get_event(
    event_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    event = crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if current_user.organization_id != event.organization_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")
    return schemas.EventOut.from_orm(event)


# ============================================================
# Admin API - Configuration
# ============================================================

@app.get("/admin/api/configuration")
async def list_configuration(
    organization_id: Optional[int] = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    org_id = organization_id if organization_id else current_user.organization_id
    if current_user.organization_id != org_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")
    configs = crud.get_configurations(db, org_id=org_id)
    return [schemas.ConfigurationOut.from_orm(c) for c in configs]


# ============================================================
# Admin API - API Keys
# ============================================================

@app.post("/admin/api/v1/organizations/{org_id}/apikey")
async def create_api_key_for_org(
    org_id: int,
    current_user: User = Depends(require_admin_or_owner),
    db: Session = Depends(get_db),
):
    org = crud.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    key = crud.create_api_key(db, org_id, f"Generated by {current_user.username}")
    return {"api_key": key.api_key, "organization_id": org_id}


@app.get("/admin/api/v1/organizations/{org_id}/apikeys")
async def list_api_keys_for_org(
    org_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    if current_user.organization_id != org_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")
    keys = crud.get_api_keys_by_organization(db, org_id)
    return [{"id": k.id, "api_key": k.api_key[:8] + "...", "description": k.description, "enabled": k.enabled} for k in keys]


# ============================================================
# Health check
# ============================================================

@app.get("/ping")
def ping():
    return {"status": "ok"}
