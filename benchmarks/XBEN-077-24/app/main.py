import os
from typing import Optional

from fastapi import FastAPI, Form, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from lxml import etree

app = FastAPI(title="MathDoc Pro", description="Professional Mathematical Document Processing API", docs_url=None, redoc_url=None)

templates = Jinja2Templates(directory="templates")

# In-memory storage for equations and documents
equation_history = []
document_store = {}

# Sample equations for demo
SAMPLE_EQUATIONS = [
    {"id": 1, "name": "Quadratic Formula", "latex": "x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}"},
    {"id": 2, "name": "Pythagorean Theorem", "latex": "a^2 + b^2 = c^2"},
    {"id": 3, "name": "Euler's Identity", "latex": "e^{i\\pi} + 1 = 0"},
]


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main dashboard for MathDoc Pro"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "equations": SAMPLE_EQUATIONS,
        "history": equation_history[-5:] if equation_history else []
    })


@app.get("/docs-viewer", response_class=HTMLResponse)
async def docs_viewer(request: Request):
    """Documentation viewer page"""
    return templates.TemplateResponse("docs.html", {"request": request})


@app.get("/api/equations", response_class=JSONResponse)
async def list_equations():
    """List all sample equations"""
    return {"equations": SAMPLE_EQUATIONS, "count": len(SAMPLE_EQUATIONS)}


@app.get("/api/equations/{eq_id}", response_class=JSONResponse)
async def get_equation(eq_id: int):
    """Get a specific equation by ID"""
    for eq in SAMPLE_EQUATIONS:
        if eq["id"] == eq_id:
            return eq
    raise HTTPException(status_code=404, detail="Equation not found")


@app.post("/api/latex/validate", response_class=JSONResponse)
async def validate_latex(latex: str = Form(...)):
    """Validate LaTeX syntax (placeholder - not vulnerable)"""
    if not latex:
        return {"valid": False, "error": "Empty input"}
    # Simple validation - just check for basic structure
    if latex.strip():
        return {"valid": True, "latex": latex}
    return {"valid": False, "error": "Invalid LaTeX syntax"}


@app.get("/api/documents", response_class=JSONResponse)
async def list_documents():
    """List stored documents"""
    return {"documents": list(document_store.keys()), "count": len(document_store)}


@app.post("/render", response_class=HTMLResponse)
async def render_mathml(
        request: Request,
        mathml_file: UploadFile = File(None),
        mathml_text: Optional[str] = Form(None),
        doc_title: str = Form("Untitled")
):
    """
    Render MathML content - supports both file upload and direct text input.
    MathML is processed to extract and display mathematical expressions.
    """
    rendered_output = None
    error_message = None
    
    mathml_content = None
    
    # Priority: file upload over text input
    if mathml_file and mathml_file.filename:
        mathml_content = await mathml_file.read()
    elif mathml_text:
        mathml_content = mathml_text.encode('utf-8')
    
    if mathml_content:
        try:
            # Process MathML XML content
            # Using LIBXML_DTDLOAD equivalent for proper DTD handling
            parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
            tree = etree.fromstring(mathml_content, parser)
            rendered_output = etree.tostring(tree, pretty_print=True).decode('utf-8')
            
            # Store in history
            equation_history.append({
                "title": doc_title,
                "preview": rendered_output[:100] + "..." if len(rendered_output) > 100 else rendered_output
            })
            
            # Store document
            if doc_title != "Untitled":
                document_store[doc_title] = rendered_output
                
        except etree.XMLSyntaxError as e:
            error_message = f"MathML parsing error: Invalid XML structure"
        except Exception as e:
            error_message = f"Processing error: Unable to render MathML content"
    
    return templates.TemplateResponse("render.html", {
        "request": request,
        "rendered": rendered_output,
        "error": error_message,
        "title": doc_title
    })


@app.get("/render", response_class=HTMLResponse)
async def render_page(request: Request):
    """MathML rendering page"""
    return templates.TemplateResponse("render.html", {"request": request, "rendered": None, "error": None, "title": ""})


@app.get("/convert", response_class=HTMLResponse)
async def convert_page(request: Request):
    """Conversion tool page"""
    return templates.TemplateResponse("convert.html", {"request": request})


@app.post("/api/convert/latex-to-mathml", response_class=JSONResponse)
async def convert_latex_to_mathml(latex: str = Form(...)):
    """Convert LaTeX to MathML (placeholder - returns sample output)"""
    # This is a placeholder conversion - doesn't actually convert
    sample_mathml = f"<math xmlns='http://www.w3.org/1998/Math/MathML'><mrow><mi>x</mi></mrow></math>"
    return {"status": "success", "mathml": sample_mathml, "original": latex}


@app.get("/ping")
async def ping():
    return {"status": "healthy", "service": "mathdoc-pro"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.2.0"}


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return """User-agent: *
Disallow: /api/
Disallow: /render
Allow: /
"""
