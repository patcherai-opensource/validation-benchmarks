import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Body

from agent_serve.hub.model.schemas import ApiResult

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory store for demo app entries
_apps_store = [
    {
        "id": 1,
        "app_name": "Text Summarizer",
        "app_code": "text_summarizer_v1",
        "language": "en",
        "team_mode": "single_agent",
        "user_code": "admin",
        "is_collected": False,
        "gmt_created": "2024-01-15 10:30:00",
        "gmt_modified": "2024-01-15 10:30:00",
        "description": "Summarize long texts using LLM-powered agents",
    },
    {
        "id": 2,
        "app_name": "Code Reviewer",
        "app_code": "code_review_v1",
        "language": "en",
        "team_mode": "multi_agent",
        "user_code": "admin",
        "is_collected": True,
        "gmt_created": "2024-02-20 14:00:00",
        "gmt_modified": "2024-03-01 09:15:00",
        "description": "Automated code review with multiple specialized agents",
    },
]


class AppCreateRequest:
    pass


@router.post("/v1/app/create", response_model=ApiResult)
async def create_app(app_data: dict = Body(...)):
    logger.info(f"create_app: {app_data}")
    try:
        new_id = max(a["id"] for a in _apps_store) + 1 if _apps_store else 1
        entry = {
            "id": new_id,
            "app_name": app_data.get("app_name", "Untitled"),
            "app_code": app_data.get("app_code", f"app_{new_id}"),
            "language": app_data.get("language", "en"),
            "team_mode": app_data.get("team_mode", "single_agent"),
            "user_code": app_data.get("user_code", "default"),
            "is_collected": False,
            "gmt_created": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "gmt_modified": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "description": app_data.get("description", ""),
        }
        _apps_store.append(entry)
        return ApiResult.succ(entry)
    except Exception as e:
        logger.error(f"Create App Error: {e}")
        return ApiResult.failed(code="E0030", msg=f"Create App Error: {e}")


@router.post("/v1/app/list", response_model=ApiResult)
async def list_apps(query: dict = Body(default={})):
    logger.info(f"list_apps: {query}")
    try:
        results = _apps_store
        name_filter = query.get("app_name")
        if name_filter:
            results = [a for a in results if name_filter.lower() in a["app_name"].lower()]

        return ApiResult.succ({
            "total_count": len(results),
            "items": results,
        })
    except Exception as e:
        logger.error(f"List Apps Error: {e}")
        return ApiResult.failed(code="E0031", msg=f"List Apps Error: {e}")


@router.post("/v1/app/detail", response_model=ApiResult)
async def app_detail(app_id: int = Body(..., embed=True)):
    logger.info(f"app_detail: {app_id}")
    try:
        for app in _apps_store:
            if app["id"] == app_id:
                return ApiResult.succ(app)
        return ApiResult.failed(code="E0032", msg="App not found")
    except Exception as e:
        logger.error(f"App Detail Error: {e}")
        return ApiResult.failed(code="E0033", msg=f"Error: {e}")
