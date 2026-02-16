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
    {"id": 1829384756, "name": "Customer Survey Q3 2024", "rows": 14523, "modified": "2024-09-28T14:32:00Z", "creator": "admin"},
    {"id": 2038475610, "name": "Product Inventory Export", "rows": 8741, "modified": "2024-10-01T09:15:00Z", "creator": "warehouse"},
    {"id": 3192847560, "name": "Sales Data Analysis", "rows": 52390, "modified": "2024-10-03T16:45:00Z", "creator": "analytics"},
    {"id": 4028374651, "name": "Employee Records Import", "rows": 1205, "modified": "2024-09-15T11:20:00Z", "creator": "hr"},
]


@app.route('/')
def index():
    project_rows = ""
    for p in PROJECTS:
        project_rows += '<tr><td><a href="/project?id={0}">{1}</a></td><td>{2}</td><td>{3}</td><td>{4}</td></tr>\n'.format(
            p["id"], cgi.escape(p["name"]), p["rows"], p["modified"], p["creator"]
        )
    return '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>DataRefine</title>
  <link rel="icon" type="image/png" href="/static/assets/fav-icon.png">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
    #header {{ background: #1a1a2e; color: white; padding: 12px 24px; display: flex; align-items: center; }}
    #header h1 {{ margin: 0; font-size: 20px; font-weight: 500; }}
    #header img {{ margin-right: 10px; }}
    .container {{ max-width: 960px; margin: 30px auto; padding: 0 20px; }}
    .panel {{ background: white; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 24px; margin-bottom: 20px; }}
    h2 {{ color: #333; font-size: 16px; margin-top: 0; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{ text-align: left; padding: 8px 12px; border-bottom: 2px solid #e0e0e0; color: #666; font-size: 12px; text-transform: uppercase; }}
    td {{ padding: 8px 12px; border-bottom: 1px solid #f0f0f0; font-size: 14px; }}
    td a {{ color: #1a73e8; text-decoration: none; }}
    td a:hover {{ text-decoration: underline; }}
    .sidebar {{ display: flex; gap: 20px; }}
    .sidebar-links {{ min-width: 200px; }}
    .sidebar-links a {{ display: block; padding: 8px 12px; color: #333; text-decoration: none; font-size: 14px; border-radius: 4px; }}
    .sidebar-links a:hover {{ background: #e8f0fe; }}
    .main-content {{ flex: 1; }}
    .btn {{ display: inline-block; padding: 8px 16px; background: #1a73e8; color: white; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; font-size: 13px; }}
    .btn:hover {{ background: #1557b0; }}
    .btn-secondary {{ background: #fff; color: #333; border: 1px solid #dadce0; }}
    .btn-secondary:hover {{ background: #f5f5f5; }}
    .actions {{ margin-top: 16px; }}
  </style>
</head>
<body>
  <div id="header">
    <img src="/static/assets/fav-icon.png" width="28" height="28" alt="">
    <h1>DataRefine</h1>
  </div>
  <div class="container">
    <div class="sidebar">
      <div class="sidebar-links">
        <a href="/">Projects</a>
        <a href="/extension/clouddata/">Cloud Import</a>
        <a href="/preferences">Preferences</a>
      </div>
      <div class="main-content">
        <div class="panel">
          <h2>Existing Projects</h2>
          <table>
            <tr><th>Name</th><th>Rows</th><th>Last Modified</th><th>Creator</th></tr>
            {0}
          </table>
          <div class="actions">
            <a class="btn" href="/extension/clouddata/">Import from Cloud</a>
            <a class="btn btn-secondary" href="#">Create Project</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>'''.format(project_rows)


@app.route('/project')
def project_view():
    pid = request.args.get('id', '')
    proj = None
    for p in PROJECTS:
        if str(p["id"]) == pid:
            proj = p
            break
    if not proj:
        return '<html><body><h1>Project not found</h1><p><a href="/">Back to projects</a></p></body></html>', 404

    return '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>DataRefine - {name}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #f5f5f5; }}
    #header {{ background: #1a1a2e; color: white; padding: 12px 24px; display: flex; align-items: center; }}
    #header h1 {{ margin: 0; font-size: 20px; font-weight: 500; }}
    .container {{ max-width: 960px; margin: 30px auto; padding: 0 20px; }}
    .panel {{ background: white; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 24px; }}
    h2 {{ margin-top: 0; }}
    .meta {{ color: #666; font-size: 13px; }}
  </style>
</head>
<body>
  <div id="header">
    <a href="/" style="color:white;text-decoration:none;display:flex;align-items:center;">
      <img src="/static/assets/fav-icon.png" width="28" height="28" alt="" style="margin-right:10px;">
      <h1>DataRefine</h1>
    </a>
  </div>
  <div class="container">
    <div class="panel">
      <h2>{name}</h2>
      <p class="meta">Project ID: {pid} &middot; {rows} rows &middot; Last modified: {modified}</p>
      <p>Use the facets and filters on the left to explore and clean your data.</p>
    </div>
  </div>
</body>
</html>'''.format(name=cgi.escape(proj["name"]), pid=proj["id"], rows=proj["rows"], modified=proj["modified"])


@app.route('/preferences')
def preferences():
    return '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>DataRefine - Preferences</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #f5f5f5; }
    #header { background: #1a1a2e; color: white; padding: 12px 24px; }
    #header h1 { margin: 0; font-size: 20px; font-weight: 500; }
    .container { max-width: 960px; margin: 30px auto; padding: 0 20px; }
    .panel { background: white; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 24px; }
    h2 { margin-top: 0; }
    label { display: block; margin: 12px 0 4px; font-size: 14px; color: #333; }
    input[type="text"], select { padding: 8px; border: 1px solid #dadce0; border-radius: 4px; width: 300px; }
  </style>
</head>
<body>
  <div id="header"><h1>DataRefine - Preferences</h1></div>
  <div class="container">
    <div class="panel">
      <h2>Application Settings</h2>
      <label>Default encoding:</label>
      <select><option>UTF-8</option><option>ISO-8859-1</option><option>Windows-1252</option></select>
      <label>Max rows to display:</label>
      <input type="text" value="50">
      <label>User interface language:</label>
      <select><option>English</option><option>Spanish</option><option>French</option><option>German</option></select>
    </div>
  </div>
</body>
</html>'''


@app.route('/extension/clouddata/')
def clouddata_index():
    return '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>DataRefine - Cloud Data Import</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #f5f5f5; }
    #header { background: #1a1a2e; color: white; padding: 12px 24px; }
    #header h1 { margin: 0; font-size: 20px; font-weight: 500; }
    .container { max-width: 960px; margin: 30px auto; padding: 0 20px; }
    .panel { background: white; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 24px; margin-bottom: 20px; }
    h2 { margin-top: 0; }
    .btn { display: inline-block; padding: 10px 20px; background: #1a73e8; color: white; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; font-size: 14px; }
    .btn:hover { background: #1557b0; }
    .info { color: #666; font-size: 13px; margin-top: 8px; }
  </style>
</head>
<body>
  <div id="header"><h1>DataRefine - Cloud Data Extension</h1></div>
  <div class="container">
    <div class="panel">
      <h2>Cloud Data Import</h2>
      <p>Import data directly from cloud spreadsheets and documents. Sign in with your cloud provider to get started.</p>
      <a class="btn" href="/extension/clouddata/connect">Sign in to Cloud Provider</a>
      <p class="info">You will be redirected to authorize access to your cloud documents.</p>
    </div>
    <div class="panel">
      <h2>Import by URL</h2>
      <p>Paste the URL of a publicly shared cloud spreadsheet:</p>
      <form action="/extension/clouddata/import" method="get">
        <input type="text" name="url" placeholder="https://docs.example.com/spreadsheet/..." style="padding:8px;width:500px;border:1px solid #dadce0;border-radius:4px;">
        <button type="submit" class="btn" style="margin-left:8px;">Next &raquo;</button>
      </form>
    </div>
  </div>
</body>
</html>'''


@app.route('/extension/clouddata/connect')
def clouddata_connect():
    return '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>DataRefine - Authorize</title>
  <style>body { font-family: sans-serif; text-align: center; padding-top: 100px; }</style>
</head>
<body>
  <p>Redirecting to cloud provider for authorization...</p>
  <script>
    window.setTimeout(function() {
      document.location.href = "/extension/clouddata/callback?token=&error=access_denied";
    }, 2000);
  </script>
</body>
</html>'''


def render_callback_page(token_param):
    return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DataRefine - Authorized</title>
</head>
<body>
  <span id="clouddata-authorized"></span>

  <script>
    var token = JSON.parse(window.atob("{token_value}"));

    var windowName = token.winname;
    var callbackName = token.cb;

    var w = window.open("", windowName);
    var callback = w[callbackName];
    if (callback) {{
      try {{
        callback();
      }} catch (e) {{
        alert(e.message);
      }}
    }} else {{
      w.close();
    }}
    window.close();
  </script>
</body>
</html>'''.format(token_value=token_param)


@app.route('/extension/clouddata/callback')
def clouddata_callback():
    token_param = request.args.get('token', '')
    page_html = render_callback_page(token_param)

    if token_param:
        result = evaluate_page(page_html)
        if result == 'XSS':
            return '''<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>DataRefine - Authorized</title>
<style>body {{ font-family: sans-serif; margin: 40px; }}</style></head>
<body><h2>Authorization Complete</h2><p>{0}</p></body></html>'''.format(flag_data)

    return page_html


@app.route('/extension/clouddata/import')
def clouddata_import():
    url = request.args.get('url', '')
    if not url:
        return redirect('/extension/clouddata/')
    return '''<!doctype html>
<html>
<head><meta charset="utf-8"><title>DataRefine - Import</title>
<style>body {{ font-family: sans-serif; margin: 40px; }}</style>
</head>
<body>
<h2>Importing from URL</h2>
<p>Source: {0}</p>
<p>Processing... This feature requires a valid cloud spreadsheet URL.</p>
<p><a href="/extension/clouddata/">Back</a></p>
</body></html>'''.format(cgi.escape(url))


@app.route('/command/core/get-version')
def get_version():
    return jsonify({"version": "3.8.3", "revision": "a1b2c3d"})


@app.route('/command/core/get-all-project-metadata')
def get_all_project_metadata():
    meta = {}
    for p in PROJECTS:
        meta[str(p["id"])] = {
            "name": p["name"],
            "rowCount": p["rows"],
            "modified": p["modified"],
            "creator": p["creator"]
        }
    return jsonify({"projects": meta})


def evaluate_page(page_content):
    proc = subprocess.Popen(["timeout", "8", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('SERVICE_HOST', 'localhost')
    port = os.getenv('SERVICE_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except:
        result = ''
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result


@app.route('/extension/clouddata/verify')
def clouddata_verify():
    token_param = request.args.get('token', '')
    if not token_param:
        return 'Authorization check failed: missing token', 400
    return redirect('/extension/clouddata/callback?token=' + urllib.quote(token_param, safe=''))


@app.errorhandler(404)
def not_found(e):
    return '''<!doctype html>
<html><head><title>DataRefine - Not Found</title>
<style>body { font-family: sans-serif; text-align: center; padding-top: 80px; color: #333; }</style>
</head><body><h1>404</h1><p>The requested resource was not found.</p><p><a href="/">Back to DataRefine</a></p></body></html>''', 404


@app.errorhandler(500)
def server_error(e):
    return '''<!doctype html>
<html><head><title>DataRefine - Error</title>
<style>body { font-family: sans-serif; text-align: center; padding-top: 80px; color: #333; }</style>
</head><body><h1>Internal Server Error</h1><p>An unexpected error occurred.</p></body></html>''', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
