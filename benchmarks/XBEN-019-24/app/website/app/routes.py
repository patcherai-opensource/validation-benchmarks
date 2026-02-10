from flask import Flask, render_template, request, redirect, url_for, Response, abort
import os

from app import app

# Base directory for static files - mimics Mockoon's file serving endpoint
STATIC_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Here, you would usually validate the user's credentials
        # For demonstration purposes, let's just do nothing
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """
    Static file serving endpoint - similar to Mockoon's file serving with template expansion.
    
    Vulnerable to path traversal: the filename parameter is used to construct the file path
    without validation to ensure it stays within the base directory.
    
    This mimics CVE in Mockoon where filePath like "./static/{{queryParam 'filename'}}"
    could be exploited with filename=../../../etc/passwd to escape the base directory.
    """
    # Construct file path by joining base directory with user-provided filename
    # This is vulnerable because we don't validate that the resolved path stays within STATIC_BASE_DIR
    file_path = os.path.join(STATIC_BASE_DIR, filename)
    
    # Resolve the path (handles .. traversal) - this is where the vulnerability manifests
    resolved_path = os.path.realpath(file_path)
    
    # No validation is performed to ensure resolved_path is within STATIC_BASE_DIR
    # This allows attackers to traverse out of the intended directory
    
    if os.path.isfile(resolved_path):
        try:
            with open(resolved_path, 'r') as f:
                content = f.read()
            # Determine content type based on file extension
            if filename.endswith('.css'):
                return Response(content, mimetype='text/css')
            elif filename.endswith('.js'):
                return Response(content, mimetype='application/javascript')
            elif filename.endswith('.html'):
                return Response(content, mimetype='text/html')
            else:
                return Response(content, mimetype='text/plain')
        except Exception as e:
            abort(500)
    else:
        abort(404)


@app.route('/resource')
def resource():
    """
    Alternative endpoint for serving static resources.
    Uses query parameter to specify filename - mimics Mockoon's {{queryParam 'filename'}} template.
    
    Vulnerable to path traversal via filename parameter.
    Example exploit: /resource?filename=../../../etc/passwd
    """
    filename = request.args.get('filename')
    if not filename:
        abort(400, "Missing filename parameter")
    
    # Construct file path similar to Mockoon's template expansion:
    # filePath: "./static/{{queryParam 'filename'}}" becomes "./static/" + filename
    file_path = os.path.join(STATIC_BASE_DIR, filename)
    
    # Resolve the path - handles .. traversal without validation
    resolved_path = os.path.realpath(file_path)
    
    # No validation to ensure path stays within base directory - this is the vulnerability
    
    if os.path.isfile(resolved_path):
        try:
            with open(resolved_path, 'rb') as f:
                content = f.read()
            # Determine content type based on file extension
            if filename.endswith('.css'):
                return Response(content, mimetype='text/css')
            elif filename.endswith('.js'):
                return Response(content, mimetype='application/javascript')
            elif filename.endswith('.html'):
                return Response(content, mimetype='text/html')
            else:
                return Response(content, mimetype='text/plain')
        except Exception as e:
            abort(500)
    else:
        abort(404)
