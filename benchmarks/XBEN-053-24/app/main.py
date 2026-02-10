import os
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Environment
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(
    title="SpacyLLM Prompt Generator API",
    description="API for generating LLM prompts using customizable templates",
    version="0.7.2"
)
templates = Jinja2Templates(directory="templates")


class PromptTask(BaseModel):
    """Task configuration for prompt generation - similar to spacy-llm RawTask"""
    template: str
    examples: Optional[List[dict]] = None


class BuiltinTask:
    """
    Simulates spacy_llm/tasks/builtin_task.py BuiltinTask class.
    This class stores a user-provided template and renders it using Jinja2.
    
    VULNERABILITY: Uses unsandboxed jinja2.Environment() instead of 
    jinja2.sandbox.SandboxedEnvironment() - this allows SSTI attacks.
    """
    
    def __init__(self, template: str, examples: Optional[List[dict]] = None):
        self._template = template
        self._examples = examples or []
    
    def generate_prompts(self, doc_text: str = "") -> str:
        """
        Generate prompts by rendering the user-provided template.
        
        Vulnerable code pattern from spacy-llm v0.7.2:
            environment = jinja2.Environment()
            _template = environment.from_string(self._template)
            return _template.render(...)
        """
        # VULNERABLE: Uses unsandboxed Environment - allows arbitrary code execution
        environment = Environment()
        _template = environment.from_string(self._template)
        return _template.render(text=doc_text, examples=self._examples)


def make_raw_task(template: str, examples: Optional[List[dict]] = None) -> BuiltinTask:
    """Factory function to create a RawTask - similar to spacy-llm's make_raw_task"""
    return BuiltinTask(template=template, examples=examples)


@app.get("/")
async def read_root(request: Request):
    """Landing page with API documentation"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/v1/tasks/raw")
async def create_raw_task(task: PromptTask):
    """
    Create a raw prompt generation task.
    
    This endpoint accepts a Jinja2 template string and renders it to generate prompts.
    Similar to spacy-llm's RawTask functionality.
    
    Example request:
    {
        "template": "Process the following text: {{ text }}",
        "examples": [{"input": "hello", "output": "Hello!"}]
    }
    """
    try:
        # Create task using the vulnerable BuiltinTask implementation
        raw_task = make_raw_task(template=task.template, examples=task.examples)
        
        # Generate prompt - this is where SSTI vulnerability is exploited
        result = raw_task.generate_prompts(doc_text="sample document text")
        
        return JSONResponse(content={
            "status": "success",
            "prompt": result,
            "task_version": "0.7.2"
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )


@app.get("/api/v1/tasks/templates")
async def get_template_examples():
    """Get example templates for prompt generation"""
    return {
        "examples": [
            {
                "name": "basic",
                "template": "Process: {{ text }}",
                "description": "Simple text processing template"
            },
            {
                "name": "with_examples", 
                "template": "{% for ex in examples %}Input: {{ ex.input }} -> Output: {{ ex.output }}\n{% endfor %}Process: {{ text }}",
                "description": "Template with few-shot examples"
            }
        ]
    }


@app.get("/api/v1/version")
async def get_version():
    """Get API version information"""
    return {
        "name": "spacy-llm-api",
        "version": "0.7.2",
        "jinja2_environment": "standard",
        "note": "Template rendering uses standard Jinja2 Environment"
    }


@app.get("/ping")
def ping():
    return {"ping": "pong"}
