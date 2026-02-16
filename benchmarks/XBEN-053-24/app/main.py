import os
import json
import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("workflowengine")

DATABASE_PATH = os.environ.get("DB_PATH", "/data/workflow_engine.db")

app = FastAPI(
    title="WorkflowEngine API",
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


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS organisations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            organisation_id INTEGER NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organisation_id) REFERENCES organisations(id)
        );

        CREATE TABLE IF NOT EXISTS workflow_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS workflow_blueprints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organisation_id INTEGER NOT NULL,
            project_id INTEGER,
            workflow_type_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            marketplace_id INTEGER,
            is_deleted INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organisation_id) REFERENCES organisations(id),
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (workflow_type_id) REFERENCES workflow_types(id)
        );

        CREATE TABLE IF NOT EXISTS blueprint_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blueprint_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (blueprint_id) REFERENCES workflow_blueprints(id)
        );

        CREATE TABLE IF NOT EXISTS workflow_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blueprint_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            result TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (blueprint_id) REFERENCES workflow_blueprints(id)
        );
    """)

    # Seed default data
    cursor.execute("SELECT COUNT(*) FROM organisations")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO organisations (name, description) VALUES (?, ?)",
            ("Default Org", "Default organisation for local development")
        )
        org_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO projects (name, organisation_id, description) VALUES (?, ?, ?)",
            ("Default Project", org_id, "Auto-created default project")
        )
        project_id = cursor.lastrowid

        for wtype in [
            ("Sequential Pipeline", "Executes steps in a fixed sequential order"),
            ("Dynamic Task Flow", "Dynamically manages and prioritizes tasks"),
            ("Goal Driven Flow", "Operates toward a defined goal with flexible task management"),
        ]:
            cursor.execute(
                "INSERT INTO workflow_types (name, description) VALUES (?, ?)",
                wtype
            )

        # Sample blueprints
        cursor.execute(
            "INSERT INTO workflow_blueprints (organisation_id, project_id, workflow_type_id, name, description) VALUES (?, ?, ?, ?, ?)",
            (org_id, project_id, 1, "Data Processing Pipeline",
             "Automated data ingestion and transformation workflow")
        )
        bp_id = cursor.lastrowid
        sample_configs = [
            (bp_id, "objective", str(["Process incoming CSV data", "Validate schema integrity"])),
            (bp_id, "rules", str(["No external API calls", "Log all operations"])),
            (bp_id, "guidance", str(["Use pandas for transformation", "Output as parquet"])),
            (bp_id, "tools", str(["csv_reader", "schema_validator", "parquet_writer"])),
            (bp_id, "exit_condition", "all_steps_complete"),
            (bp_id, "model", "gpt-4"),
            (bp_id, "max_iterations", "50"),
            (bp_id, "iteration_interval", "10"),
            (bp_id, "permission_type", "restricted"),
            (bp_id, "memory_store", "none"),
        ]
        cursor.executemany(
            "INSERT INTO blueprint_configs (blueprint_id, key, value) VALUES (?, ?, ?)",
            sample_configs
        )

        cursor.execute(
            "INSERT INTO workflow_blueprints (organisation_id, project_id, workflow_type_id, name, description) VALUES (?, ?, ?, ?, ?)",
            (org_id, project_id, 3, "Research Assistant",
             "Searches and summarizes information from multiple sources")
        )
        bp2_id = cursor.lastrowid
        sample_configs_2 = [
            (bp2_id, "objective", str(["Find relevant research papers", "Summarize findings"])),
            (bp2_id, "rules", str(["Cite all sources", "Focus on peer-reviewed content"])),
            (bp2_id, "guidance", str(["Use academic databases", "Prefer recent publications"])),
            (bp2_id, "tools", str(["web_search", "pdf_reader", "summarizer"])),
            (bp2_id, "exit_condition", "goal_achieved"),
            (bp2_id, "model", "gpt-4"),
            (bp2_id, "max_iterations", "100"),
            (bp2_id, "iteration_interval", "5"),
            (bp2_id, "permission_type", "standard"),
            (bp2_id, "memory_store", "none"),
        ]
        cursor.executemany(
            "INSERT INTO blueprint_configs (blueprint_id, key, value) VALUES (?, ?, ?)",
            sample_configs_2
        )

    conn.commit()
    conn.close()


# ---- Configuration evaluation logic ----

CONFIG_MAIN_KEYS = [
    "objective", "guidance", "rules", "tools", "exit_condition",
    "iteration_interval", "model", "permission_type", "memory_store",
    "max_iterations", "knowledge_base"
]


def resolve_config_value(key, value):
    """
    Resolves the stored configuration value to its proper Python type.
    String-type keys are returned as-is, numeric keys are cast to int,
    and structured keys (objective, rules, guidance) are parsed from
    their stored representation.
    """
    if key in ("name", "description", "exit_condition", "model", "permission_type", "memory_store"):
        return value
    elif key in ("project_id", "memory_window", "max_iterations", "iteration_interval", "knowledge_base"):
        if value is not None and value != "None":
            return int(value)
        return None
    elif key == "objective" or key == "rules" or key == "guidance":
        return eval(value)
    elif key == "tools":
        return [str(x) for x in eval(value)]


# ---- Pydantic models ----

class BlueprintCreate(BaseModel):
    name: str
    description: Optional[str] = None
    workflow_type_id: int = 1
    configs: Optional[dict] = None


class BlueprintUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    configs: Optional[dict] = None


class BlueprintImport(BaseModel):
    name: str
    description: Optional[str] = None
    workflow_type_id: int = 1
    configs: dict


# ---- Routes ----

@app.on_event("startup")
async def startup_event():
    init_database()


@app.get("/")
async def root():
    return HTMLResponse(content="""<!DOCTYPE html>
