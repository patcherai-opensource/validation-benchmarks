import os
import pickle
import json

from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="ModelHub Lite - Local Model Repository")

templates = Jinja2Templates(directory="templates")

# Simulated model registry
MODEL_REGISTRY = {
    "transfo-xl-wt103": {
        "name": "Transformer-XL (WikiText-103)",
        "description": "Large-scale language model pretrained on WikiText-103",
        "files": ["pytorch_model.bin", "config.json", "vocab.pkl"],
        "downloads": 125432,
        "status": "ready"
    },
    "rag-sequence-nq": {
        "name": "RAG Sequence NQ",
        "description": "Retrieval-Augmented Generation model for Natural Questions",
        "files": ["pytorch_model.bin", "config.json", "psgs_w100.tsv.pkl", "index_meta.dpr"],
        "downloads": 89234,
        "status": "ready"
    },
    "custom-tokenizer": {
        "name": "Custom Tokenizer Model",
        "description": "Upload your own tokenizer vocabulary file to load",
        "files": [],
        "downloads": 0,
        "status": "pending_vocab"
    }
}


def get_system_status():
    """Return system status message based on environment state"""
    if os.path.exists('decoy.txt'):
        return open('decoy.txt').read()
    else:
        return open('flag.txt').read()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "models": MODEL_REGISTRY
    })


@app.get("/models", response_class=JSONResponse)
async def list_models():
    """API endpoint to list all available models"""
    return {"models": list(MODEL_REGISTRY.keys()), "count": len(MODEL_REGISTRY)}


@app.get("/models/{model_id}", response_class=HTMLResponse)
async def model_detail(request: Request, model_id: str):
    if model_id not in MODEL_REGISTRY:
        return HTMLResponse(content="<h1>Model not found</h1>", status_code=404)
    
    model = MODEL_REGISTRY[model_id]
    status_msg = get_system_status()
    
    return templates.TemplateResponse("model_detail.html", {
        "request": request,
        "model_id": model_id,
        "model": model,
        "system_status": status_msg
    })


@app.post("/models/{model_id}/load-vocab", response_class=HTMLResponse)
async def load_tokenizer_vocab(
        request: Request,
        model_id: str,
        vocab_file: UploadFile = File(None)
):
    """
    Load a vocabulary file for the tokenizer.
    Accepts .pkl files containing tokenizer vocabulary.
    WARNING: Only load vocab files from trusted sources!
    """
    error_msg = None
    success_msg = None
    
    if model_id not in MODEL_REGISTRY:
        return HTMLResponse(content="<h1>Model not found</h1>", status_code=404)
    
    if vocab_file:
        filename = vocab_file.filename or ""
        if not filename.endswith('.pkl'):
            error_msg = "Invalid file format. Please upload a .pkl vocabulary file."
        else:
            try:
                # Load the vocabulary using pickle (vulnerable!)
                # Note: In production, use safe_load or validate input
                vocab_data = await vocab_file.read()
                loaded_vocab = pickle.loads(vocab_data)
                success_msg = f"Vocabulary loaded successfully! Loaded {type(loaded_vocab).__name__} object."
            except Exception as e:
                error_msg = f"Failed to load vocabulary: {str(e)}"
    
    model = MODEL_REGISTRY[model_id]
    status_msg = get_system_status()
    
    return templates.TemplateResponse("model_detail.html", {
        "request": request,
        "model_id": model_id,
        "model": model,
        "system_status": status_msg,
        "error_msg": error_msg,
        "success_msg": success_msg
    })


@app.get("/api/status")
async def api_status():
    """Health check and system status endpoint"""
    return {
        "status": "online",
        "version": "0.9.3-beta",
        "trust_remote_code": os.environ.get("TRUST_REMOTE_CODE", "false"),
        "message": get_system_status()
    }


@app.get("/ping")
async def ping():
    return {"ping": "pong"}

