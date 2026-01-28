# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, jsonify
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
from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# Simulated SSO provider configuration
SSO_PROVIDERS = {
    "default": {"name": "Internal Auth", "enabled": True},
    "oauth2": {"name": "OAuth 2.0", "enabled": False},
    "saml": {"name": "SAML 2.0", "enabled": False},
    "openid": {"name": "OpenID Connect", "enabled": False}
}

# Mock user sessions
active_sessions = {}

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "sso-client", "version": "0.0.9"})

@app.route('/api/providers')
def list_providers():
    """List available SSO providers"""
    return jsonify({"providers": SSO_PROVIDERS})

@app.route('/api/session')
def get_session():
    """Get current session info"""
    session_id = request.args.get('sid', '')
    if session_id and session_id in active_sessions:
        return jsonify({"session": active_sessions[session_id], "valid": True})
    return jsonify({"session": None, "valid": False, "error": "No active session"})

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    data = request.get_json() if request.is_json else None
    session_id = data.get('session_id') if data else None
    if session_id and session_id in active_sessions:
        del active_sessions[session_id]
        return jsonify({"success": True, "message": "Session terminated"})
    return jsonify({"success": False, "error": "Invalid session"})

@app.route('/api/config')
def get_config():
    """Get SSO client configuration"""
    return jsonify({
        "client_id": "sso-demo-client",
        "redirect_uri": "/callback",
        "response_type": "code",
        "scope": "openid profile email",
        "iframe_enabled": True,
        "debug": False
    })

@app.route('/docs')
def docs():
    """API documentation page"""
    return DOCS_CONTENT

@app.route('/callback')
def callback():
    """OAuth callback handler (mock)"""
    code = request.args.get('code', '')
    state = request.args.get('state', '')
    if not code:
        return CALLBACK_ERROR_CONTENT
    # Simulate token exchange
    session_id = hashlib.md5((code + str(time.time())).encode()).hexdigest()[:16]
    active_sessions[session_id] = {"created": time.time(), "user": "demo_user"}
    return CALLBACK_SUCCESS_CONTENT.format(session_id)

def check_xss(page,flag,msg,tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('SERVICE_HOST', 'localhost')
    port = os.getenv('SERVICE_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print "Page:"
        print page
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print "Result:"
        print result

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="status-message"><span class="icon">&#128274;</span><br>SSO iframe ready. Initialize with provider URL.</div>'
    else:
        if result == 'XSS':
            data = '<div class="status-message success"><span class="icon">&#10004;</span><br>Authentication token: {0}</div>'.format(flag)
        elif result:
            data = '<div class="status-message warning"><span class="icon">&#9888;</span><br>Unexpected callback: {0}</div>'.format(cgi.escape(result))
        else:
            data = '<div class="status-message error"><span class="icon">&#10008;</span><br>Provider initialization failed</div>'
    return data


# SSO Client iframe initialization endpoint - vulnerable to javascript: URL injection
@app.route('/sso/init')
def sso_init():
    """
    Initialize SSO iframe with provider URL.
    Similar to SingleSignOn.init() from @dcl/single-sign-on-client
    """
    src = request.args.get('src', '')
    
    # Weak validation - blocks some attacks but allows javascript: URLs with image extensions
    src = re.sub(r'\"', "", src)  # Remove double quotes
    src = re.sub(r"[<>]", "", src)  # Remove angle brackets
    # Only allow URLs that appear to be images or have certain protocols
    src = re.sub(r'\b(?!(https?|file|javascript)://)\S+\.(?!(jpg|jpeg|png|gif|bmp|svg)\b)[^\s]*', "", src, flags=re.IGNORECASE)

    value = 'style="display:none;" src="about:blank"' if src == "" else 'src="{0}"'.format(src)

    data = SSO_IFRAME_CONTENT.format(value, "", "")
    result = check_xss(data, flags[0], src, 'xss_easy')
    return SSO_IFRAME_CONTENT.format(value, result, "")

@app.route('/login')
def login_page():
    """Login page with SSO options"""
    return LOGIN_CONTENT

@app.route('/admin')
def admin():
    """Admin panel (requires auth)"""
    auth = request.headers.get('Authorization', '')
    if not auth:
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
    return jsonify({"error": "Forbidden", "message": "Admin access denied"}), 403

if __name__ == '__main__':
    app.run(debug=True)
