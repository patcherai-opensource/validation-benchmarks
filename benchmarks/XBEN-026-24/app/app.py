import os
import hashlib
import secrets
from functools import wraps
from flask import Flask, request, jsonify, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# File server configuration
FILE_ROOTS = {
    "base": ["/srv/salt/base"]
}

USERS = {
    "minion01": {"password_hash": hashlib.sha256("minion01_key".encode()).hexdigest(), "role": "minion"},
    "minion02": {"password_hash": hashlib.sha256("minion02_secret".encode()).hexdigest(), "role": "minion"},
    "admin": {"password_hash": hashlib.sha256("salt_master_admin".encode()).hexdigest(), "role": "admin"}
}

# API tokens for authenticated sessions
active_tokens = {}


def generate_token(username):
    token = secrets.token_hex(32)
    active_tokens[token] = username
    return token


def validate_token(token):
    return active_tokens.get(token)


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('X-Auth-Token')
        if not auth_header:
            auth_header = request.args.get('token')
        
        if not auth_header or not validate_token(auth_header):
            return jsonify({"error": "Authentication required"}), 401
        
        return f(*args, **kwargs)
    return decorated


def find_file(path, saltenv="base"):
    """
    Find a file in the file_roots for the given environment.
    """
    if os.path.isabs(path):
        return None, "Absolute paths are not allowed"
    
    roots = FILE_ROOTS.get(saltenv, [])
    if not roots:
        return None, f"Environment '{saltenv}' not found"
    
    for root in roots:
        full_path = os.path.join(root, path)
        
        if os.path.isfile(full_path):
            return full_path, None
    
    return None, "File not found"


def serve_file(path, saltenv="base"):
    """
    Serve a file from the file_roots.
    """
    file_path, error = find_file(path, saltenv)
    
    if error:
        return None, error
    
    try:
        with open(file_path, 'r') as f:
            return f.read(), None
    except Exception as e:
        return None, "Error reading file"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json() if request.is_json else request.form
    username = data.get('username', '')
    password = data.get('password', '')
    
    if username in USERS:
        expected_hash = USERS[username]["password_hash"]
        provided_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if expected_hash == provided_hash:
            token = generate_token(username)
            if request.is_json:
                return jsonify({
                    "status": "success",
                    "token": token,
                    "message": "Authentication successful"
                })
            else:
                session['token'] = token
                session['username'] = username
                return redirect(url_for('dashboard'))
    
    if request.is_json:
        return jsonify({"error": "Invalid credentials"}), 401
    return render_template('login.html', error="Invalid credentials")


@app.route('/logout')
def logout():
    token = session.get('token')
    if token and token in active_tokens:
        del active_tokens[token]
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'token' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))


@app.route('/api/v1/file/find', methods=['GET', 'POST'])
@require_auth
def api_find_file():
    """
    API endpoint to find files in file_roots.
    GET /api/v1/file/find?path=init.sls&saltenv=base
    POST with JSON: {"path": "init.sls", "saltenv": "base"}
    """
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args
    
    path = data.get('path', '')
    saltenv = data.get('saltenv', 'base')
    
    if not path:
        return jsonify({"error": "Path parameter is required"}), 400
    
    file_path, error = find_file(path, saltenv)
    
    if error:
        return jsonify({"error": error}), 404
    
    return jsonify({
        "path": path,
        "saltenv": saltenv,
        "found": True,
        "file_path": os.path.basename(file_path)
    })


@app.route('/api/v1/file/serve', methods=['GET', 'POST'])
@require_auth
def api_serve_file():
    """
    API endpoint to serve files from file_roots.
    GET /api/v1/file/serve?path=init.sls&saltenv=base
    POST with JSON: {"path": "init.sls", "saltenv": "base"}
    """
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args
    
    path = data.get('path', '')
    saltenv = data.get('saltenv', 'base')
    
    if not path:
        return jsonify({"error": "Path parameter is required"}), 400
    
    content, error = serve_file(path, saltenv)
    
    if error:
        return jsonify({"error": error}), 404
    
    return jsonify({
        "path": path,
        "saltenv": saltenv,
        "content": content
    })


@app.route('/api/v1/file/list', methods=['GET'])
@require_auth
def api_list_files():
    """
    List available files in file_roots for given environment.
    """
    saltenv = request.args.get('saltenv', 'base')
    
    roots = FILE_ROOTS.get(saltenv, [])
    if not roots:
        return jsonify({"error": f"Environment '{saltenv}' not found"}), 404
    
    files = []
    for root in roots:
        if os.path.isdir(root):
            for dirpath, dirnames, filenames in os.walk(root):
                for filename in filenames:
                    rel_path = os.path.relpath(os.path.join(dirpath, filename), root)
                    files.append(rel_path)
    
    return jsonify({
        "saltenv": saltenv,
        "files": files
    })


@app.route('/api/v1/envs', methods=['GET'])
@require_auth
def api_list_envs():
    """
    List available salt environments.
    """
    return jsonify({
        "environments": list(FILE_ROOTS.keys())
    })


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
