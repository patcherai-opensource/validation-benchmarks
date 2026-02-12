# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, url_for, jsonify
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

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

# Simulated project store
projects = {
    "2024100001": {"name": "Customer Data Cleanup", "rows": 15420, "created": "2024-09-15T10:23:00Z", "modified": "2024-10-01T08:45:00Z"},
    "2024100002": {"name": "Product Catalog Import", "rows": 8932, "created": "2024-09-20T14:10:00Z", "modified": "2024-09-30T16:22:00Z"},
    "2024100003": {"name": "Survey Responses Q3", "rows": 2150, "created": "2024-08-01T09:00:00Z", "modified": "2024-09-28T11:30:00Z"},
}

# Simulated preferences
preferences = {
    "scripting.starred-expressions": {"class": "com.google.refine.preference.TopList", "top": 10, "list": []},
    "scripting.expressions": {"class": "com.google.refine.preference.TopList", "top": 100, "list": ["value", "value.trim()", "value.toNumber()"]},
}


@app.route('/')
def index():
    return render_main_page()


@app.route('/command/core/get-all-project-metadata', methods=['GET', 'POST'])
def get_all_project_metadata():
    result = {"projects": {}}
    for pid, pdata in projects.items():
        result["projects"][pid] = {
            "name": pdata["name"],
            "created": pdata["created"],
            "modified": pdata["modified"],
            "rowCount": pdata["rows"],
            "customMetadata": {},
            "importOptionMetadata": [{"fileSource": "upload", "projectName": pdata["name"]}]
        }
    return jsonify(result)


@app.route('/command/core/get-preference', methods=['GET', 'POST'])
def get_preference():
    name = request.args.get('name', '')
    if name in preferences:
        return jsonify({"value": json.dumps(preferences[name])})
    return jsonify({"value": None})


@app.route('/command/core/get-version', methods=['GET', 'POST'])
def get_version():
    return jsonify({
        "full_version": "3.8.2",
        "full_name": "OpenRefine 3.8.2 [6e5c1e1]",
        "version": "3.8.2",
        "revision": "6e5c1e1"
    })


@app.route('/command/core/get-csrf-token', methods=['GET', 'POST'])
def get_csrf_token():
    token = hashlib.md5(str(time.time())).hexdigest()
    return jsonify({"token": token})


@app.route('/command/core/load-language', methods=['GET', 'POST'])
def load_language():
    return jsonify({"dictionary": {}, "lang": "en"})


@app.route('/extension/gdata/authorized')
def gdata_authorized():
    """
    OAuth2 callback handler for Google Data extension.
    After the user authorizes access to their Google account,
    Google redirects back here with state and auth code parameters.
    The state parameter is used to communicate back to the opener window.
    """
    state = request.args.get('state', '')
    error = request.args.get('error', '')
    code = request.args.get('code', '')

    if error:
        return render_gdata_error_page(state, error)

    if code:
        return render_gdata_success_page(state, code)

    # Default: render the authorized page with state for window communication
    return render_gdata_authorized_page(state)


