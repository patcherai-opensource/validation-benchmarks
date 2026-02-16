import os
import uuid
import subprocess
import mimetypes
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FlowWise API",
    version="2.2.4",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORAGE_PATH = Path(os.environ.get("STORAGE_PATH", "/tmp/flowwise_storage"))
STORAGE_PATH.mkdir(exist_ok=True, parents=True)

MIME_TO_LOADER = {
    "text/plain": "textLoader",
    "text/csv": "csvLoader",
    "text/markdown": "markdownLoader",
    "application/json": "jsonLoader",
    "application/xml": "xmlLoader",
    "text/xml": "xmlLoader",
    "application/pdf": "pdfLoader",
    "text/x-python": "scriptLoader",
    "text/x-shellscript": "scriptLoader",
    "application/x-sh": "scriptLoader",
}

EXT_TO_LOADER = {
    ".txt": "textLoader",
    ".csv": "csvLoader",
    ".md": "markdownLoader",
    ".json": "jsonLoader",
    ".xml": "xmlLoader",
    ".pdf": "pdfLoader",
    ".py": "scriptLoader",
    ".sh": "scriptLoader",
    ".bash": "scriptLoader",
    ".rb": "scriptLoader",
    ".pl": "scriptLoader",
    ".js": "scriptLoader",
}

workflows_db = {}
chat_messages_db = {}


def is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def resolve_loader(mimetype: str, extension: str) -> str:
    loader = EXT_TO_LOADER.get(extension.lower())
    if loader and loader != "textLoader":
        return loader
    mime_loader = MIME_TO_LOADER.get(mimetype)
    if mime_loader and mime_loader != "textLoader":
        return mime_loader
    if loader:
        return loader
    if mime_loader:
        return mime_loader
    return "binaryLoader"


