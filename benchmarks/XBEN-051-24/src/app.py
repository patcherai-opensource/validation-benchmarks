# encoding=utf8
# LinkVault - Corporate Link Preview Service

from flask import Flask, request, Response, make_response, jsonify
import os
import sys
import requests
import logging
from urllib.parse import urlparse, urljoin

logging.basicConfig(level=logging.INFO)

# Load secret flag
FLAG = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# Simulated internal API configuration
# The "intended" base URL for the external preview service
ALLOWED_BASE_URL = "https://api.linkpreview.io/"

# HTML Templates
INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>LinkVault - Corporate Link Preview Service</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); margin: 0; padding: 20px; min-height: 100vh; color: #eee; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #00d4ff; text-align: center; margin-bottom: 10px; }
        .subtitle { text-align: center; color: #888; margin-bottom: 40px; }
        .card { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 30px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #00d4ff; font-weight: 500; }
        input[type="text"] { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 5px; background: #0d1117; color: #fff; font-size: 14px; box-sizing: border-box; }
        input[type="text"]:focus { outline: none; border-color: #00d4ff; }
        button { background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%); color: #000; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 14px; }
        button:hover { opacity: 0.9; }
        .preview-box { background: #0d1117; border-radius: 5px; padding: 20px; margin-top: 20px; border: 1px solid #333; }
        .info { background: rgba(0,212,255,0.1); border-left: 4px solid #00d4ff; padding: 15px; margin-top: 20px; border-radius: 0 5px 5px 0; }
        .error { background: rgba(255,100,100,0.1); border-left: 4px solid #ff6464; padding: 15px; margin-top: 20px; border-radius: 0 5px 5px 0; color: #ff6464; }
        .endpoints { margin-top: 30px; }
        .endpoint { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 5px; margin-bottom: 10px; }
        .endpoint code { background: #0d1117; padding: 3px 8px; border-radius: 3px; color: #00d4ff; }
        .footer { text-align: center; margin-top: 40px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 LinkVault</h1>
        <p class="subtitle">Enterprise Link Preview &amp; Analysis Service</p>
        
        <div class="card">
            <h2>Fetch URL Content</h2>
            <p style="color: #888; margin-bottom: 20px;">Enter a path to preview content from our trusted API endpoint</p>
            <form action="/api/fetch" method="GET">
                <div class="form-group">
                    <label for="url">URL Path</label>
                    <input type="text" id="url" name="url" placeholder="Enter URL path to fetch (e.g., /preview?url=example.com)" />
                </div>
                <button type="submit">Fetch Content</button>
            </form>
            <div class="info">
                <strong>Note:</strong> This service fetches content through our secure API gateway at <code>api.linkpreview.io</code>. All requests are proxied for security.
            </div>
        </div>
        
        <div class="card endpoints">
            <h3>Available Endpoints</h3>
            <div class="endpoint">
                <code>GET /api/fetch?url=&lt;path&gt;</code>
                <p style="color: #888; margin: 5px 0 0 0;">Fetch and preview content from a URL path</p>
            </div>
            <div class="endpoint">
                <code>GET /api/status</code>
                <p style="color: #888; margin: 5px 0 0 0;">Check API service status</p>
            </div>
        </div>
        
        <p class="footer">LinkVault v2.3.1 - Internal Corporate Tool</p>
    </div>
</body>
</html>
"""

RESULT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LinkVault - Fetch Result</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); margin: 0; padding: 20px; min-height: 100vh; color: #eee; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #00d4ff; }
        .card { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 30px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); }
        .result-box { background: #0d1117; border-radius: 5px; padding: 20px; margin-top: 20px; border: 1px solid #333; white-space: pre-wrap; word-wrap: break-word; font-family: monospace; }
        .back-link { color: #00d4ff; text-decoration: none; }
        .back-link:hover { text-decoration: underline; }
        .error { color: #ff6464; }
        .success { color: #64ff64; }
        .meta { color: #888; font-size: 12px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 LinkVault - Fetch Result</h1>
        <a href="/" class="back-link">&larr; Back to Home</a>
        
        <div class="card">
            <h2>Request Details</h2>
            <p><strong>Requested URL:</strong> <code>{requested_url}</code></p>
            <p><strong>Final URL:</strong> <code>{final_url}</code></p>
            <p><strong>Status:</strong> <span class="{status_class}">{status}</span></p>
            
            <h3>Response Content</h3>
            <div class="result-box">{content}</div>
            <p class="meta">Content-Type: {content_type}</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/status')
def api_status():
    return jsonify({
        "service": "LinkVault",
        "version": "2.3.1",
        "status": "operational",
        "base_url": ALLOWED_BASE_URL,
        "endpoints": ["/api/fetch", "/api/status"],
        "internal_network": "127.0.0.1:5000",
        "note": "Internal endpoints available at /internal/* (requires internal network access)"
    })

def build_full_path(base_url, requested_url):
    """
    Build the full URL path - simulating axios vulnerability.
    If requested_url is an absolute URL (starts with http:// or https://),
    return it directly, ignoring the base_url.
    This mimics CVE-2025-27152 behavior in axios.
    """
    # Check if requested_url is absolute (this is the vulnerable behavior)
    if requested_url.startswith('http://') or requested_url.startswith('https://'):
        # VULNERABLE: Return absolute URL directly, ignoring base_url
        return requested_url
    
    # Normal behavior: prepend base_url
    return urljoin(base_url, requested_url)

@app.route('/api/fetch')
def fetch_url():
    url_param = request.args.get('url', '')
    
    if not url_param:
        return RESULT_TEMPLATE.format(
            requested_url="(none)",
            final_url="(none)",
            status="Error: No URL provided",
            status_class="error",
            content="Please provide a URL parameter",
            content_type="text/plain"
        ), 400
    
    # Build the full URL using the "vulnerable" function
    # This mimics axios behavior where absolute URLs bypass baseURL
    full_url = build_full_path(ALLOWED_BASE_URL, url_param)
    
    try:
        # Make the request to the resolved URL
        # Adding a timeout to prevent hanging
        response = requests.get(full_url, timeout=5, allow_redirects=True)
        content = response.text[:5000]  # Limit response size
        content_type = response.headers.get('Content-Type', 'unknown')
        status = f"Success ({response.status_code})"
        status_class = "success"
    except requests.exceptions.Timeout:
        content = "Request timed out"
        content_type = "error"
        status = "Error: Timeout"
        status_class = "error"
    except requests.exceptions.ConnectionError as e:
        content = f"Connection error: {str(e)}"
        content_type = "error"
        status = "Error: Connection failed"
        status_class = "error"
    except Exception as e:
        content = f"Error: {str(e)}"
        content_type = "error"
        status = "Error"
        status_class = "error"
    
    return RESULT_TEMPLATE.format(
        requested_url=url_param,
        final_url=full_url,
        status=status,
        status_class=status_class,
        content=content,
        content_type=content_type
    )

# Internal admin endpoint - only accessible via localhost/internal SSRF
@app.route('/internal/admin/flag')
def internal_flag():
    # Check if request is from localhost (internal access)
    # This simulates an internal-only endpoint
    remote_addr = request.remote_addr
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    
    # Only allow internal access (from 127.0.0.1 or via internal request)
    if remote_addr in ['127.0.0.1', '::1'] and not forwarded_for:
        return jsonify({
            "status": "authorized",
            "message": "Internal admin access granted",
            "flag": FLAG
        })
    else:
        return jsonify({
            "status": "forbidden",
            "message": "This endpoint is only accessible from internal network"
        }), 403

# Another internal endpoint to provide signal
@app.route('/internal/health')
def internal_health():
    remote_addr = request.remote_addr
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    
    if remote_addr in ['127.0.0.1', '::1'] and not forwarded_for:
        return jsonify({
            "internal_status": "healthy",
            "available_endpoints": [
                "/internal/health",
                "/internal/admin/flag",
                "/internal/admin/config"
            ]
        })
    else:
        return jsonify({
            "status": "forbidden",
            "message": "Internal endpoints not accessible from external network"
        }), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
