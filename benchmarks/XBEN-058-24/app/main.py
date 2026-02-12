import os
import platform
from datetime import timedelta, datetime

from fastapi import FastAPI, Depends, HTTPException, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional

SECRET_KEY = "k8s-cluster-pinot-controller-9f3a2e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Application configuration loaded at startup
_app_config = {}

def load_app_config():
    """Load application configuration from config files and environment."""
    config = {}
    config_path = os.path.join(os.path.dirname(__file__), "conf", "pinot-controller.conf")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip()
    return config

app = FastAPI(
    title="Apache Pinot Controller",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user store (loaded at startup)
_users = {}
_tables = {}
_segments = {}
_cluster_name = "PinotCluster"


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(access_token: Optional[str] = Cookie(None)):
    """Extract current user from JWT cookie. Returns None if not authenticated."""
    if not access_token:
        return None
    try:
        token = access_token.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username and username in _users:
            return username
    except JWTError:
        pass
    return None


def require_auth(access_token: Optional[str] = Cookie(None)):
    """Require valid authentication. Raises 401 if not authenticated."""
    user = get_current_user(access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@app.on_event("startup")
async def startup_event():
    global _app_config, _users, _tables, _segments

    # Load configuration
    _app_config = load_app_config()

    # Initialize users
    _users["admin"] = {
        "username": "admin",
        "hashed_password": pwd_context.hash("PinotAdmin2023!"),
        "role": "ADMIN",
    }
    _users["readonly"] = {
        "username": "readonly",
        "hashed_password": pwd_context.hash("readonly"),
        "role": "READ_ONLY",
    }

    # Initialize sample tables
    _tables = {
        "airlineStats": {
            "tableName": "airlineStats_OFFLINE",
            "tableType": "OFFLINE",
            "segmentsConfig": {
                "replication": "1",
                "retentionTimeUnit": "DAYS",
                "retentionTimeValue": "365",
            },
            "tenants": {"broker": "DefaultTenant", "server": "DefaultTenant"},
            "metadata": {},
        },
        "githubEvents": {
            "tableName": "githubEvents_REALTIME",
            "tableType": "REALTIME",
            "segmentsConfig": {
                "replication": "1",
                "retentionTimeUnit": "HOURS",
                "retentionTimeValue": "72",
            },
            "tenants": {"broker": "DefaultTenant", "server": "DefaultTenant"},
            "metadata": {},
        },
        "starbucksStores": {
            "tableName": "starbucksStores_OFFLINE",
            "tableType": "OFFLINE",
            "segmentsConfig": {
                "replication": "1",
                "retentionTimeUnit": "DAYS",
                "retentionTimeValue": "30",
            },
            "tenants": {"broker": "DefaultTenant", "server": "DefaultTenant"},
            "metadata": {},
        },
    }

    _segments = {
        "airlineStats": ["airlineStats_OFFLINE_0", "airlineStats_OFFLINE_1"],
        "githubEvents": ["githubEvents_REALTIME_0"],
        "starbucksStores": ["starbucksStores_OFFLINE_0"],
    }


# ---- Public endpoints (no auth required) ----

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, access_token: Optional[str] = Cookie(None)):
    user = get_current_user(access_token)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/health")
async def health():
    return {"status": "GOOD"}


@app.get("/ping")
async def ping():
    return {"status": "OK"}


@app.get("/appconfigs")
async def get_app_configs():
    system_config = {
        "os.name": platform.system(),
        "os.version": platform.version(),
        "os.arch": platform.machine(),
        "java.version": "11.0.15",
        "java.vm.name": "OpenJDK 64-Bit Server VM",
    }

    runtime_config = {
        "availableProcessors": os.cpu_count(),
        "totalMemory": "2147483648",
        "maxMemory": "4294967296",
        "freeMemory": "1073741824",
    }

    pinot_config = dict(_app_config)

    return {
        "systemConfig": system_config,
        "runtimeConfig": runtime_config,
        "pinotConfig": pinot_config,
        "clusterName": _cluster_name,
    }


# ---- Authentication ----

@app.post("/auth/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = _users.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid credentials"}
        )
    token = create_access_token(
        data={"sub": username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response


@app.get("/auth/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response


# ---- Authenticated endpoints ----

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: str = Depends(require_auth)):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "tables": list(_tables.keys()),
            "cluster_name": _cluster_name,
        },
    )


@app.get("/tables")
async def list_tables(user: str = Depends(require_auth)):
    return {"tables": list(_tables.keys())}


@app.get("/tables/{table_name}")
async def get_table(table_name: str, user: str = Depends(require_auth)):
    if table_name not in _tables:
        raise HTTPException(status_code=404, detail="Table not found")
    return _tables[table_name]


@app.get("/tables/{table_name}/segments")
async def get_segments(table_name: str, user: str = Depends(require_auth)):
    if table_name not in _segments:
        raise HTTPException(status_code=404, detail="Table not found")
    return {"segments": _segments[table_name]}


@app.get("/cluster/info")
async def cluster_info(user: str = Depends(require_auth)):
    return {"clusterName": _cluster_name}


@app.get("/tenants")
async def list_tenants(user: str = Depends(require_auth)):
    return {"BROKER_TENANTS": ["DefaultTenant"], "SERVER_TENANTS": ["DefaultTenant"]}


@app.get("/instances")
async def list_instances(user: str = Depends(require_auth)):
    return {
        "instances": [
            "Controller_172.17.0.2_9000",
            "Broker_172.17.0.3_8099",
            "Server_172.17.0.4_8098",
            "Minion_172.17.0.5_9514",
        ]
    }


@app.get("/schemas")
async def list_schemas(user: str = Depends(require_auth)):
    return ["airlineStats", "githubEvents", "starbucksStores"]


@app.get("/zk/ls")
async def zk_ls(path: str = "/", user: str = Depends(require_auth)):
    zk_tree = {
        "/": ["PinotCluster"],
        "/PinotCluster": [
            "CONFIGS",
            "CONTROLLER",
            "EXTERNALVIEW",
            "IDEALSTATES",
            "LIVEINSTANCES",
            "PROPERTYSTORE",
        ],
    }
    children = zk_tree.get(path, [])
    return {"path": path, "children": children}
