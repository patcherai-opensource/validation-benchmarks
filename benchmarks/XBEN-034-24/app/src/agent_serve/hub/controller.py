import logging
from typing import List, Optional

from fastapi import APIRouter, Body, File, UploadFile, Query

from agent_serve.hub.model.schemas import (
    ApiResult,
    PageFilter,
    PageResult,
    ExtensionVO,
    WorkspaceExtensionVO,
    HubUpdateParam,
)
from agent_serve.hub.extension_manager import extension_manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/v1/hub/update", response_model=ApiResult)
async def hub_update(update_param: HubUpdateParam = Body()):
    logger.info(f"hub_update: {update_param.dict()}")
    try:
        return ApiResult.succ({"status": "updated"})
    except Exception as e:
        logger.error(f"Hub Update Error: {e}")
        return ApiResult.failed(code="E0020", msg=f"Hub Update Error: {e}")


@router.post("/v1/hub/extensions/list", response_model=ApiResult)
async def list_extensions(filter_params: PageFilter = Body()):
    logger.info(f"list_extensions: {filter_params.dict()}")
    try:
        installed = extension_manager.list_installed()
        result = PageResult(
            page_index=filter_params.page_index,
            page_size=filter_params.page_size,
            total_page=1,
            total_row_count=len(installed),
            datas=installed,
        )
        return ApiResult.succ(result.dict())
    except Exception as e:
        logger.error(f"List Extensions Error: {e}")
        return ApiResult.failed(code="E0024", msg=f"List Extensions Error: {e}")


@router.post("/v1/hub/extensions/install", response_model=ApiResult)
async def install_extension(ext_name: str = Body(..., embed=True), user: Optional[str] = Body(None, embed=True)):
    logger.info(f"install_extension: {ext_name}, user={user}")
    try:
        return ApiResult.succ({"installed": ext_name})
    except Exception as e:
        logger.error(f"Extension Install Error: {e}")
        return ApiResult.failed(code="E0021", msg=f"Extension Install Error: {e}")


@router.post("/v1/hub/extensions/remove", response_model=ApiResult)
async def remove_extension(ext_name: str = Body(..., embed=True), user: Optional[str] = Body(None, embed=True)):
    logger.info(f"remove_extension: {ext_name}, user={user}")
    try:
        removed = extension_manager.remove_extension(ext_name)
        if removed:
            return ApiResult.succ(None)
        return ApiResult.failed(code="E0025", msg="Extension not found")
    except Exception as e:
        logger.error(f"Extension Remove Error: {e}")
        return ApiResult.failed(code="E0022", msg=f"Extension Remove Error: {e}")


@router.post("/v1/workspace/extension/submit", response_model=ApiResult)
async def workspace_extension_submit(doc_file: UploadFile = File(...), user: Optional[str] = None):
    logger.info(f"workspace_extension_submit: {doc_file.filename}, user={user}")
    try:
        result = await extension_manager.submit_extension(doc_file, user)
        return ApiResult.succ(result)
    except Exception as e:
        logger.error(f"Upload Extension Error: {e}")
        return ApiResult.failed(code="E0023", msg=f"Upload Extension Error: {e}")


@router.post("/v1/workspace/extensions", response_model=ApiResult)
async def list_workspace_extensions(user: Optional[str] = Body(None, embed=True)):
    logger.info(f"list_workspace_extensions: user={user}")
    try:
        installed = extension_manager.list_installed()
        return ApiResult.succ(installed)
    except Exception as e:
        logger.error(f"List Workspace Extensions Error: {e}")
        return ApiResult.failed(code="E0026", msg=f"Error: {e}")


@router.get("/v1/workspace/extension/preview/{filename}")
async def preview_extension(filename: str):
    """Preview the source of a text-based extension file."""
    import os
    try:
        safe = extension_manager._sanitize_filename(filename)
        fpath = os.path.join(extension_manager.ext_dir, safe)
        if not os.path.exists(fpath):
            return ApiResult.failed(code="E0027", msg="File not found")
        if not safe.endswith(".py"):
            return ApiResult.failed(code="E0028", msg="Only .py files can be previewed")
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(65536)
        return ApiResult.succ({"filename": safe, "content": content})
    except Exception as e:
        logger.error(f"Preview Extension Error: {e}")
        return ApiResult.failed(code="E0029", msg=f"Preview Error: {e}")
