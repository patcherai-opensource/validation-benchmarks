import logging
from typing import Optional

from fastapi import APIRouter, Body

from agent_serve.hub.model.schemas import ApiResult

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/v1/chat/completions", response_model=ApiResult)
async def chat_completions(payload: dict = Body(...)):
    logger.info(f"chat_completions request")
    try:
        model = payload.get("model", "default")
        messages = payload.get("messages", [])
        if not messages:
            return ApiResult.failed(code="E0040", msg="No messages provided")

        return ApiResult.succ({
            "model": model,
            "message": {
                "role": "assistant",
                "content": "I'm currently running in limited mode. Please configure a model backend to enable full chat capabilities.",
            },
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        })
    except Exception as e:
        logger.error(f"Chat Completions Error: {e}")
        return ApiResult.failed(code="E0041", msg=f"Chat Error: {e}")


@router.post("/v1/chat/sessions", response_model=ApiResult)
async def list_sessions(user: Optional[str] = Body(None, embed=True)):
    logger.info(f"list_sessions: user={user}")
    try:
        return ApiResult.succ({
            "total": 0,
            "sessions": [],
        })
    except Exception as e:
        logger.error(f"Sessions Error: {e}")
        return ApiResult.failed(code="E0042", msg=f"Sessions Error: {e}")
