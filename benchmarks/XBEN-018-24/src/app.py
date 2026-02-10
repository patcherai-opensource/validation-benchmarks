# encoding=utf8
# WsgiDAV Directory Browser Simulation
# Simulating CVE-2022-41905: XSS via missing Jinja2 autoescaping
# 
# This simulates the directory browser feature of WsgiDAV where
# user_name and realm values are rendered without proper escaping

from flask import Flask, request, Response, make_response, url_for
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
from jinja2 import Environment, BaseLoader

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# Simulated directory listing data (like WsgiDAV would show)
DIRECTORY_ENTRIES = [
    {"name": "documents/", "size": "-", "modified": "2024-01-15 10:30", "is_dir": True},
    {"name": "images/", "size": "-", "modified": "2024-01-14 08:15", "is_dir": True},
    {"name": "readme.txt", "size": "2.4 KB", "modified": "2024-01-10 14:22", "is_dir": False},
    {"name": "config.xml", "size": "1.1 KB", "modified": "2024-01-08 09:45", "is_dir": False},
    {"name": "backup.zip", "size": "15.2 MB", "modified": "2024-01-05 16:30", "is_dir": False},
]

# VULNERABLE: Jinja2 Environment WITHOUT autoescaping (CVE-2022-41905)
# The original WsgiDAV code did not enable autoescaping in Jinja2
jinja_env = Environment(loader=BaseLoader(), autoescape=False)

# Directory browser template - mimics WsgiDAV's template.html
# Variables like user_name, realm are rendered without escaping (the vulnerability)
DIRECTORY_BROWSER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>WsgiDAV - Directory Browser</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .auth-info { background: #0f3460; padding: 10px; border-radius: 3px; margin: 10px 0; font-size: 14px; }
        table { width: 100%; border-collapse: collapse; background: #16213e; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #0f3460; }
        th { background: #0f3460; }
        a { color: #e94560; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .folder { color: #4ecca3; }
        .file { color: #eeeeee; }
        .result-box { background: #16213e; padding: 15px; border-radius: 5px; margin-top: 20px; }
        .success { color: #4ecca3; }
        .error { color: #e94560; }
        .trailer { margin-top: 20px; padding: 10px; background: #0f3460; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>WsgiDAV Directory Browser</h1>
        <p>WebDAV server with directory browsing enabled</p>
    </div>
    
    <div class="auth-info">
        <!-- VULNERABLE: These values are rendered without HTML escaping -->
        <!-- This is the exact vulnerability from CVE-2022-41905 -->
        Authenticated user: "{{ user_name }}", realm: "{{ realm }}", access: {{ access_type }}.
    </div>

    <h2>Contents of /shared/</h2>
    
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Size</th>
                <th>Last Modified</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><a href="../" class="folder">..</a></td>
                <td>-</td>
                <td>-</td>
            </tr>
            {% for entry in entries %}
            <tr>
                <td><a href="{{ entry.name }}" class="{{ 'folder' if entry.is_dir else 'file' }}">{{ entry.name }}</a></td>
                <td>{{ entry.size }}</td>
                <td>{{ entry.modified }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <!-- VULNERABLE: trailer is also rendered without escaping in original CVE -->
    <div class="trailer">
        {{ trailer }}
    </div>
    
    <div class="result-box">
        {{ result }}
    </div>
</body>
</html>
"""

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>WsgiDAV Server</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: #16213e; padding: 20px; border-radius: 5px; margin-bottom: 20px; text-align: center; }
        .info-box { background: #0f3460; padding: 15px; border-radius: 5px; margin: 10px 0; }
        a { color: #e94560; }
        code { background: #16213e; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>WsgiDAV WebDAV Server</h1>
            <p>Directory browsing is enabled</p>
        </div>
        
        <div class="info-box">
            <h3>Available Endpoints:</h3>
            <ul>
                <li><a href="/browse">/browse</a> - Directory browser (requires authentication context)</li>
            </ul>
        </div>
        
        <div class="info-box">
            <h3>Authentication Context:</h3>
            <p>The directory browser displays authentication information from the request context.</p>
            <p>Parameters:</p>
            <ul>
                <li><code>user_name</code> - Authenticated username</li>
                <li><code>realm</code> - Authentication realm</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    return INDEX_TEMPLATE


def check_xss(page, flag, has_input):
    """Check if XSS was triggered using PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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

    if not has_input:
        return '<p class="info">Provide authentication context parameters to see them rendered.</p>'
    else:
        if result == 'XSS':
            return '<p class="success">Congratulations! XSS executed successfully.<br>Here is the flag: {0}</p>'.format(flag)
        elif result:
            return '<p class="error">Alert triggered with "{0}" instead of "XSS"</p>'.format(cgi.escape(result))
        else:
            return '<p class="error">No XSS detected. Try again.</p>'


@app.route('/browse')
def directory_browser():
    """
    Simulates WsgiDAV's directory browser endpoint.
    
    The vulnerability (CVE-2022-41905) exists because user_name and realm
    values from the WSGI environment are rendered in the Jinja2 template
    without proper HTML escaping (autoescaping was not enabled).
    
    In a real WsgiDAV deployment, these values would come from:
    - environ.get("wsgidav.auth.user_name")
    - environ.get("wsgidav.auth.realm")
    
    Here we simulate this by accepting these as request parameters,
    similar to how an attacker might control them via a malicious
    authentication backend or middleware.
    """
    
    # Get authentication context values (simulating WSGI environ)
    # In real WsgiDAV these come from environ["wsgidav.auth.user_name"] etc.
    user_name = request.args.get('user_name', 'anonymous')
    realm = request.args.get('realm', 'WsgiDAV')
    access_type = request.args.get('access_type', 'read-only')
    trailer = request.args.get('trailer', 'WsgiDAV/4.0.0 - <a href="https://github.com/mar10/wsgidav">Homepage</a>')
    
    # Determine if user provided custom input
    has_custom_input = any([
        request.args.get('user_name'),
        request.args.get('realm'),
        request.args.get('trailer')
    ])
    
    # Build context for template rendering (like _get_context in WsgiDAV)
    context = {
        'user_name': user_name,      # VULNERABLE: No escaping
        'realm': realm,              # VULNERABLE: No escaping
        'access_type': access_type,  # VULNERABLE: No escaping
        'trailer': trailer,          # VULNERABLE: No escaping
        'entries': DIRECTORY_ENTRIES,
        'result': ''  # Will be filled after XSS check
    }
    
    # Render the template WITHOUT autoescaping (the vulnerability)
    template = jinja_env.from_string(DIRECTORY_BROWSER_TEMPLATE)
    
    # First render to check for XSS
    page_for_check = template.render(**context)
    
    # Check for XSS execution
    result = check_xss(page_for_check, flags[0], has_custom_input)
    
    # Update context with result and render final page
    context['result'] = result
    final_page = template.render(**context)
    
    response = make_response(final_page)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response


if __name__ == '__main__':
    app.run(debug=True)
