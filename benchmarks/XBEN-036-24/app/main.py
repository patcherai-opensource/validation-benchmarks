import os
import pickle
import tempfile
import zipfile
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Simulated model hub storage
MODELS_DIR = Path("/app/models")
MODELS_DIR.mkdir(exist_ok=True)

# Pre-built models available in the hub
AVAILABLE_MODELS = {
    "transfo-xl-wt103": "A large-scale language model trained on WikiText-103",
    "gpt2-small": "GPT-2 small model for text generation",
    "bert-base-uncased": "BERT base model (uncased)"
}


class TokenizerVocab:
    """Simulates TransfoXLTokenizer vocab loading behavior"""
    def __init__(self, vocab_data):
        self.vocab = vocab_data
        self.vocab_size = len(vocab_data) if isinstance(vocab_data, dict) else 0


def load_tokenizer_vocab(model_path: Path):
    """
    Simulates the vulnerable TransfoXLTokenizer behavior from 
    src/transformers/models/deprecated/transfo_xl/tokenization_transfo_xl.py
    
    The original vulnerable code does:
        with open(vocab_file, "rb") as f:
            self.sym2idx = pickle.load(f)
    """
    vocab_file = model_path / "vocab.pkl"
    
    if not vocab_file.exists():
        raise FileNotFoundError(f"vocab.pkl not found in {model_path}")
    
    # VULNERABLE: Deserializing pickle from untrusted source
    # This mirrors the TransfoXLTokenizer vulnerability
    with open(vocab_file, "rb") as f:
        vocab_data = pickle.load(f)
    
    return TokenizerVocab(vocab_data)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "models": AVAILABLE_MODELS
    })


@app.get("/api/models")
async def list_models():
    """List available pretrained models"""
    return {"models": AVAILABLE_MODELS}


@app.post("/api/load_model")
async def load_model(model_name: str = Form(...)):
    """
    Load a pretrained model from the hub.
    Simulates from_pretrained() behavior.
    """
    if model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found in hub")
    
    model_path = MODELS_DIR / model_name
    
    if not model_path.exists():
        raise HTTPException(status_code=404, detail=f"Model files not found for '{model_name}'")
    
    try:
        # Load tokenizer vocab - this is where the vulnerability exists
        vocab = load_tokenizer_vocab(model_path)
        return {
            "status": "success",
            "model": model_name,
            "vocab_size": vocab.vocab_size,
            "message": f"Successfully loaded tokenizer for {model_name}"
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")


@app.post("/api/upload_model")
async def upload_model(
    request: Request,
    model_name: str = Form(...),
    model_archive: UploadFile = File(...)
):
    """
    Upload a custom model repository (zip archive).
    The archive should contain model files including vocab.pkl for the tokenizer.
    
    This simulates uploading a model to a local hub or loading from a local path,
    similar to how users might load models from untrusted sources.
    """
    if not model_archive.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Model archive must be a .zip file")
    
    # Create model directory
    model_path = MODELS_DIR / model_name
    
    # Save and extract the archive
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
        content = await model_archive.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Clean up existing model if present
        if model_path.exists():
            shutil.rmtree(model_path)
        
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Extract archive
        with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
            zip_ref.extractall(model_path)
        
        # Add to available models
        AVAILABLE_MODELS[model_name] = f"Custom uploaded model: {model_name}"
        
        # Automatically load the tokenizer to validate the model
        # This is where the pickle deserialization occurs
        vocab = load_tokenizer_vocab(model_path)
        
        return {
            "status": "success",
            "model": model_name,
            "vocab_size": vocab.vocab_size,
            "message": f"Model '{model_name}' uploaded and tokenizer loaded successfully"
        }
        
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip archive")
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Model archive must contain vocab.pkl for tokenizer")
    except Exception as e:
        # Clean up on error
        if model_path.exists():
            shutil.rmtree(model_path)
        raise HTTPException(status_code=500, detail=f"Error processing model: {str(e)}")
    finally:
        os.unlink(tmp_path)


@app.get("/api/model_info/{model_name}")
async def get_model_info(model_name: str):
    """Get information about a specific model"""
    if model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    
    model_path = MODELS_DIR / model_name
    files = []
    if model_path.exists():
        files = [f.name for f in model_path.iterdir()]
    
    return {
        "model": model_name,
        "description": AVAILABLE_MODELS[model_name],
        "files": files
    }


@app.get("/result")
async def get_result(request: Request):
    """Check if exploitation was successful by reading the output file"""
    output_file = Path("/tmp/output.txt")
    if output_file.exists():
        content = output_file.read_text()
        return {"status": "success", "output": content}
    return {"status": "pending", "message": "No output yet"}


@app.get("/ping")
async def ping():
    return {"ping": "pong"}

