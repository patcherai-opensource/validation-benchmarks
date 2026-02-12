import os
import sqlite3
from datetime import datetime
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict


DATABASE_PATH = "/app/data/superagi.db"

app = FastAPI(
    title="SuperAGI",
    description="Autonomous AI Agent Framework",
    version="0.0.14",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

templates = Jinja2Templates(directory="templates")


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db_context():
    conn = get_db()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organisation_id INTEGER DEFAULT 1,
                agent_workflow_id INTEGER DEFAULT 1,
                name TEXT NOT NULL,
                description TEXT,
                marketplace_template_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_template_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_template_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY (agent_template_id) REFERENCES agent_templates(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organisations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organisation_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                agent_template_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                agent_workflow_id INTEGER,
                is_running BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                folder_name TEXT,
                class_name TEXT,
                description TEXT
            )
        """)

        # Seed data
        cursor.execute("SELECT COUNT(*) FROM organisations")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO organisations (name, description) VALUES (?, ?)",
                ("Default Organisation", "Default SuperAGI Organisation")
            )
            cursor.execute(
                "INSERT INTO agent_workflows (name, description) VALUES (?, ?)",
                ("Goal Based Workflow", "Sequential workflow that pursues defined goals")
            )
            cursor.execute(
                "INSERT INTO agent_workflows (name, description) VALUES (?, ?)",
                ("Task Queue Workflow", "Parallel task execution workflow")
            )
            cursor.execute(
                "INSERT INTO projects (organisation_id, name, description) VALUES (?, ?, ?)",
                (1, "Default Project", "Default project for testing agents")
            )
            cursor.execute(
                "INSERT INTO tools (name, folder_name, class_name, description) VALUES (?, ?, ?, ?)",
                ("Read File", "file_toolkit", "ReadFileTool", "Read the content of a file")
            )
            cursor.execute(
                "INSERT INTO tools (name, folder_name, class_name, description) VALUES (?, ?, ?, ?)",
                ("Write File", "file_toolkit", "WriteFileTool", "Write content to a file")
            )
            cursor.execute(
                "INSERT INTO tools (name, folder_name, class_name, description) VALUES (?, ?, ?, ?)",
                ("Google Search", "google_search_toolkit", "GoogleSearchTool", "Search Google for information")
            )
            cursor.execute(
                "INSERT INTO tools (name, folder_name, class_name, description) VALUES (?, ?, ?, ?)",
                ("Web Scraper", "web_scraper_toolkit", "WebScraperTool", "Scrape content from websites")
            )

            # Seed some templates
            cursor.execute(
                "INSERT INTO agent_templates (organisation_id, agent_workflow_id, name, description, marketplace_template_id) VALUES (?, ?, ?, ?, ?)",
                (1, 1, "Research Agent", "An agent that performs research on given topics", None)
            )
            cursor.executemany(
                "INSERT INTO agent_template_configs (agent_template_id, key, value) VALUES (?, ?, ?)",
                [
                    (1, "goal", '["Research the latest developments in AI safety", "Summarize findings in a report"]'),
                    (1, "constraints", '["Only use verified sources", "Limit research to last 6 months"]'),
                    (1, "instruction", '["Be thorough", "Cite sources"]'),
                    (1, "agent_type", "Dynamic Task"),
                    (1, "tools", '["Google Search", "Web Scraper", "Read File", "Write File"]'),
                    (1, "model", "gpt-4"),
                    (1, "max_iterations", "25"),
                ]
            )

            cursor.execute(
                "INSERT INTO agent_templates (organisation_id, agent_workflow_id, name, description, marketplace_template_id) VALUES (?, ?, ?, ?, ?)",
                (1, 1, "Coding Assistant", "An agent that assists with coding tasks", None)
            )
            cursor.executemany(
                "INSERT INTO agent_template_configs (agent_template_id, key, value) VALUES (?, ?, ?)",
                [
                    (2, "goal", '["Help write clean, efficient code", "Review code for bugs and improvements"]'),
                    (2, "constraints", '["Follow PEP 8 guidelines", "Write unit tests for all functions"]'),
                    (2, "instruction", '["Write readable code with comments", "Use type hints"]'),
                    (2, "agent_type", "Dynamic Task"),
                    (2, "tools", '["Read File", "Write File"]'),
                    (2, "model", "gpt-4"),
                    (2, "max_iterations", "15"),
                ]
            )


init_db()


# ============================================================
# Models
# ============================================================

class AgentTemplateConfig(BaseModel):
    key: str
    value: str


class AgentTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    agent_configs: Optional[Dict[str, str]] = None


class AgentTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    agent_workflow_id: int = 1
    agent_configs: Optional[Dict[str, str]] = None


class MarketplaceTemplateInstall(BaseModel):
    name: str
    description: Optional[str] = ""
    agent_configs: Dict[str, str]


# ============================================================
# Agent Template Config Evaluation
# Evaluates stored config values to proper Python types
# ============================================================

class AgentTemplate:
    """Agent template model with config evaluation support."""

    @staticmethod
    def eval_agent_config(key, value):
        """Evaluate agent configuration values to proper Python types."""
        if key == "tools" or key == "exit" or key == "model":
            return value
        elif key == "goal" or key == "constraints" or key == "instruction":
            return eval(value)
        else:
            return value


# ============================================================
# Routes - Web UI
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM agent_templates")
        template_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM agents")
        agent_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tools")
        tool_count = cursor.fetchone()[0]
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "template_count": template_count,
        "agent_count": agent_count,
        "tool_count": tool_count,
    })


# ============================================================
# Routes - API: Agent Templates
# ============================================================

@app.get("/api/agent_templates/list")
async def list_agent_templates():
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, created_at, updated_at FROM agent_templates")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


@app.get("/api/agent_templates/get/{agent_template_id}")
async def get_agent_template(agent_template_id: int):
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agent_templates WHERE id = ?", (agent_template_id,))
        template = cursor.fetchone()
        if not template:
            raise HTTPException(status_code=404, detail="Agent template not found")

        cursor.execute(
            "SELECT key, value FROM agent_template_configs WHERE agent_template_id = ?",
            (agent_template_id,)
        )
        configs = cursor.fetchall()

        parsed_configs = {}
        for config in configs:
            key = config["key"]
            value = config["value"]
            parsed_configs[key] = AgentTemplate.eval_agent_config(key, value)

        result = dict(template)
        result["configs"] = parsed_configs
        return result


@app.post("/api/agent_templates/create")
async def create_agent_template(template_data: AgentTemplateCreate):
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO agent_templates (organisation_id, agent_workflow_id, name, description) VALUES (?, ?, ?, ?)",
            (1, template_data.agent_workflow_id, template_data.name, template_data.description)
        )
        template_id = cursor.lastrowid

        if template_data.agent_configs:
            for key, value in template_data.agent_configs.items():
                cursor.execute(
                    "INSERT INTO agent_template_configs (agent_template_id, key, value) VALUES (?, ?, ?)",
                    (template_id, key, value)
                )

        return {"id": template_id, "name": template_data.name, "status": "created"}


@app.put("/api/agent_templates/update_agent_template/{agent_template_id}")
async def update_agent_template(agent_template_id: int, template_data: AgentTemplateUpdate):
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM agent_templates WHERE id = ?", (agent_template_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Agent template not found")

        if template_data.name:
            cursor.execute(
                "UPDATE agent_templates SET name = ?, updated_at = ? WHERE id = ?",
                (template_data.name, datetime.utcnow().isoformat(), agent_template_id)
            )
        if template_data.description:
            cursor.execute(
                "UPDATE agent_templates SET description = ?, updated_at = ? WHERE id = ?",
                (template_data.description, datetime.utcnow().isoformat(), agent_template_id)
            )

        if template_data.agent_configs:
            for key, value in template_data.agent_configs.items():
                cursor.execute(
                    "SELECT id FROM agent_template_configs WHERE agent_template_id = ? AND key = ?",
                    (agent_template_id, key)
                )
                existing = cursor.fetchone()
                if existing:
                    cursor.execute(
                        "UPDATE agent_template_configs SET value = ? WHERE id = ?",
                        (value, existing["id"])
                    )
                else:
                    cursor.execute(
                        "INSERT INTO agent_template_configs (agent_template_id, key, value) VALUES (?, ?, ?)",
                        (agent_template_id, key, value)
                    )

        return {"id": agent_template_id, "status": "updated"}


@app.delete("/api/agent_templates/delete/{agent_template_id}")
async def delete_agent_template(agent_template_id: int):
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM agent_templates WHERE id = ?", (agent_template_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Agent template not found")
        cursor.execute("DELETE FROM agent_template_configs WHERE agent_template_id = ?", (agent_template_id,))
        cursor.execute("DELETE FROM agent_templates WHERE id = ?", (agent_template_id,))
        return {"id": agent_template_id, "status": "deleted"}


# ============================================================
# Routes - API: Marketplace (clone templates)
# ============================================================

@app.post("/api/agent_templates/clone_from_marketplace")
async def clone_agent_template_from_marketplace(template_data: MarketplaceTemplateInstall):
    """Clone an agent template from the marketplace into the local instance."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO agent_templates (organisation_id, agent_workflow_id, name, description, marketplace_template_id) VALUES (?, ?, ?, ?, ?)",
            (1, 1, template_data.name, template_data.description, None)
        )
        template_id = cursor.lastrowid

        for key, value in template_data.agent_configs.items():
            cursor.execute(
                "INSERT INTO agent_template_configs (agent_template_id, key, value) VALUES (?, ?, ?)",
                (template_id, key, value)
            )

        return {"id": template_id, "name": template_data.name, "status": "cloned"}


