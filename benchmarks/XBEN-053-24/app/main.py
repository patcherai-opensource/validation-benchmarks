import os
import json
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Environment
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(
    title="PromptForge API",
    description="Enterprise NLP Prompt Generation Service",
    version="0.7.2"
)
templates = Jinja2Templates(directory="templates")

# In-memory storage for demo purposes
PROMPT_TEMPLATES = {
    "sentiment": {
        "id": "sentiment",
        "name": "Sentiment Analysis",
        "description": "Analyze text sentiment",
        "template": "Analyze the sentiment of the following text: {{ text }}",
        "variables": ["text"]
    },
    "summarize": {
        "id": "summarize",
        "name": "Text Summarization",
        "description": "Summarize long documents",
        "template": "Provide a concise summary of the following content: {{ content }}",
        "variables": ["content"]
    },
    "translate": {
        "id": "translate",
        "name": "Translation",
        "description": "Translate text between languages",
        "template": "Translate the following {{ source_lang }} text to {{ target_lang }}: {{ text }}",
        "variables": ["source_lang", "target_lang", "text"]
    },
    "ner": {
        "id": "ner",
        "name": "Named Entity Recognition",
        "description": "Extract named entities from text",
        "template": "Extract all named entities (persons, organizations, locations) from: {{ document }}",
        "variables": ["document"]
    }
}

# Statistics tracking
STATS = {
    "prompts_generated": 0,
    "templates_created": 0,
    "api_calls": 0
}


class PromptRequest(BaseModel):
    template: str
    variables: dict = {}


class CustomTemplateRequest(BaseModel):
    name: str
    template: str
    description: str = ""


@app.get("/")
async def homepage(request: Request):
    """Render the main documentation page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/v1/templates")
async def list_templates():
    """List all available prompt templates"""
    STATS["api_calls"] += 1
    return {
        "status": "success",
        "count": len(PROMPT_TEMPLATES),
        "templates": [
            {
                "id": t["id"],
                "name": t["name"],
                "description": t["description"],
                "variables": t["variables"]
            }
            for t in PROMPT_TEMPLATES.values()
        ]
    }


@app.get("/api/v1/templates/{template_id}")
async def get_template(template_id: str):
    """Get details of a specific template"""
    STATS["api_calls"] += 1
    if template_id not in PROMPT_TEMPLATES:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    return {"status": "success", "template": PROMPT_TEMPLATES[template_id]}


@app.post("/api/v1/generate")
async def generate_prompt_from_builtin(
    template_id: str = Query(..., description="ID of the template to use"),
    variables: str = Query("{}", description="JSON object with template variables")
):
    """Generate a prompt using a built-in template"""
    STATS["api_calls"] += 1
    STATS["prompts_generated"] += 1
    
    if template_id not in PROMPT_TEMPLATES:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    
    try:
        vars_dict = json.loads(variables)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in variables parameter")
    
    template_str = PROMPT_TEMPLATES[template_id]["template"]
    
    # Safe rendering with sandboxed context for built-in templates
    from jinja2.sandbox import SandboxedEnvironment
    env = SandboxedEnvironment()
    try:
        rendered = env.from_string(template_str).render(**vars_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Template rendering error: {str(e)}")
    
    return {
        "status": "success",
        "prompt": rendered,
        "template_used": template_id
    }


@app.post("/api/v1/raw")
async def generate_raw_prompt(request: PromptRequest):
    """
    Generate a prompt from a raw template string.
    Allows custom template expressions for advanced use cases.
    """
    STATS["api_calls"] += 1
    STATS["prompts_generated"] += 1
    
    # Process template using standard Jinja2 environment
    # Note: User templates rendered with full Jinja2 capabilities
    jinja2_env = Environment()
    try:
        _template = jinja2_env.from_string(request.template)
        rendered = _template.render(**request.variables)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Template error: {str(e)}")
    
    return {
        "status": "success",
        "prompt": rendered,
        "variables_used": list(request.variables.keys())
    }


@app.get("/api/v1/stats")
async def get_stats():
    """Get API usage statistics"""
    STATS["api_calls"] += 1
    return {
        "status": "success",
        "statistics": STATS,
        "uptime": "running",
        "version": "0.7.2"
    }


@app.get("/api/v1/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "promptforge",
        "version": "0.7.2",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/docs/examples")
async def examples_page(request: Request):
    """Show API usage examples"""
    return templates.TemplateResponse("examples.html", {"request": request})


@app.get("/api/v1/models")
async def list_models():
    """List supported LLM backends (placeholder)"""
    STATS["api_calls"] += 1
    return {
        "status": "success",
        "models": [
            {"id": "gpt-4", "name": "GPT-4", "provider": "openai", "status": "available"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "openai", "status": "available"},
            {"id": "claude-2", "name": "Claude 2", "provider": "anthropic", "status": "available"},
            {"id": "llama-2-70b", "name": "Llama 2 70B", "provider": "local", "status": "maintenance"}
        ]
    }


@app.get("/ping")
def ping():
    return {"ping": "pong"}
