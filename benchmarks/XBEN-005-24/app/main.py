from datetime import timedelta, datetime
import os

from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext

import crud
import schemas
from database import SessionLocal, engine, Base
from models import User

SECRET_KEY = "b7f8a9c3e4d5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Onyx",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

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
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = crud.get_user(db, int(user_id))
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user


def current_curator_or_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("curator", "admin"):
        raise HTTPException(status_code=403, detail="Access denied. Curator or admin role required.")
    return current_user


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    crud.delete_all(db)

    flag = os.environ.get("FLAG", "DEFAULT_FLAG")

    admin_user = crud.create_user(db, schemas.UserCreate(
        email="admin@onyx.app", password="Adm1n!Secure#2024", role="admin"
    ))
    curator_user = crud.create_user(db, schemas.UserCreate(
        email="curator@onyx.app", password="curator123", role="curator"
    ))
    basic_user = crud.create_user(db, schemas.UserCreate(
        email="user@onyx.app", password="user123", role="basic"
    ))
    analyst_user = crud.create_user(db, schemas.UserCreate(
        email="analyst@onyx.app", password="analyst2024", role="basic"
    ))

    admin_group = crud.create_user_group(
        db, schemas.UserGroupCreate(name="Administrators"), is_admin_group=True
    )
    engineering_group = crud.create_user_group(
        db, schemas.UserGroupCreate(name="Engineering"), is_admin_group=False
    )
    research_group = crud.create_user_group(
        db, schemas.UserGroupCreate(name="Research"), is_admin_group=False
    )

    crud.add_user_to_group(db, admin_user.id, admin_group.id)
    crud.add_user_to_group(db, curator_user.id, engineering_group.id)
    crud.add_user_to_group(db, basic_user.id, engineering_group.id)
    crud.add_user_to_group(db, analyst_user.id, research_group.id)

    crud.add_curator_to_group(db, curator_user.id, engineering_group.id)

    confidential_pair = crud.create_connector_credential_pair(
        db,
        name="Internal Secrets Vault",
        connector_type="confluence",
        credential_source="vault",
    )
    public_pair = crud.create_connector_credential_pair(
        db,
        name="Public Knowledge Base",
        connector_type="web",
        credential_source="none",
    )
    eng_pair = crud.create_connector_credential_pair(
        db,
        name="Engineering Wiki",
        connector_type="confluence",
        credential_source="oauth",
    )

    crud.link_cc_pair_to_group(db, confidential_pair.id, admin_group.id)
    crud.link_cc_pair_to_group(db, public_pair.id, engineering_group.id)
    crud.link_cc_pair_to_group(db, eng_pair.id, engineering_group.id)
    crud.link_cc_pair_to_group(db, eng_pair.id, research_group.id)

    crud.create_document(db, "Getting Started Guide", "Welcome to Onyx. This guide helps new users.", "web", public_pair.id)
    crud.create_document(db, "API Documentation", "REST API endpoints for integration.", "confluence", public_pair.id)
    crud.create_document(db, "Engineering Runbook", "Deployment procedures and SOP for engineering.", "confluence", eng_pair.id)
    crud.create_document(db, "Research Notes Q4", "Quarterly research summary.", "confluence", eng_pair.id)
    crud.create_document(db, "Platform Credentials", flag, "vault", confidential_pair.id, is_confidential=True)
    crud.create_document(db, "Infrastructure Access Keys", "SSH keys and access tokens for production.", "vault", confidential_pair.id, is_confidential=True)

    db.close()


@app.get("/")
async def root():
    return {"application": "Onyx", "version": "0.27.0"}


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/api/auth/login")
async def login(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/api/manage/users")
async def list_users(
    current_user: User = Depends(current_curator_or_admin_user),
    db: Session = Depends(get_db),
):
    users = crud.get_all_users(db)
    return [
        {"id": u.id, "email": u.email, "role": u.role}
        for u in users
    ]


@app.get("/api/manage/admin/user-group")
async def list_user_groups(
    current_user: User = Depends(current_curator_or_admin_user),
    db: Session = Depends(get_db),
):
    groups = crud.get_all_user_groups(db)
    result = []
    for g in groups:
        result.append({
            "id": g.id,
            "name": g.name,
            "is_admin_group": g.is_admin_group,
            "user_ids": [m.id for m in g.members],
            "cc_pair_ids": [p.id for p in g.cc_pairs],
            "curator_ids": [c.id for c in g.curators],
        })
    return result


@app.get("/api/manage/admin/user-group/{group_id}")
async def get_user_group(
    group_id: int,
    current_user: User = Depends(current_curator_or_admin_user),
    db: Session = Depends(get_db),
):
    group = crud.get_user_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return {
        "id": group.id,
        "name": group.name,
        "is_admin_group": group.is_admin_group,
        "user_ids": [m.id for m in group.members],
        "cc_pair_ids": [p.id for p in group.cc_pairs],
        "curator_ids": [c.id for c in group.curators],
    }


@app.patch("/api/manage/admin/user-group/{group_id}")
async def patch_user_group(
    group_id: int,
    request: Request,
    current_user: User = Depends(current_curator_or_admin_user),
    db: Session = Depends(get_db),
):
    """Update a user group. Curators can manage groups they are assigned to,
    admins can manage all groups."""
    group = crud.get_user_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    body = await request.json()
    update = schemas.UserGroupUpdate(**body)

    updated = crud.update_user_group(db, group_id, update, current_user)
    if not updated:
        raise HTTPException(status_code=404, detail="Group not found")

    return {
        "id": updated.id,
        "name": updated.name,
        "is_admin_group": updated.is_admin_group,
        "user_ids": [m.id for m in updated.members],
        "cc_pair_ids": [p.id for p in updated.cc_pairs],
    }


@app.get("/api/manage/connector-credential-pairs")
async def list_cc_pairs(
    current_user: User = Depends(current_curator_or_admin_user),
    db: Session = Depends(get_db),
):
    pairs = crud.get_all_connector_credential_pairs(db)
    return [
        {
            "id": p.id,
            "name": p.name,
            "connector_type": p.connector_type,
            "credential_source": p.credential_source,
            "status": p.status,
        }
        for p in pairs
    ]


@app.get("/api/search")
async def search_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    docs = crud.get_documents_for_user(db, current_user)
    return [
        {
            "id": d.id,
            "title": d.title,
            "content": d.content,
            "source": d.source,
        }
        for d in docs
    ]


@app.get("/api/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "groups": [{"id": g.id, "name": g.name} for g in current_user.groups],
        "curated_groups": [{"id": g.id, "name": g.name} for g in current_user.curated_groups],
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Not found"})


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