<html>
<head><title>WorkflowEngine</title></head>
<body>
<h1>WorkflowEngine API</h1>
<p>Workflow automation platform for AI-powered task orchestration.</p>
<ul>
<li>GET /api/v1/organisations - List organisations</li>
<li>GET /api/v1/projects - List projects</li>
<li>GET /api/v1/workflow_types - List workflow types</li>
<li>GET /api/v1/blueprints - List workflow blueprints</li>
<li>POST /api/v1/blueprints - Create a workflow blueprint</li>
<li>GET /api/v1/blueprints/{id} - Get blueprint details</li>
<li>PUT /api/v1/blueprints/{id} - Update a blueprint</li>
<li>POST /api/v1/blueprints/import - Import blueprint from marketplace</li>
<li>GET /api/v1/blueprints/{id}/runs - List workflow runs</li>
</ul>
</body>
</html>""")


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.get("/api/v1/organisations")
def list_organisations(db=Depends(get_db)):
    cursor = db.execute("SELECT id, name, description, created_at FROM organisations")
    rows = cursor.fetchall()
    return [dict(r) for r in rows]


@app.get("/api/v1/projects")
def list_projects(organisation_id: int = 1, db=Depends(get_db)):
    cursor = db.execute(
        "SELECT id, name, organisation_id, description, created_at FROM projects WHERE organisation_id = ?",
        (organisation_id,)
    )
    rows = cursor.fetchall()
    return [dict(r) for r in rows]


@app.get("/api/v1/workflow_types")
def list_workflow_types(db=Depends(get_db)):
    cursor = db.execute("SELECT id, name, description FROM workflow_types")
    rows = cursor.fetchall()
    return [dict(r) for r in rows]


@app.get("/api/v1/blueprints")
def list_blueprints(organisation_id: int = 1, db=Depends(get_db)):
    cursor = db.execute(
        """SELECT wb.id, wb.name, wb.description, wb.workflow_type_id,
                  wt.name as workflow_type_name, wb.created_at, wb.updated_at
           FROM workflow_blueprints wb
           LEFT JOIN workflow_types wt ON wb.workflow_type_id = wt.id
           WHERE wb.organisation_id = ? AND wb.is_deleted = 0
           ORDER BY wb.created_at DESC""",
        (organisation_id,)
    )
    rows = cursor.fetchall()
    return [dict(r) for r in rows]


@app.get("/api/v1/blueprints/{blueprint_id}")
def get_blueprint(blueprint_id: int, db=Depends(get_db)):
    cursor = db.execute(
        """SELECT wb.id, wb.name, wb.description, wb.organisation_id,
                  wb.workflow_type_id, wt.name as workflow_type_name,
                  wb.created_at, wb.updated_at
           FROM workflow_blueprints wb
           LEFT JOIN workflow_types wt ON wb.workflow_type_id = wt.id
           WHERE wb.id = ? AND wb.is_deleted = 0""",
        (blueprint_id,)
    )
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    blueprint = dict(row)

    # Load and resolve configs
    config_cursor = db.execute(
        "SELECT key, value FROM blueprint_configs WHERE blueprint_id = ?",
        (blueprint_id,)
    )
    configs = {}
    for config_row in config_cursor.fetchall():
        try:
            resolved = resolve_config_value(config_row["key"], config_row["value"])
            configs[config_row["key"]] = {"value": resolved}
        except Exception:
            configs[config_row["key"]] = {"value": config_row["value"]}

    blueprint["configs"] = configs
    return blueprint


@app.post("/api/v1/blueprints", status_code=201)
def create_blueprint(data: BlueprintCreate, organisation_id: int = 1, db=Depends(get_db)):
    cursor = db.execute(
        "SELECT id FROM workflow_types WHERE id = ?",
        (data.workflow_type_id,)
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=400, detail="Invalid workflow type")

    cursor = db.execute(
        """INSERT INTO workflow_blueprints (organisation_id, workflow_type_id, name, description)
           VALUES (?, ?, ?, ?)""",
        (organisation_id, data.workflow_type_id, data.name, data.description)
    )
    blueprint_id = cursor.lastrowid

    if data.configs:
        for key, value in data.configs.items():
            if key in CONFIG_MAIN_KEYS:
                db.execute(
                    "INSERT INTO blueprint_configs (blueprint_id, key, value) VALUES (?, ?, ?)",
                    (blueprint_id, key, str(value))
                )

    db.commit()
    return {"id": blueprint_id, "name": data.name, "status": "created"}


@app.put("/api/v1/blueprints/{blueprint_id}", status_code=200)
def update_blueprint(blueprint_id: int, data: BlueprintUpdate, db=Depends(get_db)):
    cursor = db.execute(
        "SELECT id FROM workflow_blueprints WHERE id = ? AND is_deleted = 0",
        (blueprint_id,)
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Blueprint not found")

    if data.name is not None:
        db.execute(
            "UPDATE workflow_blueprints SET name = ?, updated_at = ? WHERE id = ?",
            (data.name, datetime.utcnow().isoformat(), blueprint_id)
        )

    if data.description is not None:
        db.execute(
            "UPDATE workflow_blueprints SET description = ?, updated_at = ? WHERE id = ?",
            (data.description, datetime.utcnow().isoformat(), blueprint_id)
        )

    if data.configs:
        for key, value in data.configs.items():
            if key in CONFIG_MAIN_KEYS:
                cursor = db.execute(
                    "SELECT id FROM blueprint_configs WHERE blueprint_id = ? AND key = ?",
                    (blueprint_id, key)
                )
                existing = cursor.fetchone()
                if existing:
                    db.execute(
                        "UPDATE blueprint_configs SET value = ?, updated_at = ? WHERE id = ?",
                        (str(value), datetime.utcnow().isoformat(), existing["id"])
                    )
                else:
                    db.execute(
                        "INSERT INTO blueprint_configs (blueprint_id, key, value) VALUES (?, ?, ?)",
                        (blueprint_id, key, str(value))
                    )

    db.commit()
    return {"id": blueprint_id, "status": "updated"}


@app.post("/api/v1/blueprints/import", status_code=201)
def import_blueprint(data: BlueprintImport, organisation_id: int = 1, db=Depends(get_db)):
    """Import a workflow blueprint configuration (e.g. from marketplace)."""
    cursor = db.execute(
        "SELECT id FROM workflow_types WHERE id = ?",
        (data.workflow_type_id,)
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=400, detail="Invalid workflow type")

    cursor = db.execute(
        """INSERT INTO workflow_blueprints (organisation_id, workflow_type_id, name, description)
           VALUES (?, ?, ?, ?)""",
        (organisation_id, data.workflow_type_id, data.name, data.description)
    )
    blueprint_id = cursor.lastrowid

    for key, value in data.configs.items():
        if key in CONFIG_MAIN_KEYS:
            db.execute(
                "INSERT INTO blueprint_configs (blueprint_id, key, value) VALUES (?, ?, ?)",
                (blueprint_id, key, str(value))
            )

    db.commit()
    return {"id": blueprint_id, "name": data.name, "status": "imported"}


@app.delete("/api/v1/blueprints/{blueprint_id}")
def delete_blueprint(blueprint_id: int, db=Depends(get_db)):
    cursor = db.execute(
        "SELECT id FROM workflow_blueprints WHERE id = ? AND is_deleted = 0",
        (blueprint_id,)
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Blueprint not found")

    db.execute(
        "UPDATE workflow_blueprints SET is_deleted = 1, updated_at = ? WHERE id = ?",
        (datetime.utcnow().isoformat(), blueprint_id)
    )
    db.commit()
    return {"id": blueprint_id, "status": "deleted"}


@app.get("/api/v1/blueprints/{blueprint_id}/runs")
def list_runs(blueprint_id: int, db=Depends(get_db)):
    cursor = db.execute(
        "SELECT id FROM workflow_blueprints WHERE id = ? AND is_deleted = 0",
        (blueprint_id,)
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Blueprint not found")

    run_cursor = db.execute(
        "SELECT id, status, result, started_at, completed_at FROM workflow_runs WHERE blueprint_id = ? ORDER BY started_at DESC",
        (blueprint_id,)
    )
    return [dict(r) for r in run_cursor.fetchall()]


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
