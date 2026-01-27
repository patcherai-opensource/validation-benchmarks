import os
import re
from urllib.parse import unquote
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

app = FastAPI(title="VFS File Manager", version="2.9.1")

# Base directory for VFS file operations - simulating Apache Commons VFS NameScope.DESCENDENT restriction
VFS_BASE_DIR = "/app/files"

class VFSResolver:
    """
    Simulates Apache Commons VFS resolveFile with NameScope.DESCENDENT.
    
    VULNERABILITY: URL-encoded path traversal sequences like %2E%2E/ are not 
    properly decoded before path validation (CVE in Apache Commons VFS < 2.10.0).
    
    The fix would be to decode URL-encoded sequences BEFORE checking for traversal.
    """
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
    
    def _check_descendent_scope(self, user_path: str) -> bool:
        """
        Check if path stays within DESCENDENT scope.
        
        BUG: Checks for '..' BEFORE URL decoding, allowing encoded bypasses.
        Real fix: decode first, then check.
        """
        # This check is flawed - it only blocks literal ".." not encoded variants
        if ".." in user_path:
            return False
        return True
    
    def resolve_file(self, relative_path: str) -> Path:
        """
        Resolve a file path relative to base directory with DESCENDENT scope.
        
        This simulates the vulnerable Apache Commons VFS behavior where 
        %2E%2E (encoded ..) bypasses the scope check.
        """
        # First, check for traversal (VULNERABLE: before decoding)
        if not self._check_descendent_scope(relative_path):
            raise ValueError("Path traversal detected: path escapes base directory scope")
        
        # Then decode the URL-encoded path (TOO LATE - check already passed)
        decoded_path = unquote(relative_path)
        
        # Normalize the path and resolve
        # Using os.path.join preserves the traversal after decoding
        full_path = os.path.normpath(os.path.join(str(self.base_path), decoded_path))
        
        return Path(full_path)
    
    def list_directory(self, relative_path: str = "") -> list:
        """List files in a directory within the VFS scope."""
        resolved = self.resolve_file(relative_path)
        
        if not resolved.exists():
            raise FileNotFoundError(f"Directory not found: {relative_path}")
        
        if not resolved.is_dir():
            raise ValueError("Not a directory")
        
        return [f.name for f in resolved.iterdir()]
    
    def read_file(self, relative_path: str) -> str:
        """Read file contents within VFS scope."""
        resolved = self.resolve_file(relative_path)
        
        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
        
        if not resolved.is_file():
            raise ValueError("Not a file")
        
        with open(resolved, 'r') as f:
            return f.read()


vfs = VFSResolver(VFS_BASE_DIR)


@app.get("/", response_class=HTMLResponse)
async def home():
    """Main page - VFS File Manager interface."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VFS Document Manager</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .nav { display: flex; gap: 15px; margin: 20px 0; }
        .nav a { color: #3498db; text-decoration: none; padding: 8px 16px; background: #ecf0f1; border-radius: 4px; }
        .nav a:hover { background: #3498db; color: white; }
        .api-docs { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }
        code { background: #2c3e50; color: #ecf0f1; padding: 2px 6px; border-radius: 3px; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .footer { margin-top: 30px; font-size: 12px; color: #7f8c8d; }
        .warning { background: #ffe6e6; border-left: 4px solid #e74c3c; padding: 10px 15px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗂️ VFS Document Manager</h1>
        <p>Virtual File System Storage powered by Apache Commons VFS</p>
        
        <div class="nav">
            <a href="/browse">📁 Browse Files</a>
            <a href="/api/list">📋 API: List Files</a>
            <a href="/api/docs">📚 API Documentation</a>
        </div>
        
        <div class="api-docs">
            <h3>API Endpoints</h3>
            <ul>
                <li><code>GET /api/list?path=</code> - List directory contents</li>
                <li><code>GET /api/read?path=</code> - Read file contents</li>
                <li><code>GET /browse?dir=</code> - Web file browser</li>
            </ul>
            <p><strong>Note:</strong> All file operations are restricted to the <code>/files</code> directory using VFS NameScope.DESCENDENT.</p>
        </div>
        
        <h3>Quick Access</h3>
        <ul>
            <li><a href="/browse?dir=documents">Documents</a></li>
            <li><a href="/browse?dir=reports">Reports</a></li>
            <li><a href="/browse?dir=images">Images</a></li>
        </ul>
        
        <div class="footer">
            <p>VFS Document Manager v2.9.1 | Using Apache Commons VFS Core</p>
            <p>Security: Path scope restrictions enforced via NameScope.DESCENDENT</p>
        </div>
    </div>
</body>
</html>"""


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "vfs-manager"}


