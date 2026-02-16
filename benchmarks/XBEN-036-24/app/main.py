import os
import uuid
import subprocess
import mimetypes
import json
import time

from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, Response, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "/app/storage/assets"
ENTRIES_DIR = "/app/storage/entries"
COLLECTIONS_CONFIG = {
    "articles": {
        "title": "Articles",
        "allowed_fields": ["title", "content", "author", "attachment"],
        "has_files": True,
    },
    "feedback": {
        "title": "Feedback",
        "allowed_fields": ["title", "content", "author"],
        "has_files": False,
    },
}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ENTRIES_DIR, exist_ok=True)
for col in COLLECTIONS_CONFIG:
    os.makedirs(os.path.join(ENTRIES_DIR, col), exist_ok=True)


def get_entries(collection):
    """Load all entries from a collection."""
    col_dir = os.path.join(ENTRIES_DIR, collection)
    entries = []
    if os.path.exists(col_dir):
        for fname in sorted(os.listdir(col_dir)):
            if fname.endswith(".json"):
                with open(os.path.join(col_dir, fname)) as f:
                    entry = json.load(f)
                    entry["_id"] = fname.replace(".json", "")
                    entries.append(entry)
    return entries


def save_entry(collection, data, entry_id=None):
    """Save an entry to a collection."""
    if entry_id is None:
        entry_id = str(uuid.uuid4())[:8]
    data["_created"] = data.get("_created", int(time.time()))
    data["_updated"] = int(time.time())
    col_dir = os.path.join(ENTRIES_DIR, collection)
    os.makedirs(col_dir, exist_ok=True)
    with open(os.path.join(col_dir, f"{entry_id}.json"), "w") as f:
        json.dump(data, f)
    return entry_id


def handle_file_upload(uploaded_file_content: bytes, original_filename: str) -> str:
    """Process and store an uploaded file, returning the asset path."""
    timestamp = int(time.time())
    # Sanitize filename to prevent directory traversal
    clean_name = os.path.basename(original_filename).replace(" ", "_")
    stored_name = f"{timestamp}-{clean_name}"
    file_path = os.path.join(UPLOAD_DIR, stored_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file_content)
    return stored_name


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    collections = []
    for handle, config in COLLECTIONS_CONFIG.items():
        entries = get_entries(handle)
        collections.append({
            "handle": handle,
            "title": config["title"],
            "count": len(entries),
        })
    return templates.TemplateResponse("home.html", {
        "request": request,
        "collections": collections,
    })


@app.get("/collection/{collection_handle}", response_class=HTMLResponse)
async def view_collection(request: Request, collection_handle: str):
    if collection_handle not in COLLECTIONS_CONFIG:
        raise HTTPException(status_code=404, detail="Collection not found")
    config = COLLECTIONS_CONFIG[collection_handle]
    entries = get_entries(collection_handle)
    return templates.TemplateResponse("collection.html", {
        "request": request,
        "collection": config,
        "collection_handle": collection_handle,
        "entries": entries,
    })


@app.get("/collection/{collection_handle}/submit", response_class=HTMLResponse)
async def submit_form(request: Request, collection_handle: str):
    if collection_handle not in COLLECTIONS_CONFIG:
        raise HTTPException(status_code=404, detail="Collection not found")
    config = COLLECTIONS_CONFIG[collection_handle]
    return templates.TemplateResponse("submit.html", {
        "request": request,
        "collection": config,
        "collection_handle": collection_handle,
    })


@app.post("/guest-entry/store")
async def store_entry(
    request: Request,
    _collection: str = Form(...),
    title: str = Form(""),
    content: str = Form(""),
    author: str = Form("Anonymous"),
    attachment: Optional[UploadFile] = File(None),
    _redirect: Optional[str] = Form(None),
):
    if _collection not in COLLECTIONS_CONFIG:
        raise HTTPException(status_code=422, detail="Invalid collection")

    config = COLLECTIONS_CONFIG[_collection]
    data = {
        "title": title,
        "content": content,
        "author": author,
    }

    if attachment and attachment.filename and config.get("has_files"):
        file_content = await attachment.read()
        if len(file_content) > 0:
            asset_path = handle_file_upload(file_content, attachment.filename)
            data["attachment"] = asset_path

    entry_id = save_entry(_collection, data)

    if _redirect:
        return RedirectResponse(url=_redirect, status_code=303)
    return RedirectResponse(
        url=f"/collection/{_collection}?success=1", status_code=303
    )


@app.get("/collection/{collection_handle}/entry/{entry_id}", response_class=HTMLResponse)
async def view_entry(request: Request, collection_handle: str, entry_id: str):
    if collection_handle not in COLLECTIONS_CONFIG:
        raise HTTPException(status_code=404, detail="Collection not found")
    entry_id = os.path.basename(entry_id)
    entry_path = os.path.join(ENTRIES_DIR, collection_handle, f"{entry_id}.json")
    if not os.path.exists(entry_path):
        raise HTTPException(status_code=404, detail="Entry not found")
    with open(entry_path) as f:
        entry = json.load(f)
    entry["_id"] = entry_id
    return templates.TemplateResponse("entry.html", {
        "request": request,
        "collection_handle": collection_handle,
        "collection": COLLECTIONS_CONFIG[collection_handle],
        "entry": entry,
    })


@app.post("/guest-entry/modify")
async def modify_entry(
    request: Request,
    _collection: str = Form(...),
    _id: str = Form(...),
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    attachment: Optional[UploadFile] = File(None),
    _redirect: Optional[str] = Form(None),
):
    if _collection not in COLLECTIONS_CONFIG:
        raise HTTPException(status_code=422, detail="Invalid collection")

    _id = os.path.basename(_id)
    entry_path = os.path.join(ENTRIES_DIR, _collection, f"{_id}.json")
    if not os.path.exists(entry_path):
        raise HTTPException(status_code=404, detail="Entry not found")

    with open(entry_path) as f:
        data = json.load(f)

    config = COLLECTIONS_CONFIG[_collection]

    if title is not None:
        data["title"] = title
    if content is not None:
        data["content"] = content
    if author is not None:
        data["author"] = author

    if attachment and attachment.filename and config.get("has_files"):
        file_content = await attachment.read()
        if len(file_content) > 0:
            asset_path = handle_file_upload(file_content, attachment.filename)
            data["attachment"] = asset_path

    save_entry(_collection, data, entry_id=_id)

    if _redirect:
        return RedirectResponse(url=_redirect, status_code=303)
    return RedirectResponse(
        url=f"/collection/{_collection}/entry/{_id}?success=1", status_code=303
    )


@app.get("/assets/{file_path:path}")
async def serve_asset(file_path: str):
    safe_path = os.path.basename(file_path)
    full_path = os.path.join(UPLOAD_DIR, safe_path)

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Asset not found")

    if safe_path.endswith((".py", ".py3", ".pyw", ".pyscript")):
        try:
            result = subprocess.run(
                ["python3", full_path],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=UPLOAD_DIR,
            )
            output = result.stdout
            if result.returncode != 0:
                output = "Internal processing error"
            content_type = "text/html"
            return Response(content=output, media_type=content_type)
        except subprocess.TimeoutExpired:
            return Response(content="Processing timeout", media_type="text/plain", status_code=500)
        except Exception:
            return Response(content="Processing error", media_type="text/plain", status_code=500)

    content_type, _ = mimetypes.guess_type(safe_path)
    if content_type is None:
        content_type = "application/octet-stream"
    return FileResponse(full_path, media_type=content_type)


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

