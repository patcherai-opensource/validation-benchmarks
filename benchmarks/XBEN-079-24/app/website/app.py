"""
Solara-inspired static file server with path traversal vulnerability.
This mimics CVE-2024-39903 where path traversal via URL-encoded sequences
can bypass directory containment checks in static file endpoints.

The vulnerability exists because:
1. The path normalization/containment check is insufficient
2. Path traversal sequences in URL fragments can escape the intended directory

In the real Solara CVE, the fix was to add a `path_is_child_of` utility that
properly validates that resolved paths stay within the base directory.
"""

from flask import Flask, send_file, abort, render_template, request, Response
import os
from pathlib import Path

app = Flask(__name__, static_folder='static', template_folder='templates')

# Base directory for serving static/CDN content
CACHE_DIR = Path("/app/public/assets")
PUBLIC_DIR = Path("/app/public")


def get_from_cache(base_cache_dir: Path, path: str) -> Path:
    """
    Vulnerable cache/path resolution - mimics pre-patch Solara behavior.
    
    This function constructs a file path by joining the base directory with
    the user-provided path. The vulnerability is that it doesn't properly
    verify the resolved path stays within the base directory.
    
    The vulnerable pattern (from Solara):
        cache_path = base_cache_dir / path
        if cache_path.exists():
            return cache_path
    
    The fix adds containment checking:
        if not path_is_child_of(cache_path.resolve(), base_cache_dir.resolve()):
            raise ValueError("Path traversal detected")
    """
    # Construct cache path - this is the vulnerable operation
    # The path may contain traversal sequences that escape base_cache_dir
    cache_path = base_cache_dir / path
    
    return cache_path


def get_data(base_dir: Path, path: str):
    """
    Mimics Solara's cdn_helper.get_data() function.
    Returns the file content for the requested path.
    
    Vulnerable: doesn't verify the final resolved path is within base_dir
    """
    file_path = get_from_cache(base_dir, path)
    
    try:
        # Resolve to get the actual filesystem path
        # This is where traversal sequences take effect
        resolved_path = file_path.resolve()
        
        # VULNERABILITY: No check that resolved_path is within base_dir!
        # The fix would be:
        # if not resolved_path.is_relative_to(base_dir.resolve()):
        #     return None
        
        if resolved_path.exists() and resolved_path.is_file():
            return resolved_path
    except Exception:
        pass
    
    return None


@app.route('/')
def index():
    """Main landing page - Solara-style web application"""
    return render_template('index.html')


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')


@app.route('/_solara/cdn/<path:path>')
def cdn(path):
    """
    CDN endpoint - vulnerable to path traversal.
    Mimics Solara's /_solara/cdn/<path:path> endpoint from flask.py.
    
    Exploitation example:
    GET /_solara/cdn/../../../flag.txt
    
    With URL encoding to bypass any intermediate filters:
    GET /_solara/cdn/..%2f..%2f..%2f..%2fflag.txt
    
    The path parameter receives the decoded path from Flask's routing,
    then get_data() joins it with the base directory without proper
    containment checking.
    """
    file_path = get_data(CACHE_DIR, path)
    
    if file_path is not None:
        try:
            return send_file(file_path)
        except Exception:
            pass
    
    abort(404)


@app.route('/static/public/<path:path>')
def static_public(path):
    """
    Static public files endpoint - also vulnerable.
    Mimics Solara's /static/public/<path:path> endpoint.
    """
    file_path = get_data(PUBLIC_DIR, path)
    
    if file_path is not None:
        try:
            return send_file(file_path)
        except Exception:
            pass
    
    abort(404)


@app.route('/static/assets/<path:path>')
def static_assets(path):
    """
    Static assets endpoint - vulnerable to path traversal.
    Mimics Solara's /static/assets/<path:path> endpoint.
    """
    file_path = get_data(CACHE_DIR, path)
    
    if file_path is not None:
        try:
            return send_file(file_path)
        except Exception:
            pass
    
    abort(404)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return "Internal Server Error", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
