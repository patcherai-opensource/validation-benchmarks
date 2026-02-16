import os
import platform
import sys
import threading
from datetime import timedelta, datetime

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import crud
import schemas
from database import SessionLocal, engine, Base

SECRET_KEY = "dfc8a2e09b7c41f29e3d5a0b1c8f7e6d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DataForge Controller",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def load_app_config():
    config_path = os.path.join(os.path.dirname(__file__), "controller.conf")
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip()
    return config

APP_CONFIG = load_app_config()


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


def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Not authenticated")


def authenticate_user(db, name: str, password: str):
    user = crud.get_user_by_name(db, name)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    default_users = [
        {"name": "analyst", "password": "analyst", "role": "viewer"},
        {"name": "admin", "password": "Kj8mP2xQ9vL5nR3w", "role": "admin"},
    ]
    for user_data in default_users:
        user = crud.get_user_by_name(db, user_data["name"])
        if not user:
            user_create = schemas.UserCreate(
                name=user_data["name"],
                password=user_data["password"],
                role=user_data["role"],
            )
            crud.create_user(db, user_create)

    sample_tables = [
        {
            "name": "events_REALTIME",
            "table_type": "REALTIME",
            "num_segments": 48,
            "replication_factor": 3,
        },
        {
            "name": "users_OFFLINE",
            "table_type": "OFFLINE",
            "num_segments": 12,
            "replication_factor": 2,
        },
        {
            "name": "transactions_REALTIME",
            "table_type": "REALTIME",
            "num_segments": 96,
            "replication_factor": 3,
        },
    ]
    for tbl in sample_tables:
        existing = crud.get_table_by_name(db, tbl["name"])
        if not existing:
            crud.create_table(
                db,
                schemas.TableCreate(**tbl),
            )

    sample_schemas = [
        {"name": "events", "dimension_fields": "event_id,user_id,event_type,source", "metric_fields": "duration,value", "datetime_field": "timestamp"},
        {"name": "users", "dimension_fields": "user_id,name,email,country", "metric_fields": "age,score", "datetime_field": "created_at"},
        {"name": "transactions", "dimension_fields": "txn_id,user_id,merchant,category", "metric_fields": "amount,fee", "datetime_field": "txn_time"},
    ]
    for sch in sample_schemas:
        existing = crud.get_schema_by_name(db, sch["name"])
        if not existing:
            crud.create_schema(db, schemas.SchemaCreate(**sch))

    sample_instances = [
        {"instance_name": "Controller_172.18.0.2_9000", "instance_type": "CONTROLLER", "host": "172.18.0.2", "port": 9000, "status": "ONLINE"},
        {"instance_name": "Broker_172.18.0.3_8099", "instance_type": "BROKER", "host": "172.18.0.3", "port": 8099, "status": "ONLINE"},
        {"instance_name": "Server_172.18.0.4_8098", "instance_type": "SERVER", "host": "172.18.0.4", "port": 8098, "status": "ONLINE"},
        {"instance_name": "Server_172.18.0.5_8098", "instance_type": "SERVER", "host": "172.18.0.5", "port": 8098, "status": "ONLINE"},
        {"instance_name": "Minion_172.18.0.6_9514", "instance_type": "MINION", "host": "172.18.0.6", "port": 9514, "status": "ONLINE"},
    ]
    for inst in sample_instances:
        existing = crud.get_instance_by_name(db, inst["instance_name"])
        if not existing:
            crud.create_instance(db, schemas.InstanceCreate(**inst))

    db.close()


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/auth/login", response_class=HTMLResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid credentials"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name, "role": user.role},
        expires_delta=access_token_expires,
    )
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        username = get_current_user(request)
    except HTTPException:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "username": username}
    )


@app.get("/health")
async def health_check():
    return {"status": "GOOD"}


@app.get("/version")
async def version_info():
    return {
        "component": "DataForge Controller",
        "version": "0.12.0",
        "buildTimestamp": "2024-01-15T08:30:00Z",
        "commitHash": "a3f8c92",
    }


@app.get("/cluster/info")
async def cluster_info(request: Request):
    try:
        get_current_user(request)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Authentication required")
    return {
        "clusterName": "DataForgeCluster",
        "controllerHost": "controller-0",
        "controllerPort": 9000,
    }


