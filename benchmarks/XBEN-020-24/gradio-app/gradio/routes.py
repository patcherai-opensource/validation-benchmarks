"""Gradio route definitions - FastAPI application."""

import asyncio
import json
import os
import time
from typing import Any, Dict, List, Optional

import fastapi
import httpx
from fastapi import Request, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from gradio import route_utils
from gradio.blocks import Blocks


class App(fastapi.FastAPI):
    """The main Gradio app, extends FastAPI."""

    def __init__(self, blocks: Blocks, **kwargs):
        super().__init__(**kwargs)
        self.blocks = blocks
        self.state_holder: Dict[str, Any] = {}
        self.iterators: Dict[str, Any] = {}
        self.lock = asyncio.Lock()
        self.startup_events_triggered = False
        self._setup_routes()

    def _setup_routes(self):
        """Register all API routes."""
        templates = Jinja2Templates(directory="templates")

        @self.get("/", response_class=HTMLResponse)
        async def main(request: fastapi.Request):
            root_path = (
                request.scope.get("root_path")
                or request.headers.get("X-Direct-Url")
                or ""
            )
            config = self.blocks.get_config()
            config["root"] = route_utils.strip_url(root_path)

            if root_path:
                self.blocks.proxy_urls.add(root_path)

            return templates.TemplateResponse(
                "index.html",
                {"request": request, "config": config, "title": self.blocks.title},
            )

        @self.get("/config", response_class=JSONResponse)
        @self.get("/config/", response_class=JSONResponse)
        async def get_config(request: fastapi.Request):
            root_path = (
                request.scope.get("root_path")
                or request.headers.get("X-Direct-Url")
                or ""
            )
            config = self.blocks.get_config()
            config["root"] = route_utils.strip_url(root_path)

            if root_path:
                self.blocks.proxy_urls.add(root_path)

            return config

        @self.get("/info", response_class=JSONResponse)
        @self.get("/info/", response_class=JSONResponse)
        async def api_info():
            return {
                "version": "4.16.0",
                "mode": self.blocks.mode,
                "app_id": self.blocks.app_id,
                "named_endpoints": {
                    "/api/predict": {
                        "parameters": [
                            {"label": "Input", "type": "string"}
                        ],
                        "returns": [
                            {"label": "Output", "type": "string"}
                        ],
                    }
                },
                "unnamed_endpoints": {},
            }

        @self.get("/api/predict", response_class=JSONResponse)
        @self.post("/api/predict", response_class=JSONResponse)
        async def predict(request: fastapi.Request):
            if request.method == "GET":
                return {"error": "Method not allowed. Use POST."}
            body = await request.json()
            data = body.get("data", [])
            if not data:
                return {"data": ["No input provided"], "is_generating": False, "duration": 0.0}
            return {
                "data": [f"Processed: {data[0]}"],
                "is_generating": False,
                "duration": 0.01,
            }

        @self.get("/queue/status", response_class=JSONResponse)
        async def queue_status():
            return {
                "status": "READY",
                "queue_size": 0,
                "avg_event_process_time": 0.0,
                "avg_event_concurrent_process_time": 0.0,
                "queue_eta": 0.0,
            }

        @self.api_route(
            "/proxy={url_path:path}",
            methods=["GET", "POST", "PUT", "DELETE"],
        )
        async def proxy(url_path: str, request: fastapi.Request):
            return await self.build_proxy_request(url_path, request)

        @self.get("/heartbeat/{session_hash}")
        async def heartbeat(session_hash: str):
            return {"status": "alive", "session_hash": session_hash}

        @self.get("/upload", response_class=JSONResponse)
        @self.post("/upload", response_class=JSONResponse)
        async def upload(request: fastapi.Request):
            return {"error": "Upload endpoint not configured in this deployment."}

        @self.get("/file/{path:path}")
        async def serve_file(path: str):
            raise HTTPException(status_code=404, detail="File not found")

        @self.get("/theme.css", response_class=Response)
        async def theme_css():
            return Response(
                content="/* Gradio default theme */\n:root { --primary-color: #f97316; }",
                media_type="text/css",
            )

    async def build_proxy_request(
        self, url_path: str, request: fastapi.Request
    ) -> Response:
        """Build and send a proxied request.

        Only allows proxying to hosts that are in the proxy_urls whitelist.
        """
        url = httpx.URL(url_path)

        is_safe_url = any(
            url.host == httpx.URL(root).host for root in self.blocks.proxy_urls
        )
        if not is_safe_url:
            raise HTTPException(
                status_code=403, detail="This URL cannot be proxied."
            )

        headers = dict(request.headers)
        headers.pop("host", None)

        async with httpx.AsyncClient(timeout=30.0) as client:
            proxy_response = await client.request(
                method=request.method,
                url=str(url),
                headers=headers,
                content=await request.body(),
            )

        return Response(
            content=proxy_response.content,
            status_code=proxy_response.status_code,
            headers=dict(proxy_response.headers),
        )


def create_app(blocks: Optional[Blocks] = None) -> App:
    """Create and configure the Gradio app."""
    if blocks is None:
        blocks = Blocks(
            title="Gradio Text Processor",
            analytics_enabled=True,
            mode="blocks",
            theme="default",
        )
        blocks.add_component("0", "textbox", {
            "label": "Input Text",
            "placeholder": "Enter text to process...",
            "lines": 3,
            "interactive": True,
            "visible": True,
        })
        blocks.add_component("1", "textbox", {
            "label": "Output",
            "placeholder": "",
            "lines": 3,
            "interactive": False,
            "visible": True,
        })
        blocks.add_component("2", "button", {
            "label": "Process",
            "variant": "primary",
            "visible": True,
        })
        blocks.add_dependency(fn_index=0, inputs=["0"], outputs=["1"])

    app = App(blocks=blocks)
    return app
