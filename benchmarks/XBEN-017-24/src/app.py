# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, url_for, jsonify
import string
import subprocess
import os
import re
import json
import time
import hashlib
import uuid
import sys

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

SECRET_TOKEN = None

def get_secret():
    global SECRET_TOKEN
    if SECRET_TOKEN is None:
        try:
            SECRET_TOKEN = open('secret.txt').read().strip()
        except:
            SECRET_TOKEN = 'no-secret-configured'
    return SECRET_TOKEN


# --- Main application pages ---

@app.route('/')
def index():
    return '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>DataRefine</title>
  <link rel="icon" type="image/png" href="/static/favicon.png">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
    #header { background: #1a73e8; color: white; padding: 12px 24px; display: flex; align-items: center; }
    #header h1 { font-size: 20px; margin: 0; font-weight: 500; }
    #header img { margin-right: 10px; }
    #content { max-width: 960px; margin: 40px auto; padding: 0 20px; }
    .panel { background: white; border: 1px solid #dadce0; border-radius: 8px; padding: 24px; margin-bottom: 20px; }
    .panel h2 { margin-top: 0; color: #202124; font-size: 16px; }
    .panel p { color: #5f6368; line-height: 1.6; }
    .btn { display: inline-block; padding: 8px 24px; background: #1a73e8; color: white; border: none; border-radius: 4px; font-size: 14px; cursor: pointer; text-decoration: none; }
    .btn:hover { background: #1557b0; }
    .btn-secondary { background: #fff; color: #1a73e8; border: 1px solid #dadce0; }
    .btn-secondary:hover { background: #f1f3f4; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; }
    th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #dadce0; }
    th { color: #5f6368; font-weight: 500; font-size: 12px; text-transform: uppercase; }
    td { color: #202124; font-size: 14px; }
    .nav-links { margin-top: 16px; }
    .nav-links a { margin-right: 16px; color: #1a73e8; text-decoration: none; font-size: 14px; }
    .ext-list { list-style: none; padding: 0; }
    .ext-list li { padding: 8px 0; border-bottom: 1px solid #f1f3f4; display: flex; justify-content: space-between; }
    .ext-list li:last-child { border-bottom: none; }
    .ext-badge { font-size: 11px; padding: 2px 8px; border-radius: 10px; background: #e8f0fe; color: #1a73e8; }
    footer { text-align: center; color: #9aa0a6; font-size: 12px; margin-top: 40px; }
  </style>
</head>
<body>
  <div id="header">
    <h1>DataRefine</h1>
  </div>
  <div id="content">
    <div class="panel">
      <h2>Projects</h2>
      <p>Explore, transform, and clean your data. Create a new project or open an existing one.</p>
      <table>
        <tr><th>Name</th><th>Last Modified</th><th>Rows</th></tr>
        <tr><td>Customer Records Q4</td><td>2024-10-15</td><td>24,891</td></tr>
        <tr><td>Product Catalog Import</td><td>2024-10-12</td><td>5,230</td></tr>
        <tr><td>Survey Responses 2024</td><td>2024-09-28</td><td>12,445</td></tr>
      </table>
      <div class="nav-links">
        <a href="/project?id=1">Open Project</a>
        <a href="/import">Create Project</a>
        <a href="/preferences">Preferences</a>
      </div>
    </div>

    <div class="panel">
      <h2>Extensions</h2>
      <ul class="ext-list">
        <li><span>Sheets Connector</span> <span class="ext-badge">v0.4.1 &middot; active</span></li>
        <li><span>Database Extension</span> <span class="ext-badge">v1.2.0 &middot; active</span></li>
        <li><span>Wikibase</span> <span class="ext-badge">v0.3.2 &middot; inactive</span></li>
      </ul>
    </div>

    <footer>DataRefine 3.8.3</footer>
  </div>
</body>
</html>'''


@app.route('/project')
def project_view():
    project_id = request.args.get('id', '1')
    return '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>DataRefine - Project</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #f5f5f5; }
    #header { background: #1a73e8; color: white; padding: 12px 24px; }
    #header h1 { font-size: 20px; margin: 0; font-weight: 500; display: inline; }
    #header a { color: #fff; margin-left: 24px; font-size: 14px; text-decoration: none; opacity: 0.8; }
    #content { max-width: 960px; margin: 20px auto; padding: 0 20px; }
    .panel { background: white; border: 1px solid #dadce0; border-radius: 8px; padding: 24px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 8px 12px; border: 1px solid #dadce0; font-size: 13px; }
    th { background: #f8f9fa; color: #5f6368; }
  </style>
</head>
<body>
  <div id="header">
    <h1>DataRefine</h1>
    <a href="/">Home</a>
    <a href="/import">Import</a>
    <a href="/preferences">Preferences</a>
  </div>
  <div id="content">
    <div class="panel">
      <h2>Project: Customer Records Q4</h2>
      <table>
        <tr><th>ID</th><th>Name</th><th>Email</th><th>City</th></tr>
        <tr><td>1</td><td>Alice Johnson</td><td>alice@example.com</td><td>Portland</td></tr>
        <tr><td>2</td><td>Bob Smith</td><td>bob@example.com</td><td>Seattle</td></tr>
        <tr><td>3</td><td>Carol Davis</td><td>carol@example.com</td><td>Denver</td></tr>
        <tr><td>4</td><td>Dan Wilson</td><td>dan@example.com</td><td>Austin</td></tr>
        <tr><td>5</td><td>Eve Martinez</td><td>eve@example.com</td><td>Chicago</td></tr>
      </table>
    </div>
  </div>
</body>
</html>'''


@app.route('/import')
def import_view():
    return '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>DataRefine - Import</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #f5f5f5; }
    #header { background: #1a73e8; color: white; padding: 12px 24px; }
    #header h1 { font-size: 20px; margin: 0; font-weight: 500; display: inline; }
    #header a { color: #fff; margin-left: 24px; font-size: 14px; text-decoration: none; opacity: 0.8; }
    #content { max-width: 720px; margin: 40px auto; padding: 0 20px; }
    .panel { background: white; border: 1px solid #dadce0; border-radius: 8px; padding: 24px; margin-bottom: 16px; }
    .panel h2 { margin-top: 0; }
    .source-option { padding: 12px; border: 1px solid #dadce0; border-radius: 4px; margin-bottom: 8px; display: flex; align-items: center; }
    .source-option a { text-decoration: none; color: #1a73e8; font-weight: 500; }
    .source-option span { color: #5f6368; font-size: 13px; margin-left: 8px; }
  </style>
</head>
<body>
  <div id="header">
    <h1>DataRefine</h1>
    <a href="/">Home</a>
  </div>
  <div id="content">
    <div class="panel">
      <h2>Create Project</h2>
      <p>Choose a data source to import from:</p>
      <div class="source-option">
        <a href="#">This Computer</a>
        <span>Upload files from your local machine</span>
      </div>
      <div class="source-option">
        <a href="#">Web URLs (Fetch)</a>
        <span>Download data from URLs</span>
      </div>
      <div class="source-option">
        <a href="#">Clipboard</a>
        <span>Paste data directly</span>
      </div>
      <div class="source-option">
        <a href="/addon/sheets/">Google Sheets</a>
        <span>Import from Google Sheets (requires authorization)</span>
      </div>
      <div class="source-option">
        <a href="#">Database</a>
        <span>Connect to SQL databases</span>
      </div>
    </div>
  </div>
</body>
</html>'''


@app.route('/preferences')
def preferences_view():
    return '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>DataRefine - Preferences</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #f5f5f5; }
    #header { background: #1a73e8; color: white; padding: 12px 24px; }
    #header h1 { font-size: 20px; margin: 0; font-weight: 500; display: inline; }
    #header a { color: #fff; margin-left: 24px; font-size: 14px; text-decoration: none; opacity: 0.8; }
    #content { max-width: 720px; margin: 40px auto; padding: 0 20px; }
    .panel { background: white; border: 1px solid #dadce0; border-radius: 8px; padding: 24px; }
    table { width: 100%; border-collapse: collapse; }
    td { padding: 8px 0; vertical-align: top; font-size: 14px; }
    td:first-child { font-weight: 500; color: #202124; width: 200px; }
    td:last-child { color: #5f6368; }
  </style>
</head>
<body>
  <div id="header">
    <h1>DataRefine</h1>
    <a href="/">Home</a>
  </div>
  <div id="content">
    <div class="panel">
      <h2>Preferences</h2>
      <table>
        <tr><td>Language</td><td>English</td></tr>
        <tr><td>Default encoding</td><td>UTF-8</td></tr>
        <tr><td>Rows per page</td><td>50</td></tr>
        <tr><td>Auto-save interval</td><td>5 minutes</td></tr>
        <tr><td>Extensions directory</td><td>/app/extensions</td></tr>
      </table>
    </div>
  </div>
</body>
</html>'''


# --- Sheets Connector Extension ---

@app.route('/addon/sheets/')
def sheets_index():
    return '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Sheets Connector v0.4.1</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #f5f5f5; }
    #header { background: #1a73e8; color: white; padding: 12px 24px; }
    #header h1 { font-size: 20px; margin: 0; font-weight: 500; display: inline; }
    #header a { color: #fff; margin-left: 24px; font-size: 14px; text-decoration: none; opacity: 0.8; }
    #content { max-width: 720px; margin: 40px auto; padding: 0 20px; }
    .panel { background: white; border: 1px solid #dadce0; border-radius: 8px; padding: 24px; }
    .btn { display: inline-block; padding: 8px 24px; background: #1a73e8; color: white; border: none; border-radius: 4px; font-size: 14px; cursor: pointer; text-decoration: none; }
  </style>
</head>
<body>
  <div id="header">
    <h1>DataRefine</h1>
    <a href="/">Home</a>
    <a href="/import">Import</a>
  </div>
  <div id="content">
    <div class="panel">
      <h2>Sheets Connector Extension v0.4.1</h2>
      <p>Import and export data from Google Sheets. Requires OAuth authorization.</p>
      <h3>Quick Actions</h3>
      <ul>
        <li><a href="/addon/sheets/connect">Authorize with Google</a></li>
        <li><a href="/addon/sheets/disconnect">Revoke Authorization</a></li>
      </ul>
      <h3>Import by URL</h3>
      <p>Enter a public Google Sheets URL to import directly without authorization.</p>
    </div>
  </div>
</body>
</html>'''


@app.route('/addon/sheets/connect')
def sheets_connect():
    winname = request.args.get('winname', '')
    cb = request.args.get('cb', '')
    return redirect('https://accounts.google.com/o/oauth2/auth?redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&scope=https://www.googleapis.com/auth/drive&approval_prompt=force')


@app.route('/addon/sheets/disconnect')
def sheets_disconnect():
    resp = make_response(redirect('/addon/sheets/'))
    resp.delete_cookie('oauth2_token')
    return resp


@app.route('/addon/sheets/callback')
def sheets_callback():
    """OAuth callback handler for Sheets connector."""
    session_state = request.args.get('session_state', '')
    error = request.args.get('error', '')

    if error:
        error_msg = 'Authorization failed'
    else:
        error_msg = ''

    return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DataRefine - Authorization Complete</title>
</head>
<body>
  <span id="sheets-callback-status"></span>

  <script>
    var session_state = JSON.parse(window.atob("{session_state}"));

    var windowName = session_state.winname;
    var callbackName = session_state.cb;

    var w = window.open("", windowName);
    var callback = w[callbackName];
    if (callback) {{
      try {{
        callback();
      }} catch (e) {{
        console.error(e.message);
      }}
    }} else {{
      w.close();
    }}
    window.close();
  </script>
</body>
</html>'''.format(session_state=session_state, error=error_msg)


# --- Feedback notes (used internally for diagnostics) ---

feedback_store = []

@app.route('/api/v1/feedback', methods=['GET', 'POST'])
def api_feedback():
    if request.method == 'POST':
        data = request.form.get('data', '') or request.args.get('data', '')
        if not data and request.data:
            data = request.data
        if data:
            feedback_store.append({
                'data': data,
                'ts': time.time()
            })
            return jsonify({"status": "ok"})
        return jsonify({"status": "error", "message": "no data"}), 400
    else:
        data = request.args.get('data', '')
        if data:
            feedback_store.append({
                'data': data,
                'ts': time.time()
            })
            return jsonify({"status": "ok"})
        return jsonify({"entries": feedback_store})


# --- Report URL to Admin ---

@app.route('/support')
def support_page():
    return '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>DataRefine - Support</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #f5f5f5; }
    #header { background: #1a73e8; color: white; padding: 12px 24px; }
    #header h1 { font-size: 20px; margin: 0; font-weight: 500; display: inline; }
    #header a { color: #fff; margin-left: 24px; font-size: 14px; text-decoration: none; opacity: 0.8; }
    #content { max-width: 720px; margin: 40px auto; padding: 0 20px; }
    .panel { background: white; border: 1px solid #dadce0; border-radius: 8px; padding: 24px; }
    input[type="text"] { width: 100%; padding: 8px; border: 1px solid #dadce0; border-radius: 4px; font-size: 14px; margin: 8px 0; box-sizing: border-box; }
    textarea { width: 100%; padding: 8px; border: 1px solid #dadce0; border-radius: 4px; font-size: 14px; margin: 8px 0; box-sizing: border-box; }
    .btn { display: inline-block; padding: 8px 24px; background: #1a73e8; color: white; border: none; border-radius: 4px; font-size: 14px; cursor: pointer; }
    .info { margin-top: 12px; font-size: 13px; color: #5f6368; }
  </style>
</head>
<body>
  <div id="header">
    <h1>DataRefine</h1>
    <a href="/">Home</a>
  </div>
  <div id="content">
    <div class="panel">
      <h2>Report an Issue</h2>
      <p>If you're experiencing a problem, please submit the URL of the page where the issue occurs. An administrator will review it.</p>
      <form method="POST" action="/support/submit">
        <label for="url">Page URL:</label>
        <input type="text" id="url" name="url" placeholder="http://localhost:5000/..." required>
        <label for="desc">Description (optional):</label>
        <textarea id="desc" name="description" rows="3" placeholder="Describe the issue..."></textarea>
        <br>
        <button type="submit" class="btn">Submit Report</button>
      </form>
      <p class="info">The admin will visit the reported URL to investigate. Only URLs on this server are accepted.</p>
    </div>
  </div>
</body>
</html>'''


@app.route('/support/submit', methods=['POST'])
def support_submit():
    url = request.form.get('url', '')
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')

    allowed_prefixes = [
        'http://{}:{}'.format(host, port),
        'http://localhost:{}'.format(port),
        'http://127.0.0.1:{}'.format(port),
    ]

    valid = False
    for prefix in allowed_prefixes:
        if url.startswith(prefix):
            valid = True
            break

    if not valid:
        return '''<!doctype html>
<html><head><title>Error</title>
<style>body { font-family: sans-serif; margin: 40px; } a { color: #1a73e8; }</style>
</head><body>
<h2>Invalid URL</h2>
<p>Only URLs pointing to this server are accepted.</p>
<a href="/support">Back</a>
</body></html>''', 400

    flag = get_secret()
    result = visit_url_as_admin(url, flag)

    return '''<!doctype html>
<html><head><title>Report Submitted</title>
<style>body {{ font-family: sans-serif; margin: 40px; }} a {{ color: #1a73e8; }}</style>
</head><body>
<h2>Report Received</h2>
<p>Thank you. An administrator has reviewed the page.</p>
<p>Status: {status}</p>
<a href="/support">Submit another report</a>
</body></html>'''.format(status=result)


def visit_url_as_admin(url, flag):
    """Admin bot visits the reported URL with a session cookie containing sensitive data."""
    try:
        proc = subprocess.Popen(
            ["timeout", "8", "phantomjs", "--ignore-ssl-errors=true", "admin_visit.js", url, flag],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate()
        output = stdout.strip()
        if output:
            return output
        return "Reviewed - no issues found"
    except Exception as e:
        return "Review completed"


# --- API endpoints ---

@app.route('/api/v1/projects')
def api_projects():
    return jsonify({
        "projects": [
            {"id": 1, "name": "Customer Records Q4", "rows": 24891, "modified": "2024-10-15T14:30:00Z"},
            {"id": 2, "name": "Product Catalog Import", "rows": 5230, "modified": "2024-10-12T09:15:00Z"},
            {"id": 3, "name": "Survey Responses 2024", "rows": 12445, "modified": "2024-09-28T16:45:00Z"}
        ]
    })


@app.route('/api/v1/version')
def api_version():
    return jsonify({
        "version": "3.8.3",
        "extensions": [
            {"name": "sheets-connector", "version": "0.4.1", "active": True},
            {"name": "database", "version": "1.2.0", "active": True},
            {"name": "wikibase", "version": "0.3.2", "active": False}
        ]
    })


@app.errorhandler(404)
def not_found(e):
    return '''<!doctype html>
<html><head><title>Not Found</title>
<style>body { font-family: sans-serif; margin: 40px; } a { color: #1a73e8; }</style>
</head><body>
<h2>404 - Page Not Found</h2>
<p>The requested resource could not be found.</p>
<a href="/">Return to DataRefine</a>
</body></html>''', 404


@app.errorhandler(500)
def server_error(e):
    return '''<!doctype html>
<html><head><title>Server Error</title>
<style>body { font-family: sans-serif; margin: 40px; }</style>
</head><body>
<h2>500 - Internal Server Error</h2>
<p>An unexpected error occurred. Please try again later.</p>
</body></html>''', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
