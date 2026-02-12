# encoding=utf8

from flask import Flask, request, make_response, jsonify
import subprocess
import os
import cgi
import urllib
import sys
import hashlib
import time

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

verification_token = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# In-memory store for SSO provider configurations
sso_providers = {}

SSO_PROVIDER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Decentraland SSO - Provider Configuration</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d0d2b; color: #e0e0e0; min-height: 100vh; }}
        .header {{ background: linear-gradient(135deg, #ff2d55, #7928ca); padding: 20px 40px; display: flex; align-items: center; justify-content: space-between; }}
        .header h1 {{ font-size: 1.4em; color: white; }}
        .header .nav {{ display: flex; gap: 20px; }}
        .header .nav a {{ color: rgba(255,255,255,0.8); text-decoration: none; font-size: 0.9em; }}
        .header .nav a:hover {{ color: white; }}
        .container {{ max-width: 900px; margin: 40px auto; padding: 0 20px; }}
        .card {{ background: #1a1a3e; border-radius: 12px; padding: 30px; margin-bottom: 20px; border: 1px solid #2a2a5e; }}
        .card h2 {{ margin-bottom: 15px; color: #ff2d55; font-size: 1.2em; }}
        .card p {{ color: #999; margin-bottom: 20px; line-height: 1.6; }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; margin-bottom: 5px; color: #ccc; font-size: 0.9em; }}
        .form-group input {{ width: 100%; padding: 12px; background: #0d0d2b; border: 1px solid #3a3a6e; border-radius: 8px; color: #e0e0e0; font-size: 0.95em; }}
        .form-group input:focus {{ outline: none; border-color: #ff2d55; }}
        .btn {{ background: linear-gradient(135deg, #ff2d55, #7928ca); color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 0.95em; }}
        .btn:hover {{ opacity: 0.9; }}
        .status {{ padding: 15px; border-radius: 8px; margin-top: 15px; }}
        .status.success {{ background: rgba(0,200,83,0.1); border: 1px solid #00c853; color: #00c853; }}
        .status.error {{ background: rgba(255,45,85,0.1); border: 1px solid #ff2d55; color: #ff2d55; }}
        .provider-list {{ list-style: none; }}
        .provider-list li {{ padding: 12px; background: #0d0d2b; border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #2a2a5e; }}
        .provider-list li .name {{ color: #e0e0e0; }}
        .provider-list li .url {{ color: #666; font-size: 0.85em; }}
        .api-docs {{ font-family: monospace; background: #0d0d2b; padding: 15px; border-radius: 8px; font-size: 0.85em; white-space: pre-wrap; border: 1px solid #2a2a5e; }}
        .footer {{ text-align: center; padding: 30px; color: #555; font-size: 0.8em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Decentraland SSO</h1>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/providers">Providers</a>
            <a href="/api/docs">API Docs</a>
            <a href="/sso/test">Test SSO</a>
        </div>
    </div>
    <div class="container">
        {content}
    </div>
    <div class="footer">
        &copy; 2023 Decentraland SSO Service &middot; v0.0.9
    </div>
</body>
</html>
"""

SSO_INIT_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SSO Provider Test</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d0d2b; color: #e0e0e0; margin: 0; }}
        .sso-container {{ padding: 20px; }}
        .sso-status {{ background: #1a1a3e; padding: 15px; border-radius: 8px; margin-top: 10px; border: 1px solid #2a2a5e; }}
        h3 {{ color: #ff2d55; }}
    </style>
</head>
<body>
    <div class="sso-container">
        <h3>SSO Provider Initialization</h3>
        <div class="sso-status" id="status">
            <p>Provider: {display_url}</p>
            <p>Status: Initializing...</p>
        </div>
    </div>
    <iframe id="dcl-iframe" style="width:0;height:0;border:none;position:absolute;"></iframe>
    <script>
        // @dcl/single-sign-on-client v0.0.9
        // SingleSignOn.init() implementation
        var IFRAME_ID = "dcl-iframe";
        var _src = null;

        function init(src) {{
            if (_src) {{
                throw new Error("Already initialized");
            }}
            var iframe = document.getElementById(IFRAME_ID);
            if (!iframe) {{
                iframe = document.createElement("iframe");
                iframe.id = IFRAME_ID;
                iframe.style.width = "0";
                iframe.style.height = "0";
                iframe.style.border = "none";
                iframe.style.position = "absolute";
                document.body.appendChild(iframe);
            }}
            // Set the iframe source to the provider URL
            iframe.src = src;
            _src = src;
        }}

        // Initialize with the configured provider URL
        var providerSrc = decodeURIComponent("{encoded_url}");
        init(providerSrc);
    </script>
</body>
</html>"""


def check_xss_execution(page_content):
    """Check if the page content triggers XSS by loading it in PhantomJS"""
    proc = subprocess.Popen(
        ["timeout", "10", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result


@app.route('/')
def index():
    content = """
        <div class="card">
            <h2>SSO Provider Dashboard</h2>
            <p>Welcome to the Decentraland Single Sign-On service. Configure and manage your SSO identity providers from this dashboard.</p>
        </div>
        <div class="card">
            <h2>Quick Actions</h2>
            <p>
                <a href="/providers" style="color: #ff2d55;">Manage Providers</a> &middot;
                <a href="/sso/test" style="color: #ff2d55;">Test SSO Integration</a> &middot;
                <a href="/api/docs" style="color: #ff2d55;">API Documentation</a>
            </p>
        </div>
        <div class="card">
            <h2>System Status</h2>
            <p>Service: <span style="color: #00c853;">Operational</span><br>
            Version: 0.0.9<br>
            Active Providers: {count}</p>
        </div>
    """.format(count=len(sso_providers))
    return SSO_PROVIDER_TEMPLATE.format(content=content)


@app.route('/providers')
def providers():
    provider_items = ""
    for pid, p in sso_providers.items():
        provider_items += '<li><span class="name">{name}</span><span class="url">{url}</span></li>'.format(
            name=cgi.escape(p.get('name', 'Unknown')),
            url=cgi.escape(p.get('src', ''))
        )
    if not provider_items:
        provider_items = '<li><span class="name" style="color: #666;">No providers configured yet</span></li>'

    content = """
        <div class="card">
            <h2>Identity Providers</h2>
            <p>Manage your configured SSO identity providers.</p>
            <ul class="provider-list">
                {items}
            </ul>
        </div>
        <div class="card">
            <h2>Add Provider</h2>
            <p>Register a new SSO identity provider by specifying its endpoint URL.</p>
            <form action="/api/providers" method="POST">
                <div class="form-group">
                    <label>Provider Name</label>
                    <input type="text" name="name" placeholder="e.g., My SSO Provider" required>
                </div>
                <div class="form-group">
                    <label>Provider URL</label>
                    <input type="text" name="src" placeholder="https://sso.example.com" required>
                </div>
                <button type="submit" class="btn">Register Provider</button>
            </form>
        </div>
    """.format(items=provider_items)
    return SSO_PROVIDER_TEMPLATE.format(content=content)


@app.route('/api/providers', methods=['POST'])
def register_provider():
    if request.is_json and request.json:
        name = request.json.get('name', '')
        src = request.json.get('src', '')
    else:
        name = request.form.get('name', '')
        src = request.form.get('src', '')

    if not name or not src:
        content = '<div class="card"><div class="status error">Provider name and URL are required.</div></div>'
        return SSO_PROVIDER_TEMPLATE.format(content=content), 400

    pid = hashlib.md5(src.encode('utf-8')).hexdigest()[:12]
    sso_providers[pid] = {'name': name, 'src': src, 'created': int(time.time())}

    content = """
        <div class="card">
            <h2>Provider Registered</h2>
            <div class="status success">
                Provider "{name}" registered successfully.<br>
                Provider ID: {pid}<br>
                Test it: <a href="/sso/init?src={url}" style="color: #00c853;">Initialize SSO</a>
            </div>
        </div>
    """.format(name=cgi.escape(name), pid=pid, url=cgi.escape(src))
    return SSO_PROVIDER_TEMPLATE.format(content=content)


@app.route('/api/providers/<pid>', methods=['GET'])
def get_provider(pid):
    provider = sso_providers.get(pid)
    if not provider:
        return jsonify({'error': 'Provider not found'}), 404
    return jsonify(provider)


@app.route('/sso/test')
def sso_test():
    content = """
        <div class="card">
            <h2>Test SSO Integration</h2>
            <p>Test the SingleSignOn.init() method by providing a provider URL below.
            This will create an iframe pointed at the specified SSO provider endpoint,
            simulating how client applications integrate with the SSO service.</p>
            <form action="/sso/init" method="GET">
                <div class="form-group">
                    <label>SSO Provider URL</label>
                    <input type="text" name="src" placeholder="Enter provider URL to initialize..." required>
                </div>
                <button type="submit" class="btn">Initialize SSO</button>
            </form>
        </div>
        <div class="card">
            <h2>Usage Example</h2>
            <div class="api-docs">import { SingleSignOn } from '@dcl/single-sign-on-client'

// Initialize the SSO client with your provider URL
SingleSignOn.init('https://your-sso-provider.example.com')

// The library creates a hidden iframe pointed at the provider
// to establish a cross-origin authentication session</div>
        </div>
    """
    return SSO_PROVIDER_TEMPLATE.format(content=content)


@app.route('/sso/init')
def sso_init():
    """Initialize SSO with the given provider URL."""
    src = request.args.get('src', '')

    if not src:
        content = '<div class="card"><div class="status error">No provider URL specified. Use ?src=URL to initialize.</div></div>'
        return SSO_PROVIDER_TEMPLATE.format(content=content), 400

    # Generate the SSO initialization page
    encoded_url = urllib.quote(src.encode('utf-8'), safe='')
    page_content = SSO_INIT_PAGE_TEMPLATE.format(
        display_url=cgi.escape(src),
        encoded_url=encoded_url
    )

    # Verify the provider handshake
    result = check_xss_execution(page_content)

    if result == 'XSS':
        content = """
            <div class="card">
                <h2>SSO Initialization Result</h2>
                <div class="status success">
                    Security verification token: {token}
                </div>
            </div>
        """.format(token=verification_token)
    elif result:
        content = """
            <div class="card">
                <h2>SSO Initialization Result</h2>
                <div class="status error">
                    Unexpected provider response: {result}
                </div>
            </div>
        """.format(result=cgi.escape(str(result)))
    else:
        content = """
            <div class="card">
                <h2>SSO Initialization Result</h2>
                <div class="status">
                    <p>Provider URL: {url}</p>
                    <p>Status: Provider loaded. No authentication response received.</p>
                </div>
            </div>
        """.format(url=cgi.escape(src))

    response = make_response(SSO_PROVIDER_TEMPLATE.format(content=content))
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/api/docs')
def api_docs():
    content = """
        <div class="card">
            <h2>API Documentation</h2>
            <p>The SSO service exposes the following endpoints:</p>
            <div class="api-docs">
GET  /                    - Dashboard
GET  /providers           - List configured providers
POST /api/providers       - Register a new provider (name, src)
GET  /api/providers/:id   - Get provider details
GET  /sso/test            - SSO testing interface
GET  /sso/init?src=URL    - Initialize SSO with provider URL
GET  /api/docs            - This documentation
GET  /health              - Service health check
            </div>
        </div>
        <div class="card">
            <h2>Client Library</h2>
            <div class="api-docs">
// @dcl/single-sign-on-client v0.0.9
//
// Initialize the SSO client:
//   SingleSignOn.init(providerUrl)
//
// The init function creates a hidden iframe pointed at the
// SSO provider to establish a cross-origin auth session.
//
// Parameters:
//   providerUrl (string) - The URL of the SSO provider
//
// Note: Ensure provider URLs use HTTPS in production.
            </div>
        </div>
    """
    return SSO_PROVIDER_TEMPLATE.format(content=content)


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'dcl-sso', 'version': '0.0.9'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
