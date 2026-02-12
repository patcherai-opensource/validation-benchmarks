# encoding=utf8
import os
import sys
import json
import subprocess
import logging
import hashlib
import time
import re
import cgi
import threading

from flask import Flask, request, Response, make_response, send_from_directory, redirect, url_for

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder=None)
app.config['PROPAGATE_EXCEPTIONS'] = False

# Read protected data from configuration file
_flag_data = ""
try:
    with open("secret.txt") as f:
        _flag_data = f.read().strip()
except:
    _flag_data = "FLAG{missing}"

# Admin session token (generated at startup)
ADMIN_TOKEN = hashlib.sha256(os.urandom(32)).hexdigest()

# Shared directory for DAV files
DAV_ROOT = "/app/dav_share"
if not os.path.isdir(DAV_ROOT):
    os.makedirs(DAV_ROOT)

# Pre-populate some sample files
_sample_files = {
    "README.txt": "Welcome to WsgiDAV file share.\nThis server provides WebDAV access to shared files.\n",
    "project-notes.txt": "Q4 planning notes - TBD\n",
    "reports/monthly-summary.csv": "month,revenue,expenses\n2022-01,50000,32000\n2022-02,55000,34000\n2022-03,48000,31000\n",
    "reports/annual-review.txt": "Annual review document placeholder.\n",
    "docs/setup-guide.md": "# Setup Guide\n\n1. Install dependencies\n2. Configure server\n3. Start service\n",
}

for fpath, content in _sample_files.items():
    full = os.path.join(DAV_ROOT, fpath)
    d = os.path.dirname(full)
    if not os.path.isdir(d):
        os.makedirs(d)
    if not os.path.isfile(full):
        with open(full, "w") as f:
            f.write(content)

# Server configuration (mutable)
_server_config = {
    "realm": "WsgiDAV File Share",
    "display_name": "admin",
    "enable_dir_browser": True,
    "server_version": "WsgiDAV/4.0.2",
    "allow_anonymous": True,
}

# Store for exfiltrated data (simulates attacker's server)
_exfil_store = {}

