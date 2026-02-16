from datetime import timedelta, datetime
from typing import Optional
import os

from fastapi import FastAPI, Depends, status, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext
import crud, schemas
from database import SessionLocal, engine, Base

SECRET_KEY = "a7b3f91e-c248-4d7a-9e5b-2f8a1c6d0e3b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Onyx Document Platform",
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
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if token.startswith("Bearer "):
        token = token[7:]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_curator_or_admin(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role not in ("admin", "curator", "global_curator"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user


def require_admin(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


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

    admin_user = crud.create_user(db, email="admin@onyx.dev", password="Kj8#mP2$vL9nQ", role="admin")
    curator_user = crud.create_user(db, email="curator@onyx.dev", password="curator", role="curator")
    basic_user = crud.create_user(db, email="user@onyx.dev", password="userpass123", role="basic")
    analyst_user = crud.create_user(db, email="analyst@onyx.dev", password="4n4lyst!2024", role="basic")

    admin_team = crud.create_team(db, name="Platform Administrators", description="Full platform access team")
    engineering_team = crud.create_team(db, name="Engineering", description="Engineering department team")
    research_team = crud.create_team(db, name="Research", description="Research department team")

    crud.add_team_member(db, team_id=admin_team.id, user_id=admin_user.id, is_curator=True)
    crud.add_team_member(db, team_id=engineering_team.id, user_id=curator_user.id, is_curator=True)
    crud.add_team_member(db, team_id=engineering_team.id, user_id=basic_user.id, is_curator=False)
    crud.add_team_member(db, team_id=research_team.id, user_id=analyst_user.id, is_curator=False)
    crud.add_team_member(db, team_id=research_team.id, user_id=curator_user.id, is_curator=False)

    admin_collection = crud.create_collection(db, name="Platform Secrets", description="Confidential platform credentials and keys", access_type="private")
    eng_collection = crud.create_collection(db, name="Engineering Docs", description="Engineering documentation", access_type="private")
    public_collection = crud.create_collection(db, name="Company Handbook", description="General company information", access_type="public")
    research_collection = crud.create_collection(db, name="Research Papers", description="Internal research papers", access_type="private")

    crud.link_team_collection(db, team_id=admin_team.id, collection_id=admin_collection.id)
    crud.link_team_collection(db, team_id=engineering_team.id, collection_id=eng_collection.id)
    crud.link_team_collection(db, team_id=research_team.id, collection_id=research_collection.id)

    crud.create_document(db, title="Platform API Keys", content=flag, collection_id=admin_collection.id)
    crud.create_document(db, title="Infrastructure Access Policy", content="All infrastructure credentials must be rotated quarterly. Contact the platform team for access requests.", collection_id=admin_collection.id)
    crud.create_document(db, title="Architecture Overview", content="The platform uses a microservices architecture with FastAPI backends and React frontends.", collection_id=eng_collection.id)
    crud.create_document(db, title="Development Setup Guide", content="Clone the repository, run docker-compose up, and navigate to http://localhost:3000", collection_id=eng_collection.id)
    crud.create_document(db, title="Onboarding Guide", content="Welcome to Onyx! Please review the company handbook and complete your compliance training.", collection_id=public_collection.id)
    crud.create_document(db, title="Code of Conduct", content="All employees are expected to maintain professional conduct.", collection_id=public_collection.id)
    crud.create_document(db, title="Q4 Research Summary", content="Research findings from Q4 indicate promising results in retrieval-augmented generation.", collection_id=research_collection.id)

    db.close()


@app.get("/")
async def root():
    return {
        "application": "Onyx Document Platform",
        "version": "0.27.0",
        "status": "running",
        "documentation": "/api/info",
    }


@app.get("/api/info")
async def api_info():
    return {
        "application": "Onyx Document Platform",
        "version": "0.27.0",
        "description": "Enterprise document management and knowledge platform",
        "authentication": {
            "method": "Bearer token",
            "login_endpoint": "POST /api/auth/login",
            "body_format": {"email": "string", "password": "string"},
        },
        "demo_accounts": [
            {"email": "curator@onyx.dev", "password": "curator", "role": "curator"},
            {"email": "user@onyx.dev", "password": "userpass123", "role": "basic"},
        ],
        "api_endpoints": [
            "GET /api/users/me",
            "GET /api/admin/team",
            "GET /api/admin/team/{team_id}",
            "PATCH /api/admin/team/{team_id}",
            "POST /api/admin/team",
            "DELETE /api/admin/team/{team_id}",
            "GET /api/document-collections",
            "GET /api/document-collections/{collection_id}/documents",
        ],
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.post("/api/auth/login")
async def login(login_req: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_req.email, login_req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        },
    }


@app.get("/api/users/me")
async def get_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }


@app.get("/api/admin/team")
async def list_teams(
    current_user=Depends(require_curator_or_admin),
    db: Session = Depends(get_db),
):
    if current_user.role == "admin":
        teams = crud.get_all_teams(db)
    else:
        teams = crud.get_teams_for_user(
            db,
            user_id=current_user.id,
            only_curator_teams=(current_user.role == "curator"),
        )

    result = []
    for team in teams:
        members = crud.get_team_members(db, team.id)
        collections = crud.get_collections_for_team(db, team.id)
        result.append({
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "is_up_to_date": team.is_up_to_date,
            "members": [
                {
                    "id": m.id,
                    "user_id": m.user_id,
                    "is_curator": m.is_curator,
                    "user": {
                        "id": m.user.id,
                        "email": m.user.email,
                        "role": m.user.role,
                    },
                }
                for m in members
            ],
            "collection_ids": [c.id for c in collections],
        })
    return result


@app.post("/api/admin/team")
async def create_team(
    team_create: schemas.TeamCreate,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    existing = db.query(crud.Team).filter(crud.Team.name == team_create.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Team with name '{team_create.name}' already exists.")

    team = crud.create_team(db, name=team_create.name)
    for uid in team_create.user_ids:
        crud.add_team_member(db, team_id=team.id, user_id=uid)
    for cid in team_create.collection_ids:
        crud.link_team_collection(db, team_id=team.id, collection_id=cid)

    return {"id": team.id, "name": team.name}


@app.patch("/api/admin/team/{team_id}")
async def update_team(
    team_id: int,
    team_update: schemas.TeamUpdate,
    current_user=Depends(require_curator_or_admin),
    db: Session = Depends(get_db),
):
    team = crud.get_team(db, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team with id '{team_id}' not found")

    if not team.is_up_to_date:
        raise HTTPException(
            status_code=409,
            detail="Team is currently syncing. Wait until the current sync has finished before editing.",
        )

    current_member_user_ids = set(m.user_id for m in team.members)
    updated_user_ids = set(team_update.user_ids)
    added_user_ids = updated_user_ids - current_member_user_ids
    removed_user_ids = current_member_user_ids - updated_user_ids

    for uid in removed_user_ids:
        crud.remove_team_member(db, team_id=team_id, user_id=uid)

    for uid in added_user_ids:
        user = crud.get_user(db, uid)
        if user is None:
            raise HTTPException(status_code=400, detail=f"User with id '{uid}' not found")
        crud.add_team_member(db, team_id=team_id, user_id=uid)

    current_collection_ids = set(
        link.collection_id for link in team.collection_links if link.is_current
    )
    updated_collection_ids = set(team_update.collection_ids)

    for cid in current_collection_ids - updated_collection_ids:
        crud.unlink_team_collection(db, team_id=team_id, collection_id=cid)

    for cid in updated_collection_ids - current_collection_ids:
        collection = crud.get_collection(db, cid)
        if collection is None:
            raise HTTPException(status_code=400, detail=f"Collection with id '{cid}' not found")
        crud.link_team_collection(db, team_id=team_id, collection_id=cid)

    team = crud.get_team(db, team_id)
    members = crud.get_team_members(db, team_id)
    collections = crud.get_collections_for_team(db, team_id)

    return {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "is_up_to_date": team.is_up_to_date,
        "members": [
            {
                "id": m.id,
                "user_id": m.user_id,
                "is_curator": m.is_curator,
            }
            for m in members
        ],
        "collection_ids": [c.id for c in collections],
    }


@app.delete("/api/admin/team/{team_id}")
async def delete_team(
    team_id: int,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    team = crud.get_team(db, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team with id '{team_id}' not found")
    db.delete(team)
    db.commit()
    return {"detail": "Team deleted"}


@app.get("/api/document-collections")
async def list_collections(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    collections = crud.get_accessible_collections_for_user(db, current_user.id)
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "access_type": c.access_type,
        }
        for c in collections
    ]


@app.get("/api/document-collections/{collection_id}/documents")
async def list_documents(
    collection_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accessible = crud.get_accessible_collections_for_user(db, current_user.id)
    accessible_ids = {c.id for c in accessible}

    if collection_id not in accessible_ids:
        raise HTTPException(status_code=403, detail="Access denied to this collection")

    documents = crud.get_documents_in_collection(db, collection_id)
    return [
        {
            "id": d.id,
            "title": d.title,
            "content": d.content,
            "collection_id": d.collection_id,
        }
        for d in documents
    ]


@app.get("/api/admin/team/{team_id}")
async def get_team_detail(
    team_id: int,
    current_user=Depends(require_curator_or_admin),
    db: Session = Depends(get_db),
):
    team = crud.get_team(db, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team with id '{team_id}' not found")

    members = crud.get_team_members(db, team_id)
    collections = crud.get_collections_for_team(db, team_id)

    return {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "is_up_to_date": team.is_up_to_date,
        "members": [
            {
                "id": m.id,
                "user_id": m.user_id,
                "is_curator": m.is_curator,
                "user": {
                    "id": m.user.id,
                    "email": m.user.email,
                    "role": m.user.role,
                },
            }
            for m in members
        ],
        "collection_ids": [c.id for c in collections],
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Not found"})


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
