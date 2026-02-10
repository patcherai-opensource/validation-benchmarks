import re
import io
import zipfile
import codecs

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from lxml import etree

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# In-memory storage for spreadsheet data
spreadsheet_data = {}


class XmlScanner:
    """
    XML Security Scanner - attempts to prevent XXE attacks
    by checking encoding and scanning for malicious patterns.
    """
    
    ENCODING_PATTERN_DOUBLE = re.compile(r'encoding="([^"]*)"')
    ENCODING_PATTERN_SINGLE = re.compile(r"encoding='([^']*)'")
    
    PATTERN_DOCTYPE = re.compile(r'<!DOCTYPE\s', re.IGNORECASE)
    PATTERN_ENTITY = re.compile(r'<!ENTITY\s', re.IGNORECASE)
    
    @classmethod
    def find_charset(cls, xml_content: bytes) -> str:
        """
        Detect the character encoding from XML prolog.
        Returns the detected encoding or None if not found.
        """
        try:
            xml_str = xml_content[:1024].decode('ascii', errors='replace')
        except:
            return None
        
        match = cls.ENCODING_PATTERN_DOUBLE.search(xml_str)
        if match:
            return match.group(1).upper()
        
        match = cls.ENCODING_PATTERN_SINGLE.search(xml_str)
        if match:
            return match.group(1).upper()
        
        return None
    
    @classmethod
    def scan(cls, xml_content: bytes) -> bytes:
        """
        Scan XML content for malicious patterns.
        Content is decoded according to detected encoding before checking for XXE patterns.
        If encoding detection fails, default to UTF-8.
        """
        charset = cls.find_charset(xml_content)
        
        if charset is None:
            charset = 'UTF-8'
        
        try:
            if charset == 'UTF-8':
                xml_str = xml_content.decode('utf-8', errors='replace')
            else:
                import codecs
                try:
                    xml_str = xml_content.decode(codecs.lookup(charset).name, errors='replace')
                except LookupError:
                    xml_str = xml_content.decode('utf-8', errors='replace')
        except:
            return xml_content
        
        if cls.PATTERN_DOCTYPE.search(xml_str):
            raise ValueError("Potentially unsafe XML: DOCTYPE detected")
        if cls.PATTERN_ENTITY.search(xml_str):
            raise ValueError("Potentially unsafe XML: ENTITY detected")
        
        return xml_content


def process_xlsx_file(file_content: bytes) -> dict:
    """
    Process an XLSX file and extract cell data.
    XLSX files are ZIP archives containing XML files.
    """
    result = {
        'cells': [],
        'errors': []
    }
    
    try:
        with zipfile.ZipFile(io.BytesIO(file_content), 'r') as zf:
            shared_strings = []
            if 'xl/sharedStrings.xml' in zf.namelist():
                try:
                    ss_content = zf.read('xl/sharedStrings.xml')
                    scanned_content = XmlScanner.scan(ss_content)
                    
                    parser = etree.XMLParser(
                        load_dtd=True,
                        resolve_entities=True,
                        recover=True
                    )
                    tree = etree.fromstring(scanned_content, parser)
                    
                    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                    for si in tree.findall('.//main:si', ns):
                        text_parts = []
                        for t in si.findall('.//main:t', ns):
                            if t.text:
                                text_parts.append(t.text)
                        shared_strings.append(''.join(text_parts))
                except ValueError as e:
                    result['errors'].append(f"Security scan failed: {str(e)}")
                    return result
                except etree.XMLSyntaxError as e:
                    pass
            
            if 'xl/worksheets/sheet1.xml' in zf.namelist():
                try:
                    sheet_content = zf.read('xl/worksheets/sheet1.xml')
                    scanned_sheet = XmlScanner.scan(sheet_content)
                    
                    parser = etree.XMLParser(
                        load_dtd=True,
                        resolve_entities=True,
                        recover=True
                    )
                    sheet_tree = etree.fromstring(scanned_sheet, parser)
                    
                    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                    for row in sheet_tree.findall('.//main:row', ns):
                        for cell in row.findall('main:c', ns):
                            cell_ref = cell.get('r', '')
                            cell_type = cell.get('t', '')
                            value_elem = cell.find('main:v', ns)
                            
                            if value_elem is not None and value_elem.text:
                                if cell_type == 's':
                                    idx = int(value_elem.text)
                                    if idx < len(shared_strings):
                                        result['cells'].append({
                                            'ref': cell_ref,
                                            'value': shared_strings[idx]
                                        })
                                else:
                                    result['cells'].append({
                                        'ref': cell_ref,
                                        'value': value_elem.text
                                    })
                except ValueError as e:
                    result['errors'].append(f"Security scan failed: {str(e)}")
                except etree.XMLSyntaxError:
                    pass
                    
    except zipfile.BadZipFile:
        result['errors'].append("Invalid XLSX file: not a valid ZIP archive")
    except Exception as e:
        result['errors'].append(f"Error processing file: {str(e)}")
    
    return result


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = spreadsheet_data.get('latest', {})
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "data": data
    })


@app.post("/upload", response_class=HTMLResponse)
async def upload_spreadsheet(
        request: Request,
        spreadsheet: UploadFile = File(...)
):
    if not spreadsheet.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if not spreadsheet.filename.endswith('.xlsx'):
        data = {
            'filename': spreadsheet.filename,
            'cells': [],
            'errors': ['Invalid file type. Please upload an XLSX file.']
        }
        spreadsheet_data['latest'] = data
        return templates.TemplateResponse("index.html", {
            "request": request,
            "data": data
        })
    
    file_content = await spreadsheet.read()
    result = process_xlsx_file(file_content)
    
    data = {
        'filename': spreadsheet.filename,
        'cells': result['cells'],
        'errors': result['errors']
    }
    spreadsheet_data['latest'] = data
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "data": data
    })


@app.get("/ping")
async def ping():
    return {"ping": "pong"}