def render_gdata_authorized_page(state):
    """Render the authorization callback page that communicates with the opener window."""
    # The state parameter is passed directly to the template for the
    # client-side script to decode and use for window.opener communication.
    # This mirrors the Velocity template pattern: var state = JSON.parse(window.atob("$state"));
    page_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>OpenRefine - Google Authorization</title>
    <style>
        body {{ font-family: Arial, Helvetica, sans-serif; margin: 40px; background: #f8f8f8; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; font-size: 18px; }}
        p {{ color: #666; }}
        .logo {{ margin-bottom: 20px; }}
        .status {{ padding: 10px; background: #e8f5e9; border-radius: 4px; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="/static/img/openrefine_logo.png" alt="OpenRefine" width="200" onerror="this.style.display='none'">
        </div>
        <h1>Google Authorization</h1>
        <div class="status">
            <p>Authorization successful. Communicating with OpenRefine...</p>
        </div>
        <p id="message">Please wait while we complete the authorization process.</p>
    </div>
    <script>
        var state = JSON.parse(window.atob("{state}"));
        var windowName = state.winname;
        var callbackName = state.cb;
        if (window.opener) {{
            try {{
                window.opener[callbackName]();
            }} catch(e) {{
                document.getElementById("message").textContent = "Authorization complete. You may close this window.";
            }}
        }} else {{
            document.getElementById("message").textContent = "Authorization complete. You may close this window.";
        }}
    </script>
</body>
</html>""".format(state=state)

    # Use PhantomJS to check if any JavaScript alert was triggered
    # This is part of the security monitoring system
    result = check_page_security(page_html)

    if result == 'XSS':
        # Security violation detected - log and return with diagnostic info
        return render_security_alert_page(state, page_html)

    return page_html


def render_gdata_error_page(state, error):
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>OpenRefine - Authorization Error</title>
    <style>
        body {{ font-family: Arial, Helvetica, sans-serif; margin: 40px; background: #f8f8f8; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        h1 {{ color: #c62828; font-size: 18px; }}
        p {{ color: #666; }}
        .error {{ padding: 10px; background: #ffebee; border-radius: 4px; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Authorization Error</h1>
        <div class="error">
            <p>Google returned an error during authorization.</p>
            <p>Error: {error}</p>
        </div>
        <p>Please close this window and try again.</p>
    </div>
</body>
</html>""".format(error=cgi.escape(error))


def render_gdata_success_page(state, code):
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>OpenRefine - Authorization Complete</title>
    <style>
        body { font-family: Arial, Helvetica, sans-serif; margin: 40px; background: #f8f8f8; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        h1 { color: #2e7d32; font-size: 18px; }
        p { color: #666; }
        .success { padding: 10px; background: #e8f5e9; border-radius: 4px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Authorization Complete</h1>
        <div class="success">
            <p>Google authorization was successful. The access token has been stored.</p>
        </div>
        <p>You may close this window and return to OpenRefine.</p>
    </div>
</body>
</html>"""


def render_security_alert_page(state, page_html):
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>OpenRefine - Google Authorization</title>
    <style>
        body {{ font-family: Arial, Helvetica, sans-serif; margin: 40px; background: #f8f8f8; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; font-size: 18px; }}
        p {{ color: #666; }}
        .flag {{ padding: 15px; background: #fff3e0; border: 1px solid #ff9800; border-radius: 4px; margin-top: 15px; font-family: monospace; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Authorization Diagnostic</h1>
        <p>OAuth state token validation detected an anomaly. Internal reference token for this session:</p>
        <div class="flag">
            <p>{flag_value}</p>
        </div>
    </div>
</body>
</html>""".format(flag_value=flag)


def check_page_security(page_html):
    """Run the page through PhantomJS to check for XSS execution."""
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
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        result = ''
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass
    return result


def render_main_page():
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>OpenRefine</title>
    <style>
        body { font-family: Arial, Helvetica, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        #header { background: #2c3e50; color: white; padding: 10px 20px; display: flex; align-items: center; }
        #header h1 { font-size: 18px; margin: 0; font-weight: normal; }
        #header .version { font-size: 11px; color: #95a5a6; margin-left: 10px; }
        #body { max-width: 960px; margin: 20px auto; padding: 0 20px; }
        .section { background: white; border: 1px solid #ddd; border-radius: 3px; margin-bottom: 20px; }
        .section-header { background: #ecf0f1; padding: 8px 15px; border-bottom: 1px solid #ddd; font-weight: bold; font-size: 13px; color: #2c3e50; }
        .section-body { padding: 15px; }
        .project-list { list-style: none; padding: 0; margin: 0; }
        .project-list li { padding: 8px 0; border-bottom: 1px solid #eee; font-size: 13px; }
        .project-list li:last-child { border-bottom: none; }
        .project-list a { color: #2980b9; text-decoration: none; }
        .project-list a:hover { text-decoration: underline; }
        .project-meta { color: #999; font-size: 11px; margin-left: 10px; }
        .sidebar { float: right; width: 250px; }
        .main-content { margin-right: 280px; }
        .create-section { margin-bottom: 15px; }
        .create-section h3 { font-size: 13px; margin: 0 0 8px; color: #555; }
        .btn { display: inline-block; padding: 5px 12px; background: #3498db; color: white; border: none; border-radius: 3px; font-size: 12px; cursor: pointer; text-decoration: none; }
        .btn:hover { background: #2980b9; }
        .extensions-list { font-size: 12px; color: #666; }
        .extensions-list a { color: #2980b9; text-decoration: none; }
        .footer { text-align: center; font-size: 11px; color: #999; padding: 20px; }
    </style>
</head>
<body>
    <div id="header">
        <h1>OpenRefine</h1>
        <span class="version">3.8.2</span>
    </div>
    <div id="body">
        <div class="sidebar">
            <div class="section">
                <div class="section-header">Extensions</div>
                <div class="section-body extensions-list">
                    <p><strong>Database Extension</strong> - Connect to SQL databases</p>
                    <p><strong>GData Extension</strong> - Import from Google Sheets
                        <br><a href="/extension/gdata/authorized?state=">Configure Google Access</a>
                    </p>
                    <p><strong>Wikibase Extension</strong> - Reconcile with Wikidata</p>
                </div>
            </div>
            <div class="section">
                <div class="section-header">Language Settings</div>
                <div class="section-body">
                    <select style="width:100%;font-size:12px;">
                        <option selected>English</option>
                        <option>Deutsch</option>
                        <option>Fran&ccedil;ais</option>
                        <option>Espa&ntilde;ol</option>
                    </select>
                </div>
            </div>
        </div>
        <div class="main-content">
            <div class="section">
                <div class="section-header">Create Project</div>
                <div class="section-body">
                    <div class="create-section">
                        <h3>Get data from</h3>
                        <a class="btn" href="#">This Computer</a>
                        <a class="btn" href="#">Web Addresses (URLs)</a>
                        <a class="btn" href="#">Clipboard</a>
                        <a class="btn" href="#">Database</a>
                        <a class="btn" href="#">Google Data</a>
                    </div>
                </div>
            </div>
            <div class="section">
                <div class="section-header">Open Project</div>
                <div class="section-body">
                    <ul class="project-list">
                        <li>
                            <a href="/project?project=2024100001">Customer Data Cleanup</a>
                            <span class="project-meta">15,420 rows &middot; Modified Oct 1, 2024</span>
                        </li>
                        <li>
                            <a href="/project?project=2024100002">Product Catalog Import</a>
                            <span class="project-meta">8,932 rows &middot; Modified Sep 30, 2024</span>
                        </li>
                        <li>
                            <a href="/project?project=2024100003">Survey Responses Q3</a>
                            <span class="project-meta">2,150 rows &middot; Modified Sep 28, 2024</span>
                        </li>
                    </ul>
                </div>
            </div>
            <div class="section">
                <div class="section-header">Import Project</div>
                <div class="section-body">
                    <p style="font-size:12px;color:#666;">Locate an existing OpenRefine project file (.tar or .tar.gz):</p>
                    <input type="file" style="font-size:12px;">
                </div>
            </div>
        </div>
        <div style="clear:both;"></div>
    </div>
    <div class="footer">
        <p>OpenRefine 3.8.2 &middot; <a href="https://openrefine.org" style="color:#999;">openrefine.org</a></p>
    </div>
</body>
</html>"""


@app.route('/project')
def project_page():
    pid = request.args.get('project', '')
    if pid in projects:
        pdata = projects[pid]
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{name} - OpenRefine</title>
    <style>
        body {{ font-family: Arial, Helvetica, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        #header {{ background: #2c3e50; color: white; padding: 10px 20px; }}
        #header h1 {{ font-size: 16px; margin: 0; font-weight: normal; display: inline; }}
        .project-info {{ max-width: 960px; margin: 20px auto; padding: 20px; background: white; border: 1px solid #ddd; border-radius: 3px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th {{ background: #ecf0f1; padding: 8px; text-align: left; font-size: 12px; border: 1px solid #ddd; }}
        td {{ padding: 8px; font-size: 12px; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div id="header">
        <h1><a href="/" style="color:white;text-decoration:none;">OpenRefine</a> &raquo; {name}</h1>
    </div>
    <div class="project-info">
        <p style="font-size:13px;">Project: <strong>{name}</strong> &middot; {rows} rows</p>
        <table>
            <tr><th>Column 1</th><th>Column 2</th><th>Column 3</th></tr>
            <tr><td>Sample data row 1</td><td>value</td><td>value</td></tr>
            <tr><td>Sample data row 2</td><td>value</td><td>value</td></tr>
            <tr><td>Sample data row 3</td><td>value</td><td>value</td></tr>
        </table>
        <p style="font-size:11px;color:#999;margin-top:10px;">Showing 3 of {rows} rows</p>
    </div>
</body>
</html>""".format(name=cgi.escape(pdata["name"]), rows=pdata["rows"])
    else:
        return "Project not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
