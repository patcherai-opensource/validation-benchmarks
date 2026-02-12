"""DB-GPT Application Server."""

import logging
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dbgpt_serve.core.config import API_VERSION
from dbgpt_serve.core.database import init_db
from dbgpt_serve.agent.hub.controller import router as plugin_router
from dbgpt_serve.agent.hub.api_routes import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("dbgpt")

app = FastAPI(
    title="DB-GPT",
    description="Database GPT - AI-native data application development framework",
    version=API_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)

# Include API routers
app.include_router(plugin_router)
app.include_router(api_router)


@app.on_event("startup")
async def startup():
    """Initialize application on startup."""
    init_db()
    # Ensure plugins directory exists
    os.makedirs("/app/plugins", exist_ok=True)
    logger.info("DB-GPT server started (version %s)", API_VERSION)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/ping")
async def ping():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/v1/health")
async def health():
    """API health check."""
    return {
        "success": True,
        "version": API_VERSION,
        "status": "running",
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler."""
    if request.url.path.startswith("/v1/"):
        return JSONResponse(
            status_code=404,
            content={"success": False, "detail": "Endpoint not found"},
        )
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "status_code": 404, "message": "Page not found"},
        status_code=404,
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Custom 500 handler."""
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "Internal server error"},
    )
