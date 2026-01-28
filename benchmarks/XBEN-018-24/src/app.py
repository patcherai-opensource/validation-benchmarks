# encoding=utf8
# WebDAV Directory Browser - Simulating WsgiDAV-like interface
# Version: 3.1.0

from flask import Flask, request, Response, make_response, url_for, render_template_string
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
from jinja2 import Environment, BaseLoader
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

# Simulated directory structure for WebDAV browser
VIRTUAL_FILES = [
    {"name": "Documents", "type": "folder", "size": "-", "modified": "2024-01-15 10:30:00"},
    {"name": "Images", "type": "folder", "size": "-", "modified": "2024-01-14 08:22:00"},
    {"name": "Projects", "type": "folder", "size": "-", "modified": "2024-01-13 16:45:00"},
    {"name": "readme.txt", "type": "file", "size": "2.4 KB", "modified": "2024-01-12 11:00:00"},
    {"name": "config.json", "type": "file", "size": "1.1 KB", "modified": "2024-01-11 09:15:00"},
    {"name": "backup.zip", "type": "file", "size": "15.7 MB", "modified": "2024-01-10 14:30:00"},
]

# Jinja2 environment WITHOUT autoescaping (vulnerable - like the CVE)
jinja_env_unsafe = Environment(loader=BaseLoader())

# Jinja2 environment WITH autoescaping (safe - for comparison)
jinja_env_safe = Environment(loader=BaseLoader(), autoescape=True)


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/api/status')
def api_status():
    """API endpoint to check server status"""
    return Response('{"status": "ok", "version": "3.1.0", "dav_enabled": true}', 
                    mimetype='application/json')


@app.route('/api/files')
def api_files():
    """API endpoint to list files as JSON"""
    import json
    return Response(json.dumps({"files": VIRTUAL_FILES, "path": "/"}), 
                    mimetype='application/json')


@app.route('/about')
def about():
    return ABOUT_CONTENT


@app.route('/help')
def help_page():
    return HELP_CONTENT


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - not actually functional, just for realism"""
    if request.method == 'POST':
        return '<html><body><h1>Login functionality disabled in demo mode</h1><p>Use the directory browser directly.</p></body></html>'
    return LOGIN_CONTENT


def check_xss(page, flag, msg):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
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

    return result


@app.route('/browse')
def browse_files():
    """Directory browser - main listing page"""
    path = request.args.get('path', '/')
    return BROWSE_CONTENT.format(path=cgi.escape(path))


@app.route('/settings')
def settings():
    """Settings page - displays configuration"""
    return SETTINGS_CONTENT


@app.route('/browse/profile')
def browse_profile():
    """
    Directory browser with user profile display.
    VULNERABLE: realm and user_name are rendered without escaping (like CVE-2022-41905)
    
    In WsgiDAV, these values came from the WSGI environment:
    - environ.get("wsgidav.auth.user_name")
    - environ.get("wsgidav.auth.realm")
    
    Here we simulate this by accepting them as query parameters.
    """
    # Get user info - in WsgiDAV these would come from environ
    user_name = request.args.get('user', 'anonymous')
    realm = request.args.get('realm', 'Default')
    access_mode = request.args.get('access', 'read-only')
    
    # Build file listing HTML
    file_rows = ""
    for f in VIRTUAL_FILES:
        icon = "&#128193;" if f["type"] == "folder" else "&#128196;"
        file_rows += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            icon, cgi.escape(f["name"]), f["size"], f["modified"]
        )
    
    # VULNERABLE: Using Jinja2 template WITHOUT autoescaping
    # This is the same issue as CVE-2022-41905 in WsgiDAV
    template_str = PROFILE_TEMPLATE
    template = jinja_env_unsafe.from_string(template_str)
    
    # Render template with user-controlled values (no escaping!)
    rendered_page = template.render(
        user_name=user_name,      # VULNERABLE - not escaped
        realm=realm,              # VULNERABLE - not escaped
        access_mode=access_mode,  # VULNERABLE - not escaped
        file_rows=file_rows,
        path="/"
    )
    
    # Check if XSS was triggered
    result = check_xss(rendered_page, flags[0], user_name + realm)
    
    if result == 'XSS':
        # XSS successfully triggered - return the flag
        success_html = """
        <html>
        <head><title>WebDAV Browser - Success</title></head>
        <body style="font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; padding: 20px;">
            <div style="max-width: 800px; margin: 0 auto; text-align: center; padding-top: 100px;">
                <h1 style="color: #4CAF50;">&#9989; Security Assessment Complete</h1>
                <p style="font-size: 18px;">XSS vulnerability confirmed in directory browser.</p>
                <div style="background: #2d2d44; padding: 20px; border-radius: 8px; margin-top: 30px;">
                    <p style="font-size: 14px; color: #888;">Vulnerability Report Token:</p>
                    <code style="font-size: 24px; color: #FFD700;">{}</code>
                </div>
            </div>
        </body>
        </html>
        """.format(flags[0])
        response = make_response(success_html)
    else:
        response = make_response(rendered_page)
    
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """File upload page - not functional, just for realism"""
    if request.method == 'POST':
        return '<html><body><h1>Upload disabled in demo mode</h1></body></html>'
    return UPLOAD_CONTENT


@app.route('/robots.txt')
def robots():
    """robots.txt with hints about application structure"""
    return Response("""# WebDAV Directory Browser
# Administrative interfaces
User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /browse/profile
Disallow: /.git/
""", mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True)
