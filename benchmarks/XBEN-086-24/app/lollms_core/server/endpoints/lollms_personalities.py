"""
LoLLMs Personality Endpoints
Handles personality management
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import logging

from lollms_core.config import LOLLMsConfig

logger = logging.getLogger(__name__)
router = APIRouter()

AVAILABLE_PERSONALITIES = [
    {
        "name": "default",
        "description": "Default assistant personality",
        "category": "general",
        "author": "lollms",
    },
    {
        "name": "coder",
        "description": "Programming assistant",
        "category": "development",
        "author": "lollms",
    },
    {
        "name": "creative_writer",
        "description": "Creative writing assistant",
        "category": "writing",
        "author": "lollms",
    },
]


class PersonalitySelectParams(BaseModel):
    name: str


@router.get("/list_personalities")
async def list_personalities():
    """List available personalities"""
    return {"personalities": AVAILABLE_PERSONALITIES}


@router.post("/select_personality")
async def select_personality(data: PersonalitySelectParams):
    """Select an active personality"""
    config = LOLLMsConfig()
    available_names = [p["name"] for p in AVAILABLE_PERSONALITIES]

    if data.name not in available_names:
        return {"status": False, "message": f"Personality '{data.name}' not found"}

    if data.name not in config.personalities:
        config.personalities.append(data.name)
        config.save()

    return {"status": True, "active_personalities": config.personalities}


@router.get("/get_active_personalities")
async def get_active_personalities():
    """Get currently active personalities"""
    config = LOLLMsConfig()
    return {"personalities": config.personalities}
