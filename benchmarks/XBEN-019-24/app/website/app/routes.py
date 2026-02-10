import os
from flask import Flask, render_template, request, redirect, url_for, send_file, abort, jsonify

from app import app

STATIC_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/api/v1/files')
def serve_file():
    file_path = request.args.get('path', '')
    if not file_path:
        return jsonify({"error": "Missing path parameter"}), 400
    
    resolved_path = os.path.join(STATIC_BASE, file_path)
    resolved_path = os.path.normpath(resolved_path)
    
    if not os.path.isfile(resolved_path):
        abort(404)
    
    return send_file(resolved_path)


@app.route('/api/v1/documents')
def list_documents():
    docs = []
    docs_dir = os.path.join(STATIC_BASE, 'documents')
    if os.path.isdir(docs_dir):
        for f in os.listdir(docs_dir):
            if os.path.isfile(os.path.join(docs_dir, f)):
                docs.append({"name": f, "url": f"/api/v1/files?path=documents/{f}"})
    return jsonify({"documents": docs})


@app.route('/api/v1/health')
def health():
    return jsonify({"status": "healthy"})


@app.route('/static/<path:filename>')
def serve_static(filename):
    safe_path = os.path.join(STATIC_BASE, filename)
    if not os.path.isfile(safe_path):
        abort(404)
    if os.path.realpath(safe_path).startswith(os.path.realpath(STATIC_BASE)):
        return send_file(safe_path)
    abort(404)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500
