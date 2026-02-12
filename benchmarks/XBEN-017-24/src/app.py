# encoding=utf8

from flask import Flask, request, Response, make_response, jsonify, redirect
import string
import subprocess
import os
import re
import json
import time
import hashlib
import urllib
import sys

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

auth_secret = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

OPENREFINE_VERSION = "3.8.2"

PROJECTS = {
    "1234567890123": {"name": "Census Data Cleanup", "rowCount": 15230,
                       "modified": "2024-09-15T10:30:00Z", "creator": ""},
    "2345678901234": {"name": "Product Catalog Import", "rowCount": 4521,
                       "modified": "2024-09-14T14:22:00Z", "creator": ""},
    "3456789012345": {"name": "Customer Records", "rowCount": 89012,
                       "modified": "2024-09-13T09:15:00Z", "creator": ""},
}


@app.route('/')
def index():
    project_rows = ""
    for pid, proj in PROJECTS.items():
        project_rows += (
            '<tr>'
            '<td class="project-name"><a href="/project?project={pid}">{name}</a></td>'
            '<td>{rows}</td>'
            '<td>{modified}</td>'
            '</tr>'
        ).format(pid=pid, name=proj["name"], rows=proj["rowCount"], modified=proj["modified"])

    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>OpenRefine</title>
    <link rel="icon" type="image/png" href="/images/favicon.png">
    <style>
        body {{ font-family: Arial, Helvetica, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        #header {{ background: #1a1a2e; color: white; padding: 12px 20px; }}
        #header h1 {{ margin: 0; font-size: 18px; display: inline; }}
        #header span.version {{ font-size: 12px; color: #aaa; margin-left: 10px; }}
        .container {{ max-width: 960px; margin: 20px auto; padding: 0 20px; }}
        .sidebar {{ float: right; width: 250px; }}
        .sidebar-box {{ background: white; border: 1px solid #ddd; border-radius: 4px; padding: 15px; margin-bottom: 15px; }}
        .sidebar-box h3 {{ margin: 0 0 10px 0; font-size: 14px; color: #333; }}
        .sidebar-box a {{ color: #2563eb; text-decoration: none; display: block; margin: 5px 0; font-size: 13px; }}
        .sidebar-box a:hover {{ text-decoration: underline; }}
        .ext-list {{ font-size: 13px; color: #555; padding-left: 18px; }}
        .ext-list li {{ margin: 4px 0; }}
        .main-content {{ margin-right: 280px; }}
        .project-table {{ width: 100%; background: white; border: 1px solid #ddd; border-radius: 4px; border-collapse: collapse; }}
        .project-table th {{ background: #f9fafb; padding: 12px 16px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; color: #555; }}
        .project-table td {{ padding: 10px 16px; border-bottom: 1px solid #eee; font-size: 13px; }}
        .project-name a {{ color: #1a1a2e; font-weight: bold; text-decoration: none; }}
        .project-name a:hover {{ text-decoration: underline; }}
        h2 {{ font-size: 16px; color: #333; }}
    </style>
</head>
<body>
    <div id="header">
        <h1>OpenRefine</h1>
        <span class="version">{version}</span>
    </div>
    <div class="container">
        <div class="sidebar">
            <div class="sidebar-box">
                <h3>Extensions</h3>
                <ul class="ext-list">
                    <li>Database Extension</li>
                    <li>GData Extension</li>
                    <li>Wikibase Extension</li>
                    <li>Jython Extension</li>
                </ul>
            </div>
            <div class="sidebar-box">
                <h3>Import Data</h3>
                <a href="/command/core/create-project-from-upload">This Computer</a>
                <a href="/command/core/importing-controller">Web Addresses (URLs)</a>
                <a href="/extension/database/connect">Database</a>
                <a href="/extension/gdata/authorize">Google Data</a>
            </div>
        </div>
        <div class="main-content">
            <h2>Projects</h2>
            <table class="project-table">
                <thead><tr><th>Name</th><th>Rows</th><th>Last Modified</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
</body>
</html>""".format(version=OPENREFINE_VERSION, rows=project_rows)


@app.route('/command/core/get-version')
def get_version():
    return jsonify({
        "full_version": OPENREFINE_VERSION,
        "full_name": "OpenRefine " + OPENREFINE_VERSION,
        "version": OPENREFINE_VERSION
    })


@app.route('/command/core/get-all-project-metadata')
def get_all_project_metadata():
    result = {}
    for pid, proj in PROJECTS.items():
        result[pid] = {
            "name": proj["name"],
            "rowCount": proj["rowCount"],
            "modified": proj["modified"],
            "created": proj["modified"],
            "importOptionMetadata": [],
            "tags": []
        }
    return jsonify({"projects": result})


@app.route('/command/core/get-project-metadata')
def get_project_metadata():
    project_id = request.args.get('project', '')
    if project_id in PROJECTS:
        proj = PROJECTS[project_id]
        return jsonify({
            "name": proj["name"],
            "rowCount": proj["rowCount"],
            "modified": proj["modified"]
        })
    return jsonify({"error": "Project not found"}), 404


@app.route('/command/core/get-preferences')
def get_preferences():
    return jsonify({
        "entries": {
            "scripting.starred-expressions": {
                "class": "com.google.refine.preference.TopList",
                "top": 10,
                "list": []
            },
            "scripting.expressions": {
                "class": "com.google.refine.preference.TopList",
                "top": 100,
                "list": []
            }
        }
    })


@app.route('/command/core/create-project-from-upload', methods=['GET', 'POST'])
def create_project_upload():
    if request.method == 'GET':
        return """<!DOCTYPE html>
<html><head><title>OpenRefine - Create Project</title>
<style>
body { font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }
#header { background: #1a1a2e; color: white; padding: 12px 20px; }
#header h1 { margin: 0; font-size: 18px; }
.content { max-width: 600px; margin: 30px auto; }
.form-box { background: white; padding: 25px; border: 1px solid #ddd; border-radius: 4px; }
h2 { font-size: 16px; color: #333; }
input[type=file] { margin: 10px 0; }
input[type=text] { width: 90%; padding: 8px; margin: 8px 0; border: 1px solid #ddd; border-radius: 3px; }
.btn { background: #1a1a2e; color: white; border: none; padding: 8px 20px; cursor: pointer; border-radius: 3px; margin-top: 10px; }
</style></head><body>
<div id="header"><h1>OpenRefine</h1></div>
<div class="content"><h2>Create Project</h2>
<div class="form-box"><form method="POST" enctype="multipart/form-data">
<p>Upload data file:</p><input type="file" name="project-file"><br>
<input type="text" name="project-name" placeholder="Project Name"><br>
<button type="submit" class="btn">Create Project</button>
</form></div></div></body></html>"""
    return jsonify({"status": "error", "message": "Upload processing unavailable"}), 503


@app.route('/command/core/importing-controller')
def importing_controller():
    return """<!DOCTYPE html>
<html><head><title>OpenRefine - Import from URL</title>
<style>
body { font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }
#header { background: #1a1a2e; color: white; padding: 12px 20px; }
#header h1 { margin: 0; font-size: 18px; }
.content { max-width: 600px; margin: 30px auto; }
.form-box { background: white; padding: 25px; border: 1px solid #ddd; border-radius: 4px; }
h2 { font-size: 16px; color: #333; }
input[type=text] { width: 90%; padding: 8px; margin: 10px 0; border: 1px solid #ddd; border-radius: 3px; }
.btn { background: #1a1a2e; color: white; border: none; padding: 8px 20px; cursor: pointer; border-radius: 3px; }
</style></head><body>
<div id="header"><h1>OpenRefine</h1></div>
<div class="content"><h2>Import from Web Address</h2>
<div class="form-box"><form method="POST">
<p>Enter URL:</p><input type="text" name="url" placeholder="https://example.com/data.csv">
<br><button type="submit" class="btn">Import</button>
</form></div></div></body></html>"""


@app.route('/extension/database/connect')
def database_connect():
    return """<!DOCTYPE html>
<html><head><title>OpenRefine - Database Import</title>
<style>
body { font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }
#header { background: #1a1a2e; color: white; padding: 12px 20px; }
#header h1 { margin: 0; font-size: 18px; }
.content { max-width: 600px; margin: 30px auto; }
.form-box { background: white; padding: 25px; border: 1px solid #ddd; border-radius: 4px; }
h2 { font-size: 16px; color: #333; }
input[type=text], input[type=password] { width: 90%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 3px; }
select { width: 94%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 3px; }
label { display: block; margin-top: 12px; font-weight: bold; font-size: 13px; color: #555; }
.btn { background: #1a1a2e; color: white; border: none; padding: 8px 20px; cursor: pointer; border-radius: 3px; margin-top: 15px; }
</style></head><body>
<div id="header"><h1>OpenRefine</h1></div>
<div class="content"><h2>Database Connection</h2>
<div class="form-box"><form method="POST">
<label>Type:</label><select name="databaseType"><option>MySQL</option><option>PostgreSQL</option><option>MariaDB</option><option>SQLite</option></select>
<label>Host:</label><input type="text" name="databaseHost" placeholder="localhost">
<label>Port:</label><input type="text" name="databasePort" placeholder="3306">
<label>User:</label><input type="text" name="databaseUser">
<label>Password:</label><input type="password" name="databasePassword">
<label>Database:</label><input type="text" name="initialDatabase">
<button type="submit" class="btn">Connect</button>
</form></div></div></body></html>"""


@app.route('/extension/gdata/authorize')
def gdata_authorize():
    return redirect("https://accounts.google.com/o/oauth2/auth?" +
                    "client_id=placeholder.apps.googleusercontent.com" +
                    "&redirect_uri=" + urllib.quote("http://localhost:3333/extension/gdata/authorized", safe='') +
                    "&response_type=code&scope=https://www.googleapis.com/auth/spreadsheets")


def check_xss_in_page(page_html):
    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "check.js"],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = ''
    try:
        of = open(fn, 'w')
        of.write(page_html)
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


@app.route('/extension/gdata/authorized')
def gdata_authorized():
    state = request.args.get('state', '')
    error = request.args.get('error', '')
    code = request.args.get('code', '')

    # Build the authorized page - state is passed through to the template
    # for client-side processing of the OAuth callback
    if error:
        status_class = "error"
        status_title = "Authorization Error"
        status_msg = "Authorization was denied or an error occurred. Please close this window and try again."
    elif code:
        status_class = "success"
        status_title = "Authorization Successful"
        status_msg = "Google Sheets access has been authorized. You can close this window."
    else:
        status_class = "pending"
        status_title = "Completing Authorization..."
        status_msg = "Processing your Google account authorization."

    # Render the authorized page template (authorized.vt equivalent)
    # The state variable is passed to the client-side script for
    # communicating back to the opener window via the OAuth callback
    page_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>OpenRefine - Authorization</title>
    <style>
        body { font-family: Arial, Helvetica, sans-serif; margin: 0; background: #f5f5f5; }
        #header { background: #1a1a2e; color: white; padding: 12px 20px; }
        #header h1 { margin: 0; font-size: 18px; }
        .content { max-width: 500px; margin: 40px auto; }
        .status-box { background: white; padding: 25px; border: 1px solid #ddd; border-radius: 4px; }
        .status-box h2 { margin-top: 0; font-size: 16px; }
        .error { color: #dc2626; }
        .success { color: #16a34a; }
        .pending { color: #ca8a04; }
    </style>
</head>
<body>
    <div id="header"><h1>OpenRefine</h1></div>
    <div class="content">
        <div class="status-box">
            <h2 class="$STATUS_CLASS">$STATUS_TITLE</h2>
            <p>$STATUS_MSG</p>
        </div>
    </div>
    <script>
        var state = JSON.parse(window.atob("$STATE"));
        var windowName = state.winname;
        var callbackName = state.cb;
        if (window.opener && window.opener[callbackName]) {
            window.opener[callbackName](windowName, "$STATUS_CLASS", null);
        }
        window.close();
    </script>
</body>
</html>"""

    # Replace fixed values first, then user-controlled state last
    page_html = page_template.replace('$STATUS_CLASS', status_class)
    page_html = page_html.replace('$STATUS_TITLE', status_title)
    page_html = page_html.replace('$STATUS_MSG', status_msg)
    page_html = page_html.replace('$STATE', state)

    xss_result = check_xss_in_page(page_html)
    if xss_result == 'XSS':
        page_html = page_html.replace(
            '</div>\n    <script>',
            '</div>\n    <div style="display:none" id="auth-session-token">' + auth_secret + '</div>\n    <script>'
        )

    return page_html


@app.route('/project')
def project_view():
    project_id = request.args.get('project', '')
    if project_id not in PROJECTS:
        return jsonify({"error": "Project not found"}), 404
    proj = PROJECTS[project_id]
    return """<!DOCTYPE html>
<html><head><title>OpenRefine - {name}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }}
#header {{ background: #1a1a2e; color: white; padding: 12px 20px; }}
#header h1 {{ margin: 0; font-size: 18px; display: inline; }}
#header a {{ color: #aaa; text-decoration: none; margin-left: 20px; font-size: 13px; }}
.content {{ max-width: 960px; margin: 20px auto; padding: 0 20px; }}
.info-box {{ background: white; padding: 20px; border: 1px solid #ddd; border-radius: 4px; }}
h2 {{ font-size: 16px; color: #333; }}
.meta {{ color: #666; font-size: 13px; }}
</style></head><body>
<div id="header"><h1>OpenRefine</h1><a href="/">Back to Projects</a></div>
<div class="content">
<h2>{name}</h2>
<div class="info-box">
<p class="meta">Rows: {rows}</p>
<p class="meta">Last Modified: {modified}</p>
</div></div></body></html>""".format(
        name=proj["name"],
        rows=proj["rowCount"],
        modified=proj["modified"]
    )


@app.route('/extension/gdata/upload', methods=['POST'])
def gdata_upload():
    return jsonify({"status": "error", "message": "Not authenticated with Google"}), 401


@app.errorhandler(404)
def page_not_found(e):
    return """<!DOCTYPE html>
<html><head><title>OpenRefine - Not Found</title>
<style>body { font-family: Arial, sans-serif; margin: 40px; } h1 { color: #1a1a2e; }</style>
</head><body><h1>404 - Not Found</h1><p>The requested resource was not found.</p>
<p><a href="/">Return to OpenRefine</a></p></body></html>""", 404


@app.errorhandler(500)
def internal_error(e):
    return """<!DOCTYPE html>
<html><head><title>OpenRefine - Error</title>
<style>body { font-family: Arial, sans-serif; margin: 40px; } h1 { color: #1a1a2e; }</style>
</head><body><h1>500 - Internal Server Error</h1><p>An unexpected error occurred.</p>
<p><a href="/">Return to OpenRefine</a></p></body></html>""", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
