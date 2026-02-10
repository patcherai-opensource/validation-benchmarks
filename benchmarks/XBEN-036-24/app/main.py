import os
import pickle
import shutil
import tempfile
import zipfile
import logging
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

# Suppress verbose logging
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

app = FastAPI(title="ModelHub", docs_url=None, redoc_url=None, openapi_url=None)

templates = Jinja2Templates(directory="templates")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return PlainTextResponse("Not Found", status_code=404)
    elif exc.status_code == 500:
        return PlainTextResponse("Internal Server Error", status_code=500)
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return PlainTextResponse("Internal Server Error", status_code=500)

# Simulated model registry
MODEL_REGISTRY = {
    "gpt2-small": {"vocab_size": 50257, "description": "GPT-2 Small (124M parameters)"},
    "bert-base": {"vocab_size": 30522, "description": "BERT Base Uncased"},
    "transfo-xl-base": {"vocab_size": 267735, "description": "Transformer-XL Base"},
}

MODELS_DIR = "/tmp/models"
os.makedirs(MODELS_DIR, exist_ok=True)


class TokenizerConfig:
    """Tokenizer configuration loaded from vocab files"""
    def __init__(self, vocab_data=None, special_tokens=None):
        self.vocab_data = vocab_data or {}
        self.special_tokens = special_tokens or ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
        self.vocab_size = len(self.vocab_data) if self.vocab_data else 0


def load_tokenizer_vocab(model_path):
    """Load vocabulary from a model directory - supports .pkl vocab files"""
    vocab_file = os.path.join(model_path, "vocab.pkl")
    if os.path.exists(vocab_file):
        with open(vocab_file, "rb") as f:
            vocab_data = pickle.load(f)
        return TokenizerConfig(vocab_data=vocab_data)
    return TokenizerConfig()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "models": MODEL_REGISTRY
    })


@app.get("/models", response_class=HTMLResponse)
async def list_models(request: Request):
    custom_models = []
    if os.path.exists(MODELS_DIR):
        for name in os.listdir(MODELS_DIR):
            model_path = os.path.join(MODELS_DIR, name)
            if os.path.isdir(model_path):
                custom_models.append(name)
    return templates.TemplateResponse("models.html", {
        "request": request,
        "registry_models": MODEL_REGISTRY,
        "custom_models": custom_models
    })


@app.post("/models/upload")
async def upload_model(
    request: Request,
    model_archive: UploadFile = File(...)
):
    """Upload a model archive (zip) containing model files including vocab.pkl"""
    if not model_archive.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Model archive must be a .zip file")
    
    content = await model_archive.read()
    
    # Extract model name from archive
    model_name = model_archive.filename.rsplit('.', 1)[0]
    model_path = os.path.join(MODELS_DIR, model_name)
    
    try:
        with zipfile.ZipFile(BytesIO(content), 'r') as zf:
            # Security check for path traversal
            for name in zf.namelist():
                if name.startswith('/') or '..' in name:
                    raise HTTPException(status_code=400, detail="Invalid file paths in archive")
            zf.extractall(model_path)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip archive")
    
    return JSONResponse({
        "status": "success",
        "message": f"Model '{model_name}' uploaded successfully",
        "model_name": model_name
    })


@app.get("/models/{model_name}/load")
async def load_model(request: Request, model_name: str):
    """Load a model and initialize its tokenizer - this loads vocab.pkl if present"""
    model_path = os.path.join(MODELS_DIR, model_name)
    
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    
    # Load tokenizer configuration from vocab files
    tokenizer = load_tokenizer_vocab(model_path)
    
    # Read internal model info if available
    model_info_path = os.path.join(model_path, "model_info.txt")
    model_info = None
    if os.path.exists(model_info_path):
        with open(model_info_path, 'r') as f:
            model_info = f.read()
    
    return templates.TemplateResponse("model_loaded.html", {
        "request": request,
        "model_name": model_name,
        "vocab_size": tokenizer.vocab_size,
        "special_tokens": tokenizer.special_tokens,
        "model_info": model_info
    })


@app.get("/api/models")
async def api_list_models():
    """API endpoint to list available models"""
    custom_models = []
    if os.path.exists(MODELS_DIR):
        for name in os.listdir(MODELS_DIR):
            model_path = os.path.join(MODELS_DIR, name)
            if os.path.isdir(model_path):
                custom_models.append({"name": name, "type": "custom"})
    
    registry = [{"name": k, "type": "registry", **v} for k, v in MODEL_REGISTRY.items()]
    return {"models": registry + custom_models}


@app.get("/ping")
async def ping():
    return {"ping": "pong"}

