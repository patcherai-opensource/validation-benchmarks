# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, jsonify, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import hashlib
import time

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flag_data = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# In-memory session store for identity bridge
_sessions = {}
_providers = {}

ALLOWED_ORIGINS = [
    "https://id.decentraland.org",
    "https://auth.decentraland.zone",
]

# ===== Identity Bridge Platform =====

@app.route('/')
def index():
    return LANDING_PAGE

@app.route('/health')
def health():
    return "ok", 200

@app.route('/docs')
def docs():
    return DOCS_PAGE

@app.route('/connect/status')
def connect_status():
    session_id = request.args.get('session', '')
    if not session_id or session_id not in _sessions:
        return jsonify({"status": "unknown", "message": "No active session found"}), 404
    return jsonify({"status": "active", "session": session_id})

@app.route('/connect/provider', methods=['GET'])
def connect_provider():
    """
    Configures an identity provider connection by loading the provider URL
    in a sandboxed frame context. The provider URL is rendered in an iframe
    for cross-origin identity negotiation.
    """
    provider_url = request.args.get('provider_url', '')
    callback = request.args.get('callback', '')
    session_id = hashlib.md5(os.urandom(8)).hexdigest()

    if not provider_url:
        return PROVIDER_PAGE.format(
            provider_frame="",
            status_msg='<div class="status-info">Provide a provider URL to establish identity connection.</div>',
            session_id=session_id
        )

    # Generate the page with provider iframe for identity negotiation
    # Escape double quotes to prevent breaking out of the src attribute value
    safe_url = provider_url.replace('"', '%22')
    frame_html = 'src="{0}"'.format(safe_url)
    page_content = PROVIDER_PAGE.format(
        provider_frame=frame_html,
        status_msg='',
        session_id=session_id
    )

    # Evaluate the provider frame in headless context for SSO handshake verification
    result = evaluate_provider(page_content, provider_url, session_id)

    if result:
        status = '<div class="status-success">Provider handshake verified. Session token: {0}</div>'.format(result)
    else:
        status = '<div class="status-info">Provider frame loaded. Awaiting handshake response.</div>'

    response = make_response(PROVIDER_PAGE.format(
        provider_frame=frame_html,
        status_msg=status,
        session_id=session_id
    ))
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


def evaluate_provider(page_content, provider_url, session_id):
    """
    Evaluates provider page in headless browser context to verify
    the SSO handshake and identity frame communication.
    """
    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "check.js"],
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
    except Exception:
        result = ""
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass

    if result == 'XSS':
        _sessions[session_id] = {"provider": provider_url, "verified": True}
        return flag_data
    elif result:
        _sessions[session_id] = {"provider": provider_url, "verified": False}
        return None
    return None


@app.route('/connect/origins')
def connect_origins():
    """Returns the list of pre-approved identity provider origins."""
    return jsonify({"allowed_origins": ALLOWED_ORIGINS})


@app.route('/api/v1/identity', methods=['GET'])
def get_identity():
    """Retrieve stored identity for a given wallet address."""
    address = request.args.get('address', '')
    if not address or not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return jsonify({"error": "Invalid address format. Must be a valid Ethereum address."}), 400
    # Check in-memory store
    key = "identity-{}".format(address.lower())
    if key in _providers:
        return jsonify({"address": address, "identity": _providers[key]})
    return jsonify({"address": address, "identity": None}), 404


@app.route('/api/v1/identity', methods=['POST'])
def store_identity():
    """Store identity data for a wallet address."""
    data = request.get_json(silent=True)
    if not data or 'address' not in data:
        return jsonify({"error": "Missing required field: address"}), 400

    address = data.get('address', '')
    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return jsonify({"error": "Invalid address format"}), 400

    identity = data.get('identity', {})
    key = "identity-{}".format(address.lower())
    _providers[key] = identity
    return jsonify({"status": "stored", "address": address}), 201


@app.route('/api/v1/identity', methods=['DELETE'])
def clear_identity():
    """Clear stored identity for a wallet address."""
    address = request.args.get('address', '')
    if not address:
        return jsonify({"error": "Missing address parameter"}), 400

    key = "identity-{}".format(address.lower())
    if key in _providers:
        del _providers[key]
    return jsonify({"status": "cleared", "address": address})


# ===== HTML Templates =====

