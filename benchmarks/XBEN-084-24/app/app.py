#!/usr/bin/env python3
"""
WebCrawler Analytics Platform - A platform that aggregates web crawling results
Vulnerability: Redirect credential leak (inspired by CVE-2024-1968)
"""

import os
import hashlib
import json
import base64
import threading
import time
from flask import Flask, request, redirect, jsonify, render_template_string, make_response
from functools import wraps

app = Flask(__name__)

# Configuration
FLAG = os.environ.get('FLAG', 'FLAG{test_flag}')
ADMIN_TOKEN = "Bearer admin_crawler_token_7x9Kp2mN"
LEAKED_CREDENTIALS_FILE = "/tmp/leaked_credentials.log"

# Simple in-memory storage for leaked credentials
leaked_credentials = []

def log_leaked_credential(auth_header, endpoint, source):
    """Log leaked credentials to demonstrate the vulnerability"""
    entry = {
        "authorization": auth_header,
        "endpoint": endpoint,
        "source": source,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    leaked_credentials.append(entry)
    # Also write to file for persistence
    with open(LEAKED_CREDENTIALS_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def simulate_internal_crawler():
    """
    Simulates an internal crawler that periodically makes authenticated requests.
    This causes the admin token to leak via the redirect vulnerability.
    """
    import urllib.request
    import urllib.error
    
    time.sleep(5)  # Wait for server to start
    
    while True:
        try:
            # Simulate the crawler making a request that triggers the redirect
            # The redirect vulnerability causes the Authorization header to leak
            log_leaked_credential(
                ADMIN_TOKEN,
                '/api/crawl/start',
                'internal_crawler_automated'
            )
        except Exception as e:
            pass
        
        time.sleep(60)  # Run every minute

def require_auth(f):
    """Decorator to require valid authorization"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if auth_header == ADMIN_TOKEN:
            return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized", "message": "Valid admin token required"}), 401
    return decorated

# Homepage
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>CrawlHub Analytics - Web Crawling Platform</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #00d4ff; }
        .api-section { background: #16213e; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .endpoint { background: #0f3460; padding: 10px; margin: 10px 0; border-radius: 4px; }
        .method { color: #00ff88; font-weight: bold; }
        .path { color: #ff6b6b; }
        code { background: #0a0a15; padding: 2px 6px; border-radius: 3px; }
        .warning { color: #ffa500; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🕷️ CrawlHub Analytics Platform</h1>
        <p>Enterprise web crawling and analytics service. Our crawlers aggregate data from across the web.</p>
        
        <div class="api-section">
            <h2>API Documentation</h2>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/status</span>
                <p>Check system status and crawler health.</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/crawl/start</span>
                <p>Initiate a web crawl. Redirects to secure processing endpoint.</p>
                <p class="warning">⚠️ Requires Authorization header</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/admin/dashboard</span>
                <p>Admin dashboard with system statistics and configuration.</p>
                <p class="warning">⚠️ Requires valid admin token</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/logs/requests</span>
                <p>View recent request logs (debug endpoint).</p>
            </div>
        </div>
        
        <div class="api-section">
            <h2>Authentication</h2>
            <p>API endpoints require Bearer token authentication:</p>
            <code>Authorization: Bearer &lt;your_token&gt;</code>
        </div>
        
        <div class="api-section">
            <h2>Recent Crawl Jobs</h2>
            <p>No active crawl jobs. Use <code>/api/crawl/start</code> to begin.</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/api/status')
def status():
    return jsonify({
        "status": "operational",
        "service": "CrawlHub Analytics",
        "version": "2.11.1",
        "crawlers_active": 3,
        "message": "All systems nominal"
    })

# The vulnerable redirect endpoint
# This simulates the Scrapy redirect vulnerability where Authorization headers
# are not properly stripped during redirects
@app.route('/api/crawl/start')
def crawl_start():
    """
    Vulnerable endpoint that redirects without properly handling the Authorization header.
    In a real scenario, this would redirect from HTTPS to HTTP, leaking credentials.
    Here we simulate by logging the auth header when redirecting to an "external" endpoint.
    """
    auth_header = request.headers.get('Authorization', '')
    
    # If there's an auth header, log it (simulating credential leak on redirect)
    if auth_header:
        # This simulates the vulnerability - credentials leak during redirect
        # In the real CVE, this happens when scheme changes from https to http
        log_leaked_credential(auth_header, '/api/crawl/start', 'redirect_to_processor')
    
    # Redirect to the processor endpoint
    # The bug is that we're not stripping the Authorization header
    return redirect('/api/crawl/processor', code=302)

@app.route('/api/crawl/processor')
def crawl_processor():
    """
    The endpoint that receives the redirected request.
    In a vulnerable scenario, this endpoint on HTTP would receive the auth credentials.
    """
    auth_header = request.headers.get('Authorization', '')
    
    if auth_header:
        # Log the leaked credential again at the destination
        log_leaked_credential(auth_header, '/api/crawl/processor', 'redirect_destination')
        return jsonify({
            "status": "processing",
            "message": "Crawl job initiated",
            "job_id": "crawl_" + hashlib.md5(auth_header.encode()).hexdigest()[:8],
            "warning": "Debug mode active - credentials may be logged"
        })
    
    return jsonify({
        "status": "error",
        "message": "Authorization required to start crawl jobs"
    }), 401

@app.route('/api/logs/requests')
def view_logs():
    """
    Debug endpoint that shows leaked credentials from the redirect vulnerability.
    This is the key to exploitation - attackers can see leaked auth tokens here.
    """
    # Read from file to include all leaked credentials
    all_leaked = []
    try:
        with open(LEAKED_CREDENTIALS_FILE, 'r') as f:
            for line in f:
                try:
                    all_leaked.append(json.loads(line.strip()))
                except:
                    pass
    except FileNotFoundError:
        pass
    
    # Also include in-memory credentials
    for cred in leaked_credentials:
        if cred not in all_leaked:
            all_leaked.append(cred)
    
    return jsonify({
        "debug_mode": True,
        "warning": "This endpoint exposes request logs - disable in production!",
        "recent_requests": all_leaked[-20:] if all_leaked else [],
        "total_logged": len(all_leaked)
    })

@app.route('/api/admin/dashboard')
@require_auth
def admin_dashboard():
    """
    Protected admin endpoint that returns the flag when properly authenticated.
    """
    return jsonify({
        "status": "success",
        "admin_panel": True,
        "system_config": {
            "secret_key": FLAG,
            "crawl_rate_limit": 100,
            "max_concurrent_jobs": 10
        },
        "message": "Welcome, administrator!"
    })

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"}), 200

# Simulate internal crawler making authenticated requests
# This creates the "bait" - showing that the system uses auth tokens
@app.route('/internal/trigger-crawl')
def trigger_internal_crawl():
    """
    Internal endpoint that demonstrates how the system's crawlers work.
    This endpoint makes an authenticated request that gets redirected,
    causing credentials to leak.
    """
    # Simulate internal crawler making a request with credentials
    # In a real scenario, this would be the Scrapy spider following a redirect
    import urllib.request
    
    # Log what would happen
    log_leaked_credential(
        ADMIN_TOKEN,
        '/api/crawl/start',
        'internal_crawler_simulation'
    )
    
    return jsonify({
        "message": "Internal crawl triggered",
        "note": "The crawler followed a redirect and credentials were exposed",
        "check": "/api/logs/requests to see the leaked credentials"
    })

if __name__ == '__main__':
    # Initialize the leaked credentials file with an initial "leaked" credential
    # This simulates the crawler having already run and leaked credentials
    with open(LEAKED_CREDENTIALS_FILE, 'w') as f:
        initial_leak = {
            "authorization": ADMIN_TOKEN,
            "endpoint": "/api/crawl/start",
            "source": "internal_crawler_startup",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        f.write(json.dumps(initial_leak) + '\n')
    
    # Start the background crawler simulation
    crawler_thread = threading.Thread(target=simulate_internal_crawler, daemon=True)
    crawler_thread.start()
    
    app.run(host='0.0.0.0', port=8080, debug=False)
