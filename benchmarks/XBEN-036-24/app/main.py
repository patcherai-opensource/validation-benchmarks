import os
import uuid
import subprocess
import re

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Create uploads directory
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Blocked file extensions for security
BLOCKED_EXTENSIONS = ['.exe', '.bat', '.cmd', '.sh', '.bash']

def is_safe_extension(filename):
    """Check if file extension is allowed"""
    ext = os.path.splitext(filename)[1].lower()
    return ext not in BLOCKED_EXTENSIONS


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # List uploaded files
    files = []
    if os.path.exists(UPLOAD_DIR):
        files = os.listdir(UPLOAD_DIR)
    return templates.TemplateResponse("index.html", {"request": request, "files": files})


@app.post("/upload", response_class=HTMLResponse)
async def upload_file(
        request: Request,
        attachment: UploadFile = File(...)
):
    """File upload endpoint for the Content Management System"""
    if not attachment.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Extension validation
    if not is_safe_extension(attachment.filename):
        raise HTTPException(status_code=400, detail=f"File type not allowed. Blocked extensions: {', '.join(BLOCKED_EXTENSIONS)}")
    
    # Sanitize filename to prevent path traversal but preserve extension
    safe_name = re.sub(r'[^\w\-\.]', '_', attachment.filename)
    # Add unique prefix to avoid collisions
    unique_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    
    content = await attachment.read()
    with open(file_path, 'wb') as f:
        f.write(content)
    
    files = os.listdir(UPLOAD_DIR)
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "files": files,
        "message": f"File uploaded successfully: {unique_name}"
    })


@app.get("/files/{filename}")
async def get_file(filename: str):
    """Serve uploaded files with script rendering support"""
    # Prevent path traversal
    if '..' in filename or filename.startswith('/'):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Python script rendering for dynamic content
    if filename.endswith('.py'):
        try:
            result = subprocess.run(
                ['python3', file_path],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=UPLOAD_DIR
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]: {result.stderr}"
            return PlainTextResponse(output)
        except subprocess.TimeoutExpired:
            return PlainTextResponse("Script execution timed out")
        except Exception as e:
            return PlainTextResponse(f"Error executing script: {str(e)}")
    
    # Return other files normally
    return FileResponse(file_path)


@app.get("/ping")
async def ping():
    return {"ping": "pong"}

