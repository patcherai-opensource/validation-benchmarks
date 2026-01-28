#!/usr/bin/env python3
"""
ConfigSync - Centralized Configuration Management System
File Server API for distributing configuration files across infrastructure
"""

from flask import Flask, request, jsonify, send_file, render_template, abort
import os
import logging

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = os.urandom(32)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('configsync')

# File roots configuration - simulating Salt's file_roots
FILE_ROOTS = {
    'base': '/opt/configsync/configs',
    'production': '/opt/configsync/production',
    'development': '/opt/configsync/development'
}

# Simulated authentication tokens (in production, this would be a database)
VALID_TOKENS = {
    'agent-token-7f3d9a': {'name': 'web-agent-01', 'role': 'agent'},
    'agent-token-2b8e4c': {'name': 'db-agent-01', 'role': 'agent'},
    'admin-token-secure': {'name': 'admin', 'role': 'admin'}
}

def verify_token(token):
    """Verify if the provided token is valid"""
    return VALID_TOKENS.get(token)

def find_file(path, environment='base'):
    """
    Find a file in the specified environment's file root
    
    VULNERABILITY: This function does not properly sanitize path traversal sequences.
    It only checks for absolute paths but doesn't prevent relative path traversal (../).
    Similar to CVE-2024-22232 in SaltStack.
    """
    # Check if path is absolute (basic check, but doesn't prevent traversal)
    if os.path.isabs(path):
        logger.warning(f"Absolute path rejected: {path}")
        return None, "Absolute paths are not allowed"
    
    # Get the root for the specified environment
    root = FILE_ROOTS.get(environment)
    if not root:
        return None, f"Unknown environment: {environment}"
    
    # VULNERABLE: os.path.join doesn't prevent directory traversal
    # The path is simply joined without checking for ../
    full_path = os.path.join(root, path)
    
    # Check if file exists
    if os.path.isfile(full_path):
        return full_path, None
    
    return None, f"File not found: {path}"

@app.route('/robots.txt')
def robots():
    """Serve robots.txt"""
    return send_file('../static/robots.txt', mimetype='text/plain')

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/docs')
def docs():
    """API documentation page"""
    return render_template('docs.html')

@app.route('/status')
def status():
    """System status page"""
    return render_template('status.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'configsync',
        'version': '2.1.4'
    })

@app.route('/api/v1/agent/register', methods=['POST'])
def register_agent():
    """
    Register a new agent (disabled in production)
    This endpoint is maintained for backwards compatibility
    """
    # In development, this would create a new agent token
    # Currently disabled - use existing agent tokens
    return jsonify({
        'error': 'Agent registration is disabled',
        'message': 'Please contact your administrator for agent credentials',
        'note': 'Existing agents should use their assigned tokens (e.g., agent-token-XXXXXX format)'
    }), 403

@app.route('/api/v1/environments')
def list_environments():
    """List available environments"""
    return jsonify({
        'environments': list(FILE_ROOTS.keys()),
        'default': 'base'
    })

@app.route('/api/v1/files', methods=['GET'])
def list_files():
    """
    List files in an environment
    Requires authentication token
    """
    token = request.headers.get('X-Auth-Token') or request.args.get('token')
    if not token or not verify_token(token):
        return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
    
    env = request.args.get('env', 'base')
    root = FILE_ROOTS.get(env)
    
    if not root or not os.path.exists(root):
        return jsonify({'error': f'Environment not found: {env}'}), 404
    
    files = []
    for f in os.listdir(root):
        full_path = os.path.join(root, f)
        if os.path.isfile(full_path):
            files.append({
                'name': f,
                'size': os.path.getsize(full_path)
            })
    
    return jsonify({
        'environment': env,
        'files': files
    })

@app.route('/api/v1/file/fetch', methods=['GET'])
def fetch_file():
    """
    Fetch a configuration file from the file server
    
    Parameters:
        - path: Path to the file (relative to file root)
        - env: Environment (base, production, development)
        - token: Authentication token (can also be in header)
    
    VULNERABLE ENDPOINT: Does not properly sanitize path parameter
    """
    token = request.headers.get('X-Auth-Token') or request.args.get('token')
    
    if not token or not verify_token(token):
        return jsonify({
            'error': 'Authentication required',
            'code': 'AUTH_REQUIRED',
            'hint': 'Provide a valid token via X-Auth-Token header or token parameter'
        }), 401
    
    path = request.args.get('path')
    if not path:
        return jsonify({
            'error': 'Missing required parameter: path',
            'code': 'MISSING_PARAM'
        }), 400
    
    env = request.args.get('env', 'base')
    
    # Find the file (vulnerable function)
    file_path, error = find_file(path, env)
    
    if error:
        logger.info(f"File fetch failed for path={path}, env={env}: {error}")
        return jsonify({
            'error': error,
            'code': 'FILE_NOT_FOUND'
        }), 404
    
    # Return file contents
    try:
        return send_file(file_path)
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        return jsonify({
            'error': 'Internal server error',
            'code': 'SERVER_ERROR'
        }), 500

@app.route('/api/v1/config/validate', methods=['POST'])
def validate_config():
    """
    Validate a configuration file syntax
    (Decoy endpoint - not vulnerable)
    """
    token = request.headers.get('X-Auth-Token') or request.args.get('token')
    if not token or not verify_token(token):
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Missing config content'}), 400
    
    # Just pretend to validate
    return jsonify({
        'valid': True,
        'message': 'Configuration syntax is valid'
    })

@app.route('/api/v1/sync/trigger', methods=['POST'])
def trigger_sync():
    """
    Trigger a configuration sync to agents
    (Decoy endpoint - not vulnerable)
    """
    token = request.headers.get('X-Auth-Token') or request.args.get('token')
    user = verify_token(token)
    
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    return jsonify({
        'status': 'sync_queued',
        'message': 'Configuration sync has been queued'
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page (decoy - no actual login mechanism)"""
    if request.method == 'POST':
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found', 'code': 'NOT_FOUND'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error', 'code': 'SERVER_ERROR'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
