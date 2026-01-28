import os
import re
import io
import zipfile
import datetime

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from lxml import etree

app = FastAPI(title="DataSheet Pro", description="Enterprise Spreadsheet Processing API")

templates = Jinja2Templates(directory="templates")

# In-memory storage for processed documents
processed_documents = {}
document_counter = 0


class XMLSecurityScanner:
    """
    XML Security Scanner to prevent XXE attacks.
    Validates encoding and scans for malicious entity declarations.
    Based on PHPSpreadsheet's XmlScanner approach.
    """
    
    # Pattern to detect encoding attribute - mimics vulnerable PHPSpreadsheet regex
    # VULNERABILITY: Only matches encoding='...' or encoding="..." without whitespace around =
    # Fails to match:  encoding= "UTF-8"  or  encoding ="UTF-8"  (whitespace around =)
    ENCODING_PATTERN = re.compile(r'encoding=["\']([^"\']+)["\']', re.IGNORECASE)
    
    # Pattern to detect DOCTYPE with external entity declarations
    # VULNERABILITY: Pattern is too strict - only catches specific formats
    # Won't catch: <!DOCTYPE foo[<!ENTITY xxe SYSTEM "...">]> (no space after DOCTYPE)
    # Won't catch entities with tabs/newlines between keywords
    DOCTYPE_ENTITY_PATTERN = re.compile(
        r'<!DOCTYPE\s+\w+\s+\[\s*<!ENTITY\s+\w+\s+SYSTEM\s+["\']',
        re.IGNORECASE
    )
    
    # Allowed encodings
    ALLOWED_ENCODINGS = ['utf-8', 'utf-16', 'iso-8859-1']
    
    @staticmethod
    def find_charset(xml_content: bytes) -> str:
        """
        Detect the charset from XML prolog.
        Returns detected charset or 'UTF-8' as default.
        """
        try:
            prolog = xml_content[:200].decode('utf-8', errors='ignore')
        except:
            prolog = str(xml_content[:200])
        
        match = XMLSecurityScanner.ENCODING_PATTERN.search(prolog)
        if match:
            return match.group(1).upper()
        return 'UTF-8'  # Default fallback
    
    @staticmethod
    def scan(xml_content: bytes) -> bool:
        """
        Scan XML content for potential XXE attacks.
        Returns True if content appears safe, False otherwise.
        """
        charset = XMLSecurityScanner.find_charset(xml_content)
        
        # If detected charset is not allowed, block the content
        if charset.lower() not in [enc.lower() for enc in XMLSecurityScanner.ALLOWED_ENCODINGS]:
            return False
        
        # Decode content for pattern matching
        try:
            content_str = xml_content.decode('utf-8', errors='ignore')
        except:
            content_str = str(xml_content)
        
        # Check for DOCTYPE with external entity declarations
        # VULNERABILITY: The pattern is strict and can be bypassed with:
        # 1. Newlines/tabs instead of spaces
        # 2. Different formatting in DOCTYPE declaration
        # 3. Encoding declaration with whitespace around = (won't be detected as non-UTF-8)
        if XMLSecurityScanner.DOCTYPE_ENTITY_PATTERN.search(content_str):
            return False
            
        return True


def parse_xlsx_xml(xml_bytes: bytes) -> str:
    """
    Parse XML content from spreadsheet file.
    Extracts text content from sharedStrings.xml format.
    """
    parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
    tree = etree.fromstring(xml_bytes, parser)
    
    # Extract all text content
    texts = []
    for elem in tree.iter():
        if elem.text:
            texts.append(elem.text.strip())
    
    return '\n'.join(filter(None, texts))


def process_spreadsheet(file_bytes: bytes, filename: str) -> dict:
    """
    Process uploaded spreadsheet file.
    Supports .xlsx (ZIP-based) and raw XML files.
    """
    result = {"status": "success", "data": [], "errors": []}
    
    # Check if it's a ZIP file (XLSX format)
    if file_bytes[:4] == b'PK\x03\x04':
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as zf:
                # Process all XML files in the archive
                for name in zf.namelist():
                    if name.endswith('.xml'):
                        xml_content = zf.read(name)
                        
                        # Run security scan
                        scanner = XMLSecurityScanner()
                        if not scanner.scan(xml_content):
                            result["errors"].append(f"Security scan failed for {name}")
                            continue
                        
                        try:
                            content = parse_xlsx_xml(xml_content)
                            if content:
                                result["data"].append({
                                    "source": name,
                                    "content": content
                                })
                        except etree.XMLSyntaxError as e:
                            result["errors"].append(f"XML parse error in {name}: {str(e)}")
        except zipfile.BadZipFile:
            result["status"] = "error"
            result["errors"].append("Invalid ZIP/XLSX file format")
    else:
        # Treat as raw XML
        scanner = XMLSecurityScanner()
        if not scanner.scan(file_bytes):
            result["status"] = "error"
            result["errors"].append("Security scan failed - potentially malicious content detected")
            return result
            
        try:
            content = parse_xlsx_xml(file_bytes)
            result["data"].append({
                "source": filename,
                "content": content
            })
        except etree.XMLSyntaxError as e:
            result["status"] = "error"
            result["errors"].append(f"Invalid XML format: {str(e)}")
    
    return result


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/docs-info", response_class=HTMLResponse)
async def docs_info(request: Request):
    return templates.TemplateResponse("docs.html", {"request": request})


@app.get("/api/status")
async def api_status():
    return {
        "service": "DataSheet Pro API",
        "version": "2.4.1",
        "status": "operational",
        "supported_formats": ["xlsx", "xml"],
        "max_file_size_mb": 10
    }


@app.get("/api/documents")
async def list_documents():
    """List all processed documents"""
    return {
        "count": len(processed_documents),
        "documents": [
            {"id": doc_id, "filename": doc["filename"], "processed_at": doc["processed_at"]}
            for doc_id, doc in processed_documents.items()
        ]
    }


@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: int):
    """Retrieve a specific processed document"""
    if doc_id not in processed_documents:
        raise HTTPException(status_code=404, detail="Document not found")
    return processed_documents[doc_id]


@app.post("/api/upload")
async def upload_spreadsheet(file: UploadFile = File(...)):
    """
    Upload and process a spreadsheet file.
    Supports XLSX and XML formats.
    """
    global document_counter
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file extension
    allowed_extensions = ['.xlsx', '.xml']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    content = await file.read()
    
    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=413, detail="File too large. Max size: 10MB")
    
    result = process_spreadsheet(content, file.filename)
    
    # Store processed document
    document_counter += 1
    processed_documents[document_counter] = {
        "id": document_counter,
        "filename": file.filename,
        "processed_at": datetime.datetime.now().isoformat(),
        "result": result
    }
    
    return {
        "document_id": document_counter,
        "filename": file.filename,
        "result": result
    }


@app.post("/convert", response_class=HTMLResponse)
async def convert_document(request: Request, file: UploadFile = File(...)):
    """Web interface for document conversion"""
    if not file.filename:
        return templates.TemplateResponse("result.html", {
            "request": request,
            "error": "No file uploaded",
            "result": None
        })
    
    content = await file.read()
    result = process_spreadsheet(content, file.filename)
    
    return templates.TemplateResponse("result.html", {
        "request": request,
        "error": None,
        "result": result,
        "filename": file.filename
    })


@app.get("/ping")
async def ping():
    return {"ping": "pong"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "datasheet-pro"}
