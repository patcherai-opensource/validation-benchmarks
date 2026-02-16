import json
import os
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
import sqlite3

app = FastAPI(
    title="DataCatalog Platform",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

DB_PATH = "/app/datacatalog.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def generate_uuid():
    return str(uuid.uuid4())


@app.on_event("startup")
def startup():
    try:
        with open("/app/flag.txt") as f:
            flag = f.read().strip()
            if flag == "FLAG":
                flag = os.getenv("FLAG", "FLAG{default-flag}")
    except FileNotFoundError:
        flag = os.getenv("FLAG", "FLAG{default-flag}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Core entity tables
    cursor.execute("""CREATE TABLE IF NOT EXISTS services (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        serviceType TEXT NOT NULL,
        description TEXT,
        deleted INTEGER DEFAULT 0,
        json TEXT,
        updatedAt TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS ingestion_pipeline (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        fqnHash TEXT,
        pipelineType TEXT,
        serviceId TEXT,
        deleted INTEGER DEFAULT 0,
        json TEXT,
        updatedAt TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS automations_task (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        nameHash TEXT,
        taskType TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'idle',
        deleted INTEGER DEFAULT 0,
        json TEXT,
        updatedAt TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS system_config (
        id TEXT PRIMARY KEY,
        configKey TEXT NOT NULL UNIQUE,
        configValue TEXT NOT NULL,
        scope TEXT DEFAULT 'internal',
        updatedAt TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS entity_relationship (
        fromId TEXT,
        toId TEXT,
        fromEntity TEXT,
        toEntity TEXT,
        relation INTEGER
    )""")

    # Seed services
    services = [
        (generate_uuid(), "production-mysql", "databaseService", "Production MySQL cluster",
         '{"connection": {"config": {"type": "Mysql", "hostPort": "prod-db:3306"}}}'),
        (generate_uuid(), "analytics-redshift", "databaseService", "Analytics Redshift warehouse",
         '{"connection": {"config": {"type": "Redshift", "hostPort": "analytics.redshift.amazonaws.com:5439"}}}'),
        (generate_uuid(), "kafka-events", "messagingService", "Event streaming platform",
         '{"connection": {"config": {"type": "Kafka", "bootstrapServers": "kafka-1:9092,kafka-2:9092"}}}'),
        (generate_uuid(), "airflow-orchestrator", "pipelineService", "Airflow pipeline orchestrator",
         '{"connection": {"config": {"type": "Airflow", "hostPort": "http://airflow:8080"}}}'),
        (generate_uuid(), "superset-dashboards", "dashboardService", "Superset dashboard service",
         '{"connection": {"config": {"type": "Superset", "hostPort": "http://superset:8088"}}}'),
    ]
    cursor.execute("DELETE FROM services")
    for s in services:
        cursor.execute(
            "INSERT INTO services (id, name, serviceType, description, json, updatedAt) VALUES (?, ?, ?, ?, ?, ?)",
            (s[0], s[1], s[2], s[3], s[4], datetime.utcnow().isoformat())
        )

    # Seed ingestion pipelines
    pipelines = [
        (generate_uuid(), "production-mysql.metadata_ingestion", "metadata", services[0][0],
         '{"name": "production-mysql.metadata_ingestion", "pipelineType": "metadata", "fullyQualifiedName": "production-mysql.metadata_ingestion"}'),
        (generate_uuid(), "production-mysql.usage_ingestion", "usage", services[0][0],
         '{"name": "production-mysql.usage_ingestion", "pipelineType": "usage", "fullyQualifiedName": "production-mysql.usage_ingestion"}'),
        (generate_uuid(), "analytics-redshift.metadata_ingestion", "metadata", services[1][0],
         '{"name": "analytics-redshift.metadata_ingestion", "pipelineType": "metadata", "fullyQualifiedName": "analytics-redshift.metadata_ingestion"}'),
        (generate_uuid(), "kafka-events.metadata_ingestion", "metadata", services[2][0],
         '{"name": "kafka-events.metadata_ingestion", "pipelineType": "metadata", "fullyQualifiedName": "kafka-events.metadata_ingestion"}'),
    ]
    cursor.execute("DELETE FROM ingestion_pipeline")
    for p in pipelines:
        cursor.execute(
            "INSERT INTO ingestion_pipeline (id, name, pipelineType, serviceId, json, updatedAt, fqnHash) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (p[0], p[1], p[2], p[3], p[4], datetime.utcnow().isoformat(), p[1].replace(".", "_"))
        )

    # Seed automation tasks
    task_types = ["testConnection", "dataProfiler", "dataQuality", "lineageIngestion"]
    statuses = ["idle", "running", "completed", "failed"]
    cursor.execute("DELETE FROM automations_task")
    for i in range(12):
        tid = generate_uuid()
        task_type = task_types[i % len(task_types)]
        status = statuses[i % len(statuses)]
        name = f"task_{task_type}_{i}"
        task_json = json.dumps({
            "id": tid,
            "name": name,
            "taskType": task_type,
            "status": status,
            "fullyQualifiedName": name,
            "request": {"serviceType": "Database", "connectionType": "Mysql"},
            "response": None
        })
        cursor.execute(
            "INSERT INTO automations_task (id, name, nameHash, taskType, status, json, updatedAt) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (tid, name, name.replace("_", ""), task_type, status, task_json, datetime.utcnow().isoformat())
        )

    # Store sensitive data in system_config
    cursor.execute("DELETE FROM system_config")
    cursor.execute(
        "INSERT INTO system_config (id, configKey, configValue, scope, updatedAt) VALUES (?, ?, ?, ?, ?)",
        (generate_uuid(), "jwt.signing.key", "aW50ZXJuYWwtand0LXNlY3JldC1rZXk=", "internal", datetime.utcnow().isoformat())
    )
    cursor.execute(
        "INSERT INTO system_config (id, configKey, configValue, scope, updatedAt) VALUES (?, ?, ?, ?, ?)",
        (generate_uuid(), "platform.api.token", flag, "internal", datetime.utcnow().isoformat())
    )
    cursor.execute(
        "INSERT INTO system_config (id, configKey, configValue, scope, updatedAt) VALUES (?, ?, ?, ?, ?)",
        (generate_uuid(), "auth.provider.config", '{"provider": "basic", "publicKeyUrls": []}', "public", datetime.utcnow().isoformat())
    )
    cursor.execute(
        "INSERT INTO system_config (id, configKey, configValue, scope, updatedAt) VALUES (?, ?, ?, ?, ?)",
        (generate_uuid(), "elasticsearch.host", "http://elasticsearch:9200", "public", datetime.utcnow().isoformat())
    )

    conn.commit()
    conn.close()


# --- Health check ---
@app.get("/ping")
def ping():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# --- Root UI ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("/app/static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


# --- Configuration endpoint ---
@app.get("/api/v1/system/config")
def get_config():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT configKey, configValue FROM system_config WHERE scope = 'public'")
    rows = cursor.fetchall()
    conn.close()
    config = {row["configKey"]: row["configValue"] for row in rows}
    return {"data": config}


# --- Services ---
@app.get("/api/v1/services")
def list_services(
    serviceType: str = Query(None, description="Filter by service type"),
    limit: int = Query(10, ge=1, le=100),
    include: str = Query("non-deleted", description="Include deleted entities")
):
    conn = get_db_connection()
    cursor = conn.cursor()
    conditions = []
    params = []
    if include == "non-deleted":
        conditions.append("deleted = 0")
    elif include == "deleted":
        conditions.append("deleted = 1")

    if serviceType:
        conditions.append("serviceType = ?")
        params.append(serviceType)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"SELECT id, name, serviceType, description, updatedAt FROM services {where} ORDER BY name LIMIT ?"
    params.append(limit)
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    data = [dict(row) for row in rows]
    return {"data": data, "paging": {"total": len(data)}}


@app.get("/api/v1/services/{service_id}")
def get_service(service_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Service not found")
    result = dict(row)
    if result.get("json"):
        result["connection"] = json.loads(result["json"]).get("connection", {})
    result.pop("json", None)
    return result


# --- Ingestion Pipelines ---
@app.get("/api/v1/services/ingestionPipelines")
def list_pipelines(
    service: str = Query(None, description="Filter by service name"),
    pipelineType: str = Query(None, description="Filter by pipeline type"),
    limit: int = Query(10, ge=1, le=100)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    conditions = ["deleted = 0"]
    params = []

    if pipelineType:
        conditions.append("pipelineType = ?")
        params.append(pipelineType)

    where = "WHERE " + " AND ".join(conditions)
    query = f"SELECT id, name, pipelineType, serviceId, updatedAt FROM ingestion_pipeline {where} ORDER BY name LIMIT ?"
    params.append(limit)
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    data = [dict(row) for row in rows]
    return {"data": data, "paging": {"total": len(data)}}


# --- Automations / Tasks ---
# Listing with count
@app.get("/api/v1/automations/tasks")
def list_tasks(
    fields: str = Query(None, description="Fields requested in the returned resource"),
    limit: int = Query(10, ge=1, le=1000000, description="Limit results"),
    before: str = Query(None, description="Returns list of tasks before this cursor"),
    after: str = Query(None, description="Returns list of tasks after this cursor"),
    include: str = Query("non-deleted", description="Include all, deleted, or non-deleted entities"),
    taskType: str = Query(None, description="Filter by taskType"),
    status: str = Query(None, description="Filter by status")
):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build base condition
    if include == "non-deleted":
        condition = "WHERE deleted = 0"
    elif include == "deleted":
        condition = "WHERE deleted = 1"
    else:
        condition = "WHERE TRUE"

    # Build SQL condition with filters
    sql_condition = f"{condition} "

    if taskType is not None:
        sql_condition += f"AND taskType='{taskType}' "

    if status is not None:
        sql_condition += f"AND status='{status}' "

    # Count query
    count_query = f"SELECT COUNT(*) as total FROM automations_task {sql_condition}"

    # List query with pagination
    if after is not None:
        list_query = f"SELECT json FROM automations_task {sql_condition} AND name > '{after}' ORDER BY name LIMIT {limit}"
    elif before is not None:
        list_query = f"SELECT json FROM (SELECT name, json FROM automations_task {sql_condition} AND name < '{before}' ORDER BY name DESC LIMIT {limit}) sub ORDER BY name"
    else:
        list_query = f"SELECT json FROM automations_task {sql_condition} ORDER BY name LIMIT {limit}"

    try:
        cursor.execute(count_query)
        total = cursor.fetchone()["total"]

        cursor.execute(list_query)
        rows = cursor.fetchall()
        conn.close()

        data = []
        for row in rows:
            try:
                parsed = json.loads(row["json"])
                data.append(parsed)
            except (json.JSONDecodeError, TypeError):
                data.append({"raw": row["json"]})

        return {
            "data": data,
            "paging": {
                "total": total
            }
        }
    except Exception:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid request parameters")


@app.get("/api/v1/automations/tasks/{task_id}")
def get_task(task_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM automations_task WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    result = dict(row)
    if result.get("json"):
        try:
            result = json.loads(result["json"])
        except json.JSONDecodeError:
            pass
    return result


@app.get("/api/v1/automations/tasks/{task_id}/status")
def get_task_status(task_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, status, updatedAt FROM automations_task WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(row)


# --- Version info ---
@app.get("/api/v1/system/version")
def get_version():
    return {
        "version": "1.4.1",
        "revision": "a3b2c1d",
        "timestamp": "2024-01-15T10:30:00Z"
    }


# --- Custom error handlers ---
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"code": 404, "message": "Resource not found"}
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "Internal server error"}
    )
