import logging
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from agent_serve.hub.controller import router as hub_router
from agent_serve.app.controller import router as app_router
from agent_serve.chat.controller import router as chat_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gpt-serve")

app = FastAPI(
    title="GPT-Serve API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "err_code": "E5000", "err_msg": "Internal Server Error", "data": None},
    )


@app.get("/", response_class=HTMLResponse)
async def index():
    return """<!DOCTYPE html>
<html>
<head><title>GPT-Serve Platform</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background: #0d1117; color: #c9d1d9; }
.header { background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 32px; display: flex; align-items: center; }
.header h1 { font-size: 20px; margin: 0; color: #58a6ff; }
.container { max-width: 960px; margin: 40px auto; padding: 0 20px; }
.card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 24px; margin-bottom: 16px; }
.card h3 { margin-top: 0; color: #58a6ff; }
.card p { color: #8b949e; line-height: 1.6; }
.status { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #3fb950; margin-right: 8px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.endpoint { font-family: monospace; background: #0d1117; padding: 4px 8px; border-radius: 3px; font-size: 13px; }
</style></head>
<body>
<div class="header"><h1>&#x1f916; GPT-Serve Platform</h1></div>
<div class="container">
<div class="card"><span class="status"></span> System Online - v0.7.0</div>
<div class="grid">
<div class="card"><h3>Agent Hub</h3><p>Manage and deploy AI agent extensions. Upload custom extensions to enhance agent capabilities.</p>
<p class="endpoint">POST /api/v1/hub/extensions/list</p>
<p class="endpoint">POST /api/v1/hub/extensions/install</p>
<p class="endpoint">POST /api/v1/hub/extensions/remove</p>
<p class="endpoint">POST /api/v1/workspace/extension/submit</p>
</div>
<div class="card"><h3>Agent Apps</h3><p>Create and manage GPT-powered applications with custom agent configurations.</p>
<p class="endpoint">POST /api/v1/app/create</p>
<p class="endpoint">POST /api/v1/app/list</p>
</div>
<div class="card"><h3>Chat</h3><p>Interactive conversations with deployed agents and models.</p>
<p class="endpoint">POST /api/v1/chat/completions</p>
<p class="endpoint">POST /api/v1/chat/sessions</p>
</div>
</div>
<div class="card"><h3>API Documentation</h3><p>All endpoints accept JSON request bodies and return standardized response objects with <code>success</code>, <code>err_code</code>, <code>err_msg</code>, and <code>data</code> fields.</p></div>
</div>
</body></html>"""


@app.get("/ping")
async def health_check():
    return {"status": "ok"}


app.include_router(hub_router, prefix="/api")
app.include_router(app_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
