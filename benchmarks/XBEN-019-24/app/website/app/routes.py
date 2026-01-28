from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import json

from app import app

# Mock API configuration storage
mock_endpoints = [
    {"id": 1, "method": "GET", "path": "/api/users", "status": 200, "body": '{"users": []}'},
    {"id": 2, "method": "POST", "path": "/api/login", "status": 200, "body": '{"token": "abc123"}'},
    {"id": 3, "method": "GET", "path": "/api/products", "status": 200, "body": '{"products": []}'},
]

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', endpoints=mock_endpoints)

@app.route('/endpoints')
def list_endpoints():
    """List all configured mock endpoints"""
    return jsonify({"success": True, "endpoints": mock_endpoints})

@app.route('/endpoints/<int:endpoint_id>')
def get_endpoint(endpoint_id):
    """Get a specific mock endpoint configuration"""
    for ep in mock_endpoints:
        if ep['id'] == endpoint_id:
            return jsonify({"success": True, "endpoint": ep})
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.route('/docs')
def docs():
    """API Documentation page"""
    return render_template('docs.html')

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "1.2.0"})

@app.route('/api/v1/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "running": True,
        "mock_server": "active",
        "endpoints_count": len(mock_endpoints)
    })

# File serving endpoint for mock responses
@app.route('/files')
def serve_file():
    """
    Serve files from the configured responses directory.
    Used for FILE type responses in mock endpoints.
    """
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({"error": "Missing 'path' parameter"}), 400
    
    # Resolve the file path relative to responses directory
    base_dir = os.path.join(app.root_path, 'responses')
    
    # Get directory and filename from path
    directory = os.path.dirname(file_path) or '.'
    filename = os.path.basename(file_path)
    
    full_dir = os.path.join(base_dir, directory)
    
    try:
        return send_from_directory(full_dir, filename)
    except Exception as e:
        return jsonify({"error": "File not found", "details": str(e)}), 404

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static assets"""
    return send_from_directory('static', filename)

@app.route('/robots.txt')
def robots():
    """Serve robots.txt"""
    return send_from_directory('static', 'robots.txt')

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "message": "The requested resource does not exist"}), 404
