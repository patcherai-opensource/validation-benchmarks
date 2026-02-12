import json
import os
import sqlite3
import hashlib
import time
import base64

from fastapi import FastAPI, HTTPException, Request, Query, Header
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI(
    title="OpenMetadata",
    description="Open Metadata REST API",
    version="1.4.1",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE = "/app/openmetadata.db"

# User credentials - default OpenMetadata setup
USERS = {
    "admin": "admin",
    "ingestion-bot": "ingestion-bot",
}

# Active tokens mapped to usernames
_active_tokens = {}


def _generate_token(username):
    """Generate a JWT-like token for the user."""
    header = base64.urlsafe_b64encode(b'{"alg":"RS256","typ":"JWT"}').decode().rstrip("=")
    payload_data = json.dumps({"sub": username, "iat": int(time.time()), "iss": "open-metadata.org"})
    payload = base64.urlsafe_b64encode(payload_data.encode()).decode().rstrip("=")
    sig = hashlib.sha256(f"{username}{int(time.time())}".encode()).hexdigest()[:43]
    token = f"{header}.{payload}.{sig}"
    _active_tokens[token] = username
    return token


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def verify_auth(authorization: Optional[str] = None):
    """Verify bearer token authentication.
    Returns the user identity or raises 401."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")
    token = authorization.replace("Bearer ", "")
    user = _active_tokens.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


@app.on_event("startup")
def startup():
    try:
        with open("flag.txt") as f:
            flag = f.read().strip()
            if flag == "FLAG":
                flag = os.getenv("FLAG", "FLAG{default-flag}")
        # Remove flag file after reading
        os.remove("flag.txt")
    except FileNotFoundError:
        flag = os.getenv("FLAG", "FLAG{default-flag}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Create workflow tables matching OpenMetadata schema
    cursor.execute('''CREATE TABLE IF NOT EXISTS automations_workflow (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        workflowType TEXT NOT NULL,
        status TEXT NOT NULL,
        description TEXT,
        response TEXT,
        owner TEXT,
        createdAt INTEGER,
        updatedAt INTEGER,
        deleted INTEGER DEFAULT 0
    )''')

    # Create additional tables for realism
    cursor.execute('''CREATE TABLE IF NOT EXISTS workflow_run (
        id TEXT PRIMARY KEY,
        workflow_id TEXT,
        status TEXT,
        startedAt INTEGER,
        endedAt INTEGER,
        FOREIGN KEY (workflow_id) REFERENCES automations_workflow(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS entity_metadata (
        id TEXT PRIMARY KEY,
        type TEXT,
        name TEXT,
        fqn TEXT,
        json TEXT
    )''')

    # Seed data
    cursor.execute('DELETE FROM automations_workflow')
    cursor.execute('DELETE FROM workflow_run')
    cursor.execute('DELETE FROM entity_metadata')

    now = int(time.time() * 1000)

    # Regular workflows visible in normal listing
    workflows = [
        ("a1b2c3d4-1111-4000-8000-000000000001", "metadata_ingestion_redshift",
         "TEST_CONNECTION", "Successful", "Test connection workflow for Redshift source",
         '{"steps": [{"name": "CheckAccess", "passed": true}]}', "admin", now, now, 0),
        ("a1b2c3d4-2222-4000-8000-000000000002", "profiler_workflow_bigquery",
         "TEST_CONNECTION", "Failed", "Test connection workflow for BigQuery profiler",
         '{"steps": [{"name": "CheckAccess", "passed": false}]}', "admin", now, now, 0),
        ("a1b2c3d4-3333-4000-8000-000000000003", "lineage_workflow_snowflake",
         "TEST_CONNECTION", "Successful", "Test connection for Snowflake lineage",
         '{"steps": [{"name": "GetSchemas", "passed": true}]}', "ingestion-bot", now, now, 0),
        ("a1b2c3d4-4444-4000-8000-000000000004", "metadata_ingestion_mysql",
         "TEST_CONNECTION", "Running", "Test connection for MySQL source",
         '{"steps": [{"name": "CheckAccess", "passed": true}]}', "admin", now, now, 0),
        ("a1b2c3d4-5555-4000-8000-000000000005", "dbt_workflow",
         "TEST_CONNECTION", "Successful", "Test connection for dbt integration",
         '{"steps": [{"name": "ValidateConfig", "passed": true}]}', "admin", now, now, 0),
    ]

    for wf in workflows:
        cursor.execute(
            "INSERT INTO automations_workflow (id, name, workflowType, status, description, response, owner, createdAt, updatedAt, deleted) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", wf
        )

    # Internal system workflow containing sensitive configuration
    cursor.execute(
        "INSERT INTO automations_workflow (id, name, workflowType, status, description, response, owner, createdAt, updatedAt, deleted) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("a1b2c3d4-9999-4000-8000-000000000099", "system_secrets_migration",
         "INTERNAL", "Completed", flag,
         '{"migrated": true}', "system", now, now, 1)
    )

    # Seed workflow runs
    runs = [
        ("run-001", "a1b2c3d4-1111-4000-8000-000000000001", "Successful", now - 3600000, now - 3500000),
        ("run-002", "a1b2c3d4-2222-4000-8000-000000000002", "Failed", now - 7200000, now - 7100000),
        ("run-003", "a1b2c3d4-4444-4000-8000-000000000004", "Running", now - 60000, None),
    ]
    for run in runs:
        cursor.execute(
            "INSERT INTO workflow_run (id, workflow_id, status, startedAt, endedAt) VALUES (?, ?, ?, ?, ?)", run
        )

    # Seed entity metadata
    entities = [
        ("ent-001", "databaseService", "Redshift Production", "redshift_prod",
         '{"serviceType": "Redshift", "connection": {"config": {}}}'),
        ("ent-002", "databaseService", "BigQuery Analytics", "bigquery_analytics",
         '{"serviceType": "BigQuery", "connection": {"config": {}}}'),
        ("ent-003", "databaseService", "MySQL Operations", "mysql_ops",
         '{"serviceType": "Mysql", "connection": {"config": {}}}'),
    ]
    for ent in entities:
        cursor.execute(
            "INSERT INTO entity_metadata (id, type, name, fqn, json) VALUES (?, ?, ?, ?, ?)", ent
        )

    conn.commit()
    conn.close()


# ---- API v1 Endpoints ----

@app.get("/api/v1/system/version")
def get_version():
    return {
        "version": "1.4.1",
        "revision": "a3f2b1c",
        "timestamp": "2024-08-15T10:30:00Z"
    }


@app.get("/api/v1/system/config")
def get_system_config():
    return {
        "authorizerConfiguration": {
            "className": "org.openmetadata.service.security.DefaultAuthorizer",
            "adminPrincipals": ["admin"],
            "allowedEmailRegistrationDomains": ["all"]
        },
        "authenticationConfiguration": {
            "provider": "basic",
            "publicKeyUrls": [],
            "authority": "https://accounts.google.com",
            "enableSelfSignup": True
        },
        "pipelineServiceClientConfiguration": {
            "enabled": True,
            "apiEndpoint": "http://ingestion:8080"
        }
    }


@app.get("/api/v1/system/config/auth")
def get_auth_config():
    return {
        "provider": "basic",
        "providerName": "basic",
        "authority": "https://accounts.google.com",
        "callbackUrl": "http://localhost:8585/callback",
        "jwtPrincipalClaims": ["email", "preferred_username", "sub"]
    }


@app.post("/api/v1/users/login")
async def login(request: Request):
    """Authenticate user and return access token."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request body")

    email = data.get("email", "")
    password = data.get("password", "")

    # Extract username from email
    username = email.split("@")[0] if "@" in email else email

    if username in USERS and USERS[username] == password:
        token = _generate_token(username)
        return {
            "tokenType": "Bearer",
            "accessToken": token,
            "expiryDuration": 3600,
        }

    raise HTTPException(status_code=401, detail="Invalid email or password")


