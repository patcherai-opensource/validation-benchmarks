"""Additional API routes for the DB-GPT agent hub."""

import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from dbgpt_serve.core.database import AgentConfig, Conversation, get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class AgentConfigRequest(BaseModel):
    agent_name: str
    model_name: Optional[str] = "chatgpt_proxyllm"
    prompt_template: Optional[str] = ""
    max_tokens: Optional[int] = 4096
    temperature: Optional[str] = "0.7"


class ChatRequest(BaseModel):
    chat_mode: Optional[str] = "chat_normal"
    model_name: Optional[str] = "chatgpt_proxyllm"
    user_input: str
    conv_uid: Optional[str] = None
    user_id: Optional[str] = None


@router.get("/v1/agent/configs")
async def list_agent_configs(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List all agent configurations."""
    configs = db.query(AgentConfig).all()
    return {
        "success": True,
        "data": [
            {
                "id": c.id,
                "agent_name": c.agent_name,
                "model_name": c.model_name,
                "max_tokens": c.max_tokens,
                "temperature": c.temperature,
            }
            for c in configs
        ],
    }


@router.post("/v1/agent/configs")
async def create_agent_config(
    request: AgentConfigRequest,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Create a new agent configuration."""
    existing = (
        db.query(AgentConfig)
        .filter(AgentConfig.agent_name == request.agent_name)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Agent '{request.agent_name}' already exists",
        )

    config = AgentConfig(
        agent_name=request.agent_name,
        model_name=request.model_name,
        prompt_template=request.prompt_template,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
    )
    db.add(config)
    db.commit()
    db.refresh(config)

    return {
        "success": True,
        "data": {
            "id": config.id,
            "agent_name": config.agent_name,
        },
    }


@router.get("/v1/chat/conversations")
async def list_conversations(
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List conversation history."""
    query = db.query(Conversation)
    if user_id:
        query = query.filter(Conversation.user_id == user_id)

    convs = query.order_by(Conversation.created_at.desc()).limit(50).all()
    return {
        "success": True,
        "data": [
            {
                "conv_uid": c.conv_uid,
                "chat_mode": c.chat_mode,
                "summary": c.summary,
                "model_name": c.model_name,
                "created_at": str(c.created_at),
            }
            for c in convs
        ],
    }


@router.post("/v1/chat/completions")
async def chat_completions(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Send a chat message (model backend not connected)."""
    conv_uid = request.conv_uid or str(uuid.uuid4())

    # Record conversation
    existing = (
        db.query(Conversation)
        .filter(Conversation.conv_uid == conv_uid)
        .first()
    )
    if not existing:
        conv = Conversation(
            conv_uid=conv_uid,
            user_id=request.user_id,
            chat_mode=request.chat_mode,
            model_name=request.model_name,
            summary=request.user_input[:200],
        )
        db.add(conv)
        db.commit()

    return {
        "success": True,
        "data": {
            "conv_uid": conv_uid,
            "model_name": request.model_name,
            "response": "Model backend is not connected. Please configure a valid LLM model server.",
        },
    }


@router.get("/v1/models")
async def list_models() -> Dict[str, Any]:
    """List available LLM models."""
    return {
        "success": True,
        "data": [
            {
                "model_name": "chatgpt_proxyllm",
                "model_type": "proxy",
                "status": "inactive",
                "description": "OpenAI ChatGPT proxy model",
            },
            {
                "model_name": "vicuna-13b-v1.5",
                "model_type": "huggingface",
                "status": "inactive",
                "description": "Vicuna 13B v1.5",
            },
            {
                "model_name": "llama-2-7b-chat",
                "model_type": "huggingface",
                "status": "inactive",
                "description": "Llama 2 7B Chat",
            },
        ],
    }
