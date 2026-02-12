import os
import uuid
import shutil
import zipfile
import hashlib
import secrets
import io
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Form, UploadFile, File, Request, Response, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from lxml import etree

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "/app/var/invoices/templates"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Authentication & Users ---

USERS = {
    "admin": {
        "password_hash": hashlib.sha256(b"admin").hexdigest(),
        "role": "ROLE_SUPER_ADMIN",
        "display_name": "Administrator",
        "email": "admin@kimai.local",
        "enabled": True,
    },
    "susan": {
        "password_hash": hashlib.sha256(b"timetrack99").hexdigest(),
        "role": "ROLE_USER",
        "display_name": "Susan Miller",
        "email": "susan@kimai.local",
        "enabled": True,
    },
    "john": {
        "password_hash": hashlib.sha256(b"johnpass123").hexdigest(),
        "role": "ROLE_TEAMLEAD",
        "display_name": "John Davis",
        "email": "john@kimai.local",
        "enabled": True,
    },
}

PERMISSIONS = {
    "ROLE_SUPER_ADMIN": [
        "view_invoice", "create_invoice", "manage_invoice_template",
        "upload_invoice_template", "view_timesheet", "create_timesheet",
        "view_customer", "manage_customer", "view_project", "manage_project",
        "view_activity", "manage_activity", "view_user", "manage_user",
        "system_configuration",
    ],
    "ROLE_TEAMLEAD": [
        "view_invoice", "create_invoice", "view_timesheet", "create_timesheet",
        "view_customer", "view_project", "view_activity",
    ],
    "ROLE_USER": [
        "view_timesheet", "create_timesheet",
    ],
}


def get_current_user(request: Request):
    username = request.session.get("username")
    if not username or username not in USERS:
        return None
    return {"username": username, **USERS[username]}


def require_auth(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user


def has_permission(user: dict, permission: str) -> bool:
    role = user.get("role", "")
    return permission in PERMISSIONS.get(role, [])


# --- Sample Data ---

CUSTOMERS = [
    {"id": 1, "name": "Acme Corp", "number": "C-001", "country": "US", "currency": "USD", "contact": "Robert Brown", "visible": True},
    {"id": 2, "name": "Global Solutions GmbH", "number": "C-002", "country": "DE", "currency": "EUR", "contact": "Klaus Weber", "visible": True},
    {"id": 3, "name": "TechStart Ltd", "number": "C-003", "country": "GB", "currency": "GBP", "contact": "Emma Wilson", "visible": True},
]

PROJECTS = [
    {"id": 1, "name": "Website Redesign", "customer_id": 1, "visible": True, "budget": 50000},
    {"id": 2, "name": "ERP Integration", "customer_id": 2, "visible": True, "budget": 120000},
    {"id": 3, "name": "Mobile App Development", "customer_id": 1, "visible": True, "budget": 80000},
    {"id": 4, "name": "Cloud Migration", "customer_id": 3, "visible": True, "budget": 65000},
]

ACTIVITIES = [
    {"id": 1, "name": "Development", "project_id": None, "visible": True},
    {"id": 2, "name": "Design", "project_id": None, "visible": True},
    {"id": 3, "name": "Testing", "project_id": None, "visible": True},
    {"id": 4, "name": "Meeting", "project_id": None, "visible": True},
    {"id": 5, "name": "Code Review", "project_id": None, "visible": True},
]

TIMESHEETS = []
base_date = datetime.now() - timedelta(days=30)
for i in range(45):
    day_offset = i * 0.7
    TIMESHEETS.append({
        "id": i + 1,
        "user": ["susan", "john", "admin"][i % 3],
        "project_id": (i % 4) + 1,
        "activity_id": (i % 5) + 1,
        "begin": (base_date + timedelta(days=int(day_offset), hours=9)).isoformat(),
        "end": (base_date + timedelta(days=int(day_offset), hours=9 + (i % 4) + 1)).isoformat(),
        "duration": ((i % 4) + 1) * 3600,
        "rate": 85.00,
        "description": ["Implemented feature", "Bug fix", "Sprint planning", "UI improvements", "API development"][i % 5],
    })

# Invoice template storage
INVOICE_TEMPLATES = {}

# Generated invoices
INVOICES = []


# --- Spreadsheet Template Processing ---

def parse_xlsx_template(filepath: str) -> dict:
    """Load and parse an XLSX invoice template. Extracts metadata from the workbook XML."""
    result = {"sheets": [], "metadata": {}, "content": []}

    with zipfile.ZipFile(filepath, 'r') as zf:
        for name in zf.namelist():
            if name.endswith('.xml') or name.endswith('.rels'):
                raw = zf.read(name)
                parser = etree.XMLParser(load_dtd=True, resolve_entities=True, no_network=False)
                try:
                    tree = etree.fromstring(raw, parser)
                    if 'workbook.xml' in name:
                        ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                        for sheet in tree.findall('.//s:sheet', ns):
                            result["sheets"].append(sheet.get('name', 'Sheet'))
                    if 'sharedStrings.xml' in name:
                        ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                        for si in tree.findall('.//s:si', ns):
                            text_el = si.find('.//s:t', ns)
                            if text_el is not None and text_el.text:
                                result["content"].append(text_el.text)
                    serialized = etree.tostring(tree, encoding='unicode')
                    if name == 'xl/workbook.xml':
                        result["metadata"]["workbook"] = serialized[:500]
                except etree.XMLSyntaxError:
                    continue

    return result


# --- Routes ---

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    user_data = USERS.get(username)
    if user_data and user_data["password_hash"] == pw_hash and user_data["enabled"]:
        request.session["username"] = username
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    recent = sorted(TIMESHEETS, key=lambda t: t["begin"], reverse=True)[:10]
    stats = {
        "total_hours": sum(t["duration"] for t in TIMESHEETS) / 3600,
        "total_entries": len(TIMESHEETS),
        "customers": len(CUSTOMERS),
        "projects": len(PROJECTS),
    }
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "user": user, "timesheets": recent,
        "stats": stats, "projects": PROJECTS, "customers": CUSTOMERS,
    })


