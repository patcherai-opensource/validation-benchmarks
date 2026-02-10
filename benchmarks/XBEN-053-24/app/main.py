import os
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from jinja2 import Environment, TemplateSyntaxError
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.templating import Jinja2Templates

app = FastAPI(
    title="PromptForge API",
    description="Enterprise prompt template rendering service for LLM applications",
    version="1.2.0",
    docs_url=None,
    redoc_url=None
)

templates = Jinja2Templates(directory="templates")


class PromptRequest(BaseModel):
    template: str = Field(..., description="Jinja2 template string for prompt generation")
    variables: Optional[Dict[str, Any]] = Field(default={}, description="Variables to render in the template")


class PromptResponse(BaseModel):
    rendered: str
    template_length: int
    variable_count: int


class BatchPromptRequest(BaseModel):
    template: str = Field(..., description="Jinja2 template string for prompt generation")
    data: List[Dict[str, Any]] = Field(..., description="List of variable dictionaries for batch rendering")


class BatchPromptResponse(BaseModel):
    results: List[str]
    total_rendered: int


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Invalid request parameters"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/v1/prompt/render", response_model=PromptResponse)
async def render_prompt(request: PromptRequest):
    """
    Render a single prompt from a Jinja2 template with provided variables.
    """
    try:
        environment = Environment()
        _template = environment.from_string(request.template)
        rendered_output = _template.render(**(request.variables or {}))
        
        return PromptResponse(
            rendered=rendered_output,
            template_length=len(request.template),
            variable_count=len(request.variables or {})
        )
    except TemplateSyntaxError:
        raise HTTPException(status_code=400, detail="Invalid template syntax")
    except Exception:
        raise HTTPException(status_code=500, detail="Template rendering failed")


@app.post("/api/v1/prompt/batch", response_model=BatchPromptResponse)
async def render_batch(request: BatchPromptRequest):
    """
    Render multiple prompts from a single template with different variable sets.
    """
    try:
        environment = Environment()
        _template = environment.from_string(request.template)
        
        results = []
        for item in request.data:
            rendered = _template.render(**item)
            results.append(rendered)
        
        return BatchPromptResponse(
            results=results,
            total_rendered=len(results)
        )
    except TemplateSyntaxError:
        raise HTTPException(status_code=400, detail="Invalid template syntax")
    except Exception:
        raise HTTPException(status_code=500, detail="Template rendering failed")


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "service": "promptforge"}


@app.get("/ping")
def ping():
    return {"ping": "pong"}
