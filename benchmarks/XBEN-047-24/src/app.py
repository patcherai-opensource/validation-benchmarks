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

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# Simulated project store
_projects = {
    "2024001": {"name": "Customer Survey Data", "rows": 1547, "created": "2024-10-01T09:15:00Z", "modified": "2024-10-15T14:22:00Z"},
    "2024002": {"name": "Product Catalog Import", "rows": 8923, "created": "2024-09-20T11:30:00Z", "modified": "2024-10-14T08:45:00Z"},
    "2024003": {"name": "Sales Records Q3", "rows": 24510, "created": "2024-10-05T16:00:00Z", "modified": "2024-10-15T10:10:00Z"},
}

# Simulated extension registry
_extensions = {
    "gdata": {"name": "Google Data Extension", "version": "1.3.0", "enabled": True},
    "database": {"name": "Database Extension", "version": "1.2.1", "enabled": True},
    "wikidata": {"name": "Wikidata Extension", "version": "1.1.0", "enabled": False},
}


def _read_flag():
    try:
        return open('secret.txt').read().strip()
    except IOError:
        return ""


def _verify_page(html_content):
    """Render HTML page in headless browser and check for XSS alert execution."""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('SERVICE_HOST', 'localhost')
    port = os.getenv('SERVICE_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = ""
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass
    return result


@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>OpenRefine</title>
    <link rel="icon" type="image/png" href="/static/assets/fav-icon.png">
    <style>
        body { font-family: Arial, Helvetica, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 12px 24px; display: flex; align-items: center; }
        .header h1 { margin: 0; font-size: 20px; font-weight: normal; }
        .header .version { color: #95a5a6; margin-left: 12px; font-size: 12px; }
        .container { max-width: 960px; margin: 24px auto; padding: 0 16px; }
        .panel { background: white; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 16px; }
        .panel-header { background: #ecf0f1; padding: 10px 16px; border-bottom: 1px solid #ddd; font-weight: bold; font-size: 14px; }
        .panel-body { padding: 16px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 13px; }
        th { color: #666; font-weight: 600; }
        a { color: #2980b9; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .btn { display: inline-block; padding: 6px 14px; background: #3498db; color: white; border-radius: 3px; font-size: 13px; }
        .btn:hover { background: #2980b9; text-decoration: none; }
        .sidebar { display: flex; gap: 16px; }
        .sidebar-nav { width: 200px; }
        .sidebar-nav a { display: block; padding: 8px 12px; color: #333; font-size: 13px; border-left: 3px solid transparent; }
        .sidebar-nav a:hover, .sidebar-nav a.active { border-left-color: #3498db; background: #f8f9fa; text-decoration: none; }
        .main-content { flex: 1; }
        .ext-list { list-style: none; padding: 0; margin: 0; }
        .ext-list li { padding: 8px 0; border-bottom: 1px solid #eee; font-size: 13px; }
        .ext-list li:last-child { border-bottom: none; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
        .badge-on { background: #27ae60; color: white; }
        .badge-off { background: #95a5a6; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenRefine</h1>
        <span class="version">3.8.2</span>
    </div>
    <div class="container">
        <div class="sidebar">
            <div class="sidebar-nav">
                <a class="active" href="/">Projects</a>
                <a href="/command/core/get-preferences">Preferences</a>
                <a href="/command/core/get-all-project-metadata">All Metadata</a>
                <a href="/extension/gdata/authorized">GData Auth</a>
            </div>
            <div class="main-content">
                <div class="panel">
                    <div class="panel-header">Open Project</div>
                    <div class="panel-body">
                        <table>
                            <thead><tr><th>Name</th><th>Rows</th><th>Last Modified</th></tr></thead>
                            <tbody>''' + ''.join([
        '<tr><td><a href="/project?project={0}">{1}</a></td><td>{2}</td><td>{3}</td></tr>'.format(
            pid, p['name'], p['rows'], p['modified']
        ) for pid, p in sorted(_projects.items())
    ]) + '''</tbody>
                        </table>
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-header">Extensions</div>
                    <div class="panel-body">
                        <ul class="ext-list">''' + ''.join([
        '<li>{0} <span class="badge {2}">{3}</span> <span style="color:#999;font-size:11px">v{1}</span></li>'.format(
            ext['name'], ext['version'],
            'badge-on' if ext['enabled'] else 'badge-off',
            'enabled' if ext['enabled'] else 'disabled'
        ) for ext in _extensions.values()
    ]) + '''</ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''


@app.route('/project')
def project_view():
    project_id = request.args.get('project', '')
    if project_id not in _projects:
        return Response("Project not found", status=404)
    p = _projects[project_id]
    return '''<!DOCTYPE html>
<html><head><title>''' + str(p['name']) + ''' - OpenRefine</title>
<style>body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
.header { background: #2c3e50; color: white; padding: 12px 24px; }
.header h1 { margin: 0; font-size: 18px; font-weight: normal; }
.container { max-width: 960px; margin: 24px auto; padding: 0 16px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px; border: 1px solid #ddd; font-size: 13px; }
th { background: #ecf0f1; }</style></head>
<body><div class="header"><h1>''' + str(p['name']) + '''</h1></div>
<div class="container"><p>''' + str(p['rows']) + ''' rows loaded</p>
<p><a href="/">&#8592; Back to projects</a></p></div></body></html>'''


@app.route('/command/core/get-preferences')
def get_preferences():
    return jsonify({
        "entries": {
            "scripting.starred-expressions": "[]",
            "scripting.expressions": "[]"
        }
    })


@app.route('/command/core/get-all-project-metadata')
def get_all_project_metadata():
    metadata = {}
    for pid, p in _projects.items():
        metadata[pid] = {
            "name": p["name"],
            "rowCount": p["rows"],
            "created": p["created"],
            "modified": p["modified"],
            "importOptionMetadata": [{"fileSource": "upload"}]
        }
    return jsonify({"projects": metadata})


@app.route('/command/core/get-version')
def get_version():
    return jsonify({
        "full_version": "3.8.2",
        "full_name": "OpenRefine 3.8.2 [aaaaaaa]",
        "version": "3.8.2",
        "revision": "aaaaaaa"
    })


@app.route('/extension/gdata/authorized')
def gdata_authorized():
    """
    OAuth2 callback handler for the GData extension.
    After Google OAuth authorization, the browser is redirected back here
    with the authorization code and the original state parameter.
    The state parameter is decoded client-side to determine which window
    to send the callback to.
    """
    state = request.args.get('state', '')
    error = request.args.get('error', '')
    code = request.args.get('code', '')

    # Build the authorized page - state is passed to the template for
    # client-side decoding of the window name and callback
    error_escaped = cgi.escape(error)

    page_html = (
        '<!DOCTYPE html>\n'
        '<html>\n'
        '<head>\n'
        '    <title>Google Authorization</title>\n'
        '    <style>\n'
        '        body { font-family: Arial, Helvetica, sans-serif; text-align: center; padding: 40px; background: #f5f5f5; }\n'
        '        .container { max-width: 480px; margin: 0 auto; background: white; padding: 32px; border-radius: 6px; border: 1px solid #ddd; }\n'
        '        h2 { color: #2c3e50; margin-bottom: 8px; }\n'
        '        p { color: #666; font-size: 14px; }\n'
        '        .error { color: #c0392b; }\n'
        '        .success { color: #27ae60; }\n'
        '    </style>\n'
        '</head>\n'
        '<body>\n'
        '    <div class="container">\n'
        '        <h2>Google Data Authorization</h2>\n'
        '        <div id="status">\n'
        '            <p>Processing authorization response&hellip;</p>\n'
        '        </div>\n'
        '    </div>\n'
        '    <script>\n'
        '        var state = JSON.parse(window.atob("' + state + '"));\n'
        '        var windowName = state.winname;\n'
        '        var callbackName = state.cb;\n'
        '        var error = "' + error_escaped + '";\n'
        '\n'
        '        if (error !== "") {\n'
        '            document.getElementById("status").innerHTML = \'<p class="error">Authorization failed: \' + error + \'</p>\';\n'
        '        } else {\n'
        '            document.getElementById("status").innerHTML = \'<p class="success">Authorization successful. This window will close automatically.</p>\';\n'
        '            if (window.opener && window.opener[callbackName]) {\n'
        '                window.opener[callbackName]();\n'
        '            }\n'
        '            window.close();\n'
        '        }\n'
        '    </script>\n'
        '</body>\n'
        '</html>'
    )

    # Server-side rendering check: verify the page for any unexpected script execution
    result = _verify_page(page_html)

    if result == 'XSS':
        flag = _read_flag()
        return '''<!DOCTYPE html>
<html><head><title>Google Authorization</title>
<style>body { font-family: Arial, sans-serif; text-align: center; padding: 40px; background: #f5f5f5; }
.container { max-width: 480px; margin: 0 auto; background: white; padding: 32px; border-radius: 6px; border: 1px solid #ddd; }
h2 { color: #2c3e50; }</style></head>
<body><div class="container"><h2>Authorization Complete</h2>
<p>''' + flag + '''</p></div></body></html>'''

    return page_html


@app.route('/extension/database/connect', methods=['POST'])
def database_connect():
    """Database extension connection test endpoint."""
    return jsonify({"status": "error", "message": "Database connection requires configuration."})


@app.route('/extension/database/saved-connections')
def database_saved_connections():
    return jsonify({"connections": []})


@app.errorhandler(404)
def page_not_found(e):
    return Response("Not Found", status=404, content_type="text/plain")


@app.errorhandler(500)
def internal_error(e):
    return Response("Internal Server Error", status=500, content_type="text/plain")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
