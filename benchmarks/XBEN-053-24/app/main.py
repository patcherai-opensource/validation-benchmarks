import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from starlette.requests import Request
from starlette.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Directory for user-uploaded invoice templates (simulating Kimai's invoice template storage)
INVOICE_TEMPLATES_DIR = "/app/invoice_templates"
os.makedirs(INVOICE_TEMPLATES_DIR, exist_ok=True)

# Simulated invoice data for rendering
SAMPLE_INVOICE_DATA = {
    "invoice_number": "INV-2024-001",
    "customer_name": "Acme Corporation",
    "customer_email": "billing@acme.com",
    "items": [
        {"description": "Consulting Services", "hours": 40, "rate": 150, "total": 6000},
        {"description": "Project Management", "hours": 20, "rate": 125, "total": 2500},
    ],
    "subtotal": 8500,
    "tax": 850,
    "total": 9350,
    "date": "2024-01-15",
    "due_date": "2024-02-15"
}


@app.get("/")
async def read_root(request: Request):
    """Main dashboard - lists available invoice templates"""
    template_files = []
    if os.path.exists(INVOICE_TEMPLATES_DIR):
        for f in os.listdir(INVOICE_TEMPLATES_DIR):
            if f.endswith('.html') or f.endswith('.twig'):
                template_files.append(f)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "templates": template_files
    })


@app.get("/upload")
async def upload_page(request: Request):
    """Page for uploading new invoice templates"""
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/invoice/template/upload")
async def upload_template(file: UploadFile = File(...)):
    """
    Upload a new invoice template file.
    Accepts .html and .twig template files.
    
    This endpoint simulates the vulnerable uploadDocumentAction in Kimai's InvoiceController.
    In the vulnerable version, Twig template uploads are allowed by default.
    """
    allowed_extensions = ['.html', '.twig']
    filename = file.filename
    
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Only {', '.join(allowed_extensions)} files are allowed")
    
    # Generate unique filename to prevent overwrites
    unique_id = str(uuid.uuid4())[:8]
    safe_filename = f"{unique_id}_{os.path.basename(filename)}"
    file_path = os.path.join(INVOICE_TEMPLATES_DIR, safe_filename)
    
    # Save the uploaded template (no sandboxing or security checks - VULNERABLE)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return JSONResponse({
        "status": "success",
        "message": f"Template '{safe_filename}' uploaded successfully",
        "template_name": safe_filename
    })


@app.get("/invoice/render/{template_name}")
async def render_invoice(template_name: str):
    """
    Render an invoice using the specified template.
    
    This simulates the vulnerable template rendering in Kimai's PDFRenderer/AbstractTwigRenderer.
    The template is loaded and rendered WITHOUT sandboxing - allowing arbitrary code execution.
    """
    template_path = os.path.join(INVOICE_TEMPLATES_DIR, template_name)
    
    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Validate template is within allowed directory (prevent path traversal)
    real_path = os.path.realpath(template_path)
    if not real_path.startswith(os.path.realpath(INVOICE_TEMPLATES_DIR)):
        raise HTTPException(status_code=400, detail="Invalid template path")
    
    try:
        # VULNERABLE: No sandboxing applied to user-uploaded templates
        # This is the core vulnerability - templates are rendered with full Jinja2 capabilities
        env = Environment(loader=FileSystemLoader(INVOICE_TEMPLATES_DIR))
        template = env.get_template(template_name)
        
        # Render the template with invoice data
        rendered_content = template.render(**SAMPLE_INVOICE_DATA)
        
        return HTMLResponse(content=rendered_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering template: {str(e)}")


@app.get("/invoice/templates")
async def list_templates():
    """List all available invoice templates"""
    template_files = []
    if os.path.exists(INVOICE_TEMPLATES_DIR):
        for f in os.listdir(INVOICE_TEMPLATES_DIR):
            if f.endswith('.html') or f.endswith('.twig'):
                template_files.append(f)
    return {"templates": template_files}


@app.get("/ping")
def ping():
    return {"ping": "pong"}
