import os
import uuid
import shutil
import zipfile
import secrets
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Form, UploadFile, File, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from lxml import etree

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

templates = Jinja2Templates(directory="templates")

# Data storage
UPLOAD_DIR = Path("/app/data/report_templates")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

GENERATED_DIR = Path("/app/data/generated")
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

# Admin credentials (configured during initial setup)
ADMIN_USER = "admin"
ADMIN_PASS_HASH = hashlib.sha256("admin".encode()).hexdigest()

# In-memory data stores
timesheet_entries = []
report_templates = {}
generated_reports = {}

# Seed some timesheet data
def seed_data():
    projects = ["Website Redesign", "Mobile App", "API Integration", "Database Migration"]
    activities = ["Development", "Testing", "Code Review", "Documentation", "Meetings"]
    users = ["john.doe", "jane.smith", "bob.wilson"]
    base_date = datetime(2024, 11, 1)
    
    for i in range(25):
        entry = {
            "id": i + 1,
            "user": users[i % len(users)],
            "project": projects[i % len(projects)],
            "activity": activities[i % len(activities)],
            "description": f"Task #{i+1} - {activities[i % len(activities)]}",
            "date": (base_date + timedelta(days=i % 30)).strftime("%Y-%m-%d"),
            "duration": round(1.5 + (i % 6) * 0.5, 1),
            "rate": 85.00 + (i % 4) * 15,
            "billable": i % 3 != 0
        }
        entry["total"] = round(entry["duration"] * entry["rate"], 2)
        timesheet_entries.append(entry)

seed_data()

# Auth dependency
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        return None
    return user

class AuthRedirectException(Exception):
    pass

@app.exception_handler(AuthRedirectException)
async def auth_redirect_handler(request: Request, exc: AuthRedirectException):
    return RedirectResponse(url="/auth/login", status_code=303)

def require_auth(request: Request):
    user = get_current_user(request)
    if not user:
        raise AuthRedirectException()
    return user

def require_admin(request: Request):
    user = require_auth(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user


LICENSE_FILE = "/etc/kronos/license.key"

@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": None
    })


@app.post("/auth/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    if username == ADMIN_USER and pw_hash == ADMIN_PASS_HASH:
        request.session["user"] = {
            "username": username,
            "role": "admin",
            "display_name": "Administrator"
        }
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Invalid credentials"
    })


@app.get("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=303)


@app.get("/system/info", response_class=HTMLResponse)
async def system_info(request: Request, user: dict = Depends(require_admin)):
    license_status = "Active" if os.path.exists(LICENSE_FILE) else "Not Found"
    return templates.TemplateResponse("system_info.html", {
        "request": request,
        "user": user,
        "version": "2.19.0",
        "license_status": license_status,
        "license_file": LICENSE_FILE,
        "python_version": "3.9",
        "data_dir": str(UPLOAD_DIR.parent),
    })


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: dict = Depends(require_auth)):
    total_hours = sum(e["duration"] for e in timesheet_entries)
    total_revenue = sum(e["total"] for e in timesheet_entries if e["billable"])
    billable_count = sum(1 for e in timesheet_entries if e["billable"])
    projects = list(set(e["project"] for e in timesheet_entries))
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "total_hours": round(total_hours, 1),
        "total_revenue": round(total_revenue, 2),
        "entry_count": len(timesheet_entries),
        "billable_count": billable_count,
        "projects": projects,
        "recent_entries": timesheet_entries[-5:]
    })


@app.get("/timesheet", response_class=HTMLResponse)
async def timesheet_list(request: Request, user: dict = Depends(require_auth)):
    return templates.TemplateResponse("timesheet.html", {
        "request": request,
        "user": user,
        "entries": timesheet_entries
    })


@app.get("/reporting/templates", response_class=HTMLResponse)
async def list_report_templates(request: Request, user: dict = Depends(require_admin)):
    return templates.TemplateResponse("report_templates.html", {
        "request": request,
        "user": user,
        "templates": report_templates
    })


@app.post("/reporting/templates/upload")
async def upload_report_template(
    request: Request,
    user: dict = Depends(require_admin),
    template_name: str = Form(...),
    template_file: UploadFile = File(...)
):
    # Validate file extension
    if not template_file.filename.endswith(('.xlsx', '.xls')):
        return templates.TemplateResponse("report_templates.html", {
            "request": request,
            "user": user,
            "templates": report_templates,
            "error": "Only .xlsx and .xls files are accepted as report templates."
        })

    # Check file size limit (5MB)
    content = await template_file.read()
    if len(content) > 5 * 1024 * 1024:
        return templates.TemplateResponse("report_templates.html", {
            "request": request,
            "user": user,
            "templates": report_templates,
            "error": "File size exceeds the 5MB limit."
        })

    template_id = str(uuid.uuid4())[:8]
    file_path = UPLOAD_DIR / f"{template_id}_{template_file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(content)

    report_templates[template_id] = {
        "id": template_id,
        "name": template_name,
        "filename": template_file.filename,
        "filepath": str(file_path),
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "uploaded_by": user["username"]
    }

    return RedirectResponse(url="/reporting/templates", status_code=303)


@app.post("/reporting/templates/{template_id}/delete")
async def delete_report_template(
    request: Request,
    template_id: str,
    user: dict = Depends(require_admin)
):
    tpl = report_templates.pop(template_id, None)
    if tpl:
        try:
            os.remove(tpl["filepath"])
        except OSError:
            pass
    return RedirectResponse(url="/reporting/templates", status_code=303)


