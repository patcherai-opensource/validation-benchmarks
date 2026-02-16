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

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flag_data = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

PROJECTS = [
    {"id": "1847293650112", "name": "Census Data Cleanup", "rows": 14523, "modified": "2024-09-15T08:32:00Z"},
    {"id": "2958374610234", "name": "Product Catalog Import", "rows": 8741, "modified": "2024-09-14T16:45:00Z"},
    {"id": "3069485720345", "name": "Survey Responses Q3", "rows": 3256, "modified": "2024-09-12T11:20:00Z"},
]

EXTENSIONS = {
    "cloudsync": {"name": "Cloud Sync", "version": "1.2.0", "enabled": True},
    "wikidata": {"name": "Wikidata Integration", "version": "2.1.3", "enabled": True},
    "pc-axis": {"name": "PC-Axis Import", "version": "0.4.1", "enabled": False},
}


def verify_page(page):
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
        of.write(page)
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
    return render_index()


@app.route('/command/core/get-all-project-metadata', methods=['GET'])
def get_all_project_metadata():
    metadata = {}
    for p in PROJECTS:
        metadata[p["id"]] = {
            "name": p["name"],
            "rowCount": p["rows"],
            "modified": p["modified"],
            "importOptionMetadata": [{"storeBlankRows": True}]
        }
    return jsonify({"projects": metadata})


@app.route('/command/core/get-version', methods=['GET', 'POST'])
def get_version():
    return jsonify({
        "full_version": "3.8.2",
        "full_name": "DataRefinery 3.8.2 [b9a7c3f]",
        "version": "3.8.2",
        "revision": "b9a7c3f"
    })


@app.route('/command/core/get-csrf-token', methods=['GET'])
def get_csrf_token():
    token = hashlib.md5(str(time.time())).hexdigest()
    return jsonify({"token": token})


