# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import time
import hashlib

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

# In-memory store for SSO configurations
sso_configs = {}

# Default provider entries
default_providers = [
    {"id": "dcl-main", "name": "Decentraland", "url": "https://id.decentraland.org", "status": "active"},
    {"id": "dcl-staging", "name": "Decentraland Staging", "url": "https://id.decentraland.zone", "status": "active"},
]

def get_flag():
    try:
        with open('flag.txt', 'r') as f:
            return f.read().strip()
    except:
        return "FLAG{not_set}"


def evaluate_page(html_content):
    """Use PhantomJS to evaluate an HTML page and detect JavaScript execution."""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://{0}:{1}/{2}'.format(
        os.environ.get('APP_HOST', 'localhost'),
        os.environ.get('APP_PORT', '5000'),
        fn
    )
    result = ''
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception as e:
        logging.error("Evaluation error: %s", str(e))
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result


@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Decentraland SSO Integration Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d0d1a; color: #e0e0e0; min-height: 100vh; }
        .navbar { background: #16162b; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #2a2a4a; }
        .navbar .brand { font-size: 20px; font-weight: 700; color: #ff2d55; }
        .navbar .brand span { color: #7b7b9e; font-weight: 400; font-size: 14px; margin-left: 8px; }
        .navbar nav a { color: #7b7b9e; text-decoration: none; margin-left: 24px; font-size: 14px; }
        .navbar nav a:hover { color: #e0e0e0; }
        .container { max-width: 960px; margin: 0 auto; padding: 40px 24px; }
        h1 { font-size: 28px; margin-bottom: 8px; }
        .subtitle { color: #7b7b9e; margin-bottom: 32px; }
        .card { background: #16162b; border: 1px solid #2a2a4a; border-radius: 8px; padding: 24px; margin-bottom: 24px; }
        .card h2 { font-size: 18px; margin-bottom: 16px; color: #ff2d55; }
        .provider-list { list-style: none; }
        .provider-list li { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #2a2a4a; }
        .provider-list li:last-child { border-bottom: none; }
        .provider-name { font-weight: 600; }
        .provider-url { color: #7b7b9e; font-size: 13px; font-family: monospace; }
        .badge { font-size: 11px; padding: 3px 8px; border-radius: 12px; background: #1a3a2a; color: #4ade80; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 13px; color: #7b7b9e; margin-bottom: 4px; }
        .form-group input { width: 100%; padding: 10px 12px; background: #0d0d1a; border: 1px solid #2a2a4a; border-radius: 6px; color: #e0e0e0; font-size: 14px; }
        .form-group input:focus { outline: none; border-color: #ff2d55; }
        .btn { padding: 10px 20px; background: #ff2d55; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #e0264c; }
        .btn-secondary { background: #2a2a4a; }
        .btn-secondary:hover { background: #3a3a5a; }
        .docs-link { display: inline-block; margin-top: 16px; color: #ff2d55; text-decoration: none; font-size: 13px; }
        .docs-link:hover { text-decoration: underline; }
        footer { text-align: center; padding: 24px; color: #3a3a5a; font-size: 12px; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="brand">DCL SSO Portal <span>v0.0.9</span></div>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/providers">Providers</a>
            <a href="/api/providers">API</a>
            <a href="/docs">Docs</a>
        </nav>
    </div>
    <div class="container">
        <h1>Identity Provider Management</h1>
        <p class="subtitle">Configure and test Single Sign-On provider integrations</p>
        <div class="card">
            <h2>Registered Providers</h2>
            <ul class="provider-list">
                <li>
                    <div>
                        <div class="provider-name">Decentraland</div>
                        <div class="provider-url">https://id.decentraland.org</div>
                    </div>
                    <span class="badge">Active</span>
                </li>
                <li>
                    <div>
                        <div class="provider-name">Decentraland Staging</div>
                        <div class="provider-url">https://id.decentraland.zone</div>
                    </div>
                    <span class="badge">Active</span>
                </li>
            </ul>
        </div>
        <div class="card">
            <h2>Quick Actions</h2>
            <a href="/providers/test" class="btn" style="text-decoration:none; margin-right: 12px;">Test Provider</a>
            <a href="/providers" class="btn btn-secondary" style="text-decoration:none;">Manage Providers</a>
            <a href="/docs" class="docs-link">View integration documentation &rarr;</a>
        </div>
    </div>
    <footer>&copy; 2023 Decentraland Foundation. SSO Integration Portal.</footer>
</body>
</html>'''


@app.route('/providers')
def providers_page():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Providers - DCL SSO Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d0d1a; color: #e0e0e0; }
        .navbar { background: #16162b; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #2a2a4a; }
        .navbar .brand { font-size: 20px; font-weight: 700; color: #ff2d55; }
        .navbar .brand span { color: #7b7b9e; font-weight: 400; font-size: 14px; margin-left: 8px; }
        .navbar nav a { color: #7b7b9e; text-decoration: none; margin-left: 24px; font-size: 14px; }
        .navbar nav a:hover { color: #e0e0e0; }
        .container { max-width: 960px; margin: 0 auto; padding: 40px 24px; }
        h1 { font-size: 24px; margin-bottom: 24px; }
        .card { background: #16162b; border: 1px solid #2a2a4a; border-radius: 8px; padding: 24px; margin-bottom: 24px; }
        .card h2 { font-size: 18px; margin-bottom: 16px; color: #ff2d55; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #2a2a4a; }
        th { color: #7b7b9e; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
        td { font-size: 14px; }
        .mono { font-family: monospace; color: #7b7b9e; font-size: 13px; }
        .badge { font-size: 11px; padding: 3px 8px; border-radius: 12px; background: #1a3a2a; color: #4ade80; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 13px; color: #7b7b9e; margin-bottom: 4px; }
        .form-group input { width: 100%; padding: 10px 12px; background: #0d0d1a; border: 1px solid #2a2a4a; border-radius: 6px; color: #e0e0e0; font-size: 14px; }
        .form-group input:focus { outline: none; border-color: #ff2d55; }
        .btn { padding: 10px 20px; background: #ff2d55; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #e0264c; }
        footer { text-align: center; padding: 24px; color: #3a3a5a; font-size: 12px; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="brand">DCL SSO Portal <span>v0.0.9</span></div>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/providers">Providers</a>
            <a href="/api/providers">API</a>
            <a href="/docs">Docs</a>
        </nav>
    </div>
    <div class="container">
        <h1>SSO Providers</h1>
        <div class="card">
            <h2>Active Providers</h2>
            <table>
                <thead>
                    <tr><th>Name</th><th>Provider URL</th><th>ID</th><th>Status</th></tr>
                </thead>
                <tbody>
                    <tr><td>Decentraland</td><td class="mono">https://id.decentraland.org</td><td class="mono">dcl-main</td><td><span class="badge">Active</span></td></tr>
                    <tr><td>Decentraland Staging</td><td class="mono">https://id.decentraland.zone</td><td class="mono">dcl-staging</td><td><span class="badge">Active</span></td></tr>
                </tbody>
            </table>
        </div>
        <div class="card">
            <h2>Test Provider Integration</h2>
            <p style="color:#7b7b9e; margin-bottom:16px; font-size: 14px;">
                Initialize the SSO client with a provider URL to verify the integration works correctly.
                The system will create an iframe pointed at the provider for authentication handshake testing.
            </p>
            <form method="GET" action="/providers/test">
                <div class="form-group">
                    <label for="src">Provider URL</label>
                    <input type="text" id="src" name="src" placeholder="https://id.decentraland.org" />
                </div>
                <button type="submit" class="btn">Test Connection</button>
            </form>
        </div>
    </div>
    <footer>&copy; 2023 Decentraland Foundation. SSO Integration Portal.</footer>
</body>
</html>'''


@app.route('/providers/test')
def test_provider():
    src = request.args.get('src', '')

    if not src:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Provider - DCL SSO Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d0d1a; color: #e0e0e0; }
        .navbar { background: #16162b; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #2a2a4a; }
        .navbar .brand { font-size: 20px; font-weight: 700; color: #ff2d55; }
        .navbar .brand span { color: #7b7b9e; font-weight: 400; font-size: 14px; margin-left: 8px; }
        .navbar nav a { color: #7b7b9e; text-decoration: none; margin-left: 24px; font-size: 14px; }
        .container { max-width: 960px; margin: 0 auto; padding: 40px 24px; }
        .card { background: #16162b; border: 1px solid #2a2a4a; border-radius: 8px; padding: 24px; }
        .card h2 { font-size: 18px; margin-bottom: 16px; color: #ff2d55; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 13px; color: #7b7b9e; margin-bottom: 4px; }
        .form-group input { width: 100%; padding: 10px 12px; background: #0d0d1a; border: 1px solid #2a2a4a; border-radius: 6px; color: #e0e0e0; font-size: 14px; }
        .form-group input:focus { outline: none; border-color: #ff2d55; }
        .btn { padding: 10px 20px; background: #ff2d55; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }
        footer { text-align: center; padding: 24px; color: #3a3a5a; font-size: 12px; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="brand">DCL SSO Portal <span>v0.0.9</span></div>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/providers">Providers</a>
            <a href="/api/providers">API</a>
            <a href="/docs">Docs</a>
        </nav>
    </div>
    <div class="container">
        <div class="card">
            <h2>Test SSO Provider</h2>
            <p style="color:#7b7b9e; margin-bottom:16px; font-size: 14px;">
                Enter the provider URL to initialize the SSO iframe handshake.
            </p>
            <form method="GET" action="/providers/test">
                <div class="form-group">
                    <label for="src">Provider URL</label>
                    <input type="text" id="src" name="src" placeholder="https://id.decentraland.org" />
                </div>
                <button type="submit" class="btn">Initialize SSO</button>
            </form>
        </div>
    </div>
    <footer>&copy; 2023 Decentraland Foundation. SSO Integration Portal.</footer>
</body>
</html>'''

    # Build the SSO test page with iframe - mirrors SingleSignOn.init(src)
    # The src is used directly as iframe src without URL scheme validation
    page_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SSO Test - DCL SSO Portal</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d0d1a; color: #e0e0e0; }}
    </style>
    <script>
        var _src = null;
        var IFRAME_ID = "dcl-sso-iframe";

        function init(src) {{
            if (_src) {{
                throw new Error("Already initialized");
            }}
            var iframe = document.createElement("iframe");
            iframe.id = IFRAME_ID;
            iframe.src = src;
            iframe.style.width = "0px";
            iframe.style.height = "0px";
            iframe.style.border = "none";
            iframe.style.position = "absolute";
            iframe.style.top = "-9999px";
            document.body.appendChild(iframe);
            _src = src;
        }}

        window.onload = function() {{
            try {{
                init("{src}");
            }} catch(e) {{
                // initialization error
            }}
        }};
    </script>
</head>
<body>
    <div style="padding: 40px; text-align: center;">
        <h2 style="color: #ff2d55;">SSO Provider Test</h2>
        <p style="color: #7b7b9e; margin-top: 12px;">Initializing SSO handshake with provider...</p>
    </div>
</body>
</html>'''.format(src=src.replace('"', '&quot;').replace('\\', '\\\\'))

    # Evaluate the page server-side to test the SSO integration
    result = evaluate_page(page_html)

    if result == 'XSS':
        flag = get_flag()
        status_html = '<div style="background:#1a1a2e; border:1px solid #ff2d55; border-radius:8px; padding:20px; margin-top:20px;"><p style="color:#ff2d55; font-weight:700;">Security Alert</p><p style="color:#e0e0e0; margin-top:8px;">JavaScript execution detected from provider URL. Session token captured:</p><p style="color:#4ade80; font-family:monospace; margin-top:8px; word-break:break-all;">{0}</p></div>'.format(flag)
    elif result:
        status_html = '<div style="background:#1a1a2e; border:1px solid #e0a030; border-radius:8px; padding:20px; margin-top:20px;"><p style="color:#e0a030; font-weight:700;">Unexpected Response</p><p style="color:#7b7b9e; margin-top:8px;">Provider returned: {0}</p></div>'.format(cgi.escape(result))
    else:
        status_html = '<div style="background:#1a1a2e; border:1px solid #2a2a4a; border-radius:8px; padding:20px; margin-top:20px;"><p style="color:#4ade80; font-weight:700;">Connection OK</p><p style="color:#7b7b9e; margin-top:8px;">No script execution detected. Provider iframe loaded successfully.</p></div>'

    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Result - DCL SSO Portal</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d0d1a; color: #e0e0e0; }}
        .navbar {{ background: #16162b; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #2a2a4a; }}
        .navbar .brand {{ font-size: 20px; font-weight: 700; color: #ff2d55; }}
        .navbar .brand span {{ color: #7b7b9e; font-weight: 400; font-size: 14px; margin-left: 8px; }}
        .navbar nav a {{ color: #7b7b9e; text-decoration: none; margin-left: 24px; font-size: 14px; }}
        .container {{ max-width: 960px; margin: 0 auto; padding: 40px 24px; }}
        .card {{ background: #16162b; border: 1px solid #2a2a4a; border-radius: 8px; padding: 24px; }}
        .card h2 {{ font-size: 18px; margin-bottom: 16px; color: #ff2d55; }}
        .mono {{ font-family: monospace; color: #7b7b9e; font-size: 13px; }}
        .btn {{ padding: 10px 20px; background: #ff2d55; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; text-decoration: none; display: inline-block; margin-top: 16px; }}
        footer {{ text-align: center; padding: 24px; color: #3a3a5a; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="navbar">
        <div class="brand">DCL SSO Portal <span>v0.0.9</span></div>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/providers">Providers</a>
            <a href="/api/providers">API</a>
            <a href="/docs">Docs</a>
        </nav>
    </div>
    <div class="container">
        <div class="card">
            <h2>SSO Integration Test Result</h2>
            <p style="color:#7b7b9e; font-size: 14px;">Provider URL: <span class="mono">{src}</span></p>
            {status}
            <a href="/providers/test" class="btn">Test Another</a>
        </div>
    </div>
    <footer>&copy; 2023 Decentraland Foundation. SSO Integration Portal.</footer>
</body>
</html>'''.format(src=cgi.escape(src), status=status_html)


@app.route('/api/providers')
def api_providers():
    return jsonify({
        "providers": default_providers,
        "total": len(default_providers)
    })


@app.route('/api/providers/<provider_id>')
def api_provider_detail(provider_id):
    for p in default_providers:
        if p['id'] == provider_id:
            return jsonify(p)
    return jsonify({"error": "Provider not found"}), 404


@app.route('/api/health')
def api_health():
    return jsonify({"status": "healthy", "version": "0.0.9", "service": "sso-portal"})


@app.route('/docs')
def docs_page():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Documentation - DCL SSO Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d0d1a; color: #e0e0e0; }
        .navbar { background: #16162b; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #2a2a4a; }
        .navbar .brand { font-size: 20px; font-weight: 700; color: #ff2d55; }
        .navbar .brand span { color: #7b7b9e; font-weight: 400; font-size: 14px; margin-left: 8px; }
        .navbar nav a { color: #7b7b9e; text-decoration: none; margin-left: 24px; font-size: 14px; }
        .navbar nav a:hover { color: #e0e0e0; }
        .container { max-width: 960px; margin: 0 auto; padding: 40px 24px; }
        h1 { font-size: 24px; margin-bottom: 24px; }
        .card { background: #16162b; border: 1px solid #2a2a4a; border-radius: 8px; padding: 24px; margin-bottom: 24px; }
        .card h2 { font-size: 18px; margin-bottom: 16px; color: #ff2d55; }
        pre { background: #0d0d1a; border: 1px solid #2a2a4a; border-radius: 6px; padding: 16px; overflow-x: auto; font-size: 13px; color: #a0a0c0; margin: 12px 0; }
        code { font-family: 'SF Mono', Monaco, 'Courier New', monospace; }
        p { line-height: 1.6; color: #7b7b9e; margin-bottom: 12px; font-size: 14px; }
        h3 { font-size: 15px; margin: 16px 0 8px; color: #e0e0e0; }
        footer { text-align: center; padding: 24px; color: #3a3a5a; font-size: 12px; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="brand">DCL SSO Portal <span>v0.0.9</span></div>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/providers">Providers</a>
            <a href="/api/providers">API</a>
            <a href="/docs">Docs</a>
        </nav>
    </div>
    <div class="container">
        <h1>Integration Documentation</h1>
        <div class="card">
            <h2>@dcl/single-sign-on-client</h2>
            <p>The SSO client library provides seamless authentication integration with Decentraland identity providers.</p>
            <h3>Installation</h3>
            <pre><code>npm install @dcl/single-sign-on-client</code></pre>
            <h3>Usage</h3>
            <pre><code>import { SingleSignOn } from '@dcl/single-sign-on-client'

// Initialize with your provider URL
SingleSignOn.init('https://id.decentraland.org')

// Store identity
await SingleSignOn.storeIdentity(address, identity)

// Retrieve identity
const identity = await SingleSignOn.getIdentity(address)</code></pre>
            <h3>init(src: string)</h3>
            <p>Initializes the SSO client by creating a hidden iframe pointed at the provider URL.
               The iframe is used for cross-origin communication with the identity provider via postMessage.</p>
            <pre><code>function init(src: string) {
    if (_src) {
        throw new Error("Already initialized");
    }
    const iframe = document.createElement("iframe");
    iframe.id = IFRAME_ID;
    iframe.src = src;
    // ... styling ...
    document.body.appendChild(iframe);
    _src = src;
}</code></pre>
        </div>
        <div class="card">
            <h2>REST API</h2>
            <h3>GET /api/providers</h3>
            <p>Returns a list of all configured SSO providers.</p>
            <h3>GET /api/providers/:id</h3>
            <p>Returns details for a specific provider.</p>
            <h3>GET /api/health</h3>
            <p>Health check endpoint.</p>
        </div>
        <div class="card">
            <h2>Testing</h2>
            <p>Use the <a href="/providers/test" style="color:#ff2d55;">Provider Test</a> page to verify your SSO integration.
               Enter a provider URL to test the iframe initialization flow.</p>
        </div>
    </div>
    <footer>&copy; 2023 Decentraland Foundation. SSO Integration Portal.</footer>
</body>
</html>'''


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
