import os
from typing import Optional

from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from lxml import etree
from users import schemas

app = FastAPI(title="MathML Equation Renderer", version="1.2.0")

templates = Jinja2Templates(directory="templates")

# In-memory storage for equations
equation_storage = {}


def list_directory(path):
    result = []
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        result.append('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            result.append('{}{}'.format(subindent, f))
    return result


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    equation = equation_storage.get("current", schemas.Equation())
    return templates.TemplateResponse("index.html", {"request": request, "equation": equation})


@app.post("/render", response_class=HTMLResponse)
async def render_mathml(
        request: Request,
        title: str = Form(...),
        description: str = Form(""),
        mathml_file: UploadFile = File(None)
):
    """
    Process and render MathML equations.
    Accepts MathML XML files for mathematical expression rendering.
    """
    equation = schemas.Equation(title=title, description=description)

    if mathml_file:
        mathml_content = await mathml_file.read()
        try:
            # Process MathML XML with DTD loading enabled for proper entity handling
            parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
            tree = etree.fromstring(mathml_content, parser)
            equation.rendered_output = etree.tostring(tree).decode()
        except etree.XMLSyntaxError as e:
            print(f"MathML parsing error: {e}")
            equation.rendered_output = f"<span class='error'>Error: Invalid MathML format. Please provide valid MathML XML.</span>"

    equation_storage["current"] = equation
    return templates.TemplateResponse("index.html", {"request": request, "equation": equation})


@app.get("/api/equations", response_class=HTMLResponse)
async def list_equations(request: Request):
    """List available equation templates"""
    return templates.TemplateResponse("equations.html", {"request": request})


@app.get("/ping")
async def ping():
    return {"status": "healthy", "service": "mathml-renderer"}


@app.get("/hint")
async def read_root(request: Request):
    files = list_directory('/app')
    return templates.TemplateResponse("hint.html", {"request": request, "files": files})