@app.get("/browse", response_class=HTMLResponse)
async def browse(dir: str = ""):
    """Web-based file browser."""
    try:
        files = vfs.list_directory(dir)
        current_dir = dir if dir else "(root)"
        
        file_list = ""
        for f in sorted(files):
            file_path = f"{dir}/{f}" if dir else f
            file_list += f'<li><a href="/browse?dir={file_path}">{f}/</a> | <a href="/api/read?path={file_path}">📄 Read</a></li>\n'
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Browse: {current_dir}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .container {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; font-size: 1.5em; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ padding: 8px 10px; border-bottom: 1px solid #ecf0f1; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .nav {{ margin-bottom: 20px; }}
        .path {{ background: #ecf0f1; padding: 8px 12px; border-radius: 4px; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav"><a href="/">← Home</a> | <a href="/browse">Root</a></div>
        <h1>📁 Directory Browser</h1>
        <p class="path">Current path: /files/{current_dir}</p>
        <ul>
            {file_list if file_list else '<li>Empty directory</li>'}
        </ul>
    </div>
</body>
</html>"""
    except FileNotFoundError as e:
        return HTMLResponse(f"<h1>Error</h1><p>Directory not found: {dir}</p><p><a href='/browse'>Back</a></p>", status_code=404)
    except ValueError as e:
        return HTMLResponse(f"<h1>Security Error</h1><p>{str(e)}</p><p>Path traversal is not allowed.</p><p><a href='/browse'>Back</a></p>", status_code=403)


@app.get("/api/list")
async def api_list(path: str = ""):
    """
    List directory contents via API.
    
    Path is resolved relative to VFS base directory with DESCENDENT scope restriction.
    """
    try:
        files = vfs.list_directory(path)
        return {
            "status": "success",
            "path": path if path else "/",
            "files": files,
            "resolver": "VFSResolver",
            "scope": "DESCENDENT"
        }
    except FileNotFoundError as e:
        return JSONResponse(
            {"status": "error", "message": str(e), "resolver": "VFSResolver"},
            status_code=404
        )
    except ValueError as e:
        return JSONResponse(
            {"status": "error", "message": str(e), "security": "NameScope.DESCENDENT violation"},
            status_code=403
        )


@app.get("/api/read")
async def api_read(path: str):
    """
    Read file contents via API.
    
    File path is resolved with VFS DESCENDENT scope to prevent directory traversal.
    """
    try:
        content = vfs.read_file(path)
        return {
            "status": "success",
            "path": path,
            "content": content,
            "resolver": "VFSResolver",
            "scope": "DESCENDENT"
        }
    except FileNotFoundError as e:
        return JSONResponse(
            {"status": "error", "message": str(e), "resolver": "VFSResolver"},
            status_code=404
        )
    except ValueError as e:
        return JSONResponse(
            {"status": "error", "message": str(e), "security": "NameScope.DESCENDENT violation"},
            status_code=403
        )
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": f"Failed to read file: {str(e)}"},
            status_code=500
        )


@app.get("/api/docs", response_class=HTMLResponse)
async def api_docs():
    """API Documentation page."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VFS API Documentation</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1, h2 { color: #2c3e50; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }
        code { background: #ecf0f1; padding: 2px 6px; border-radius: 3px; }
        .endpoint { border-left: 4px solid #3498db; padding-left: 15px; margin: 20px 0; }
        .method { background: #3498db; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold; }
        .security { background: #ffe6e6; border-left: 4px solid #e74c3c; padding: 10px 15px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 VFS File Manager API</h1>
        <p><a href="/">← Back to Home</a></p>
        
        <h2>Overview</h2>
        <p>This API provides access to the virtual file system using Apache Commons VFS library patterns.</p>
        <p>All paths are resolved relative to the base directory with <code>NameScope.DESCENDENT</code> restrictions.</p>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> /api/list</h3>
            <p>List contents of a directory.</p>
            <p><strong>Parameters:</strong></p>
            <ul>
                <li><code>path</code> (optional) - Relative path to directory</li>
            </ul>
            <p><strong>Example:</strong></p>
            <pre>GET /api/list?path=documents</pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> /api/read</h3>
            <p>Read contents of a file.</p>
            <p><strong>Parameters:</strong></p>
            <ul>
                <li><code>path</code> (required) - Relative path to file</li>
            </ul>
            <p><strong>Example:</strong></p>
            <pre>GET /api/read?path=documents/readme.txt</pre>
        </div>
        
        <div class="security">
            <h3>⚠️ Security Notice</h3>
            <p>Path traversal sequences (e.g., <code>..</code>) are blocked to prevent unauthorized file access.</p>
            <p>All file operations are restricted to the designated file storage directory using VFS NameScope.DESCENDENT.</p>
        </div>
        
        <h2>VFS Configuration</h2>
        <pre>
FileSystemManager fsManager = VFS.getManager();
FileObject baseDir = fsManager.resolveFile("/app/files");

// Resolve with DESCENDENT scope - files must be under baseDir
FileObject file = baseDir.resolveFile(userPath, NameScope.DESCENDENT);
        </pre>
        
        <p class="footer">VFS Document Manager v2.9.1 | Apache Commons VFS 2.9.1</p>
    </div>
</body>
</html>"""
