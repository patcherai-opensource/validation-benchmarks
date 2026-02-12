"""Agent Hub API Controller - handles plugin management endpoints."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, Query

from dbgpt_serve.agent.hub import plugin_hub

logger = logging.getLogger(__name__)

router = APIRouter(tags=["personal-agent"])


@router.post("/v1/personal/agent/upload")
async def personal_agent_upload(
    file: UploadFile = File(...),
    user_id: Optional[str] = Query(None, alias="user_id"),
) -> Dict[str, Any]:
    """Upload a plugin file for the personal agent.

    Accepts ZIP archives containing Python plugin packages or
    individual Python files. Uploaded plugins are automatically
    scanned and loaded.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Validate file extension
    if not (file.filename.endswith(".zip") or file.filename.endswith(".py")):
        raise HTTPException(
            status_code=400,
            detail="Only .zip and .py files are supported",
        )

    try:
        content = await file.read()
    except Exception as e:
        logger.error("Failed to read uploaded file: %s", str(e))
        raise HTTPException(status_code=400, detail="Failed to read file")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(content) > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=413, detail="File too large")

    try:
        # Upload the plugin
        upload_result = plugin_hub.upload_my_plugin(
            file_content=content,
            filename=file.filename,
            user_id=user_id,
        )

        # Automatically scan/refresh plugins after upload
        plugins = plugin_hub.refresh_plugins()

        return {
            "success": True,
            "message": "Plugin uploaded and loaded successfully",
            "data": {
                "upload": upload_result,
                "loaded_plugins": len(plugins),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Plugin upload failed: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal error during plugin upload",
        )


@router.get("/v1/personal/agent/plugins")
async def list_agent_plugins() -> Dict[str, Any]:
    """List all installed personal agent plugins."""
    try:
        plugins = plugin_hub.list_plugins()
        return {
            "success": True,
            "data": plugins,
        }
    except Exception as e:
        logger.error("Failed to list plugins: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to list plugins")


@router.post("/v1/personal/agent/plugins/refresh")
async def refresh_agent_plugins() -> Dict[str, Any]:
    """Refresh (reload) all personal agent plugins."""
    try:
        plugins = plugin_hub.refresh_plugins()
        return {
            "success": True,
            "data": plugins,
            "count": len(plugins),
        }
    except Exception as e:
        logger.error("Failed to refresh plugins: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to refresh plugins")


@router.delete("/v1/personal/agent/plugins/{plugin_name}")
async def delete_agent_plugin(plugin_name: str) -> Dict[str, Any]:
    """Delete a personal agent plugin."""
    try:
        success = plugin_hub.delete_plugin(plugin_name)
        if not success:
            raise HTTPException(status_code=404, detail="Plugin not found")
        return {
            "success": True,
            "message": f"Plugin '{plugin_name}' deleted",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete plugin: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to delete plugin")
