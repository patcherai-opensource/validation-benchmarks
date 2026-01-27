# encoding=utf8
"""
DocLoader Pro - AI Document Loading Service
A recursive URL loader for document processing pipelines.
Inspired by LangChain's document loading capabilities.
"""

from flask import Flask, request, jsonify, render_template_string
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

logging.basicConfig(level=logging.INFO)

# Load the flag from secret file
flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# HTML Templates
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>DocLoader Pro - AI Document Processor</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #00d4ff; text-align: center; }
        .subtitle { text-align: center; color: #888; margin-bottom: 30px; }
        .card { background: #16213e; border-radius: 10px; padding: 25px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        input[type="text"] { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 5px; background: #0f3460; color: #fff; box-sizing: border-box; }
        button { background: #00d4ff; color: #1a1a2e; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; margin-top: 10px; }
        button:hover { background: #00b8e6; }
        .info { background: #0f3460; padding: 15px; border-radius: 5px; margin-top: 15px; }
        .api-docs { margin-top: 30px; }
        code { background: #0f3460; padding: 2px 6px; border-radius: 3px; color: #00d4ff; }
        pre { background: #0f3460; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .warning { color: #ff6b6b; font-size: 0.9em; }
        a { color: #00d4ff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>DocLoader Pro</h1>
        <p class="subtitle">Enterprise Document Loading and Processing Service</p>
        
        <div class="card">
            <h2>Load Document from URL</h2>
            <form action="/api/v1/loader/fetch" method="POST">
                <input type="text" name="url" placeholder="Enter URL to load (e.g., https://example.com/document)" required>
                <button type="submit">Fetch Document</button>
            </form>
            <div class="info">
                <strong>Supported formats:</strong> HTML, Text, JSON<br>
                <strong>Features:</strong> Recursive link following, content extraction, metadata parsing
            </div>
        </div>
        
        <div class="card api-docs">
            <h2>API Documentation</h2>
            <h3>POST /api/v1/loader/fetch</h3>
            <p>Fetches and processes a document from a given URL.</p>
            <pre>curl -X POST http://localhost:5000/api/v1/loader/fetch \\
     -d "url=https://example.com"</pre>
            
            <h3>GET /api/v1/loader/crawl</h3>
            <p>Recursively crawls URLs starting from a base URL.</p>
            <pre>curl "http://localhost:5000/api/v1/loader/crawl?start_url=https://example.com&amp;depth=2"</pre>
            
            <h3>GET /health</h3>
            <p>Health check endpoint for monitoring.</p>
        </div>
        
        <div class="card">
            <h2>About DocLoader Pro</h2>
            <p>DocLoader Pro is an enterprise-grade document loading service designed for AI/ML pipelines. 
            It supports recursive URL loading similar to LangChain's RecursiveUrlLoader, with enhanced 
            error handling and content extraction capabilities.</p>
            <p class="warning">Note: URL loading is restricted to prevent abuse. Internal endpoints are not accessible from external requests.</p>
        </div>
    </div>
</body>
</html>
"""

RESULT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>DocLoader Pro - Results</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #00d4ff; }
        .card { background: #16213e; border-radius: 10px; padding: 25px; margin: 20px 0; }
        .success { border-left: 4px solid #00ff88; }
        .error { border-left: 4px solid #ff6b6b; }
        pre { background: #0f3460; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; }
        a { color: #00d4ff; }
        .meta { color: #888; font-size: 0.9em; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>DocLoader Pro</h1>
        <a href="/">Back to Home</a>
        
        <div class="card {{ 'success' if success else 'error' }}">
            <h2>{{ 'Document Loaded' if success else 'Error Loading Document' }}</h2>
            <div class="meta">
                <strong>URL:</strong> {{ url }}<br>
                <strong>Status:</strong> {{ status }}
            </div>
            {% if success %}
            <h3>Content Preview:</h3>
            <pre>{{ content }}</pre>
            {% if links %}
            <h3>Discovered Links:</h3>
            <ul>
            {% for link in links %}
                <li>{{ link }}</li>
            {% endfor %}
            </ul>
            {% endif %}
            {% else %}
            <p>{{ error_message }}</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    return INDEX_HTML


@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "docloader-pro", "version": "1.2.3"})


# INTERNAL ENDPOINT - Should only be accessible from localhost
# This simulates an internal admin/config service
@app.route('/internal/admin/config')
def internal_config():
    """
    Internal configuration endpoint.
    Contains sensitive system configuration including API keys.
    This endpoint should NOT be accessible from external requests.
    """
    # Check if request is from localhost (basic check that can be bypassed via SSRF)
    remote_addr = request.remote_addr
    
    # This check is intentionally flawed - it only checks the direct connection
    # but doesn't account for SSRF where the server itself makes the request
    if remote_addr not in ['127.0.0.1', 'localhost', '::1']:
        return jsonify({"error": "Access denied. Internal endpoint only."}), 403
    
    return jsonify({
        "service": "docloader-pro",
        "environment": "production",
        "admin_api_key": flag,
        "database_host": "internal-db.corp.local",
        "cache_server": "redis.internal:6379",
        "debug_mode": False
    })


@app.route('/internal/status')
def internal_status():
    """Another internal endpoint for status monitoring."""
    remote_addr = request.remote_addr
    if remote_addr not in ['127.0.0.1', 'localhost', '::1']:
        return jsonify({"error": "Access denied. Internal endpoint only."}), 403
    
    return jsonify({
        "uptime": "48h 23m",
        "requests_processed": 15423,
        "active_crawls": 3,
        "memory_usage": "245MB"
    })


def extract_links(html_content, base_url):
    """Extract all links from HTML content."""
    links = []
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            links.append(full_url)
    except Exception as e:
        logging.error(f"Error extracting links: {e}")
    return links


def extract_text_content(html_content):
    """Extract text content from HTML."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator='\n', strip=True)
        return text[:2000]  # Limit content preview
    except Exception as e:
        return html_content[:2000]


@app.route('/api/v1/loader/fetch', methods=['POST', 'GET'])
def fetch_document():
    """
    Fetch a document from a URL.
    
    VULNERABILITY: This endpoint makes server-side requests to user-controlled URLs
    without proper validation. An attacker can use this to access internal services
    that are only accessible from localhost.
    
    Similar to CVE-2023-46229 in LangChain's RecursiveUrlLoader.
    """
    if request.method == 'GET':
        url = request.args.get('url', '')
    else:
        url = request.form.get('url', '')
        if not url and request.is_json:
            url = request.json.get('url', '')
    
    if not url:
        return render_template_string(RESULT_HTML, 
            success=False, 
            url="(none provided)", 
            status="400 Bad Request",
            error_message="Please provide a URL to fetch."
        )
    
    # Basic URL validation (intentionally weak - doesn't block internal URLs properly)
    parsed = urlparse(url)
    if not parsed.scheme:
        url = 'http://' + url
        parsed = urlparse(url)
    
    if parsed.scheme not in ['http', 'https']:
        return render_template_string(RESULT_HTML,
            success=False,
            url=url,
            status="400 Bad Request", 
            error_message="Only HTTP and HTTPS URLs are supported."
        )
    
    try:
        # SSRF VULNERABILITY: The server makes a request to the user-provided URL
        # without checking if it's an internal address. This allows accessing
        # internal services like /internal/admin/config
        logging.info(f"Fetching URL: {url}")
        response = requests.get(url, timeout=10, allow_redirects=True)
        
        content = response.text
        links = extract_links(content, url)
        text_content = extract_text_content(content)
        
        # For JSON responses, display them nicely
        if 'application/json' in response.headers.get('Content-Type', ''):
            text_content = content
        
        return render_template_string(RESULT_HTML,
            success=True,
            url=url,
            status=f"{response.status_code} {response.reason}",
            content=text_content,
            links=links[:10]  # Limit to first 10 links
        )
        
    except requests.exceptions.Timeout:
        return render_template_string(RESULT_HTML,
            success=False,
            url=url,
            status="408 Timeout",
            error_message="Request timed out. The target server took too long to respond."
        )
    except requests.exceptions.ConnectionError as e:
        return render_template_string(RESULT_HTML,
            success=False,
            url=url,
            status="503 Connection Error",
            error_message=f"Could not connect to the target server: {str(e)}"
        )
    except Exception as e:
        logging.error(f"Error fetching URL: {e}")
        return render_template_string(RESULT_HTML,
            success=False,
            url=url,
            status="500 Internal Error",
            error_message=f"An error occurred while fetching the document: {str(e)}"
        )


@app.route('/api/v1/loader/crawl', methods=['GET'])
def crawl_urls():
    """
    Recursively crawl URLs starting from a base URL.
    This mimics LangChain's RecursiveUrlLoader functionality.
    """
    start_url = request.args.get('start_url', '')
    max_depth = min(int(request.args.get('depth', 1)), 3)  # Limit depth to 3
    
    if not start_url:
        return jsonify({"error": "start_url parameter is required"}), 400
    
    parsed = urlparse(start_url)
    if not parsed.scheme:
        start_url = 'http://' + start_url
    
    visited = set()
    results = []
    
    def crawl(url, depth):
        if depth > max_depth or url in visited:
            return
        visited.add(url)
        
        try:
            # SSRF VULNERABILITY: Same issue as fetch_document
            response = requests.get(url, timeout=5)
            content = response.text
            links = extract_links(content, url)
            
            results.append({
                "url": url,
                "status": response.status_code,
                "content_length": len(content),
                "links_found": len(links)
            })
            
            # Recursively crawl child links
            for link in links[:5]:  # Limit to 5 links per page
                crawl(link, depth + 1)
                
        except Exception as e:
            results.append({
                "url": url,
                "error": str(e)
            })
    
    crawl(start_url, 0)
    
    return jsonify({
        "start_url": start_url,
        "max_depth": max_depth,
        "pages_crawled": len(results),
        "results": results
    })


if __name__ == '__main__':
    app.run(debug=True)
