import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Environment
from starlette.requests import Request
from starlette.templating import Jinja2Templates

app = FastAPI(
    title="PromptForge API",
    description="Advanced NLP Prompt Generation Service",
    version="0.7.2"
)
templates = Jinja2Templates(directory="templates")


# Sample data for prompt generation
SAMPLE_ENTITIES = [
    {"text": "Apple", "label": "ORG"},
    {"text": "Tim Cook", "label": "PERSON"},
    {"text": "Cupertino", "label": "GPE"}
]

DEFAULT_TEMPLATE = """Extract named entities from the following text:
Text: {{ text }}
Entities found: {{ entities }}"""


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/generate")
async def generate_prompt(request: Request):
    """
    Generate an NLP prompt using a custom Jinja2 template.
    Accepts JSON body with 'template' field for custom prompt formatting.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    
    template_str = body.get("template", DEFAULT_TEMPLATE)
    text = body.get("text", "Apple was founded by Steve Jobs in Cupertino.")
    entities = body.get("entities", SAMPLE_ENTITIES)
    
    # Render the template with provided context
    jinja2_env = Environment()
    try:
        _template = jinja2_env.from_string(template_str)
        rendered = _template.render(text=text, entities=entities)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Template rendering error: {str(e)}")
    
    return JSONResponse({
        "status": "success",
        "prompt": rendered,
        "metadata": {
            "template_length": len(template_str),
            "text_length": len(text),
            "entity_count": len(entities)
        }
    })


@app.get("/api/generate")
async def generate_prompt_get(template: Optional[str] = None, text: Optional[str] = None):
    """
    GET endpoint for simple prompt generation.
    Supports 'template' query parameter for custom templates.
    """
    template_str = template or DEFAULT_TEMPLATE
    text_str = text or "Apple was founded by Steve Jobs in Cupertino."
    entities = SAMPLE_ENTITIES
    
    # Render the template
    jinja2_env = Environment()
    try:
        _template = jinja2_env.from_string(template_str)
        rendered = _template.render(text=text_str, entities=entities)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Template rendering error: {str(e)}")
    
    return JSONResponse({
        "status": "success",
        "prompt": rendered
    })


@app.get("/api/templates")
async def list_templates():
    """List available default templates for NLP tasks."""
    return JSONResponse({
        "templates": [
            {
                "name": "ner",
                "description": "Named Entity Recognition template",
                "template": DEFAULT_TEMPLATE
            },
            {
                "name": "classification",
                "description": "Text classification template", 
                "template": "Classify the following text:\nText: {{ text }}\nCategory:"
            },
            {
                "name": "summarization",
                "description": "Text summarization template",
                "template": "Summarize the following text:\n{{ text }}\n\nSummary:"
            }
        ]
    })


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({"status": "healthy", "version": "0.7.2"})


@app.get("/ping")
def ping():
    return {"ping": "pong"}
