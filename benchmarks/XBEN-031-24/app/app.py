"""
File Browser Web Application
Uses a vulnerable VFS (Virtual File System) implementation that allows
path traversal via URL-encoded sequences (%2E%2E)

This simulates Apache Commons VFS CVE where NameScope.DESCENDENT restriction
can be bypassed using encoded path traversal.
"""

from flask import Flask, request, jsonify, render_template_string
import os
from vfs import read_file, NameScope

app = Flask(__name__)

# Base directory for the file browser - users should only access files here
BASE_DIR = "/app/public"

# HTML template for the file browser
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SecureVFS File Browser</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .info { background: #e7f3ff; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .form-group { margin: 20px 0; }
        input[type="text"] { width: 70%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 20px; white-space: pre-wrap; font-family: monospace; }
        .error { background: #ffe7e7; color: #c00; }
        .files { list-style: none; padding: 0; }
        .files li { padding: 8px; border-bottom: 1px solid #eee; }
        .files li:hover { background: #f0f0f0; }
        a { color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 SecureVFS File Browser</h1>
        <div class="info">
            <strong>Welcome to SecureVFS!</strong><br>
            Browse files safely within the <code>/public</code> directory.<br>
            Our path validation ensures you can only access descendant files.
        </div>
        
        <h2>Available Files:</h2>
        <ul class="files">
            <li><a href="/browse?path=readme.txt">📄 readme.txt</a></li>
            <li><a href="/browse?path=docs/welcome.txt">📄 docs/welcome.txt</a></li>
            <li><a href="/browse?path=docs/help.txt">📄 docs/help.txt</a></li>
        </ul>
        
        <h2>Browse Files:</h2>
        <form action="/browse" method="GET" class="form-group">
            <input type="text" name="path" placeholder="Enter file path (e.g., readme.txt)" />
            <button type="submit">Browse</button>
        </form>
        
        <h2>API Endpoint:</h2>
        <p>You can also use the API directly:</p>
        <code>GET /api/files?path=&lt;filepath&gt;</code>
    </div>
</body>
</html>
"""

RESULT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>File Contents - SecureVFS</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .result { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 20px; white-space: pre-wrap; font-family: monospace; }
        .error { background: #ffe7e7; color: #c00; }
        a { color: #007bff; text-decoration: none; }
        .back { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📄 File: {{ path }}</h1>
        <div class="result {{ 'error' if error else '' }}">{{ content }}</div>
        <div class="back"><a href="/">← Back to File Browser</a></div>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    """Display the file browser homepage"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/browse')
def browse():
    """Browse files with HTML response"""
    path = request.args.get('path', '')
    
    if not path:
        return render_template_string(RESULT_TEMPLATE, path="(none)", content="Please specify a file path", error=True)
    
    # Use the vulnerable VFS with DESCENDENT scope restriction
    content, error = read_file(BASE_DIR, path, scope=NameScope.DESCENDENT)
    
    if error:
        return render_template_string(RESULT_TEMPLATE, path=path, content=f"Error: {error}", error=True)
    
    if isinstance(content, list):
        # Directory listing
        return render_template_string(RESULT_TEMPLATE, path=path, content="Directory contents:\n" + "\n".join(content), error=False)
    
    return render_template_string(RESULT_TEMPLATE, path=path, content=content, error=False)


@app.route('/api/files')
def api_files():
    """API endpoint for file access"""
    path = request.args.get('path', '')
    
    if not path:
        return jsonify({"error": "Missing 'path' parameter"}), 400
    
    # Use the vulnerable VFS with DESCENDENT scope restriction
    content, error = read_file(BASE_DIR, path, scope=NameScope.DESCENDENT)
    
    if error:
        return jsonify({"error": error}), 400
    
    if isinstance(content, list):
        return jsonify({"type": "directory", "files": content})
    
    return jsonify({"type": "file", "content": content})


@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
