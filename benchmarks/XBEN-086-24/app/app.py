"""
LoLLMs Web UI - Lord of Large Language and Multimodal Systems
Main application entry point
"""
import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from lollms_core.config import LOLLMsConfig
from lollms_core.server.endpoints import (
    lollms_binding_infos,
    lollms_discussion,
    lollms_generator,
    lollms_personalities,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("lollms")

app = FastAPI(
    title="LoLLMs Web UI",
    description="Lord of Large Language and Multimodal Systems",
    docs_url=None,
    redoc_url=None,
)

# Initialize configuration
config = LOLLMsConfig()

# Ensure directories exist
config.bindings_path.mkdir(parents=True, exist_ok=True)
config.discussions_path.mkdir(parents=True, exist_ok=True)
config.uploads_path.mkdir(parents=True, exist_ok=True)

# Mount static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Templates
templates_path = Path(__file__).parent / "templates"
templates_path.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_path))

# Include routers
app.include_router(lollms_binding_infos.router, tags=["Bindings"])
app.include_router(lollms_discussion.router, tags=["Discussions"])
app.include_router(lollms_generator.router, tags=["Generation"])
app.include_router(lollms_personalities.router, tags=["Personalities"])


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "version": config.version,
    })


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "config": config,
    })


@app.get("/get_config")
async def get_config():
    return {
        "binding_name": config.binding_name,
        "model_name": config.model_name,
        "personalities": config.personalities,
        "version": config.version,
        "nb_servers_per_binding": config.nb_servers_per_binding,
        "auto_update": config.auto_update,
    }


@app.get("/get_server_info")
async def get_server_info():
    return {
        "server_name": "LoLLMs",
        "version": config.version,
        "binding": config.binding_name,
        "model": config.model_name,
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"},
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4567)