# Directory browser HTML template
# Uses Python string formatting for template rendering
DIR_BROWSER_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Directory listing for %(path)s</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 12px 20px; }
        .header h1 { margin: 0; font-size: 18px; font-weight: normal; }
        .header .meta { font-size: 12px; color: #bdc3c7; margin-top: 4px; }
        .container { max-width: 960px; margin: 20px auto; background: white; border: 1px solid #ddd; border-radius: 4px; }
        .breadcrumb { padding: 10px 20px; background: #ecf0f1; border-bottom: 1px solid #ddd; font-size: 13px; }
        .breadcrumb a { color: #2980b9; text-decoration: none; }
        .breadcrumb a:hover { text-decoration: underline; }
        table { width: 100%%; border-collapse: collapse; }
        th { text-align: left; padding: 8px 20px; background: #f8f9fa; border-bottom: 2px solid #ddd; font-size: 13px; color: #555; }
        td { padding: 8px 20px; border-bottom: 1px solid #eee; font-size: 13px; }
        td a { color: #2980b9; text-decoration: none; }
        td a:hover { text-decoration: underline; }
        .icon { margin-right: 6px; }
        .footer { padding: 10px 20px; font-size: 11px; color: #999; border-top: 1px solid #ddd; }
        .upload-form { padding: 10px 20px; border-top: 1px solid #ddd; }
        .upload-form input[type=file] { font-size: 12px; }
        .upload-form button { font-size: 12px; padding: 4px 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>%(server_version)s &mdash; Directory Browser</h1>
        <div class="meta">Authenticated user: &quot;%(user_name)s&quot;, realm: &quot;%(realm)s&quot;, access: read-write.</div>
    </div>
    <div class="container">
        <div class="breadcrumb">%(breadcrumb)s</div>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Last Modified</th>
                </tr>
            </thead>
            <tbody>
%(rows)s
            </tbody>
        </table>
        <div class="upload-form">
            <form method="POST" enctype="multipart/form-data" action="%(upload_action)s">
                <input type="file" name="file"> <button type="submit">Upload</button>
            </form>
        </div>
        <div class="footer">%(trailer)s</div>
    </div>
</body>
</html>"""

ROW_TEMPLATE_DIR = '                <tr><td><span class="icon">&#128193;</span><a href="%(href)s">%(name)s/</a></td><td>Directory</td><td>&mdash;</td><td>%(mtime)s</td></tr>'
ROW_TEMPLATE_FILE = '                <tr><td><span class="icon">&#128196;</span><a href="%(href)s">%(name)s</a></td><td>File</td><td>%(size)s</td><td>%(mtime)s</td></tr>'
ROW_PARENT = '                <tr><td><span class="icon">&#11014;</span><a href="%(href)s">..</a></td><td></td><td></td><td></td></tr>'


def _format_size(size):
    if size < 1024:
        return "%d B" % size
    elif size < 1024 * 1024:
        return "%.1f KB" % (size / 1024.0)
    else:
        return "%.1f MB" % (size / (1024.0 * 1024.0))


def _format_time(ts):
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))


def _build_breadcrumb(path):
    parts = [p for p in path.split("/") if p]
    crumbs = ['<a href="/browse/">root</a>']
    accumulated = "/browse/"
    for p in parts:
        accumulated += p + "/"
        crumbs.append('<a href="%s">%s</a>' % (accumulated, cgi.escape(p)))
    return " / ".join(crumbs)


def _render_directory(dir_path, url_path):
    """Render directory listing using string template formatting."""
    rows = []

    # Parent directory link
    if url_path.rstrip("/") != "/browse":
        parent = "/".join(url_path.rstrip("/").split("/")[:-1]) + "/"
        rows.append(ROW_PARENT % {"href": parent})

    entries = []
    try:
        entries = sorted(os.listdir(dir_path))
    except OSError:
        pass

    dirs = []
    files = []
    for entry in entries:
        full = os.path.join(dir_path, entry)
        if os.path.isdir(full):
            dirs.append(entry)
        elif os.path.isfile(full):
            files.append(entry)

    for d in sorted(dirs):
        full = os.path.join(dir_path, d)
        mtime = _format_time(os.path.getmtime(full))
        href = url_path.rstrip("/") + "/" + d + "/"
        rows.append(ROW_TEMPLATE_DIR % {"href": href, "name": cgi.escape(d), "mtime": mtime})

    for f in sorted(files):
        full = os.path.join(dir_path, f)
        mtime = _format_time(os.path.getmtime(full))
        size = _format_size(os.path.getsize(full))
        href = url_path.rstrip("/") + "/" + f
        rows.append(ROW_TEMPLATE_FILE % {"href": href, "name": cgi.escape(f), "size": size, "mtime": mtime})

    breadcrumb = _build_breadcrumb(url_path.replace("/browse", ""))

    # Build context for template rendering
    context = {
        "path": cgi.escape(url_path),
        "server_version": _server_config["server_version"],
        "user_name": _server_config["display_name"],  # NOT escaped
        "realm": _server_config["realm"],              # NOT escaped
        "breadcrumb": breadcrumb,
        "rows": "\n".join(rows),
        "upload_action": url_path,
        "trailer": "Powered by %s" % _server_config["server_version"],
    }

    return DIR_BROWSER_TEMPLATE % context


@app.route('/')
def index():
    """Server info page"""
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>WsgiDAV Server</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px auto; max-width: 700px; background: #f5f5f5; }
        .card { background: white; border: 1px solid #ddd; border-radius: 4px; padding: 30px; }
        h1 { color: #2c3e50; margin-top: 0; }
        .info { color: #555; font-size: 14px; line-height: 1.8; }
        .info dt { font-weight: bold; }
        a { color: #2980b9; }
        .nav { margin-top: 20px; }
        .nav a { display: inline-block; margin-right: 15px; padding: 6px 14px; background: #2980b9; color: white; text-decoration: none; border-radius: 3px; font-size: 13px; }
        .nav a:hover { background: #3498db; }
    </style>
</head>
<body>
    <div class="card">
        <h1>WsgiDAV/4.0.2</h1>
        <dl class="info">
            <dt>Server</dt><dd>WsgiDAV/4.0.2 Python/2.7</dd>
            <dt>Realm</dt><dd>%s</dd>
            <dt>Directory Browsing</dt><dd>%s</dd>
            <dt>Authentication</dt><dd>Basic (optional)</dd>
        </dl>
        <div class="nav">
            <a href="/browse/">Browse Files</a>
            <a href="/server/config">Server Configuration</a>
            <a href="/report">Report Issue</a>
        </div>
    </div>
</body>
</html>""" % (cgi.escape(_server_config["realm"]),
              "Enabled" if _server_config["enable_dir_browser"] else "Disabled")


@app.route('/browse/', defaults={'subpath': ''})
@app.route('/browse/<path:subpath>')
def browse(subpath):
    """Directory browser endpoint - mirrors WsgiDAV dir_browser"""
    if not _server_config["enable_dir_browser"]:
        return Response("Directory browsing is disabled.", status=403)

    # Resolve filesystem path
    fs_path = os.path.join(DAV_ROOT, subpath)
    fs_path = os.path.normpath(fs_path)

    # Prevent directory traversal
    if not fs_path.startswith(DAV_ROOT):
        return Response("Forbidden", status=403)

    if not os.path.exists(fs_path):
        return Response("Not Found", status=404)

    if os.path.isdir(fs_path):
        url_path = "/browse/" + subpath
        if not url_path.endswith("/"):
            return redirect(url_path + "/")
        html = _render_directory(fs_path, url_path)
        return Response(html, content_type="text/html")
    else:
        # Serve the file
        directory = os.path.dirname(fs_path)
        filename = os.path.basename(fs_path)
        return send_from_directory(directory, filename)


@app.route('/browse/<path:subpath>', methods=['POST'])
def upload_file(subpath):
    """Handle file uploads to the DAV share"""
    fs_path = os.path.join(DAV_ROOT, subpath)
    fs_path = os.path.normpath(fs_path)
    if not fs_path.startswith(DAV_ROOT):
        return Response("Forbidden", status=403)
    if not os.path.isdir(fs_path):
        return Response("Not a directory", status=400)

    if 'file' not in request.files:
        return redirect("/browse/" + subpath)

    f = request.files['file']
    if f.filename:
        # Sanitize filename
        safe_name = re.sub(r'[^\w\.\-]', '_', f.filename)
        dest = os.path.join(fs_path, safe_name)
        if dest.startswith(DAV_ROOT):
            f.save(dest)

    return redirect("/browse/" + subpath)


@app.route('/browse/', methods=['POST'], defaults={'subpath': ''})
def upload_file_root(subpath=''):
    return upload_file('')


@app.route('/server/config', methods=['GET'])
def get_config():
    """Server configuration page"""
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Server Configuration - WsgiDAV</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px auto; max-width: 700px; background: #f5f5f5; }
        .card { background: white; border: 1px solid #ddd; border-radius: 4px; padding: 30px; }
        h1 { color: #2c3e50; margin-top: 0; font-size: 20px; }
        label { display: block; margin-top: 15px; font-weight: bold; font-size: 13px; color: #555; }
        input[type=text] { width: 100%%; padding: 8px; border: 1px solid #ddd; border-radius: 3px; font-size: 13px; margin-top: 4px; box-sizing: border-box; }
        .btn { margin-top: 20px; padding: 8px 20px; background: #2980b9; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 13px; }
        .btn:hover { background: #3498db; }
        .note { font-size: 11px; color: #999; margin-top: 4px; }
        a { color: #2980b9; font-size: 13px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Server Configuration</h1>
        <p style="font-size:13px;color:#666;">Modify the WsgiDAV server display settings. Changes take effect immediately on the directory browser interface.</p>
        <form method="POST" action="/server/config">
            <label for="realm">Realm</label>
            <input type="text" id="realm" name="realm" value="%s">
            <div class="note">Display name for the authentication realm shown in the directory browser.</div>

            <label for="display_name">Display Name</label>
            <input type="text" id="display_name" name="display_name" value="%s">
            <div class="note">Username displayed in the directory browser header.</div>

            <button type="submit" class="btn">Save Configuration</button>
        </form>
        <br>
        <a href="/browse/">&larr; Back to file browser</a>
    </div>
</body>
</html>""" % (cgi.escape(_server_config["realm"], quote=True),
              cgi.escape(_server_config["display_name"], quote=True))


@app.route('/server/config', methods=['POST'])
def update_config():
    """Update server configuration - allows setting realm and display_name"""
    realm = request.form.get('realm', _server_config['realm'])
    display_name = request.form.get('display_name', _server_config['display_name'])

    _server_config['realm'] = realm
    _server_config['display_name'] = display_name

    return redirect('/server/config')


@app.route('/api/config', methods=['GET'])
def api_get_config():
    """REST API for configuration"""
    return Response(
        json.dumps({
            "realm": _server_config["realm"],
            "display_name": _server_config["display_name"],
            "enable_dir_browser": _server_config["enable_dir_browser"],
            "server_version": _server_config["server_version"],
        }),
        content_type="application/json"
    )


@app.route('/api/config', methods=['PUT', 'POST'])
def api_update_config():
    """REST API for updating configuration"""
    try:
        data = request.get_json(force=True)
    except:
        data = {}

    if 'realm' in data:
        _server_config['realm'] = data['realm']
    if 'display_name' in data:
        _server_config['display_name'] = data['display_name']

    return Response(
        json.dumps({"status": "ok", "config": {
            "realm": _server_config["realm"],
            "display_name": _server_config["display_name"],
        }}),
        content_type="application/json"
    )


@app.route('/admin/flag')
def admin_flag():
    """Protected endpoint - only accessible with admin token cookie"""
    token = request.cookies.get('admin_token', '')
    if token == ADMIN_TOKEN:
        return Response(_flag_data, content_type="text/plain")
    return Response("Forbidden", status=403)


@app.route('/report', methods=['GET'])
def report_form():
    """Report a URL for the admin to review"""
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Report URL - WsgiDAV</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px auto; max-width: 700px; background: #f5f5f5; }
        .card { background: white; border: 1px solid #ddd; border-radius: 4px; padding: 30px; }
        h1 { color: #2c3e50; margin-top: 0; font-size: 20px; }
        input[type=text] { width: 100%%; padding: 8px; border: 1px solid #ddd; border-radius: 3px; font-size: 13px; margin-top: 4px; box-sizing: border-box; }
        .btn { margin-top: 15px; padding: 8px 20px; background: #2980b9; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 13px; }
        a { color: #2980b9; font-size: 13px; }
        .msg { padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 3px; color: #155724; font-size: 13px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Report URL to Administrator</h1>
        <p style="font-size:13px;color:#666;">Submit a URL for the server administrator to review. The admin will visit the page in their browser.</p>
        <form method="POST" action="/report">
            <label style="font-weight:bold;font-size:13px;color:#555;">URL</label>
            <input type="text" name="url" placeholder="http://localhost:5000/browse/" style="margin-top:6px;">
            <button type="submit" class="btn">Submit for Review</button>
        </form>
        <br>
        <a href="/">&larr; Back to home</a>
    </div>
</body>
</html>"""


@app.route('/report', methods=['POST'])
def report_submit():
    """Admin bot visits the reported URL with their session cookie"""
    url = request.form.get('url', '')
    if not url:
        return Response("No URL provided", status=400)

    # Validate URL is local
    if not url.startswith('http'):
        url = 'http://localhost:' + os.environ.get('FLASK_PORT', '5000') + url

    def visit_url(target_url, token):
        try:
            proc = subprocess.Popen(
                ["timeout", "10", "phantomjs", "--ignore-ssl-errors=true", "admin_visit.js"],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            payload = json.dumps({"url": target_url, "token": token})
            proc.stdin.write(payload + "\n")
            proc.stdin.close()
            proc.wait()
        except Exception as e:
            logging.error("Bot visit error: %s" % str(e))

    t = threading.Thread(target=visit_url, args=(url, ADMIN_TOKEN))
    t.daemon = True
    t.start()

    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Report Submitted - WsgiDAV</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px auto; max-width: 700px; background: #f5f5f5; }
        .card { background: white; border: 1px solid #ddd; border-radius: 4px; padding: 30px; }
        h1 { color: #2c3e50; margin-top: 0; font-size: 20px; }
        .msg { padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 3px; color: #155724; font-size: 13px; }
        a { color: #2980b9; font-size: 13px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Report Submitted</h1>
        <div class="msg">The administrator will review the submitted URL shortly.</div>
        <br>
        <a href="/">&larr; Back to home</a>
    </div>
</body>
</html>"""


@app.route('/api/log', methods=['POST', 'GET'])
def log_endpoint():
    """Server activity log collector endpoint."""
    if request.method == 'GET':
        data = request.args.get('data', '')
    else:
        data = request.form.get('data', '') or request.data

    if data:
        _exfil_store['latest'] = data
        _exfil_store['timestamp'] = time.time()

    return Response("ok", content_type="text/plain")


@app.route('/api/log/latest', methods=['GET'])
def log_latest():
    """Retrieve latest log entry"""
    if 'latest' in _exfil_store:
        return Response(
            json.dumps({"data": _exfil_store['latest'], "timestamp": _exfil_store.get('timestamp', 0)}),
            content_type="application/json"
        )
    return Response(json.dumps({"data": None}), content_type="application/json")


# Health check endpoint
@app.route('/ping')
def ping():
    return Response("pong", content_type="text/plain")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('FLASK_PORT', '5000')))
