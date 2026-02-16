import hashlib
import json
import os
import secrets
import shutil
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
CACHE_DIR = BASE_DIR / "data" / "cache"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
CONFIG_PATH = Path("/etc/datalens/config.json")
SECRETS_PATH = Path("/etc/datalens/api_keys")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# In-memory session and event tracking
active_sessions = {}
event_results = {}
component_registry = {}


def get_app_config():
    return {
        "mode": "blocks",
        "dev_mode": False,
        "analytics_enabled": False,
        "components": [
            {
                "id": 1,
                "type": "textbox",
                "props": {
                    "label": "Input Text",
                    "placeholder": "Enter text to analyze...",
                    "lines": 3,
                    "interactive": True,
                },
            },
            {
                "id": 2,
                "type": "uploadbutton",
                "props": {
                    "label": "Upload Document",
                    "file_count": "single",
                    "file_types": [".txt", ".csv", ".json", ".pdf"],
                    "interactive": True,
                },
            },
            {
                "id": 3,
                "type": "textbox",
                "props": {
                    "label": "Analysis Result",
                    "interactive": False,
                    "lines": 5,
                },
            },
            {
                "id": 4,
                "type": "file",
                "props": {
                    "label": "Processed Output",
                    "interactive": False,
                },
            },
        ],
        "dependencies": [
            {
                "targets": [1, 2],
                "trigger": "then",
                "inputs": [1, 2],
                "outputs": [3, 4],
                "api_name": "analyze",
                "fn_index": 0,
            }
        ],
        "layout": {
            "id": 0,
            "children": [
                {"id": 1},
                {"id": 2},
                {"id": 3},
                {"id": 4},
            ],
        },
        "title": "DataLens - Document Analysis Platform",
        "version": "4.19.1",
        "is_colab": False,
        "theme": "default",
    }


def relocate_resource_to_cache(file_path: str) -> str:
    """
    Relocates a file resource into the application cache directory.
    Copies the file and returns the cached path for serving.
    """
    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")

    file_hash = hashlib.sha256(str(file_path).encode()).hexdigest()[:16]
    cache_subdir = CACHE_DIR / file_hash
    cache_subdir.mkdir(parents=True, exist_ok=True)

    dest = cache_subdir / src.name
    if not dest.exists():
        shutil.copy2(str(src), str(dest))

    return str(dest)


def resolve_input_data(data: Any) -> Any:
    """
    Process component input data, relocating any file references to cache.
    Handles nested structures with file objects containing 'path' keys.
    """
    if isinstance(data, dict):
        if "path" in data and isinstance(data["path"], str):
            cached = relocate_resource_to_cache(data["path"])
            data["path"] = cached
            if "url" not in data or data["url"] is None:
                data["url"] = f"/resource={cached}"
            return data
        return {k: resolve_input_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [resolve_input_data(item) for item in data]
    return data


def run_analysis(inputs: list) -> list:
    """Execute the analysis function with given inputs."""
    text_input = inputs[0] if len(inputs) > 0 else ""
    file_input = inputs[1] if len(inputs) > 1 else None

    result_text = ""
    result_file = None

    if text_input and isinstance(text_input, str):
        word_count = len(text_input.split())
        char_count = len(text_input)
        result_text = (
            f"Document Analysis Report\n"
            f"{'=' * 40}\n"
            f"Word count: {word_count}\n"
            f"Character count: {char_count}\n"
            f"Avg word length: {char_count / max(word_count, 1):.1f}\n"
        )

    if file_input and isinstance(file_input, dict) and "path" in file_input:
        fpath = Path(file_input["path"])
        if fpath.exists():
            try:
                content = fpath.read_text(errors="replace")
                lines = content.strip().split("\n")
                result_text += (
                    f"\nFile Analysis: {file_input.get('orig_name', fpath.name)}\n"
                    f"Lines: {len(lines)}\n"
                    f"Size: {fpath.stat().st_size} bytes\n"
                )
                result_file = {
                    "path": str(fpath),
                    "orig_name": file_input.get("orig_name", fpath.name),
                    "size": fpath.stat().st_size,
                }
            except Exception:
                result_text += "\nFile analysis: binary file detected, skipping text analysis\n"

    if not result_text:
        result_text = "No input provided. Please enter text or upload a document."

    return [result_text, result_file]


@app.get("/ping")
async def health_check():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "config": get_app_config()},
    )


@app.get("/info")
async def app_info():
    config = get_app_config()
    return {
        "version": config["version"],
        "mode": config["mode"],
        "analytics_enabled": config["analytics_enabled"],
        "app_dir": str(BASE_DIR),
        "config_path": str(CONFIG_PATH),
    }


@app.get("/config")
async def app_config():
    return get_app_config()


@app.post("/upload")
async def upload_file(files: UploadFile = File(...)):
    if not files.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    safe_name = Path(files.filename).name
    file_hash = hashlib.sha256(
        f"{safe_name}{time.time()}{secrets.token_hex(8)}".encode()
    ).hexdigest()[:16]

    dest_dir = UPLOAD_DIR / file_hash
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / safe_name

    content = await files.read()
    dest_path.write_bytes(content)

    return [str(dest_path)]


@app.post("/task/submit")
async def task_submit(request: Request):
    """
    Submit a processing task. Accepts component data and processes it
    through the configured analysis pipeline.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    session_hash = body.get("session_hash", secrets.token_hex(16))
    fn_index = body.get("fn_index", 0)
    data = body.get("data", [])
    event_id = str(uuid.uuid4())

    processed_data = resolve_input_data(data)

    try:
        outputs = run_analysis(processed_data)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Processing error.")

    output_data = []
    for out in outputs:
        if isinstance(out, dict) and "path" in out:
            cached_path = relocate_resource_to_cache(out["path"])
            out["path"] = cached_path
            out["url"] = f"/resource={cached_path}"
        output_data.append(out)

    event_results[event_id] = {
        "event_id": event_id,
        "data": output_data,
        "is_generating": False,
        "duration": 0.1,
        "average_duration": 0.1,
    }

    return {"event_id": event_id}


@app.get("/task/status/{event_id}")
async def task_status(event_id: str):
    if event_id in event_results:
        return {
            "msg": "process_completed",
            "output": event_results[event_id],
            "success": True,
        }
    return {
        "msg": "process_pending",
        "output": None,
        "success": True,
    }


@app.get("/resource={file_path:path}")
async def serve_resource(file_path: str, request: Request):
    """Serve a cached file resource."""
    abs_path = Path(file_path).resolve()

    if not abs_path.exists():
        raise HTTPException(status_code=404, detail="Resource not found.")

    if abs_path.is_dir():
        raise HTTPException(status_code=403, detail="Directory listing not permitted.")

    is_in_cache = str(abs_path).startswith(str(CACHE_DIR.resolve()))
    is_in_uploads = str(abs_path).startswith(str(UPLOAD_DIR.resolve()))

    if not (is_in_cache or is_in_uploads):
        raise HTTPException(status_code=403, detail="Access denied.")

    return FileResponse(
        str(abs_path),
        headers={"Accept-Ranges": "bytes"},
    )


@app.get("/examples")
async def get_examples():
    return {
        "examples": [
            {
                "inputs": [
                    "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the English alphabet.",
                    None,
                ],
                "description": "Basic text analysis",
            },
            {
                "inputs": [
                    "Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.",
                    None,
                ],
                "description": "ML description analysis",
            },
        ]
    }
