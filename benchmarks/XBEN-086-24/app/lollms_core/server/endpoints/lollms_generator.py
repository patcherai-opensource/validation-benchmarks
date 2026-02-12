"""
LoLLMs Text Generation Endpoints
Handles text generation requests
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from lollms_core.config import LOLLMsConfig

logger = logging.getLogger(__name__)
router = APIRouter()


class GenerateRequest(BaseModel):
    prompt: str
    n_predict: int = 128
    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.9
    stream: bool = False


class GenerateResponse(BaseModel):
    text: str
    tokens_generated: int


@router.post("/generate")
async def generate_text(data: GenerateRequest):
    """Generate text from a prompt"""
    config = LOLLMsConfig()

    if not config.binding_name:
        raise HTTPException(
            status_code=503,
            detail="No binding configured. Please install and select a binding first."
        )

    # In a real deployment, this would use the loaded binding to generate text
    response_text = f"[Model response placeholder - binding: {config.binding_name}] Echo: {data.prompt[:100]}"

    return GenerateResponse(
        text=response_text,
        tokens_generated=len(response_text.split()),
    )


@router.get("/get_generation_status")
async def get_generation_status():
    """Get current generation status"""
    return {
        "status": "idle",
        "current_model": LOLLMsConfig().model_name or "none",
        "current_binding": LOLLMsConfig().binding_name or "none",
    }
