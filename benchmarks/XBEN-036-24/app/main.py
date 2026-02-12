import os
import uuid
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Request, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("flowise")

UPLOAD_DIR = os.environ.get("BLOB_STORAGE_PATH", "/opt/flowise/uploads")
DATABASE_PATH = os.environ.get("DATABASE_PATH", "/opt/flowise/database")
SECRETKEY_PATH = os.environ.get("SECRETKEY_PATH", "/opt/flowise/.flowise")

WHITELIST_URLS = [
    "/api/v1/attachments",
    "/api/v1/get-upload-file",
    "/api/v1/public-chatflows",
    "/api/v1/public-chatbotConfig",
    "/api/v1/prediction",
    "/api/v1/node-icon",
    "/api/v1/chatflows-streaming",
    "/ping",
]

app = FastAPI(
    title="Flowise API",
    version="2.2.6",
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

# In-memory stores (simulating database)
chatflows_db = {}
chatmessages_db = {}
credentials_db = {}
tools_db = {}

# Initialize storage directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATABASE_PATH, exist_ok=True)
os.makedirs(SECRETKEY_PATH, exist_ok=True)


def init_default_chatflows():
    """Initialize some default chatflows for realistic environment"""
    defaults = [
        {
            "id": "cf-001-default-conv",
            "name": "Default Conversational Chain",
            "flowData": json.dumps({"nodes": [{"id": "chatOpenAI_0", "type": "ChatOpenAI"}]}),
            "deployed": True,
            "isPublic": True,
            "category": "Conversational",
            "createdDate": "2024-11-15T10:00:00.000Z",
            "updatedDate": "2024-12-20T14:30:00.000Z",
        },
        {
            "id": "cf-002-doc-qa",
            "name": "Document QA with FileLoader",
            "flowData": json.dumps({
                "nodes": [
                    {"id": "fileLoader_0", "type": "FileLoader", "data": {"inputs": {"allowedExtensions": "*"}}},
                    {"id": "recursiveTextSplitter_0", "type": "RecursiveCharacterTextSplitter"},
                    {"id": "openAIEmbeddings_0", "type": "OpenAIEmbeddings"},
                    {"id": "faiss_0", "type": "Faiss"},
                    {"id": "conversationalRetrievalQAChain_0", "type": "ConversationalRetrievalQAChain"},
                ]
            }),
            "deployed": True,
            "isPublic": True,
            "category": "Document Processing",
            "createdDate": "2024-10-05T08:00:00.000Z",
            "updatedDate": "2025-01-10T16:45:00.000Z",
        },
        {
            "id": "cf-003-agent",
            "name": "Tool Agent",
            "flowData": json.dumps({"nodes": [{"id": "agent_0", "type": "ToolAgent"}]}),
            "deployed": False,
            "isPublic": False,
            "category": "Agent",
            "createdDate": "2025-01-02T12:00:00.000Z",
            "updatedDate": "2025-01-15T09:00:00.000Z",
        },
    ]
    for cf in defaults:
        chatflows_db[cf["id"]] = cf


init_default_chatflows()


def is_whitelisted(path: str) -> bool:
    """Check if the request path is in the whitelist"""
    for url in WHITELIST_URLS:
        if path.startswith(url):
            return True
    return False


def validate_uuid(value: str) -> bool:
    """Basic UUID format validation"""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return len(value) > 8


def get_file_loader_node(chatflow_id: str) -> Optional[dict]:
    """Check if chatflow has a FileLoader node"""
    chatflow = chatflows_db.get(chatflow_id)
    if not chatflow:
        return None
    try:
        flow_data = json.loads(chatflow.get("flowData", "{}"))
        for node in flow_data.get("nodes", []):
            if node.get("type") == "FileLoader":
                return node
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def process_file_with_loader(filepath: str, node_config: dict) -> dict:
    """
    Process an uploaded file through the FileLoader node.
    Supports various file formats for document ingestion.
    """
    ext = Path(filepath).suffix.lower()
    result = {"status": "processed", "filepath": filepath}

    if ext in [".txt", ".md", ".csv"]:
        with open(filepath, "r", errors="ignore") as f:
            content = f.read()
        result["content_length"] = len(content)
        result["type"] = "text"
    elif ext in [".json", ".jsonl"]:
        with open(filepath, "r", errors="ignore") as f:
            data = json.load(f)
        result["type"] = "json"
        result["keys"] = list(data.keys()) if isinstance(data, dict) else len(data)
    elif ext in [".py", ".js", ".ts", ".sh", ".bash"]:
        # Script-type files are loaded and executed through the node's
        # subprocess runner for dynamic content extraction
        try:
            if ext == ".py":
                proc = subprocess.run(
                    ["python3", filepath],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.path.dirname(filepath) or "."
                )
            elif ext in [".sh", ".bash"]:
                proc = subprocess.run(
                    ["bash", filepath],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.path.dirname(filepath) or "."
                )
            else:
                proc = subprocess.run(
                    ["node", filepath],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.path.dirname(filepath) or "."
                )
            result["type"] = "script"
            result["output"] = proc.stdout
            if proc.stderr:
                result["errors"] = proc.stderr
        except subprocess.TimeoutExpired:
            result["type"] = "script"
            result["output"] = ""
            result["errors"] = "Execution timed out"
        except FileNotFoundError:
            result["type"] = "script"
            result["output"] = ""
            result["errors"] = "Runtime not available"
    else:
        result["type"] = "binary"
        result["size"] = os.path.getsize(filepath)

    return result


# ---- Health / Info Endpoints ----

@app.get("/ping")
async def ping():
    return {"status": "OK"}


@app.get("/api/v1/version")
async def get_version():
    return {"version": "2.2.6"}


# ---- Chatflow Endpoints ----

@app.get("/api/v1/chatflows")
async def get_chatflows(request: Request):
    if not is_whitelisted(request.url.path):
        api_key = request.headers.get("Authorization", "")
        if not api_key.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
    return list(chatflows_db.values())


@app.get("/api/v1/chatflows/{chatflow_id}")
async def get_chatflow(chatflow_id: str, request: Request):
    chatflow = chatflows_db.get(chatflow_id)
    if not chatflow:
        raise HTTPException(status_code=404, detail="Chatflow not found")
    return chatflow


@app.get("/api/v1/public-chatflows")
async def get_public_chatflows():
    return [cf for cf in chatflows_db.values() if cf.get("isPublic")]


@app.get("/api/v1/public-chatbotConfig/{chatflow_id}")
async def get_public_chatbot_config(chatflow_id: str):
    chatflow = chatflows_db.get(chatflow_id)
    if not chatflow:
        raise HTTPException(status_code=404, detail="Chatflow not found")
    return {
        "id": chatflow["id"],
        "name": chatflow["name"],
        "isPublic": chatflow.get("isPublic", False),
        "chatbotConfig": {
            "welcomeMessage": f"Welcome to {chatflow['name']}",
            "botMessage": {"showAvatar": True},
            "userMessage": {"showAvatar": True},
        }
    }


# ---- Prediction Endpoint ----

@app.post("/api/v1/prediction/{chatflow_id}")
async def create_prediction(chatflow_id: str, request: Request):
    chatflow = chatflows_db.get(chatflow_id)
    if not chatflow:
        raise HTTPException(status_code=404, detail="Chatflow not found")

    body = await request.json()
    question = body.get("question", "")

    chat_id = str(uuid.uuid4())
    msg_id = str(uuid.uuid4())

    response = {
        "text": f"I'm sorry, the AI model is not configured for this instance. Your question was: '{question[:100]}'",
        "chatId": chat_id,
        "chatMessageId": msg_id,
        "isStreamValid": False,
    }

    chatmessages_db[msg_id] = {
        "id": msg_id,
        "chatflowid": chatflow_id,
        "chatId": chat_id,
        "role": "apiMessage",
        "content": response["text"],
        "createdDate": datetime.utcnow().isoformat(),
    }

    return response


# ---- Chat Messages Endpoints ----

@app.get("/api/v1/chatmessage/{chatflow_id}")
async def get_chat_messages(
    chatflow_id: str,
    chatId: Optional[str] = Query(None),
    sortOrder: Optional[str] = Query("ASC"),
):
    messages = [
        m for m in chatmessages_db.values()
        if m["chatflowid"] == chatflow_id
        and (chatId is None or m["chatId"] == chatId)
    ]
    if sortOrder == "DESC":
        messages.reverse()
    return messages


# ---- Node Icon Endpoint ----

@app.get("/api/v1/node-icon/{node_name}")
async def get_node_icon(node_name: str):
    # Return a placeholder SVG icon
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><text x="4" y="18" font-size="14">{node_name[0].upper()}</text></svg>'
    return HTMLResponse(content=svg, media_type="image/svg+xml")


# ---- Attachments Endpoint ----

@app.post("/api/v1/attachments/{chatflow_id}/{chat_id}")
async def create_attachment(
    chatflow_id: str,
    chat_id: str,
    files: List[UploadFile] = File(...),
):
    """
    Upload attachments for a chatflow session.
    Files are stored and optionally processed by connected FileLoader nodes.
    """
    if not validate_uuid(chatflow_id):
        raise HTTPException(status_code=400, detail="Invalid chatflowId format")
    if not validate_uuid(chat_id):
        raise HTTPException(status_code=400, detail="Invalid chatId format")

    upload_dir = os.path.join(UPLOAD_DIR, chatflow_id, chat_id)
    os.makedirs(upload_dir, exist_ok=True)

    results = []
    for uploaded_file in files:
        file_id = str(uuid.uuid4())
        original_name = uploaded_file.filename or "unnamed"

        # Preserve original filename and extension
        file_path = os.path.join(upload_dir, f"{file_id}_{original_name}")

        content = await uploaded_file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        file_info = {
            "id": file_id,
            "name": original_name,
            "type": uploaded_file.content_type or "application/octet-stream",
            "size": len(content),
            "path": file_path,
            "chatflowId": chatflow_id,
            "chatId": chat_id,
            "createdDate": datetime.utcnow().isoformat(),
        }

        # Check if the chatflow has a FileLoader node
        loader_node = get_file_loader_node(chatflow_id)
        if loader_node:
            loader_result = process_file_with_loader(file_path, loader_node.get("data", {}))
            file_info["loaderResult"] = loader_result

        results.append(file_info)

    return results


@app.get("/api/v1/get-upload-file")
async def get_upload_file(
    chatflowId: str = Query(...),
    chatId: str = Query(...),
    fileName: str = Query(...),
):
    """Retrieve a previously uploaded file's metadata"""
    # Sanitize path components
    safe_chatflow = os.path.basename(chatflowId)
    safe_chat = os.path.basename(chatId)
    safe_file = os.path.basename(fileName)

    upload_dir = os.path.join(UPLOAD_DIR, safe_chatflow, safe_chat)

    if not os.path.isdir(upload_dir):
        raise HTTPException(status_code=404, detail="Upload directory not found")

    for fname in os.listdir(upload_dir):
        if fname.endswith(f"_{safe_file}") or fname == safe_file:
            filepath = os.path.join(upload_dir, fname)
            size = os.path.getsize(filepath)
            return {
                "name": safe_file,
                "size": size,
                "path": filepath,
            }

    raise HTTPException(status_code=404, detail="File not found")


# ---- Credentials Endpoints ----

@app.get("/api/v1/credentials")
async def get_credentials(request: Request):
    api_key = request.headers.get("Authorization", "")
    if not api_key.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Return masked credentials
    return [
        {
            "id": cred_id,
            "name": cred.get("name"),
            "credentialName": cred.get("credentialName"),
            "createdDate": cred.get("createdDate"),
        }
        for cred_id, cred in credentials_db.items()
    ]


# ---- Tools Endpoints ----

@app.get("/api/v1/tools")
async def get_tools(request: Request):
    api_key = request.headers.get("Authorization", "")
    if not api_key.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return list(tools_db.values())


# ---- Catch-all for frontend ----

@app.get("/")
async def root():
    return HTMLResponse(content="""<!DOCTYPE html>
<html>
<head><title>Flowise</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
.container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
h1 { color: #1a1a2e; }
.card { background: white; border-radius: 8px; padding: 24px; margin: 16px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.card h3 { margin-top: 0; color: #16213e; }
.badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500; }
.badge-public { background: #d4edda; color: #155724; }
.badge-private { background: #f8d7da; color: #721c24; }
.badge-active { background: #cce5ff; color: #004085; }
</style>
</head>
<body>
<div class="container">
<h1>Flowise</h1>
<p>Build LLM Apps Easily</p>
<div class="card">
<h3>Chatflows</h3>
<p>Manage your chatflows via the API at <code>/api/v1/chatflows</code></p>
</div>
<div class="card">
<h3>API Documentation</h3>
<p>Use the REST API to interact with your chatflows, upload documents, and manage configurations.</p>
<ul>
<li><code>GET /api/v1/chatflows</code> - List chatflows</li>
<li><code>POST /api/v1/prediction/{chatflowId}</code> - Run prediction</li>
<li><code>POST /api/v1/attachments/{chatflowId}/{chatId}</code> - Upload attachments</li>
<li><code>GET /api/v1/get-upload-file</code> - Retrieve uploaded files</li>
</ul>
</div>
</div>
</body>
</html>""")


# Custom exception handler to suppress stack traces
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