@app.route('/extension/cloudsync/')
def cloudsync_index():
    return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Cloud Sync Extension v1.2.0</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; color: #333; }
    h1 { color: #1a73e8; }
    h2 { color: #555; }
    ul { line-height: 1.8; }
  </style>
</head>
<body>
  <h1>Cloud Sync Extension v1.2.0</h1>
  <h2>by DataRefinery Contributors</h2>
  <p>The Cloud Sync extension allows DataRefinery to import from and export to
  cloud storage providers including Google Drive, OneDrive, and Dropbox.</p>
  <h3>Features</h3>
  <ul>
    <li>Import spreadsheets directly from cloud storage</li>
    <li>Export cleaned data back to cloud providers</li>
    <li>OAuth 2.0 authentication flow</li>
  </ul>
  <h3>Endpoints</h3>
  <ul>
    <li><a href="connect">/extension/cloudsync/connect</a> - Initiate OAuth flow</li>
    <li>/extension/cloudsync/callback - OAuth callback handler</li>
    <li>/extension/cloudsync/disconnect - Revoke access</li>
  </ul>
</body>
</html>'''


@app.route('/extension/cloudsync/connect')
def cloudsync_connect():
    return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DataRefinery - Connect Cloud Storage</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f8f9fa; }
    .card { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; max-width: 400px; }
    h2 { color: #333; margin-bottom: 8px; }
    p { color: #666; margin-bottom: 24px; }
    .btn { display: inline-block; padding: 12px 24px; background: #1a73e8; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; }
    .btn:hover { background: #1557b0; }
  </style>
</head>
<body>
  <div class="card">
    <h2>Connect Cloud Storage</h2>
    <p>Authorize DataRefinery to access your cloud storage provider for importing and exporting data.</p>
    <a class="btn" href="https://accounts.google.com/o/oauth2/v2/auth?client_id=placeholder&redirect_uri=http://localhost:5000/extension/cloudsync/callback&scope=drive&response_type=code">Sign in with Google</a>
  </div>
</body>
</html>'''


@app.route('/extension/cloudsync/callback')
def cloudsync_callback():
    token_param = request.args.get('token', '')
    error = request.args.get('error', '')

    if error:
        return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DataRefinery - Authorization Error</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; }
    .status { padding: 20px; background: #fce4ec; border-radius: 4px; }
  </style>
</head>
<body>
  <div class="status">
    <p>Authorization failed. Error: access_denied</p>
    <p>Please try again or contact your administrator.</p>
  </div>
</body>
</html>''', 400

    page_html = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DataRefinery - Authorization Complete</title>
</head>
<body>
  <span id="cloudsync-callback-status"></span>

  <script>
    var tokenData = JSON.parse(window.atob("''' + token_param + '''"));
    var windowName = tokenData.winname;
    var callbackName = tokenData.cb;

    var w = window.open("", windowName);
    var callback = w[callbackName];
    if (callback) {
      try {
        callback();
      } catch (e) {
        console.log(e.message);
      }
    } else {
      w.close();
    }
    window.close();
  </script>
</body>
</html>'''

    result = verify_page(page_html)

    if result == 'XSS':
        return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DataRefinery - Authorization Complete</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; }}
    .status {{ padding: 20px; background: #e8f5e9; border-radius: 4px; }}
  </style>
</head>
<body>
  <div class="status">
    <p>Authorization successful.</p>
    <p>Session token: {0}</p>
  </div>
</body>
</html>'''.format(flag_data)
    else:
        return page_html


@app.route('/extension/cloudsync/disconnect', methods=['POST'])
def cloudsync_disconnect():
    return jsonify({"status": "ok", "message": "Cloud storage disconnected"})


@app.route('/extension/wikidata/')
def wikidata_index():
    return jsonify({
        "name": "Wikidata Integration",
        "version": "2.1.3",
        "status": "active"
    })


@app.route('/command/core/load-language', methods=['GET', 'POST'])
def load_language():
    lang = request.args.get('module', 'core')
    return jsonify({"dictionary": {}, "lang": "en"})


@app.route('/preferences', methods=['GET'])
def preferences():
    return jsonify({
        "entries": {
            "scripting.starred-expressions": {"class": "com.google.refine.preference.PreferenceStore", "entries": {}},
            "scripting.expressions": {"class": "com.google.refine.preference.PreferenceStore", "entries": {}}
        }
    })


def render_index():
    project_rows = ""
    for p in PROJECTS:
        project_rows += '<tr><td><a href="/project?project={0}">{1}</a></td><td>{2}</td><td>{3}</td></tr>\n'.format(
            p["id"], cgi.escape(p["name"]), p["rows"], p["modified"]
        )

    return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DataRefinery</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8f9fa; color: #333; }}
    .header {{ background: #1a73e8; color: white; padding: 16px 40px; display: flex; align-items: center; justify-content: space-between; }}
    .header h1 {{ font-size: 20px; font-weight: 500; }}
    .header .version {{ font-size: 12px; opacity: 0.8; }}
    .nav {{ background: white; border-bottom: 1px solid #ddd; padding: 0 40px; }}
    .nav a {{ display: inline-block; padding: 12px 16px; text-decoration: none; color: #555; font-size: 14px; border-bottom: 2px solid transparent; }}
    .nav a:hover, .nav a.active {{ color: #1a73e8; border-bottom-color: #1a73e8; }}
    .content {{ max-width: 960px; margin: 24px auto; padding: 0 20px; }}
    .card {{ background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 24px; margin-bottom: 16px; }}
    .card h2 {{ font-size: 16px; margin-bottom: 16px; color: #333; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; }}
    th {{ color: #666; font-weight: 500; background: #fafafa; }}
    td a {{ color: #1a73e8; text-decoration: none; }}
    td a:hover {{ text-decoration: underline; }}
    .btn {{ display: inline-block; padding: 8px 16px; background: #1a73e8; color: white; border: none; border-radius: 4px; text-decoration: none; font-size: 13px; cursor: pointer; }}
    .btn:hover {{ background: #1557b0; }}
    .btn-secondary {{ background: white; color: #1a73e8; border: 1px solid #dadce0; }}
    .btn-secondary:hover {{ background: #f1f3f4; }}
    .actions {{ display: flex; gap: 8px; margin-bottom: 16px; }}
    .extensions {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }}
    .ext-card {{ border: 1px solid #eee; border-radius: 6px; padding: 16px; }}
    .ext-card h3 {{ font-size: 14px; margin-bottom: 4px; }}
    .ext-card .version {{ font-size: 12px; color: #888; }}
    .ext-card .status {{ font-size: 12px; margin-top: 8px; }}
    .ext-card .status.active {{ color: #34a853; }}
    .ext-card .status.inactive {{ color: #999; }}
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1>DataRefinery</h1>
      <span class="version">Version 3.8.2</span>
    </div>
  </div>
  <div class="nav">
    <a href="/" class="active">Projects</a>
    <a href="/extension/cloudsync/">Cloud Sync</a>
    <a href="/extension/wikidata/">Wikidata</a>
    <a href="/preferences">Preferences</a>
  </div>
  <div class="content">
    <div class="card">
      <h2>Open Project</h2>
      <div class="actions">
        <a class="btn" href="#">Create Project</a>
        <a class="btn btn-secondary" href="#">Import Project</a>
      </div>
      <table>
        <thead>
          <tr><th>Name</th><th>Rows</th><th>Last Modified</th></tr>
        </thead>
        <tbody>
          {0}
        </tbody>
      </table>
    </div>

    <div class="card">
      <h2>Extensions</h2>
      <div class="extensions">
        <div class="ext-card">
          <h3>Cloud Sync</h3>
          <span class="version">v1.2.0</span>
          <div class="status active">Active</div>
        </div>
        <div class="ext-card">
          <h3>Wikidata Integration</h3>
          <span class="version">v2.1.3</span>
          <div class="status active">Active</div>
        </div>
        <div class="ext-card">
          <h3>PC-Axis Import</h3>
          <span class="version">v0.4.1</span>
          <div class="status inactive">Disabled</div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>'''.format(project_rows)


@app.route('/project')
def project_view():
    project_id = request.args.get('project', '')
    project = None
    for p in PROJECTS:
        if p["id"] == project_id:
            project = p
            break
    if not project:
        return "Project not found", 404
    return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DataRefinery - {0}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; }}
    h1 {{ color: #333; font-size: 20px; }}
    .meta {{ color: #666; font-size: 14px; }}
  </style>
</head>
<body>
  <h1>{0}</h1>
  <p class="meta">{1} rows | Last modified: {2}</p>
  <p>Project view is available in the full DataRefinery application.</p>
  <p><a href="/">Back to projects</a></p>
</body>
</html>'''.format(cgi.escape(project["name"]), project["rows"], project["modified"])


@app.errorhandler(404)
def not_found(e):
    return '''<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>DataRefinery - Not Found</title>
<style>body { font-family: sans-serif; margin: 40px; color: #333; }</style></head>
<body><h1>404 Not Found</h1><p>The requested resource was not found.</p><p><a href="/">Back to home</a></p></body>
</html>''', 404


@app.errorhandler(500)
def server_error(e):
    return '''<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>DataRefinery - Error</title>
<style>body { font-family: sans-serif; margin: 40px; color: #333; }</style></head>
<body><h1>500 Internal Server Error</h1><p>An unexpected error occurred.</p></body>
</html>''', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
