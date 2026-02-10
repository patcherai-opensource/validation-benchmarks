"""
Salt-like File Server - Vulnerable to CVE-2024-22232 style path traversal

This simulates the SaltStack fileserver vulnerability where:
1. Absolute paths are rejected (os.path.isabs check)
2. But relative paths with '../' traversal sequences are NOT properly validated
3. os.path.join allows escaping the configured file_roots
"""
import os
import hashlib
import secrets
from functools import wraps
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Configuration - mimics SaltStack file_roots configuration
FILE_ROOTS = {
    "base": "/srv/salt/base"
}

# Simple authentication (mimics Salt master authentication)
# In real SaltStack, this would be minion/API authentication
API_TOKENS = {}
MASTER_KEY = secrets.token_hex(16)

def generate_token(username):
    """Generate an API token for authenticated access"""
    token = hashlib.sha256(f"{username}{MASTER_KEY}".encode()).hexdigest()[:32]
    API_TOKENS[token] = username
    return token

# Pre-generate a token for test user (simulates authenticated minion/user)
TEST_TOKEN = generate_token("minion01")

def require_auth(f):
    """Authentication decorator - requires valid API token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('X-Auth-Token', '')
        if auth_header not in API_TOKENS:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated

def find_file(path, saltenv="base"):
    """
    Find a file in the file_roots.
    
    VULNERABLE: This function only checks for absolute paths but does NOT
    properly validate path traversal sequences like '../'
    
    This is the core of CVE-2024-22232 - the path is not properly sanitized
    before being joined with the root directory.
    """
    if saltenv not in FILE_ROOTS:
        return None, f"Environment '{saltenv}' not found"
    
    root = FILE_ROOTS[saltenv]
    
    # VULNERABLE CHECK: Only rejects absolute paths
    # But allows relative paths with '../' traversal sequences
    if os.path.isabs(path):
        return None, "Absolute paths are not allowed"
    
    # VULNERABLE: os.path.join with unsanitized path allows traversal
    # For example: os.path.join("/srv/salt/base", "../../etc/passwd")
    # resolves to "/srv/salt/base/../../etc/passwd" which normalizes to "/etc/passwd"
    full_path = os.path.join(root, path)
    
    # Note: A secure implementation would use something like:
    # full_path = os.path.normpath(os.path.join(root, path))
    # if not full_path.startswith(root):
    #     return None, "Access denied: path outside file_roots"
    
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return full_path, None
    
    return None, "File not found"

def serve_file(path, saltenv="base"):
    """
    Serve a file from the file_roots.
    
    VULNERABLE: Uses find_file which doesn't properly validate paths
    """
    full_path, error = find_file(path, saltenv)
    
    if error:
        return None, error
    
    try:
        with open(full_path, 'r') as f:
            return f.read(), None
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    """Landing page - shows file server info"""
    return render_template('index.html')

@app.route('/api/auth', methods=['POST'])
def authenticate():
    """
    Simple authentication endpoint.
    Returns a token for API access.
    
    For this demo, any username/password combo works to get a token.
    """
    data = request.get_json() or {}
    username = data.get('username', 'anonymous')
    password = data.get('password', '')
    
    # Simple auth - in real SaltStack this would be more complex
    if username and password:
        token = generate_token(username)
        return jsonify({
            "status": "ok",
            "token": token,
            "message": "Authentication successful"
        })
    
    return jsonify({"error": "Username and password required"}), 400

@app.route('/api/fileserver/find', methods=['GET'])
@require_auth
def api_find_file():
    """
    API endpoint to find a file in file_roots.
    
    VULNERABLE: The 'path' parameter is not properly sanitized for traversal
    """
    path = request.args.get('path', '')
    saltenv = request.args.get('saltenv', 'base')
    
    if not path:
        return jsonify({"error": "Path parameter required"}), 400
    
    full_path, error = find_file(path, saltenv)
    
    if error:
        return jsonify({"error": error}), 404 if "not found" in error.lower() else 400
    
    return jsonify({
        "status": "found",
        "path": path,
        "saltenv": saltenv
    })

@app.route('/api/fileserver/serve', methods=['GET'])
@require_auth
def api_serve_file():
    """
    API endpoint to serve/read a file from file_roots.
    
    VULNERABLE: The 'path' parameter allows path traversal via '../'
    sequences, enabling reading of arbitrary files on the system.
    
    Example exploit:
    GET /api/fileserver/serve?path=../../../flag.txt
    """
    path = request.args.get('path', '')
    saltenv = request.args.get('saltenv', 'base')
    
    if not path:
        return jsonify({"error": "Path parameter required"}), 400
    
    content, error = serve_file(path, saltenv)
    
    if error:
        return jsonify({"error": error}), 404 if "not found" in error.lower() else 400
    
    return jsonify({
        "status": "ok",
        "path": path,
        "saltenv": saltenv,
        "content": content
    })

@app.route('/api/fileserver/list', methods=['GET'])
@require_auth
def api_list_files():
    """List files in the file_roots (for legitimate use)"""
    saltenv = request.args.get('saltenv', 'base')
    
    if saltenv not in FILE_ROOTS:
        return jsonify({"error": f"Environment '{saltenv}' not found"}), 404
    
    root = FILE_ROOTS[saltenv]
    files = []
    
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            rel_path = os.path.relpath(os.path.join(dirpath, filename), root)
            files.append(rel_path)
    
    return jsonify({
        "status": "ok",
        "saltenv": saltenv,
        "files": files
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
