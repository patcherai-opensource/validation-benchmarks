import os
import uuid
import hashlib
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Cookie, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic
from jinja2 import Environment, BaseLoader
from starlette.requests import Request
from starlette.templating import Jinja2Templates

app = FastAPI(title="TimeTracker Pro", version="2.0.9")
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

# In-memory storage for simplicity
USERS = {
    "admin": {"password": "kimai2023!", "role": "admin"},
    "manager": {"password": "tr4ck3r!", "role": "manager"},
    "user": {"password": "timekeep", "role": "user"}
}

SESSIONS = {}
UPLOADED_TEMPLATES = {}

# Sample timesheet data for realistic appearance
TIMESHEETS = [
    {"id": 1, "project": "Website Redesign", "hours": 8.5, "date": "2024-01-15", "user": "jsmith"},
    {"id": 2, "project": "API Integration", "hours": 6.0, "date": "2024-01-15", "user": "mjones"},
    {"id": 3, "project": "Database Migration", "hours": 4.25, "date": "2024-01-14", "user": "jsmith"},
    {"id": 4, "project": "Code Review", "hours": 2.0, "date": "2024-01-14", "user": "admin"},
]

PROJECTS = [
    {"id": 1, "name": "Website Redesign", "client": "Acme Corp", "budget": 50000},
    {"id": 2, "name": "API Integration", "client": "TechStart Inc", "budget": 25000},
    {"id": 3, "name": "Database Migration", "client": "DataFlow Ltd", "budget": 35000},
]

# Default invoice templates (built-in, safe)
DEFAULT_TEMPLATES = {
    "standard": """
<html>
<head><title>Invoice</title></head>
<body>
<h1>Invoice #{{ invoice_id }}</h1>
<p>Client: {{ client_name }}</p>
<p>Date: {{ invoice_date }}</p>
<p>Total Hours: {{ total_hours }}</p>
<p>Amount Due: ${{ amount }}</p>
</body>
</html>
""",
    "detailed": """
<html>
<head><title>Detailed Invoice</title></head>
<body>
<h1>Detailed Invoice #{{ invoice_id }}</h1>
<p>Client: {{ client_name }}</p>
<p>Project: {{ project_name }}</p>
<hr>
{% for entry in entries %}
<p>{{ entry.date }} - {{ entry.hours }} hours</p>
{% endfor %}
<hr>
<p><strong>Total: ${{ amount }}</strong></p>
</body>
</html>
"""
}


def get_session_user(session_id: Optional[str] = Cookie(None)):
    """Validate session and return user info"""
    if not session_id or session_id not in SESSIONS:
        return None
    return SESSIONS[session_id]


def require_auth(session_id: Optional[str] = Cookie(None)):
    """Require valid authentication"""
    user = get_session_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_manager(session_id: Optional[str] = Cookie(None)):
    """Require manager or admin role"""
    user = require_auth(session_id)
    if user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user


@app.get("/")
async def home(request: Request, session_id: Optional[str] = Cookie(None)):
    user = get_session_user(session_id)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    if username in USERS and USERS[username]["password"] == password:
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = {"username": username, "role": USERS[username]["role"]}
        resp = RedirectResponse(url="/dashboard", status_code=302)
        resp.set_cookie(key="session_id", value=session_id, httponly=True)
        return resp
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@app.get("/logout")
async def logout(response: Response, session_id: Optional[str] = Cookie(None)):
    if session_id and session_id in SESSIONS:
        del SESSIONS[session_id]
    resp = RedirectResponse(url="/", status_code=302)
    resp.delete_cookie("session_id")
    return resp


@app.get("/dashboard")
async def dashboard(request: Request, user: dict = Depends(require_auth)):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "timesheets": TIMESHEETS[:5],
        "projects": PROJECTS
    })


@app.get("/api/timesheets")
async def get_timesheets(user: dict = Depends(require_auth)):
    return {"timesheets": TIMESHEETS}


@app.get("/api/projects")
async def get_projects(user: dict = Depends(require_auth)):
    return {"projects": PROJECTS}


@app.get("/api/users")
async def get_users(user: dict = Depends(require_manager)):
    # Don't expose passwords
    return {"users": [{"username": u, "role": USERS[u]["role"]} for u in USERS]}


# Invoice/Export functionality (vulnerable section)
@app.get("/invoice")
async def invoice_page(request: Request, user: dict = Depends(require_manager)):
    custom_templates = list(UPLOADED_TEMPLATES.keys())
    return templates.TemplateResponse("invoice.html", {
        "request": request,
        "user": user,
        "projects": PROJECTS,
        "default_templates": list(DEFAULT_TEMPLATES.keys()),
        "custom_templates": custom_templates
    })


@app.get("/invoice/templates")
async def list_templates(user: dict = Depends(require_manager)):
    """List available invoice templates"""
    templates_list = list(DEFAULT_TEMPLATES.keys()) + ["custom:" + k for k in UPLOADED_TEMPLATES.keys()]
    return {"templates": templates_list}