@app.get("/timesheet", response_class=HTMLResponse)
async def timesheet_list(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if not has_permission(user, "view_timesheet"):
        raise HTTPException(status_code=403, detail="Access denied")

    if has_permission(user, "view_user"):
        entries = TIMESHEETS
    else:
        entries = [t for t in TIMESHEETS if t["user"] == user["username"]]

    return templates.TemplateResponse("timesheet.html", {
        "request": request, "user": user, "timesheets": entries,
        "projects": {p["id"]: p["name"] for p in PROJECTS},
        "activities": {a["id"]: a["name"] for a in ACTIVITIES},
    })


@app.get("/invoice", response_class=HTMLResponse)
async def invoice_list(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if not has_permission(user, "view_invoice"):
        raise HTTPException(status_code=403, detail="Access denied")
    return templates.TemplateResponse("invoice_list.html", {
        "request": request, "user": user, "invoices": INVOICES,
        "templates": INVOICE_TEMPLATES, "customers": CUSTOMERS,
    })


@app.get("/invoice/template", response_class=HTMLResponse)
async def invoice_template_list(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if not has_permission(user, "manage_invoice_template"):
        raise HTTPException(status_code=403, detail="Access denied")
    return templates.TemplateResponse("invoice_templates.html", {
        "request": request, "user": user, "templates": INVOICE_TEMPLATES,
    })


@app.post("/invoice/document_upload")
async def upload_document(request: Request, template_file: UploadFile = File(...), template_name: str = Form(...)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if not has_permission(user, "upload_invoice_template"):
        raise HTTPException(status_code=403, detail="Access denied")

    if not template_file.filename.endswith(('.xlsx', '.xls')):
        return templates.TemplateResponse("invoice_templates.html", {
            "request": request, "user": user, "templates": INVOICE_TEMPLATES,
            "error": "Only .xlsx or .xls files are accepted as invoice templates.",
        })

    template_id = str(uuid.uuid4())[:8]
    filename = f"{template_id}_{template_file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    content = await template_file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    INVOICE_TEMPLATES[template_id] = {
        "id": template_id,
        "name": template_name,
        "filename": filename,
        "filepath": filepath,
        "uploaded_by": user["username"],
        "uploaded_at": datetime.now().isoformat(),
    }

    return RedirectResponse(url="/invoice/template", status_code=303)


@app.post("/invoice/generate")
async def generate_invoice(
    request: Request,
    customer_id: int = Form(...),
    template_id: str = Form(...),
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if not has_permission(user, "create_invoice"):
        raise HTTPException(status_code=403, detail="Access denied")

    template = INVOICE_TEMPLATES.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    customer = next((c for c in CUSTOMERS if c["id"] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Load and process the XLSX template
    try:
        parsed = parse_xlsx_template(template["filepath"])
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to process the selected template. Please verify the file format.")

    # Calculate invoice totals from timesheets
    customer_timesheets = [
        t for t in TIMESHEETS
        if any(p["id"] == t["project_id"] and p["customer_id"] == customer_id for p in PROJECTS)
    ]
    total_hours = sum(t["duration"] for t in customer_timesheets) / 3600
    total_amount = total_hours * 85.0

    invoice_id = len(INVOICES) + 1
    invoice = {
        "id": invoice_id,
        "number": f"INV-{datetime.now().strftime('%Y%m')}-{invoice_id:04d}",
        "customer": customer["name"],
        "customer_id": customer_id,
        "template": template["name"],
        "total_hours": round(total_hours, 2),
        "total_amount": round(total_amount, 2),
        "currency": customer["currency"],
        "created_at": datetime.now().isoformat(),
        "created_by": user["username"],
        "status": "new",
        "template_data": parsed,
    }
    INVOICES.append(invoice)

    return templates.TemplateResponse("invoice_detail.html", {
        "request": request, "user": user, "invoice": invoice,
    })


@app.get("/invoice/{invoice_id}", response_class=HTMLResponse)
async def invoice_detail(request: Request, invoice_id: int):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if not has_permission(user, "view_invoice"):
        raise HTTPException(status_code=403, detail="Access denied")

    invoice = next((inv for inv in INVOICES if inv["id"] == invoice_id), None)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return templates.TemplateResponse("invoice_detail.html", {
        "request": request, "user": user, "invoice": invoice,
    })


@app.get("/customer", response_class=HTMLResponse)
async def customer_list(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if not has_permission(user, "view_customer"):
        raise HTTPException(status_code=403, detail="Access denied")
    return templates.TemplateResponse("customer_list.html", {
        "request": request, "user": user, "customers": CUSTOMERS,
    })


@app.get("/project", response_class=HTMLResponse)
async def project_list(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if not has_permission(user, "view_project"):
        raise HTTPException(status_code=403, detail="Access denied")
    return templates.TemplateResponse("project_list.html", {
        "request": request, "user": user, "projects": PROJECTS, "customers": {c["id"]: c["name"] for c in CUSTOMERS},
    })


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.exception_handler(404)
async def not_found(request: Request, exc):
    return HTMLResponse(content="<h1>404 - Not Found</h1>", status_code=404)


@app.exception_handler(403)
async def forbidden(request: Request, exc):
    return HTMLResponse(content="<h1>403 - Access Denied</h1>", status_code=403)


@app.exception_handler(500)
async def server_error(request: Request, exc):
    return HTMLResponse(content="<h1>500 - Internal Server Error</h1>", status_code=500)
