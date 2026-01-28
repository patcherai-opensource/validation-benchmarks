import os
import pickle
import json
import hashlib
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="TransformerHub", description="Community Model Repository", version="0.8.2")

templates = Jinja2Templates(directory="templates")

# Simulated model registry
MODEL_REGISTRY = {
    "bert-base-uncased": {
        "id": "bert-base-uncased",
        "author": "google",
        "downloads": 15420891,
        "tags": ["text-classification", "fill-mask"],
        "library": "transformers",
        "created": "2019-06-24",
        "vocab_loaded": True
    },
    "gpt2": {
        "id": "gpt2",
        "author": "openai",
        "downloads": 8923451,
        "tags": ["text-generation"],
        "library": "transformers",
        "created": "2019-02-14",
        "vocab_loaded": True
    },
    "transfo-xl-wt103": {
        "id": "transfo-xl-wt103",
        "author": "community",
        "downloads": 234892,
        "tags": ["text-generation", "deprecated"],
        "library": "transformers",
        "created": "2020-03-12",
        "vocab_loaded": False
    },
    "roberta-base": {
        "id": "roberta-base",
        "author": "facebook",
        "downloads": 5123098,
        "tags": ["text-classification"],
        "library": "transformers",
        "created": "2019-07-26",
        "vocab_loaded": True
    }
}

# Simulated user session with API key
API_KEYS = {
    "hf_demo_key_12345": {"user": "demo_user", "access": "read"},
}


def get_system_status():
    """Get current system status for admin dashboard"""
    if os.path.exists('decoy.txt'):
        status_file = open('decoy.txt').read()
    else:
        status_file = open('flag.txt').read()
    return status_file


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """Main landing page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "models": MODEL_REGISTRY,
        "total_models": len(MODEL_REGISTRY)
    })


@app.get("/models", response_class=JSONResponse)
async def list_models(
    author: str = None,
    tag: str = None,
    limit: int = 10
):
    """List available models in the repository"""
    result = list(MODEL_REGISTRY.values())
    
    if author:
        result = [m for m in result if m["author"] == author]
    if tag:
        result = [m for m in result if tag in m["tags"]]
    
    return {"models": result[:limit], "total": len(result)}


@app.get("/models/{model_id}", response_class=JSONResponse)
async def get_model(model_id: str):
    """Get details for a specific model"""
    if model_id not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="Model not found")
    return MODEL_REGISTRY[model_id]


@app.get("/api/v1/health")
async def health_check():
    """API health check endpoint"""
    return {"status": "healthy", "version": "0.8.2", "service": "transformerhub"}


@app.get("/api/v1/tokenizer/{model_id}/config", response_class=JSONResponse)
async def get_tokenizer_config(model_id: str):
    """Get tokenizer configuration for a model"""
    if model_id not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return {
        "model_id": model_id,
        "tokenizer_class": "PreTrainedTokenizerFast",
        "vocab_size": 30522,
        "model_max_length": 512,
        "padding_side": "right",
        "truncation_side": "right"
    }


@app.post("/api/v1/tokenizer/load", response_class=HTMLResponse)
async def load_tokenizer_vocab(
    request: Request,
    vocab_file: UploadFile = File(None),
    model_name: str = Form(None)
):
    """
    Load custom vocabulary file for tokenizer initialization.
    Supports .pkl format for backwards compatibility with older TransfoXL models.
    """
    result_message = None
    vocab_info = None
    
    if vocab_file:
        filename = vocab_file.filename or ""
        content = await vocab_file.read()
        
        # Accept vocab files
        if filename.endswith('.pkl') or filename.endswith('.pickle'):
            try:
                # Load vocabulary data for tokenizer initialization
                vocab_data = pickle.loads(content)
                vocab_info = {
                    "loaded": True,
                    "filename": filename,
                    "size": len(content)
                }
                result_message = f"Successfully loaded vocabulary from {filename}"
            except Exception as e:
                result_message = f"Error loading vocabulary: {str(e)}"
        elif filename.endswith('.json'):
            try:
                vocab_data = json.loads(content)
                vocab_info = {
                    "loaded": True,
                    "filename": filename,
                    "vocab_size": len(vocab_data) if isinstance(vocab_data, dict) else "unknown"
                }
                result_message = f"Successfully loaded JSON vocabulary from {filename}"
            except Exception as e:
                result_message = f"Error parsing JSON vocabulary: {str(e)}"
        else:
            result_message = "Unsupported file format. Please upload .pkl or .json vocabulary files."
    
    # Get system status for display
    system_status = get_system_status()
    
    return templates.TemplateResponse("tokenizer.html", {
        "request": request,
        "result_message": result_message,
        "vocab_info": vocab_info,
        "system_status": system_status,
        "model_name": model_name
    })


@app.get("/api/v1/tokenizer/upload", response_class=HTMLResponse)
async def tokenizer_upload_page(request: Request):
    """Page for uploading custom tokenizer vocabulary"""
    system_status = get_system_status()
    return templates.TemplateResponse("tokenizer.html", {
        "request": request,
        "result_message": None,
        "vocab_info": None,
        "system_status": system_status,
        "model_name": None
    })


@app.get("/docs/api", response_class=HTMLResponse)
async def api_docs(request: Request):
    """API documentation page"""
    return templates.TemplateResponse("docs.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """About page"""
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/ping")
async def ping():
    return {"ping": "pong"}