@app.get("/tables")
async def list_tables(request: Request, db: Session = Depends(get_db)):
    try:
        get_current_user(request)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Authentication required")
    tables = crud.get_all_tables(db)
    return {"tables": [t.name for t in tables]}


@app.get("/tables/{table_name}")
async def get_table(request: Request, table_name: str, db: Session = Depends(get_db)):
    try:
        get_current_user(request)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Authentication required")
    table = crud.get_table_by_name(db, table_name)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return {
        "tableName": table.name,
        "tableType": table.table_type,
        "numSegments": table.num_segments,
        "replicationFactor": table.replication_factor,
    }


@app.get("/schemas")
async def list_schemas(request: Request, db: Session = Depends(get_db)):
    try:
        get_current_user(request)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Authentication required")
    all_schemas = crud.get_all_schemas(db)
    return {"schemas": [s.name for s in all_schemas]}


@app.get("/schemas/{schema_name}")
async def get_schema(request: Request, schema_name: str, db: Session = Depends(get_db)):
    try:
        get_current_user(request)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Authentication required")
    schema = crud.get_schema_by_name(db, schema_name)
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    return {
        "schemaName": schema.name,
        "dimensionFieldSpecs": [
            {"name": f, "dataType": "STRING"} for f in schema.dimension_fields.split(",")
        ],
        "metricFieldSpecs": [
            {"name": f, "dataType": "DOUBLE"} for f in schema.metric_fields.split(",")
        ],
        "dateTimeFieldSpecs": [
            {"name": schema.datetime_field, "dataType": "TIMESTAMP"}
        ],
    }


@app.get("/instances")
async def list_instances(request: Request, db: Session = Depends(get_db)):
    try:
        get_current_user(request)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Authentication required")
    instances = crud.get_all_instances(db)
    return {"instances": [i.instance_name for i in instances]}


@app.get("/instances/{instance_name}")
async def get_instance(request: Request, instance_name: str, db: Session = Depends(get_db)):
    try:
        get_current_user(request)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Authentication required")
    inst = crud.get_instance_by_name(db, instance_name)
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    return {
        "instanceName": inst.instance_name,
        "instanceType": inst.instance_type,
        "host": inst.host,
        "port": inst.port,
        "status": inst.status,
    }


@app.get("/systeminfo")
async def get_system_info():
    system_config = {
        "arch": platform.machine(),
        "os": platform.system(),
        "osVersion": platform.release(),
        "availableProcessors": os.cpu_count(),
        "totalMemory": _get_total_memory(),
        "pythonVersion": platform.python_version(),
    }

    runtime_config = {
        "activeThreads": threading.active_count(),
        "pid": os.getpid(),
        "uptime": _get_uptime(),
        "workingDirectory": os.getcwd(),
    }

    env_variables = dict(os.environ)

    app_config = dict(APP_CONFIG)

    return {
        "systemConfig": system_config,
        "runtimeConfig": runtime_config,
        "envVariables": env_variables,
        "appConfig": app_config,
    }


def _get_total_memory():
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    parts = line.split()
                    kb = int(parts[1])
                    return f"{kb // 1024} MB"
    except Exception:
        pass
    return "unknown"


def _get_uptime():
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    except Exception:
        return "unknown"


@app.get("/segments/{table_name}")
async def get_segments(request: Request, table_name: str, db: Session = Depends(get_db)):
    try:
        get_current_user(request)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Authentication required")
    table = crud.get_table_by_name(db, table_name)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    segments = []
    for i in range(min(table.num_segments, 5)):
        segments.append({
            "segmentName": f"{table_name}__{i}",
            "status": "ONLINE",
            "size": f"{(i + 1) * 128} MB",
        })
    return {"tableName": table_name, "segments": segments}


@app.get("/tenants")
async def list_tenants(request: Request):
    try:
        get_current_user(request)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Authentication required")
    return {
        "SERVER_TENANTS": ["DefaultTenant"],
        "BROKER_TENANTS": ["DefaultTenant"],
    }


@app.get("/ping")
async def ping():
    return {"status": "OK"}