# ============================================================
# Routes - API: Agents
# ============================================================

@app.get("/api/agents/list")
async def list_agents():
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, is_running, created_at FROM agents")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


@app.post("/api/agents/create_from_template/{agent_template_id}")
async def create_agent_from_template(agent_template_id: int, name: str = "New Agent"):
    with get_db_context() as conn:
        cursor = conn.cursor()

        # Get template
        cursor.execute("SELECT * FROM agent_templates WHERE id = ?", (agent_template_id,))
        template = cursor.fetchone()
        if not template:
            raise HTTPException(status_code=404, detail="Agent template not found")

        # Create agent
        cursor.execute(
            "INSERT INTO agents (project_id, agent_template_id, name, description, agent_workflow_id) VALUES (?, ?, ?, ?, ?)",
            (1, agent_template_id, name, template["description"], template["agent_workflow_id"])
        )
        agent_id = cursor.lastrowid

        # Copy configs from template to agent
        cursor.execute(
            "SELECT key, value FROM agent_template_configs WHERE agent_template_id = ?",
            (agent_template_id,)
        )
        configs = cursor.fetchall()
        for config in configs:
            cursor.execute(
                "INSERT INTO agent_configs (agent_id, key, value) VALUES (?, ?, ?)",
                (agent_id, config["key"], config["value"])
            )

        return {"id": agent_id, "name": name, "status": "created"}


# ============================================================
# Routes - API: Agent Workflows
# ============================================================

@app.get("/api/agent_workflows/list")
async def list_workflows():
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM agent_workflows")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# ============================================================
# Routes - API: Tools
# ============================================================

@app.get("/api/tools/list")
async def list_tools():
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, folder_name, class_name, description FROM tools")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# ============================================================
# Routes - API: Organisations & Projects
# ============================================================

@app.get("/api/organisations/list")
async def list_organisations():
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM organisations")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


@app.get("/api/projects/list")
async def list_projects():
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, organisation_id, name, description, created_at FROM projects")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# ============================================================
# Health check
# ============================================================

@app.get("/ping")
def ping():
    return {"status": "ok"}


# ============================================================
# Global exception handler
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
