from flask import Flask, render_template, request, redirect, url_for, send_file, abort, jsonify, Response
import os
import urllib.parse

from app import app

# Base directory for public resources (simulating FileSystemResource location)
PUBLIC_RESOURCES_ROOT = '/var/www/springapp/public'
# Secret data directory (above the public root)
DATA_DIR = '/var/www/springapp/data'

def is_invalid_path(path):
    """
    Basic path validation - mimics Spring's isInvalidPath check.
    Checks for obvious path traversal but fails to detect encoded forms.
    """
    # Block obvious path traversal sequences
    if '..' in path:
        return True
    if path.startswith('/'):
        return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return jsonify({"status": "UP", "application": "Spring Resource Server", "version": "6.1.2"})

@app.route('/resources')
def serve_resource():
    """
    Serves static resources from the public directory.
    Simulates Spring Framework's RouterFunctions.resources() with FileSystemResource.
    
    CVE-2024-38816 style vulnerability:
    - The path parameter is checked BEFORE decoding
    - But then decoded when constructing the file path
    - Allows encoded path traversal like %2e%2e/ to bypass validation
    """
    resource_path = request.args.get('path', '')
    
    if not resource_path:
        abort(400, description="Missing 'path' parameter")
    
    # First validation pass - checks raw input (VULNERABILITY: checks before decode)
    if is_invalid_path(resource_path):
        abort(400, description="Invalid path: path traversal detected")
    
    # URL decode the path (simulating how Spring decodes the path segment)
    decoded_path = urllib.parse.unquote(resource_path)
    
    # Second decode pass for double-encoded sequences (CVE-2024-38816 specific behavior)
    # Spring would sometimes decode twice in certain configurations
    if '%' in decoded_path:
        decoded_path = urllib.parse.unquote(decoded_path)
    
    # Construct full path (vulnerable - uses decoded path)
    full_path = os.path.join(PUBLIC_RESOURCES_ROOT, decoded_path)
    
    # Normalize the path
    full_path = os.path.normpath(full_path)
    
    # Check if file exists and serve it
    if os.path.isfile(full_path):
        try:
            return send_file(full_path)
        except Exception as e:
            abort(500, description=f"Error reading file: {str(e)}")
    else:
        abort(404, description="Resource not found")

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # Authentication always fails for demo
        return render_template('admin_login.html', error="Invalid credentials")
    return render_template('admin_login.html')

@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Resource not found", status=404), 404

@app.errorhandler(400) 
def bad_request(e):
    return jsonify(error=str(e.description), status=400), 400

@app.errorhandler(500)
def server_error(e):
    return jsonify(error=str(e.description), status=500), 500