def process_spreadsheet_xml(file_path: str, replacements: dict) -> str:
    """
    Load and process a spreadsheet template file.
    Parses the internal XML structure for template variable substitution.
    Returns path to generated output file.
    """
    output_path = GENERATED_DIR / f"report_{uuid.uuid4().hex[:12]}.xlsx"
    
    # Copy template as base
    shutil.copy2(file_path, str(output_path))
    
    # Process the XLSX (ZIP) contents for template substitution
    processed_parts = {}
    
    with zipfile.ZipFile(file_path, 'r') as zf:
        for name in zf.namelist():
            if name.endswith('.xml') or name.endswith('.rels'):
                raw_xml = zf.read(name)
                try:
                    parser = etree.XMLParser(resolve_entities=True, load_dtd=True)
                    tree = etree.fromstring(raw_xml, parser)
                    
                    # Perform template substitutions
                    xml_str = etree.tostring(tree, xml_declaration=True, encoding='UTF-8')
                    decoded = xml_str.decode('utf-8', errors='replace')
                    
                    for key, value in replacements.items():
                        decoded = decoded.replace("${" + key + "}", str(value))
                    
                    processed_parts[name] = decoded.encode('utf-8')
                except etree.XMLSyntaxError:
                    processed_parts[name] = raw_xml
    
    # Rebuild the XLSX with processed XML
    if processed_parts:
        temp_path = str(output_path) + ".tmp"
        with zipfile.ZipFile(file_path, 'r') as zf_in:
            with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zf_out:
                for name in zf_in.namelist():
                    if name in processed_parts:
                        zf_out.writestr(name, processed_parts[name])
                    else:
                        zf_out.writestr(name, zf_in.read(name))
        shutil.move(temp_path, str(output_path))
    
    return str(output_path)


@app.post("/reporting/generate", response_class=HTMLResponse)
async def generate_report(
    request: Request,
    user: dict = Depends(require_admin),
    template_id: str = Form(...),
    date_from: str = Form(""),
    date_to: str = Form(""),
    project_filter: str = Form("")
):
    projects = list(set(e["project"] for e in timesheet_entries))
    
    tpl = report_templates.get(template_id)
    if not tpl:
        return templates.TemplateResponse("report_generate.html", {
            "request": request,
            "user": user,
            "templates": report_templates,
            "projects": projects,
            "entries": timesheet_entries,
            "error": "Template not found.",
            "result": None
        })

    # Filter entries
    filtered = timesheet_entries[:]
    if project_filter:
        filtered = [e for e in filtered if e["project"] == project_filter]
    if date_from:
        filtered = [e for e in filtered if e["date"] >= date_from]
    if date_to:
        filtered = [e for e in filtered if e["date"] <= date_to]

    # Build replacements dict
    total_hours = sum(e["duration"] for e in filtered)
    total_amount = sum(e["total"] for e in filtered if e["billable"])
    
    replacements = {
        "report.title": f"Timesheet Report",
        "report.date": datetime.now().strftime("%Y-%m-%d"),
        "report.generated_by": user["display_name"],
        "report.total_entries": str(len(filtered)),
        "report.total_hours": str(round(total_hours, 1)),
        "report.total_amount": f"{total_amount:.2f}",
        "report.currency": "USD",
        "report.period_start": date_from or "N/A",
        "report.period_end": date_to or "N/A",
    }

    try:
        output_path = process_spreadsheet_xml(tpl["filepath"], replacements)
        report_id = str(uuid.uuid4())[:8]
        generated_reports[report_id] = {
            "id": report_id,
            "template": tpl["name"],
            "path": output_path,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "entries": len(filtered),
            "total_hours": round(total_hours, 1),
            "total_amount": round(total_amount, 2)
        }
        
        return templates.TemplateResponse("report_generate.html", {
            "request": request,
            "user": user,
            "templates": report_templates,
            "projects": projects,
            "entries": timesheet_entries,
            "error": None,
            "result": generated_reports[report_id],
            "report_id": report_id
        })
    except Exception as e:
        return templates.TemplateResponse("report_generate.html", {
            "request": request,
            "user": user,
            "templates": report_templates,
            "projects": projects,
            "entries": timesheet_entries,
            "error": "Failed to process template. Please check the template file format.",
            "result": None
        })


@app.get("/reporting/generate", response_class=HTMLResponse)
async def report_generate_page(request: Request, user: dict = Depends(require_admin)):
    projects = list(set(e["project"] for e in timesheet_entries))
    return templates.TemplateResponse("report_generate.html", {
        "request": request,
        "user": user,
        "templates": report_templates,
        "projects": projects,
        "entries": timesheet_entries,
        "error": None,
        "result": None
    })


@app.get("/reporting/download/{report_id}")
async def download_report(request: Request, report_id: str, user: dict = Depends(require_admin)):
    report = generated_reports.get(report_id)
    if not report or not os.path.exists(report["path"]):
        raise HTTPException(status_code=404, detail="Report not found")
    
    def iterfile():
        with open(report["path"], "rb") as f:
            yield from f
    
    return StreamingResponse(
        iterfile(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="report_{report_id}.xlsx"'
        }
    )
