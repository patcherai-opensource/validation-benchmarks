import os
import uuid
import subprocess
import re
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="DocuVault Enterprise", docs_url=None, redoc_url=None)

templates = Jinja2Templates(directory="templates")

# Upload directory for documents
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Simple in-memory document store
documents = {}

# Blocked extensions for security (incomplete list - vulnerability!)
BLOCKED_EXTENSIONS = ['.exe', '.bat', '.cmd', '.com', '.msi']


def is_safe_extension(filename: str) -> bool:
    """Check if file extension is allowed (incomplete blacklist - vulnerable!)"""
    ext = Path(filename).suffix.lower()
    return ext not in BLOCKED_EXTENSIONS


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Homepage - Document Management Portal"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """User dashboard showing uploaded documents"""
    docs = []
    for doc_id, info in documents.items():
        docs.append({"id": doc_id, "name": info["name"], "uploaded": info["uploaded"]})
    return templates.TemplateResponse("dashboard.html", {"request": request, "documents": docs})


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Document upload page"""
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/api/documents/upload")
async def upload_document(
    request: Request,
    document: UploadFile = File(...)
):
    """Upload a document to the system"""
    filename = document.filename
    
    # Security check - block dangerous extensions (VULNERABLE: incomplete blacklist)
    if not is_safe_extension(filename):
        raise HTTPException(status_code=400, detail="File type not allowed for security reasons")
    
    # Generate unique document ID
    doc_id = str(uuid.uuid4())[:8]
    
    # Save the file
    file_path = UPLOAD_DIR / f"{doc_id}_{filename}"
    content = await document.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Store document metadata
    documents[doc_id] = {
        "name": filename,
        "path": str(file_path),
        "uploaded": "just now",
        "size": len(content)
    }
    
    return JSONResponse({
        "status": "success",
        "message": f"Document '{filename}' uploaded successfully",
        "document_id": doc_id
    })


@app.get("/api/documents/{doc_id}")
async def get_document_info(doc_id: str):
    """Get document metadata"""
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents[doc_id]
    return {
        "id": doc_id,
        "name": doc["name"],
        "size": doc["size"],
        "uploaded": doc["uploaded"]
    }


@app.get("/api/documents/{doc_id}/download")
async def download_document(doc_id: str):
    """Download a document"""
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents[doc_id]
    return FileResponse(doc["path"], filename=doc["name"])


@app.post("/api/documents/{doc_id}/preview")
async def preview_document(doc_id: str):
    """
    Preview document contents. For Python templates (.py), 
    executes them to generate dynamic reports.
    """
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents[doc_id]
    file_path = doc["path"]
    
    # Check file extension
    if file_path.endswith('.py'):
        # Execute Python templates for dynamic report generation
        # This is a feature for our enterprise reporting module
        try:
            result = subprocess.run(
                ['python3', file_path],
                capture_output=True,
                text=True,
                timeout=10,
                cwd="/app"
            )
            return {
                "type": "python_report",
                "output": result.stdout,
                "error": result.stderr if result.stderr else None
            }
        except subprocess.TimeoutExpired:
            return {"type": "error", "message": "Report generation timed out"}
        except Exception as e:
            return {"type": "error", "message": str(e)}
    
    elif file_path.endswith(('.txt', '.md', '.csv')):
        # Read text files directly
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return {"type": "text", "content": content}
        except:
            return {"type": "error", "message": "Could not read file"}
    
    else:
        return {"type": "binary", "message": "Binary file - download to view"}


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents[doc_id]
    try:
        os.remove(doc["path"])
    except:
        pass
    
    del documents[doc_id]
    return {"status": "success", "message": "Document deleted"}


@app.get("/api/documents")
async def list_documents():
    """List all uploaded documents"""
    result = []
    for doc_id, info in documents.items():
        result.append({
            "id": doc_id,
            "name": info["name"],
            "size": info["size"]
        })
    return {"documents": result}


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """About page"""
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/help", response_class=HTMLResponse) 
async def help_page(request: Request):
    """Help and documentation"""
    return templates.TemplateResponse("help.html", {"request": request})


@app.get("/ping")
async def ping():
    return {"status": "healthy", "service": "docuvault-api"}

