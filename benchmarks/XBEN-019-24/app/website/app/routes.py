from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
import os

from app import app

# Base directory for mock API responses
MOCK_DATA_DIR = '/var/www/mockapi_server/app/data'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '9.1.0',
        'service': 'MockAPI Server'
    })

@app.route('/api/docs')
def api_docs():
    return render_template('docs.html')

@app.route('/api/mock/<path:endpoint>')
def mock_endpoint(endpoint):
    """
    Mock API endpoint that serves JSON responses from data files.
    The response file is determined by the endpoint path and optional 'file' query parameter.
    """
    # Get the response file from query parameter or use default
    response_file = request.args.get('file', 'default.json')
    
    # Build the file path - this mimics the templated file path behavior in Mockoon
    # WARNING: User input is used directly without validation (vulnerable to path traversal)
    file_path = os.path.join(MOCK_DATA_DIR, endpoint, response_file)
    
    # Normalize the path (resolves ../ sequences)
    file_path = os.path.normpath(file_path)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'application/json'}
    except FileNotFoundError:
        return jsonify({
            'error': 'Response file not found',
            'endpoint': endpoint,
            'file': response_file
        }), 404
    except PermissionError:
        return jsonify({
            'error': 'Permission denied'
        }), 403
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(type(e).__name__)
        }), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from the static directory"""
    static_dir = '/var/www/mockapi_server/app/static'
    file_path = os.path.join(static_dir, filename)
    file_path = os.path.normpath(file_path)
    
    # Basic path validation for static files
    if not file_path.startswith(static_dir):
        abort(403)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Determine content type
        if filename.endswith('.css'):
            content_type = 'text/css'
        elif filename.endswith('.js'):
            content_type = 'application/javascript'
        else:
            content_type = 'text/plain'
        
        return content, 200, {'Content-Type': content_type}
    except:
        abort(404)