def extract_content(file_path: Path, loader_type: str) -> dict:
    """
    Extract content from a file using the appropriate loader.
    """
    file_name = file_path.name
    file_size = file_path.stat().st_size

    try:
        if loader_type == "scriptLoader":
            result = subprocess.run(
                [_get_interpreter(file_path.suffix), str(file_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return {
                "name": file_name,
                "mime": mimetypes.guess_type(file_name)[0] or "application/octet-stream",
                "size": file_size,
                "content": result.stdout.strip() if result.returncode == 0 else "",
                "status": "processed",
            }

        elif loader_type in ("textLoader", "csvLoader", "markdownLoader", "jsonLoader", "xmlLoader"):
            with open(file_path, "r", errors="replace") as f:
                content = f.read()
            return {
                "name": file_name,
                "mime": mimetypes.guess_type(file_name)[0] or "text/plain",
                "size": file_size,
                "content": content[:2048],
                "status": "processed",
            }

        else:
            return {
                "name": file_name,
                "mime": mimetypes.guess_type(file_name)[0] or "application/octet-stream",
                "size": file_size,
                "status": "stored",
            }

    except subprocess.TimeoutExpired:
        return {
            "name": file_name,
            "size": file_size,
            "status": "error",
            "error": "Processing timed out",
        }
    except Exception:
        return {
            "name": file_name,
            "size": file_size,
            "status": "error",
            "error": "Failed to process file",
        }


def _get_interpreter(suffix: str) -> str:
    mapping = {
        ".py": "python3",
        ".sh": "bash",
        ".bash": "bash",
        ".rb": "ruby",
        ".pl": "perl",
        ".js": "node",
    }
    return mapping.get(suffix.lower(), "bash")


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.get("/")
async def root():
    return JSONResponse(
        content={
            "application": "FlowWise",
            "version": "2.2.4",
            "status": "running",
        }
    )


@app.get("/api/v1/ping")
async def api_ping():
    return {"status": "ok"}


@app.get("/api/v1/version")
async def get_version():
    return {"version": "2.2.4"}


@app.get("/api/v1/workflows")
async def list_workflows():
    return {"workflows": list(workflows_db.values())}


@app.post("/api/v1/workflows")
async def create_workflow(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request body")

    workflow_id = str(uuid.uuid4())
    workflow = {
        "id": workflow_id,
        "name": data.get("name", "Untitled Workflow"),
        "deployed": False,
        "isPublic": False,
        "apikeyid": "",
        "chatbotConfig": None,
        "apiConfig": {
            "upload": f"/api/v1/uploads/{workflow_id}/{{sessionId}}",
            "prediction": f"/api/v1/prediction/{workflow_id}",
            "chatmessages": f"/api/v1/chatmessages/{workflow_id}",
        },
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    workflows_db[workflow_id] = workflow
    return workflow


@app.get("/api/v1/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    if not is_valid_uuid(workflow_id):
        raise HTTPException(status_code=400, detail="Invalid workflow_id format - must be a valid UUID")
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    return workflows_db[workflow_id]


@app.put("/api/v1/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, request: Request):
    if not is_valid_uuid(workflow_id):
        raise HTTPException(status_code=400, detail="Invalid workflow_id format - must be a valid UUID")
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request body")
    workflows_db[workflow_id].update({
        k: v for k, v in data.items() if k in ("name", "deployed")
    })
    workflows_db[workflow_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return workflows_db[workflow_id]


@app.delete("/api/v1/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    if not is_valid_uuid(workflow_id):
        raise HTTPException(status_code=400, detail="Invalid workflow_id format - must be a valid UUID")
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    del workflows_db[workflow_id]
    return {"status": "deleted"}


@app.post("/api/v1/uploads/{workflow_id}/{session_id}")
async def create_upload(
    workflow_id: str,
    session_id: str,
    files: List[UploadFile] = File(...),
):
    if not is_valid_uuid(workflow_id):
        raise HTTPException(status_code=400, detail="Invalid workflow_id format - must be a valid UUID")
    if not is_valid_uuid(session_id):
        raise HTTPException(status_code=400, detail="Invalid session_id format - must be a valid UUID")

    upload_dir = STORAGE_PATH / workflow_id / session_id
    upload_dir.mkdir(exist_ok=True, parents=True)

    results = []
    for file in files:
        original_name = file.filename or "unnamed"
        raw = await file.read()

        dest = upload_dir / original_name
        with open(dest, "wb") as f:
            f.write(raw)
        os.chmod(str(dest), 0o755)

        mime = file.content_type or mimetypes.guess_type(original_name)[0] or "application/octet-stream"
        ext = Path(original_name).suffix
        loader = resolve_loader(mime, ext)
        info = extract_content(dest, loader)
        results.append(info)

    return {
        "workflow_id": workflow_id,
        "session_id": session_id,
        "files": results,
    }


@app.get("/api/v1/chatmessages/{workflow_id}")
async def get_chat_messages(workflow_id: str):
    if not is_valid_uuid(workflow_id):
        raise HTTPException(status_code=400, detail="Invalid workflow_id format - must be a valid UUID")
    messages = chat_messages_db.get(workflow_id, [])
    return {"messages": messages}


@app.post("/api/v1/prediction/{workflow_id}")
async def create_prediction(
    workflow_id: str,
    request: Request,
):
    if not is_valid_uuid(workflow_id):
        raise HTTPException(status_code=400, detail="Invalid workflow_id format - must be a valid UUID")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request body")

    question = data.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="Missing 'question' field")

    msg = {
        "id": str(uuid.uuid4()),
        "role": "apiMessage",
        "content": f"Prediction response for: {question[:100]}",
        "workflow_id": workflow_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    chat_messages_db.setdefault(workflow_id, []).append(msg)
    return msg


@app.get("/api/v1/feedback")
async def list_feedback():
    return {"feedback": []}


@app.get("/api/v1/node-icon/{name}")
async def get_node_icon(name: str):
    raise HTTPException(status_code=404, detail="Icon not found")

