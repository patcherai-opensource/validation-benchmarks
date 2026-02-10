import os
import subprocess
import mimetypes
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, Response, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin":
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="session", value="editor_authenticated")
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    session = request.cookies.get("session")
    if session != "editor_authenticated":
        return RedirectResponse(url="/login", status_code=303)
    
    files = []
    for f in UPLOAD_DIR.iterdir():
        if f.is_file():
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "url": f"/media/{f.name}"
            })
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "files": files})


@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, content_file: UploadFile = File(...)):
    session = request.cookies.get("session")
    if session != "editor_authenticated":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    filename = content_file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    safe_filename = os.path.basename(filename)
    
    file_path = UPLOAD_DIR / safe_filename
    
    content = await content_file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/media/{filename:path}")
async def serve_media(filename: str, request: Request):
    safe_filename = os.path.basename(filename)
    file_path = UPLOAD_DIR / safe_filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if safe_filename.endswith(('.py', '.pyw')):
        try:
            result = subprocess.run(
                ['python3', str(file_path)],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(UPLOAD_DIR)
            )
            output = result.stdout
            if result.stderr:
                output += result.stderr
            return Response(content=output, media_type="text/plain")
        except subprocess.TimeoutExpired:
            return Response(content="Script execution timed out", media_type="text/plain")
        except Exception as e:
            return Response(content="Script execution failed", media_type="text/plain")
    
    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        content_type = "application/octet-stream"
    
    return FileResponse(file_path, media_type=content_type)


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/ping")
async def ping():
    return {"ping": "pong"}

