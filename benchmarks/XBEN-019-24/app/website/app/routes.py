from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, abort
import os
import re
from urllib.parse import unquote

from app import app

# Simulating a document management system
DOCS_BASE = '/var/www/springdocs/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'xlsx', 'png', 'jpg'}

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # Demo - always fail login
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/api/v1/documents')
def list_documents():
    """List available document categories"""
    return jsonify({
        "status": "success",
        "categories": [
            {"id": 1, "name": "reports", "count": 12},
            {"id": 2, "name": "templates", "count": 8},
            {"id": 3, "name": "archives", "count": 3}
        ],
        "total": 23
    })

@app.route('/api/v1/documents/<category>')
def get_category(category):
    """Get documents in a category"""
    # Simulated response
    docs = {
        "reports": ["Q1_2024.pdf", "Q2_2024.pdf", "annual_summary.docx"],
        "templates": ["invoice.xlsx", "letter.docx", "memo.txt"],
        "archives": ["backup_2023.zip"]
    }
    if category in docs:
        return jsonify({"status": "success", "documents": docs[category]})
    return jsonify({"status": "error", "message": "Category not found"}), 404

@app.route('/api/v1/health')
def health():
    return jsonify({"status": "healthy", "version": "2.1.4", "framework": "Spring Boot"})

@app.route('/api/v1/user/profile')
def user_profile():
    return jsonify({"status": "error", "message": "Authentication required"}), 401

# Public resources endpoint for serving static files
@app.route('/public/<path:filepath>')
def serve_public_resource(filepath):
    """
    Serve public static resources from the uploads directory.
    Implements path validation to prevent directory traversal.
    
    Security: Validates the raw path to block traversal sequences.
    Note: Flask/Werkzeug decodes URL path once before routing.
    """
    # Security validation on the raw filepath (already decoded once by Flask)
    # Block obvious traversal attempts
    if '..' in filepath or filepath.startswith('/'):
        abort(403, description="Access denied: Invalid path detected")
    
    # Block direct access to sensitive filenames  
    blocked_names = ['flag', 'secret', 'passwd', 'shadow', 'key', 'private']
    for blocked in blocked_names:
        if blocked in filepath.lower():
            abort(403, description="Access denied: Restricted resource")
    
    # VULNERABLE: The validation above only checks the Flask-decoded path.
    # If user sends double-encoded sequences like %252e%252e, Flask decodes 
    # to %2e%2e which passes our checks (no literal '..' present).
    # But when we decode again below for file access, %2e%2e becomes '..'
    # enabling path traversal.
    
    # Construct full path manually (vulnerable pattern inspired by Spring CVE)
    base_dir = os.path.join(app.root_path, 'static', 'uploads')
    
    # Decode the filepath for file access (this is the vulnerable double-decode)
    final_path = unquote(filepath)
    full_path = os.path.join(base_dir, final_path)
    
    # Attempt to serve the file
    try:
        # Normalize to resolve ../ sequences after join
        normalized = os.path.normpath(full_path)
        if os.path.isfile(normalized):
            directory = os.path.dirname(normalized)
            filename = os.path.basename(normalized)
            return send_from_directory(directory, filename)
        else:
            abort(404, description="File not found")
    except Exception as e:
        abort(404, description="Resource not found")

# Legacy resource endpoint (deprecated but still active for compatibility)
@app.route('/resources')
def legacy_resources():
    """Legacy endpoint - redirects to new API"""
    return redirect('/api/v1/documents')

@app.route('/static-assets/<path:filename>')
def static_assets(filename):
    """Serve CSS/JS assets"""
    return send_from_directory('static', filename)

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@app.route('/admin')
def admin():
    """Admin panel - requires authentication"""
    return jsonify({"status": "error", "message": "Admin access requires authentication"}), 401

@app.route('/api/v1/config')
def config():
    """Application configuration endpoint"""
    return jsonify({
        "status": "success",
        "config": {
            "app_name": "SpringDocs Enterprise",
            "version": "2.1.4",
            "storage_backend": "filesystem",
            "upload_path": "/public/{category}/{filename}",
            "max_file_size": "50MB"
        }
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Resource not found"}), 404

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"status": "error", "message": str(e.description)}), 403
