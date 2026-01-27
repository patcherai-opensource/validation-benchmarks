import os
import base64

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from starlette.requests import Request
from starlette.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Base directory for media storage
MEDIA_BASE_DIR = "/app/media"


def get_decoded_path(node: str) -> str:
    """Decode base64-encoded path from node parameter."""
    try:
        decoded = base64.b64decode(node).decode('utf-8')
        return decoded
    except Exception:
        return ""


def list_files_in_directory(path: str) -> list:
    """List all files and directories in the given path."""
    result = []
    try:
        if os.path.isdir(path):
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                result.append({
                    "name": item,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                })
    except Exception as e:
        pass
    return result


@app.get("/")
async def read_root(request: Request):
    """Main admin panel dashboard."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/admin/media")
async def media_browser(request: Request, node: str = None):
    """
    WYSIWYG Media Browser - Browse uploaded media files.
    The 'node' parameter is base64-encoded path relative to media directory.
    """
    if not node:
        # Default to base media directory
        current_path = MEDIA_BASE_DIR
        relative_path = ""
    else:
        # Decode the node parameter to get the path
        # VULNERABILITY: No validation for path traversal sequences
        decoded_path = get_decoded_path(node)
        current_path = os.path.join(MEDIA_BASE_DIR, decoded_path)
        relative_path = decoded_path
    
    files = list_files_in_directory(current_path)
    
    return templates.TemplateResponse("media.html", {
        "request": request,
        "files": files,
        "current_path": relative_path,
        "node": node or ""
    })


@app.get("/admin/media/download")
async def download_file(node: str):
    """
    Download a media file.
    The 'node' parameter is base64-encoded path to the file.
    """
    if not node:
        raise HTTPException(status_code=400, detail="Missing node parameter")
    
    # Decode the node parameter
    # VULNERABILITY: Path traversal - no validation for ../ sequences
    decoded_path = get_decoded_path(node)
    file_path = os.path.join(MEDIA_BASE_DIR, decoded_path)
    
    # Check if file exists
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Return file content
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return JSONResponse(content={
            "filename": os.path.basename(file_path),
            "content": content,
            "status": "success"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@app.post("/admin/media/delete")
async def delete_folder(node: str):
    """
    Delete a media folder.
    The 'node' parameter is base64-encoded path to the folder.
    Similar to Magento's deleteFolderAction vulnerability.
    """
    if not node:
        raise HTTPException(status_code=400, detail="Missing node parameter")
    
    decoded_path = get_decoded_path(node)
    folder_path = os.path.join(MEDIA_BASE_DIR, decoded_path)
    
    # For safety in this demo, we just return info about what would be deleted
    return JSONResponse(content={
        "action": "delete",
        "target_path": folder_path,
        "decoded_node": decoded_path,
        "status": "deletion_simulated"
    })


@app.get("/api/storage/info")
async def storage_info():
    """Get storage information for the media library."""
    return JSONResponse(content={
        "version": "1.9.4.5",
        "media_path": MEDIA_BASE_DIR,
        "encoding": "base64",
        "api_endpoints": [
            "/admin/media - Browse media files",
            "/admin/media/download?node=<base64_path> - Download file",
            "/admin/media/delete?node=<base64_path> - Delete folder"
        ]
    })


@app.get("/ping")
def ping():
    return {"ping": "pong"}
