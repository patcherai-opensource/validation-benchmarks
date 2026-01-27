import os
import uuid
import secrets
from pathlib import Path

from fastapi import FastAPI, Form, UploadFile, File, HTTPException, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment
from starlette.requests import Request
from starlette.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Session storage (in-memory for simplicity)
sessions = {}

# User database
users = {
    "manager": {"password": "timetrack2024", "role": "manager"},
    "employee": {"password": "worker123", "role": "employee"}
}

# Template storage directory
TEMPLATE_DIR = Path("/app/invoice_templates")
TEMPLATE_DIR.mkdir(exist_ok=True)

# Store uploaded templates per user
user_templates = {}


def get_current_user(session_id: str = Cookie(None)):
    """Get current authenticated user from session"""
    if not session_id or session_id not in sessions:
        return None
    return sessions[session_id]


def require_auth(session_id: str = Cookie(None)):
    """Dependency that requires authentication"""
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


@app.get("/")
async def index(request: Request, session_id: str = Cookie(None)):
    user = get_current_user(session_id)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/login")
async def login_page(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in users and users[username]["password"] == password:
        session_id = secrets.token_hex(32)
        sessions[session_id] = {"username": username, "role": users[username]["role"]}
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@app.get("/logout")
async def logout(session_id: str = Cookie(None)):
    if session_id and session_id in sessions:
        del sessions[session_id]
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="session_id")
    return response


@app.get("/dashboard")
async def dashboard(request: Request, user: dict = Depends(require_auth)):
    username = user["username"]
    user_tmpls = user_templates.get(username, [])
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "templates": user_tmpls
    })


@app.get("/templates/upload")
async def upload_page(request: Request, user: dict = Depends(require_auth)):
    if user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Only managers can upload templates")
    return templates.TemplateResponse("upload.html", {"request": request, "user": user})


@app.post("/templates/upload")
async def upload_template(
    request: Request,
    template_file: UploadFile = File(...),
    template_name: str = Form(...),
    user: dict = Depends(require_auth)
):
    """Upload a custom invoice template - managers only"""
    if user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Only managers can upload templates")
    
    # Check file extension
    filename = template_file.filename
    if not filename.endswith(('.html', '.tpl', '.j2')):
        return templates.TemplateResponse("upload.html", {
            "request": request,
            "user": user,
            "error": "Only .html, .tpl, and .j2 template files are allowed"
        })
    
    # Read template content
    content = await template_file.read()
    template_content = content.decode('utf-8')
    
    # Save template
    template_id = str(uuid.uuid4())[:8]
    username = user["username"]
    
    if username not in user_templates:
        user_templates[username] = []
    
    user_templates[username].append({
        "id": template_id,
        "name": template_name,
        "filename": filename,
        "content": template_content
    })
    
    return RedirectResponse(url="/dashboard?success=Template+uploaded", status_code=302)


@app.get("/invoice/preview/{template_id}")
async def preview_invoice(
    request: Request,
    template_id: str,
    user: dict = Depends(require_auth)
):
    """Preview/render an invoice using the selected template"""
    username = user["username"]
    
    # Find template
    template_data = None
    for tmpl in user_templates.get(username, []):
        if tmpl["id"] == template_id:
            template_data = tmpl
            break
    
    if not template_data:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Sample invoice data
    invoice_data = {
        "invoice_number": "INV-2024-001",
        "client_name": "Acme Corporation",
        "date": "2024-01-15",
        "items": [
            {"description": "Consulting Services", "hours": 40, "rate": 150, "total": 6000},
            {"description": "Development Work", "hours": 80, "rate": 125, "total": 10000},
        ],
        "subtotal": 16000,
        "tax": 1280,
        "total": 17280,
        "company_name": "TimeTracker Pro",
        "username": username
    }
    
    # VULNERABLE: Render user-provided template without sandboxing
    # This allows SSTI attacks similar to CVE-2023-46245
    try:
        jinja2_env = Environment()
        rendered = jinja2_env.from_string(template_data["content"]).render(**invoice_data)
        return HTMLResponse(content=rendered)
    except Exception as e:
        return HTMLResponse(content=f"<h3>Template Error</h3><pre>{str(e)}</pre>", status_code=400)


@app.get("/invoice/export/{template_id}")
async def export_invoice(
    request: Request,
    template_id: str,
    user: dict = Depends(require_auth)
):
    """Export invoice - same as preview but conceptually different endpoint"""
    return await preview_invoice(request, template_id, user)


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.get("/api/templates")
async def list_templates(user: dict = Depends(require_auth)):
    """API endpoint to list user's templates"""
    username = user["username"]
    return {"templates": user_templates.get(username, [])}
