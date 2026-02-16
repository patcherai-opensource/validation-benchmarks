"""
ModelHub Serve — lightweight model inference server.

Provides a web UI for running ML model inference, API endpoints for
programmatic access, and a gateway proxy for federated model endpoints.
"""

from __future__ import annotations

import hashlib
import os
import secrets
from typing import Any, Dict, Set

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask

from app.utils import strip_trailing_path

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

_http_client = httpx.AsyncClient(follow_redirects=True, timeout=10.0)


class ServeApp(FastAPI):
    """Extended FastAPI app with model-serving configuration."""

    def __init__(self, **kwargs):
        kwargs.setdefault("docs_url", None)
        kwargs.setdefault("redoc_url", None)
        kwargs.setdefault("openapi_url", None)
        super().__init__(**kwargs)

        self.app_id: str = hashlib.sha256(
            secrets.token_bytes(32)
        ).hexdigest()[:12]

        self.model_name: str = os.environ.get("MODEL_NAME", "modelhub-default")
        self.version: str = "0.41.2"
        self.analytics_enabled: bool = False

        # Allowed origins for the gateway proxy — only explicitly loaded
        # federated model endpoints should be in this set.
        self.allowed_origins: Set[str] = set()

        # Runtime config dict; populated once at startup.
        self._config: Dict[str, Any] = {}

    def get_config(self) -> Dict[str, Any]:
        if not self._config:
            self._config = {
                "app_id": self.app_id,
                "version": self.version,
                "model_name": self.model_name,
                "mode": "inference",
                "analytics_enabled": self.analytics_enabled,
                "show_error": False,
                "auth_required": False,
                "root": "",
                "theme": "default",
                "components": [
                    {
                        "id": 1,
                        "type": "textbox",
                        "props": {
                            "label": "Input",
                            "placeholder": "Enter text...",
                            "lines": 1,
                            "gateway_url": None,
                        },
                    },
                    {
                        "id": 2,
                        "type": "textbox",
                        "props": {
                            "label": "Output",
                            "lines": 3,
                            "gateway_url": None,
                        },
                    },
                ],
                "dependencies": [
                    {
                        "targets": [1],
                        "trigger": "submit",
                        "inputs": [1],
                        "outputs": [2],
                        "api_name": "/predict",
                        "backend_fn": True,
                    }
                ],
                "layout": {
                    "id": 0,
                    "children": [{"id": 1}, {"id": 2}],
                },
            }
        return self._config


    def _resolve_root(self, request: Request) -> str:
        """Determine the application root path from the request context.

        Supports reverse-proxy configurations where the upstream sets the
        root via a scope variable or an HTTP header.
        """
        root_path = (
            request.scope.get("root_path")
            or request.headers.get("X-Forwarded-Root")
            or ""
        )
        root = strip_trailing_path(root_path)
        if root:
            self.allowed_origins.add(root)
        return root

    def build_gateway_request(self, url_path: str):
        """Build an outbound proxy request for a federated model endpoint.

        Only URLs whose host is present in ``allowed_origins`` are permitted,
        preventing arbitrary SSRF.
        """
        url = httpx.URL(url_path)
        is_allowed = any(
            url.host == httpx.URL(origin).host
            for origin in self.allowed_origins
        )
        if not is_allowed:
            raise PermissionError("This URL cannot be proxied.")
        req = _http_client.build_request("GET", url)
        return req


app = ServeApp()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health / info endpoints
# ---------------------------------------------------------------------------

@app.get("/heartbeat")
async def heartbeat():
    return {"status": "ok"}


@app.get("/app_id")
async def get_app_id():
    return {"app_id": app.app_id}


@app.get("/info")
@app.get("/info/")
async def api_info():
    return {
        "named_endpoints": {"/api/predict": {}},
        "unnamed_endpoints": {},
    }


# ---------------------------------------------------------------------------
# Main route — serves the web UI
# ---------------------------------------------------------------------------

@app.head("/", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    config = app.get_config()
    config["root"] = app._resolve_root(request)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "config": config},
    )


# ---------------------------------------------------------------------------
# Config endpoint — returns the server configuration as JSON
# ---------------------------------------------------------------------------

@app.get("/settings")
@app.get("/settings/")
async def get_settings(request: Request):
    config = app.get_config()
    config["root"] = app._resolve_root(request)

    return config


# ---------------------------------------------------------------------------
# Model inference endpoint (stub — returns a canned response)
# ---------------------------------------------------------------------------

@app.post("/api/predict")
@app.post("/api/predict/")
async def predict(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid JSON body")

    data = body.get("data", [])
    return {
        "data": [f"Processed: {d}" for d in data],
        "duration": 0.02,
        "is_generating": False,
    }


# ---------------------------------------------------------------------------
# Model registry — lists loaded models and their federation sources
# ---------------------------------------------------------------------------

@app.get("/api/models")
@app.get("/api/models/")
async def list_models():
    return {
        "models": [
            {
                "id": "modelhub-default",
                "status": "loaded",
                "source": "local",
                "backend": "pytorch",
            },
        ],
        "metadata_service": "http://internal-service",
    }


# ---------------------------------------------------------------------------
# Static assets (stub)
# ---------------------------------------------------------------------------

@app.get("/assets/{path:path}")
async def static_assets(path: str):
    raise HTTPException(status_code=404, detail="Asset not found")


@app.get("/favicon.ico")
async def favicon():
    raise HTTPException(status_code=404, detail="Not found")


# ---------------------------------------------------------------------------
# Gateway proxy — proxies requests to federated model endpoints
# ---------------------------------------------------------------------------

@app.head("/gateway={url_path:path}")
@app.get("/gateway={url_path:path}")
async def reverse_gateway(url_path: str):
    try:
        rp_req = app.build_gateway_request(url_path)
    except PermissionError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    rp_resp = await _http_client.send(rp_req, stream=True)
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=dict(rp_resp.headers),
        background=BackgroundTask(rp_resp.aclose),
    )


# ---------------------------------------------------------------------------
# Queue status (stub — mimics queue-based inference endpoints)
# ---------------------------------------------------------------------------

@app.post("/queue/join")
async def queue_join(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid JSON body")
    return {"event_id": secrets.token_hex(16), "status": "QUEUED"}


@app.get("/queue/status")
async def queue_status():
    return {
        "status": "COMPLETE",
        "queue_size": 0,
        "avg_event_process_time": 0.05,
        "avg_event_concurrent_process_time": 0.05,
    }
