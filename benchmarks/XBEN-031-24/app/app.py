#!/usr/bin/env python3
"""
Change Detection Service - Monitor URLs for changes
Based on changedetection.io architecture

CVE-2024-51998: Path traversal via file URI bypass
The URL validation checks for 'file://' but 'file:/' bypasses the check
"""

from flask import Flask, request, render_template_string, redirect, url_for, jsonify
import re
import os
import uuid
import urllib.request
import urllib.error
from urllib.parse import urlparse
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# In-memory storage for watches
watches = {}

# Environment variable to control file URI access (disabled by default)
ALLOW_FILE_URI = os.environ.get('ALLOW_FILE_URI', 'false').lower() == 'true'

def is_safe_url(url):
    """
    Validate URL to prevent file access.
    
    CVE-2024-51998 VULNERABILITY:
    This check only blocks 'file://' (two slashes) but 'file:/' (one slash) 
    is also valid according to the file URI specification and bypasses this check.
    """
    if not ALLOW_FILE_URI:
        # Vulnerable check: only checks for file:// not file:/
        if re.search(r'^file://', url, re.IGNORECASE):
            return False, "File URIs are not allowed"
    
    # Basic URL validation
    if not url or len(url) < 5:
        return False, "URL too short"
    
    return True, None

def fetch_url_content(url):
    """
    Fetch content from a URL.
    This function is the sink where the vulnerability is exploited.
    """
    try:
        parsed = urlparse(url)
        
        # Handle file:/ URIs (the vulnerability)
        if parsed.scheme.lower() == 'file':
            # Extract path - handle both file:/ and file:// formats
            if url.lower().startswith('file:///'):
                file_path = url[7:]  # Remove 'file://'
            elif url.lower().startswith('file://'):
                file_path = url[7:]  # Remove 'file://'
            elif url.lower().startswith('file:/'):
                file_path = url[6:]  # Remove 'file:/'
            else:
                file_path = parsed.path
            
            # Read file content
            with open(file_path, 'r') as f:
                return f.read()
        
        # Handle HTTP(S) URLs
        req = urllib.request.Request(url, headers={'User-Agent': 'ChangeDetection/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    
    except FileNotFoundError:
        return f"Error: File not found"
    except PermissionError:
        return f"Error: Permission denied"
    except Exception as e:
        return f"Error fetching URL: {str(e)}"

# HTML Templates
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ChangeDetection.io - Web Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .form-group { margin: 20px 0; }
        input[type="text"] { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
        button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .watch-list { margin-top: 30px; }
        .watch-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #007bff; }
        .watch-item a { color: #007bff; text-decoration: none; }
        .watch-item a:hover { text-decoration: underline; }
        .status { font-size: 12px; color: #666; margin-top: 5px; }
        .info-box { background: #e7f3ff; border: 1px solid #b6d4fe; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .info-box h3 { margin: 0 0 10px 0; color: #084298; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 ChangeDetection.io</h1>
        <div class="info-box">
            <h3>Web Page Change Detection</h3>
            <p>Monitor any URL for changes. Add a watch below and we'll track it for you.</p>
            <p><small>Supported protocols: http://, https://</small></p>
        </div>
        
        <form action="/form_quick_watch_add" method="POST">
            <div class="form-group">
                <input type="text" name="url" placeholder="Enter URL to monitor (e.g., https://example.com)" required>
            </div>
            <button type="submit">+ Add Watch</button>
        </form>
        
        {% if watches %}
        <div class="watch-list">
            <h2>Your Watches ({{ watches|length }})</h2>
            {% for watch_id, watch in watches.items() %}
            <div class="watch-item">
                <strong>{{ watch.url }}</strong>
                <div class="status">
                    Status: {{ watch.status }} | 
                    <a href="/preview/{{ watch_id }}">View Preview</a> |
                    <a href="/check/{{ watch_id }}">Check Now</a> |
                    <a href="/delete/{{ watch_id }}">Delete</a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

PREVIEW_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Preview - {{ watch.url }}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; font-size: 18px; }
        .preview-content { background: #1e1e1e; color: #d4d4d4; padding: 20px; border-radius: 4px; white-space: pre-wrap; font-family: monospace; overflow-x: auto; max-height: 600px; overflow-y: auto; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .info { color: #666; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <p><a href="/">← Back to Dashboard</a></p>
        <h1>Preview: {{ watch.url }}</h1>
        <p class="info">Last checked: {{ watch.last_checked or 'Never' }}</p>
        <div class="preview-content">{{ content }}</div>
    </div>
</body>
</html>
'''

ERROR_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 100px auto; padding: 20px; }
        .error { background: #f8d7da; color: #721c24; padding: 20px; border-radius: 4px; border: 1px solid #f5c6cb; }
        a { color: #007bff; }
    </style>
</head>
<body>
    <div class="error">
        <h2>Error</h2>
        <p>{{ message }}</p>
        <p><a href="/">← Back to Dashboard</a></p>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    """Main dashboard showing all watches"""
    return render_template_string(INDEX_TEMPLATE, watches=watches)

@app.route('/form_quick_watch_add', methods=['POST'])
def form_quick_watch_add():
    """
    Add a new watch - this is the entry point for the vulnerability.
    The attacker controls the URL parameter.
    """
    url = request.form.get('url', '').strip()
    
    if not url:
        return render_template_string(ERROR_TEMPLATE, message="URL is required"), 400
    
    # Validate URL (vulnerable check)
    is_safe, error = is_safe_url(url)
    if not is_safe:
        return render_template_string(ERROR_TEMPLATE, message=error), 400
    
    # Create new watch
    watch_id = str(uuid.uuid4())[:8]
    watches[watch_id] = {
        'url': url,
        'status': 'pending',
        'content': None,
        'last_checked': None
    }
    
    logging.info(f"New watch added: {watch_id} -> {url}")
    
    # Automatically check the watch
    return redirect(url_for('check_watch', watch_id=watch_id))

@app.route('/check/<watch_id>')
def check_watch(watch_id):
    """Check a watch and fetch its content"""
    if watch_id not in watches:
        return render_template_string(ERROR_TEMPLATE, message="Watch not found"), 404
    
    watch = watches[watch_id]
    url = watch['url']
    
    logging.info(f"Checking watch {watch_id}: {url}")
    
    # Fetch content (this is where the vulnerability is exploited)
    content = fetch_url_content(url)
    
    # Update watch
    from datetime import datetime
    watch['content'] = content
    watch['status'] = 'checked'
    watch['last_checked'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return redirect(url_for('preview_watch', watch_id=watch_id))

@app.route('/preview/<watch_id>')
def preview_watch(watch_id):
    """Preview the content of a watch"""
    if watch_id not in watches:
        return render_template_string(ERROR_TEMPLATE, message="Watch not found"), 404
    
    watch = watches[watch_id]
    content = watch.get('content', 'No content yet. Click "Check Now" to fetch.')
    
    return render_template_string(PREVIEW_TEMPLATE, watch=watch, content=content)

@app.route('/delete/<watch_id>')
def delete_watch(watch_id):
    """Delete a watch"""
    if watch_id in watches:
        del watches[watch_id]
    return redirect(url_for('index'))

@app.route('/api/watches', methods=['GET'])
def api_list_watches():
    """API endpoint to list all watches"""
    return jsonify(watches)

@app.route('/health')
def health():
    """Health check endpoint"""
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