@app.get("/api/v1/users/loggedInUser")
def get_logged_in_user(authorization: Optional[str] = Header(None)):
    """Get the currently logged in user."""
    user = verify_auth(authorization)
    return {
        "name": user,
        "email": f"{user}@openmetadata.org",
        "isAdmin": user == "admin",
    }


@app.get("/api/v1/automations/workflows")
def list_workflows(
    request: Request,
    workflowType: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    before: Optional[str] = Query(None),
    after: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
):
    """List automation workflows with optional filtering by workflowType and status.
    Mirrors the OpenMetadata CollectionDAO.WorkflowDAO listing methods."""
    user = verify_auth(authorization)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Build SQL condition - only show non-deleted workflows
    condition = "deleted = 0"

    if workflowType:
        condition = f"{condition} AND workflowType='{workflowType}'"

    if status:
        condition = f"{condition} AND status='{status}'"

    # listAfter / listBefore pagination
    if after:
        condition = f"{condition} AND name > '{after}'"
    elif before:
        condition = f"{condition} AND name < '{before}'"

    query = f"SELECT * FROM automations_workflow WHERE {condition} ORDER BY name LIMIT {limit}"

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
    except Exception:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid request parameters")

    workflows = []
    for row in rows:
        workflows.append({
            "id": row["id"],
            "name": row["name"],
            "workflowType": row["workflowType"],
            "status": row["status"],
            "description": row["description"],
            "response": row["response"],
            "owner": row["owner"],
        })

    # Count query for pagination metadata
    count_condition = "deleted = 0"
    if workflowType:
        count_condition = f"{count_condition} AND workflowType='{workflowType}'"
    if status:
        count_condition = f"{count_condition} AND status='{status}'"

    count_query = f"SELECT COUNT(*) as total FROM automations_workflow WHERE {count_condition}"
    try:
        cursor.execute(count_query)
        total = cursor.fetchone()["total"]
    except Exception:
        total = len(workflows)

    conn.close()

    return {
        "data": workflows,
        "paging": {
            "total": total,
            "after": workflows[-1]["name"] if len(workflows) == limit else None,
            "before": workflows[0]["name"] if before and workflows else None,
        }
    }