# Hidden endpoint for template upload - simulating the vulnerable Kimai feature
# This endpoint is not linked from the UI but exists in the API
@app.post("/invoice/document_upload")
async def upload_template(
    template_file: UploadFile = File(...),
    template_name: str = Form(...),
    user: dict = Depends(require_manager)
):
    """
    Upload a custom invoice template.
    Supported formats: .html, .twig (Jinja2 templates)
    """
    filename = template_file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Allow .html, .twig, .j2 extensions
    valid_extensions = ['.html', '.twig', '.j2', '.jinja2']
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in valid_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Supported: {', '.join(valid_extensions)}"
        )
    
    content = await template_file.read()
    template_content = content.decode('utf-8')
    
    # Store the template (no sanitization - vulnerable!)
    UPLOADED_TEMPLATES[template_name] = {
        "content": template_content,
        "filename": filename,
        "uploaded_by": user["username"],
        "uploaded_at": datetime.now().isoformat()
    }
    
    return {
        "status": "success",
        "message": f"Template '{template_name}' uploaded successfully",
        "template_name": template_name
    }


@app.get("/invoice/render")
async def render_invoice(
    request: Request,
    template: str,
    project_id: int = 1,
    user: dict = Depends(require_manager)
):
    """Render an invoice using the specified template"""
    
    # Find project
    project = next((p for p in PROJECTS if p["id"] == project_id), PROJECTS[0])
    entries = [t for t in TIMESHEETS if t.get("project") == project["name"]]
    total_hours = sum(e["hours"] for e in entries)
    
    # Invoice context data
    context = {
        "invoice_id": f"INV-{project_id:04d}",
        "client_name": project["client"],
        "project_name": project["name"],
        "invoice_date": datetime.now().strftime("%Y-%m-%d"),
        "total_hours": total_hours,
        "amount": total_hours * 75,  # $75/hour rate
        "entries": entries
    }
    
    # Determine template source
    if template.startswith("custom:"):
        template_key = template[7:]
        if template_key not in UPLOADED_TEMPLATES:
            raise HTTPException(status_code=404, detail="Template not found")
        template_content = UPLOADED_TEMPLATES[template_key]["content"]
    elif template in DEFAULT_TEMPLATES:
        template_content = DEFAULT_TEMPLATES[template]
    else:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # VULNERABLE: Render user-supplied template without sandbox
    # This mirrors CVE-2023-46245 in Kimai
    try:
        jinja_env = Environment(loader=BaseLoader())
        tpl = jinja_env.from_string(template_content)
        rendered = tpl.render(**context)
        return HTMLResponse(content=rendered)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template rendering error: {str(e)}")


@app.get("/invoice/download")
async def download_invoice(
    template: str,
    project_id: int = 1,
    user: dict = Depends(require_manager)
):
    """Download invoice as rendered HTML (triggers template rendering)"""
    return await render_invoice(None, template, project_id, user)


# API documentation endpoints (helps with discovery)
@app.get("/api/v1/docs")
async def api_docs():
    """Partial API documentation"""
    return {
        "version": "2.0.9",
        "endpoints": {
            "/api/timesheets": "GET - List timesheets",
            "/api/projects": "GET - List projects",
            "/api/users": "GET - List users (manager+)",
            "/invoice": "GET - Invoice generation page",
            "/invoice/templates": "GET - List available templates"
        },
        "note": "Additional endpoints available. See full documentation."
    }


@app.get("/robots.txt")
async def robots():
    return HTMLResponse(content="""User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /invoice/
Disallow: /backup/
# Note: document_upload functionality restricted to managers
""", media_type="text/plain")


@app.get("/settings")
async def settings_page(request: Request, user: dict = Depends(require_auth)):
    return templates.TemplateResponse("settings.html", {"request": request, "user": user})


@app.get("/api/settings")
async def get_settings(user: dict = Depends(require_manager)):
    """Get application settings"""
    return {
        "app_name": "TimeTracker Pro",
        "version": "2.0.9",
        "features": {
            "invoice_upload_twig": True,  # Hint about Twig/template upload
            "custom_templates": True,
            "export_formats": ["html", "pdf"],
            "sandbox_mode": False  # Security configuration hint
        },
        "paths": {
            "templates": "/app/templates",
            "uploads": "/app/uploads",
            "documents": "/app/invoice/document_upload"
        }
    }


@app.get("/backup/config.bak")
async def get_backup_config():
    """Serve backup configuration file (should be protected in production!)"""
    try:
        with open("config.bak", "r") as f:
            return HTMLResponse(content=f.read(), media_type="text/plain")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")


@app.get("/ping")
def ping():
    return {"ping": "pong", "app": "TimeTracker Pro", "version": "2.0.9"}
