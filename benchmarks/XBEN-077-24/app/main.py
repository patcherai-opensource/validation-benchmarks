import os
import io
import zipfile
import tempfile

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from lxml import etree

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# In-memory storage for uploaded spreadsheet data
spreadsheet_data = {}


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


def parse_xlsx_content(xlsx_bytes):
    """
    Parse XLSX file and extract shared strings data.
    This mimics PhpSpreadsheet's behavior of extracting XML parts from XLSX archives.
    """
    cells = []
    errors = []
    
    try:
        # XLSX files are ZIP archives containing XML files
        with zipfile.ZipFile(io.BytesIO(xlsx_bytes), 'r') as zip_ref:
            # List files in the archive for debugging
            file_list = zip_ref.namelist()
            
            # Try to read shared strings (contains text cell values)
            # This is where PhpSpreadsheet's vulnerability exists - in processing these XML files
            for xml_file in ['xl/sharedStrings.xml', 'xl/workbook.xml', 'xl/styles.xml']:
                if xml_file in file_list:
                    try:
                        xml_content = zip_ref.read(xml_file)
                        
                        # Vulnerable XML parsing - mimics PhpSpreadsheet's behavior
                        # The parser is configured to resolve external entities (XXE vulnerability)
                        parser = etree.XMLParser(
                            load_dtd=True, 
                            resolve_entities=True,
                            no_network=False
                        )
                        
                        tree = etree.fromstring(xml_content, parser)
                        
                        # Extract text content from shared strings
                        if xml_file == 'xl/sharedStrings.xml':
                            # Find all text elements (t tags in the spreadsheetml namespace)
                            for elem in tree.iter():
                                if elem.text and elem.text.strip():
                                    cells.append(elem.text.strip())
                    except etree.XMLSyntaxError as e:
                        errors.append(f"XML parsing error in {xml_file}: {str(e)}")
                    except Exception as e:
                        errors.append(f"Error processing {xml_file}: {str(e)}")
                        
    except zipfile.BadZipFile:
        errors.append("Invalid XLSX file format - file is not a valid ZIP archive")
    except Exception as e:
        errors.append(f"Error reading spreadsheet: {str(e)}")
    
    return cells, errors


@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    data = spreadsheet_data.get('current', {'cells': [], 'errors': [], 'filename': None})
    return templates.TemplateResponse("index.html", {"request": request, "data": data})


@app.post("/upload", response_class=HTMLResponse)
async def upload_spreadsheet(
        request: Request,
        spreadsheet: UploadFile = File(...)
):
    """Upload and process an Excel spreadsheet file"""
    result = {'cells': [], 'errors': [], 'filename': spreadsheet.filename}
    
    # Check file extension
    if not spreadsheet.filename.lower().endswith('.xlsx'):
        result['errors'].append("Only .xlsx files are supported. Please upload a valid Excel spreadsheet.")
    else:
        content = await spreadsheet.read()
        
        if len(content) == 0:
            result['errors'].append("Uploaded file is empty")
        else:
            cells, errors = parse_xlsx_content(content)
            result['cells'] = cells
            result['errors'] = errors
    
    spreadsheet_data['current'] = result
    return templates.TemplateResponse("index.html", {"request": request, "data": result})


@app.get("/ping")
async def ping():
    return {"ping": "pong"}


@app.get("/api/status")
async def api_status():
    """API endpoint for status check"""
    return {
        "status": "online",
        "service": "SpreadSheet Analytics Pro",
        "version": "2.1.4",
        "supported_formats": [".xlsx"]
    }


@app.get("/hint")
async def read_hint(request: Request):
    files = list_directory('/app')
    return templates.TemplateResponse("hint.html", {"request": request, "files": files})