LANDING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Identity Bridge - Decentralized SSO Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; }
        .header { background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 20px; color: #f0f6fc; }
        .header nav a { color: #8b949e; text-decoration: none; margin-left: 24px; font-size: 14px; }
        .header nav a:hover { color: #c9d1d9; }
        .hero { text-align: center; padding: 80px 32px; }
        .hero h2 { font-size: 48px; color: #f0f6fc; margin-bottom: 16px; }
        .hero p { font-size: 20px; color: #8b949e; max-width: 600px; margin: 0 auto 32px; }
        .btn { display: inline-block; padding: 12px 24px; background: #238636; color: #fff; text-decoration: none; border-radius: 6px; font-size: 16px; }
        .btn:hover { background: #2ea043; }
        .features { display: flex; justify-content: center; gap: 32px; padding: 0 32px 80px; flex-wrap: wrap; }
        .feature { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 24px; max-width: 300px; }
        .feature h3 { color: #f0f6fc; margin-bottom: 8px; }
        .feature p { color: #8b949e; font-size: 14px; }
        .footer { text-align: center; padding: 32px; border-top: 1px solid #30363d; color: #484f58; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Identity Bridge</h1>
        <nav>
            <a href="/docs">Documentation</a>
            <a href="/connect/provider">Connect Provider</a>
            <a href="/api/v1/identity?address=0x0000000000000000000000000000000000000000">API</a>
        </nav>
    </div>
    <div class="hero">
        <h2>Decentralized Identity Bridge</h2>
        <p>Connect your identity provider for seamless cross-origin authentication. Supports iframe-based SSO handshake protocol.</p>
        <a href="/connect/provider" class="btn">Connect Identity Provider</a>
    </div>
    <div class="features">
        <div class="feature">
            <h3>Cross-Origin SSO</h3>
            <p>Securely negotiate identity across origins using our iframe bridge protocol.</p>
        </div>
        <div class="feature">
            <h3>Wallet Integration</h3>
            <p>Native support for Ethereum wallet addresses and cryptographic identity chains.</p>
        </div>
        <div class="feature">
            <h3>Provider Verification</h3>
            <p>Automated headless verification of identity provider handshake responses.</p>
        </div>
    </div>
    <div class="footer">
        Identity Bridge Platform v0.9.2 &mdash; Decentralized Authentication Infrastructure
    </div>
</body>
</html>
"""

DOCS_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation - Identity Bridge</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; }
        .header { background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 20px; color: #f0f6fc; }
        .header nav a { color: #8b949e; text-decoration: none; margin-left: 24px; font-size: 14px; }
        .content { max-width: 800px; margin: 40px auto; padding: 0 32px; }
        .content h2 { color: #f0f6fc; margin: 32px 0 16px; font-size: 24px; border-bottom: 1px solid #30363d; padding-bottom: 8px; }
        .content h3 { color: #f0f6fc; margin: 24px 0 12px; font-size: 18px; }
        .content p { color: #8b949e; margin-bottom: 16px; line-height: 1.6; }
        .content code { background: #161b22; padding: 2px 6px; border-radius: 3px; font-size: 14px; color: #c9d1d9; }
        pre { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px; overflow-x: auto; margin-bottom: 16px; }
        pre code { padding: 0; background: none; }
        .endpoint { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px; margin-bottom: 16px; }
        .method { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; margin-right: 8px; }
        .get { background: #1f6feb33; color: #58a6ff; }
        .post { background: #23863633; color: #3fb950; }
        .delete { background: #da363333; color: #f85149; }
        .footer { text-align: center; padding: 32px; border-top: 1px solid #30363d; color: #484f58; font-size: 12px; margin-top: 60px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Identity Bridge</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/docs">Documentation</a>
            <a href="/connect/provider">Connect Provider</a>
        </nav>
    </div>
    <div class="content">
        <h2>Identity Bridge Documentation</h2>
        <p>Identity Bridge provides a cross-origin SSO protocol using iframe-based identity negotiation.
        Identity providers are loaded in a sandboxed frame context where the handshake is verified server-side.</p>

        <h3>How It Works</h3>
        <p>The platform loads your identity provider URL in an iframe for cross-origin communication.
        The provider frame is evaluated in a headless browser context to verify the SSO handshake protocol.
        Upon successful verification, a session token is issued.</p>

        <h2>API Reference</h2>

        <div class="endpoint">
            <p><span class="method get">GET</span> <code>/connect/provider</code></p>
            <p>Initiates an identity provider connection. Loads the specified provider URL in an iframe context for handshake verification.</p>
            <p><strong>Parameters:</strong></p>
            <p><code>provider_url</code> - The URL of the identity provider to connect</p>
            <p><code>callback</code> - Optional callback URL for post-authentication redirect</p>
        </div>

        <div class="endpoint">
            <p><span class="method get">GET</span> <code>/connect/origins</code></p>
            <p>Returns the list of pre-approved identity provider origins.</p>
        </div>

        <div class="endpoint">
            <p><span class="method get">GET</span> <code>/connect/status</code></p>
            <p>Check the status of an active session.</p>
            <p><strong>Parameters:</strong> <code>session</code> - Session identifier</p>
        </div>

        <div class="endpoint">
            <p><span class="method get">GET</span> <code>/api/v1/identity</code></p>
            <p>Retrieve stored identity for a wallet address.</p>
            <p><strong>Parameters:</strong> <code>address</code> - Ethereum wallet address (0x format)</p>
        </div>

        <div class="endpoint">
            <p><span class="method post">POST</span> <code>/api/v1/identity</code></p>
            <p>Store identity data for a wallet address.</p>
            <p><strong>Body:</strong> JSON with <code>address</code> and <code>identity</code> fields</p>
        </div>

        <div class="endpoint">
            <p><span class="method delete">DELETE</span> <code>/api/v1/identity</code></p>
            <p>Clear stored identity for a wallet address.</p>
            <p><strong>Parameters:</strong> <code>address</code> - Ethereum wallet address</p>
        </div>

        <h2>Provider Integration</h2>
        <p>To integrate your identity provider, supply its URL via the <code>/connect/provider</code> endpoint.
        The provider URL is loaded in an iframe element for cross-origin identity negotiation.
        Only HTTPS origins are recommended for production use.</p>

        <h3>Example</h3>
        <pre><code>GET /connect/provider?provider_url=https://id.example.org</code></pre>
    </div>
    <div class="footer">
        Identity Bridge Platform v0.9.2
    </div>
</body>
</html>
"""

PROVIDER_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connect Provider - Identity Bridge</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; }}
        .header {{ background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }}
        .header h1 {{ font-size: 20px; color: #f0f6fc; }}
        .header nav a {{ color: #8b949e; text-decoration: none; margin-left: 24px; font-size: 14px; }}
        .content {{ max-width: 800px; margin: 40px auto; padding: 0 32px; }}
        .content h2 {{ color: #f0f6fc; margin-bottom: 16px; }}
        .form-group {{ margin-bottom: 16px; }}
        .form-group label {{ display: block; margin-bottom: 4px; color: #8b949e; font-size: 14px; }}
        .form-group input {{ width: 100%; padding: 8px 12px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; }}
        .btn {{ display: inline-block; padding: 8px 16px; background: #238636; color: #fff; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; }}
        .btn:hover {{ background: #2ea043; }}
        .provider-frame {{ margin-top: 24px; border: 1px solid #30363d; border-radius: 6px; overflow: hidden; }}
        .provider-frame iframe {{ width: 100%; height: 200px; border: none; }}
        .status-info {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 12px 16px; margin-top: 16px; color: #8b949e; }}
        .status-success {{ background: #23863622; border: 1px solid #238636; border-radius: 6px; padding: 12px 16px; margin-top: 16px; color: #3fb950; }}
        .session-info {{ margin-top: 16px; font-size: 12px; color: #484f58; }}
        .footer {{ text-align: center; padding: 32px; border-top: 1px solid #30363d; color: #484f58; font-size: 12px; margin-top: 60px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Identity Bridge</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/docs">Documentation</a>
            <a href="/connect/provider">Connect Provider</a>
        </nav>
    </div>
    <div class="content">
        <h2>Connect Identity Provider</h2>
        <form method="get" action="/connect/provider">
            <div class="form-group">
                <label for="provider_url">Provider URL</label>
                <input type="text" id="provider_url" name="provider_url" placeholder="https://id.example.org">
            </div>
            <button type="submit" class="btn">Verify Provider</button>
        </form>
        <div class="provider-frame">
            <iframe id="identity-bridge-frame" {provider_frame}></iframe>
        </div>
        {status_msg}
        <div class="session-info">Session: {session_id}</div>
    </div>
    <div class="footer">
        Identity Bridge Platform v0.9.2
    </div>
</body>
</html>
"""


@app.errorhandler(404)
def not_found(e):
    return make_response(jsonify({"error": "Not found"}), 404)

@app.errorhandler(500)
def server_error(e):
    return make_response(jsonify({"error": "Internal server error"}), 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