@app.get("/api/v1/services/databaseServices")
def list_database_services(authorization: Optional[str] = Header(None)):
    """List registered database services."""
    user = verify_auth(authorization)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entity_metadata WHERE type = 'databaseService'")
    rows = cursor.fetchall()
    conn.close()

    services = []
    for row in rows:
        services.append({
            "id": row["id"],
            "name": row["name"],
            "fullyQualifiedName": row["fqn"],
            "serviceType": json.loads(row["json"]).get("serviceType", "Unknown"),
        })

    return {"data": services, "paging": {"total": len(services)}}


@app.get("/api/v1/automations/workflows/{workflow_id}/runs")
def list_workflow_runs(
    workflow_id: str,
    authorization: Optional[str] = Header(None),
):
    """List execution runs for a specific workflow."""
    user = verify_auth(authorization)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workflow_run WHERE workflow_id = ? ORDER BY startedAt DESC", (workflow_id,))
    rows = cursor.fetchall()
    conn.close()

    runs = []
    for row in rows:
        runs.append({
            "id": row["id"],
            "workflowId": row["workflow_id"],
            "status": row["status"],
            "startedAt": row["startedAt"],
            "endedAt": row["endedAt"],
        })

    return {"data": runs, "paging": {"total": len(runs)}}


@app.get("/api/v1/automations/workflows/{workflow_id}")
def get_workflow(workflow_id: str, authorization: Optional[str] = Header(None)):
    """Get a specific workflow by ID."""
    user = verify_auth(authorization)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM automations_workflow WHERE id = ? AND deleted = 0", (workflow_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    return {
        "id": row["id"],
        "name": row["name"],
        "workflowType": row["workflowType"],
        "status": row["status"],
        "description": row["description"],
        "response": row["response"],
        "owner": row["owner"],
    }


# ---- Health & Root ----

@app.get("/ping")
def ping():
    return "pong"


@app.get("/api/v1/system/health")
def health_check():
    return {"status": "healthy"}


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"code": 404, "message": "Not Found"}
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "Internal Server Error"}
    )
