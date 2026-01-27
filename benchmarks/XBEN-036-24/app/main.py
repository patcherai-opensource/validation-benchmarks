import os
import base64
import hashlib
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException, Depends, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="airflow_secret_key_2024_xben036")

templates = Jinja2Templates(directory="templates")

# Simulated DAG files database - maps file paths to DAG IDs contained in them
# Each "file" can contain multiple DAGs with different access levels
DAG_FILES = {
    "dags/public_workflows.py": ["public_etl", "public_report"],
    "dags/shared_workflows.py": ["shared_pipeline", "admin_secrets"],
    "dags/private_admin.py": ["admin_backup", "admin_credentials"]
}

# DAG source code (the actual content of workflows)
DAG_SOURCES = {
    "dags/public_workflows.py": '''# Public Workflows
from airflow import DAG
from airflow.operators.python import PythonOperator

# DAG: public_etl
with DAG("public_etl", schedule_interval="@daily") as dag:
    def extract(): return "Extracting public data"
    def transform(): return "Transforming data"
    def load(): return "Loading to warehouse"

# DAG: public_report 
with DAG("public_report", schedule_interval="@weekly") as dag:
    def generate_report(): return "Generating weekly report"
''',
    "dags/shared_workflows.py": '''# Shared Workflows - Mixed Access Levels
from airflow import DAG
from airflow.operators.python import PythonOperator

# DAG: shared_pipeline (accessible to analysts)
with DAG("shared_pipeline", schedule_interval="@hourly") as dag:
    def process_shared_data(): return "Processing shared data"

# DAG: admin_secrets (ADMIN ONLY - contains sensitive config)
with DAG("admin_secrets", schedule_interval="@once") as dag:
    # SENSITIVE: Admin credentials and secrets
    ADMIN_DB_PASSWORD = "super_secret_admin_pwd"
    SECRET_FLAG = "FLAG_PLACEHOLDER"  # Will be replaced at build time
    def backup_secrets(): 
        return f"Backing up secrets: {SECRET_FLAG}"
''',
    "dags/private_admin.py": '''# Private Admin Workflows
from airflow import DAG  
from airflow.operators.python import PythonOperator

# DAG: admin_backup
with DAG("admin_backup", schedule_interval="@monthly") as dag:
    def full_backup(): return "Running full system backup"

# DAG: admin_credentials
with DAG("admin_credentials", schedule_interval="@yearly") as dag:
    def rotate_credentials(): return "Rotating admin credentials"
'''
}

# User database with roles and DAG access permissions
USERS = {
    "admin": {"password": "admin_secure_2024", "role": "admin", "dag_access": ["public_etl", "public_report", "shared_pipeline", "admin_secrets", "admin_backup", "admin_credentials"]},
    "analyst": {"password": "analyst123", "role": "analyst", "dag_access": ["public_etl", "public_report", "shared_pipeline"]},
    "viewer": {"password": "viewer123", "role": "viewer", "dag_access": ["public_etl", "public_report"]}
}

def generate_file_token(filepath: str) -> str:
    """Generate a token for accessing DAG source files"""
    return base64.urlsafe_b64encode(filepath.encode()).decode()

def decode_file_token(token: str) -> str:
    """Decode a file token back to filepath"""
    try:
        return base64.urlsafe_b64decode(token.encode()).decode()
    except:
        return None

def get_current_user(request: Request) -> Optional[dict]:
    """Get current logged-in user from session"""
    username = request.session.get("username")
    if username and username in USERS:
        return {"username": username, **USERS[username]}
    return None

def user_has_dag_access(user: dict, dag_id: str) -> bool:
    """Check if user has access to a specific DAG"""
    return dag_id in user.get("dag_access", [])

def user_has_any_dag_access_in_file(user: dict, filepath: str) -> bool:
    """VULNERABLE: Only checks if user has access to ANY dag in the file, not ALL"""
    dag_ids = DAG_FILES.get(filepath, [])
    for dag_id in dag_ids:
        if user_has_dag_access(user, dag_id):
            return True
    return False

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in USERS and USERS[username]["password"] == password:
        request.session["username"] = username
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/", status_code=302)
    
    # Show user's accessible DAGs
    accessible_dags = []
    for filepath, dag_ids in DAG_FILES.items():
        for dag_id in dag_ids:
            if user_has_dag_access(user, dag_id):
                file_token = generate_file_token(filepath)
                accessible_dags.append({
                    "dag_id": dag_id,
                    "filepath": filepath,
                    "file_token": file_token
                })
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "dags": accessible_dags
    })

@app.get("/api/v1/dagSources/{file_token}", response_class=JSONResponse)
async def get_dag_source(request: Request, file_token: str):
    """
    VULNERABLE ENDPOINT: Returns DAG source code for a file
    BUG: Only checks if user has access to ANY DAG in the file,
    not if they have access to ALL DAGs in the file.
    This allows information disclosure of restricted DAGs.
    """
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    filepath = decode_file_token(file_token)
    if not filepath or filepath not in DAG_FILES:
        raise HTTPException(status_code=404, detail="DAG file not found")
    
    # VULNERABLE CHECK: Only verifies user has access to SOME dag in the file
    # Should check access to ALL dags but doesn't
    if not user_has_any_dag_access_in_file(user, filepath):
        raise HTTPException(status_code=403, detail="Access denied: You don't have permission to view this DAG file")
    
    # Returns FULL source code including restricted DAGs
    source_code = DAG_SOURCES.get(filepath, "# No source available")
    
    return {
        "file_path": filepath,
        "file_token": file_token,
        "content": source_code
    }

@app.get("/api/v1/dags", response_class=JSONResponse)
async def list_dags(request: Request):
    """List all DAGs visible to current user"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    visible_dags = []
    for filepath, dag_ids in DAG_FILES.items():
        for dag_id in dag_ids:
            if user_has_dag_access(user, dag_id):
                visible_dags.append({
                    "dag_id": dag_id,
                    "file_path": filepath,
                    "file_token": generate_file_token(filepath)
                })
    
    return {"dags": visible_dags, "total": len(visible_dags)}

@app.get("/api/v1/files", response_class=JSONResponse)
async def list_dag_files(request: Request):
    """List all DAG files and their tokens (for browsing)"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    files = []
    for filepath in DAG_FILES.keys():
        files.append({
            "file_path": filepath,
            "file_token": generate_file_token(filepath),
            "dag_count": len(DAG_FILES[filepath])
        })
    
    return {"files": files}

@app.get("/ping")
async def ping():
    return {"status": "ok", "service": "AirFlow DAG Manager"}

