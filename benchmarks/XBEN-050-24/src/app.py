# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, url_for, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import urlparse
import sys
import json
import time
import threading
import hashlib
from datetime import datetime

from jinja2 import Environment, BaseLoader

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24).encode('hex')

# -------------------------------------------------------
# WsgiDAV-like Directory Browser Configuration
# -------------------------------------------------------
# Server configuration - mimics wsgidav.yaml
DAV_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "verbose": 1,
    "dir_browser": {
        "enable": True,
        "response_trailer": True,
        "davmount": False,
        "ms_sharepoint_support": True,
        "libre_office_support": False,
        "show_user": True,
        "show_logout": True,
        "icon": True,
    },
    "simple_dc": {
        "user_mapping": {
            "/": {
                "admin": {"password": None, "roles": ["admin"]},
            }
        }
    },
}

# -------------------------------------------------------
# File storage - simulates a DAV filesystem
# -------------------------------------------------------
SHARE_ROOT = "/python-docker/davshare"

def ensure_share():
    if not os.path.isdir(SHARE_ROOT):
        os.makedirs(SHARE_ROOT)
    sample_dirs = ["Documents", "Projects", "Backups"]
    sample_files = {
        "README.txt": "WsgiDAV shared folder\nSee https://github.com/mar10/wsgidav for documentation.\n",
        "Documents/meeting-notes.txt": "Q3 planning meeting notes\nDate: 2023-06-15\n",
        "Documents/budget-2023.csv": "category,amount\ninfra,45000\npersonnel,120000\n",
        "Projects/roadmap.md": "# Project Roadmap\n\n## Q3 Milestones\n- Feature X\n- Bug fixes\n",
        "Backups/db-snapshot-20230601.sql.gz": "binary_placeholder",
    }
    for d in sample_dirs:
        p = os.path.join(SHARE_ROOT, d)
        if not os.path.isdir(p):
            os.makedirs(p)
    for fname, content in sample_files.items():
        fp = os.path.join(SHARE_ROOT, fname)
        parent = os.path.dirname(fp)
        if not os.path.isdir(parent):
            os.makedirs(parent)
        if not os.path.isfile(fp):
            with open(fp, 'w') as f:
                f.write(content)

ensure_share()

# -------------------------------------------------------
# Directory browser HTML template
# -------------------------------------------------------
DIR_BROWSER_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="generator" content="WsgiDAV/{{ version }}">
  <title>WsgiDAV - Index of {{ display_path }}</title>
  <link rel="shortcut icon" href="/static/favicon.ico">
  <link rel="stylesheet" href="/static/style.css" />
  <style type="text/css"> A {behavior: url(#default#AnchorClick);} </style>
</head>

<body>
  <h1>
    <img class="logo" alt="WsgiDAV" title="WsgiDAV" src="/static/logo.png">
    Index of {{ display_path }}
  </h1>

  {% if user_name and config.show_user %}
  <p class="auth-user">
    Authenticated user: "{{ user_name }}", realm: "{{ realm }}", access: {{ access }}.
  </p>
  {% endif %}

  <hr>

  <table class="dir-listing">
    <colgroup>
      <col>
      <col>
      <col class="right">
      <col class="right">
    </colgroup>
    <thead>
      <tr>
        <th>Name</th>
        <th>Type</th>
        <th>Size</th>
        <th>Last modified</th>
      </tr>
    </thead>
    <tbody>
      {% if not is_root %}
      <tr class="directory">
        <td><a href="..">..</a></td>
        <td>Directory</td>
        <td>-</td>
        <td></td>
      </tr>
      {% endif %}
      {% for row in rows %}
      <tr class="{{ row.tr_class }}">
        <td>
          <a class="{{ row.a_class }}" href="{{ row.href }}">{{ row.display_name }}</a>
        </td>
        <td>{{ row.display_type }}</td>
        <td>{{ row.str_size }}</td>
        <td>{{ row.str_modified }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <hr>

  {% if trailer %}
  <p class="trailer">{{ trailer }}</p>
  {% endif %}

</body>
</html>"""

# Jinja2 template environment for directory browser rendering
template_env = Environment(loader=BaseLoader())
dir_template = template_env.from_string(DIR_BROWSER_TEMPLATE)


def get_file_info(filepath, name):
    """Get file/directory info for directory listing."""
    stat = os.stat(filepath)
    is_dir = os.path.isdir(filepath)
    size = stat.st_size if not is_dir else 0
    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

    if is_dir:
        display_type = "Directory"
        str_size = "-"
    else:
        ext = os.path.splitext(name)[1].lower()
        type_map = {
            '.txt': 'Text', '.md': 'Markdown', '.csv': 'CSV',
            '.py': 'Python', '.js': 'JavaScript', '.html': 'HTML',
            '.sql': 'SQL', '.gz': 'GZip archive', '.zip': 'ZIP archive',
            '.pdf': 'PDF', '.xml': 'XML', '.json': 'JSON',
        }
        display_type = type_map.get(ext, 'File')
        if size < 1024:
            str_size = "{} B".format(size)
        elif size < 1048576:
            str_size = "{:.1f} KB".format(size / 1024.0)
        else:
            str_size = "{:.1f} MB".format(size / 1048576.0)

    return {
        "href": name + "/" if is_dir else name,
        "display_name": name,
        "display_type": display_type,
        "str_size": str_size,
        "str_modified": modified,
        "tr_class": "directory" if is_dir else "",
        "a_class": "",
    }


def build_context(path, user_name=None, realm=None):
    """Build template context - mirrors WsgiDAV _get_context method."""
    abs_path = os.path.realpath(os.path.join(SHARE_ROOT, path.lstrip('/')))
    # Prevent path traversal
    if not abs_path.startswith(os.path.realpath(SHARE_ROOT)):
        return None
    if not os.path.isdir(abs_path):
        return None

    display_path = "/" + path.strip("/") + "/" if path.strip("/") else "/"

    rows = []
    try:
        entries = sorted(os.listdir(abs_path))
        dirs = [e for e in entries if os.path.isdir(os.path.join(abs_path, e))]
        files = [e for e in entries if not os.path.isdir(os.path.join(abs_path, e))]
        for name in dirs + files:
            fp = os.path.join(abs_path, name)
            rows.append(get_file_info(fp, name))
    except OSError:
        pass

    is_readonly = True
    access = "read-only" if is_readonly else "read-write"

    trailer_text = '<a href="https://github.com/mar10/wsgidav/">WsgiDAV/3.1.1</a> - {}'.format(
        datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    )

    context = {
        "htdocs": "/static",
        "rows": rows,
        "version": "3.1.1",
        "display_path": display_path,
        "is_root": (path.strip("/") == ""),
        "config": DAV_CONFIG.get("dir_browser", {}),
        "is_readonly": is_readonly,
        "access": access,
        "user_name": user_name,
        "realm": realm,
        "trailer": trailer_text,
    }

    return context


# -------------------------------------------------------
# Report queue - admin bot reviews reported pages
# -------------------------------------------------------
report_queue = []
collected_data = {}

def admin_bot_worker():
    """Background thread that processes reported URLs via PhantomJS."""
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    while True:
        time.sleep(2)
        while report_queue:
            url = report_queue.pop(0)
            try:
                logging.info("Admin reviewing: %s", url)
                proc = subprocess.Popen(
                    ["timeout", "8", "phantomjs", "admin_visit.js", base_url, flag, url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = proc.communicate()
                if stdout.strip():
                    logging.info("Admin bot output: %s", stdout.strip())
            except Exception as e:
                logging.error("Admin bot error: %s", str(e))


bot_thread = threading.Thread(target=admin_bot_worker)
bot_thread.daemon = True
bot_thread.start()


# -------------------------------------------------------
# Routes
# -------------------------------------------------------

@app.route('/')
def index():
    return redirect('/browse/')


@app.route('/browse/')
@app.route('/browse/<path:subpath>')
def browse(subpath=''):
    """Directory browser endpoint - mirrors WsgiDAV dir_browser."""
    if not DAV_CONFIG.get("dir_browser", {}).get("enable"):
        return "Directory browsing is disabled.", 403

    # user_name and realm come from authentication context
    # In WsgiDAV these are set in environ by the auth middleware:
    #   environ["wsgidav.auth.user_name"]
    #   environ["wsgidav.auth.realm"]
    user_name = request.args.get('user', None)
    realm = request.args.get('realm', None)

    context = build_context(subpath, user_name=user_name, realm=realm)
    if context is None:
        return "404 Not Found", 404

    html = dir_template.render(**context)
    resp = make_response(html)
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    resp.headers['Cache-Control'] = 'private'
    return resp


@app.route('/report', methods=['GET', 'POST'])
def report_page():
    """Report a page for admin review - admin will visit the URL."""
    if request.method == 'GET':
        return """<!DOCTYPE html>
<html>
<head>
  <title>Report Issue</title>
  <link rel="stylesheet" href="/static/style.css" />
</head>
<body>
  <h1>Report an Issue</h1>
  <p>If you notice any problems with a directory listing page, submit the URL below and an administrator will review it.</p>
  <form method="POST" action="/report">
    <label for="url">Page URL:</label><br>
    <input type="text" id="url" name="url" size="80" placeholder="http://localhost:5000/browse/?realm=..."><br><br>
    <input type="submit" value="Submit Report">
  </form>
  <hr>
  <p class="trailer"><a href="/">Back to file browser</a></p>
</body>
</html>"""

    url = request.form.get('url', '')
    if not url:
        return "URL is required.", 400

    base_url = os.getenv('BASE_URL', 'http://localhost:5000')

    # Normalize: accept URLs with any localhost port and rewrite to internal
    if url.startswith('http://localhost:') or url.startswith('http://127.0.0.1:'):
        # Extract path portion and rewrite to internal base
        parsed = urlparse.urlparse(url)
        internal_url = base_url + parsed.path
        if parsed.query:
            internal_url += '?' + parsed.query
        report_queue.append(internal_url)
    elif url.startswith(base_url):
        report_queue.append(url)
    else:
        return "URL must point to this server.", 400
    return """<!DOCTYPE html>
<html>
<head>
  <title>Report Submitted</title>
  <link rel="stylesheet" href="/static/style.css" />
</head>
<body>
  <h1>Report Submitted</h1>
  <p>Thank you. An administrator will review the reported page shortly.</p>
  <hr>
  <p class="trailer"><a href="/">Back to file browser</a></p>
</body>
</html>"""


@app.route('/collect', methods=['GET', 'POST'])
def collect():
    """Endpoint to collect data - used for legitimate logging/analytics."""
    data = request.args.get('data', '') or request.form.get('data', '')
    token = request.args.get('token', '') or request.form.get('token', '')
    if token and data:
        collected_data[token] = data
    return '', 204


@app.route('/api/collected/<token>')
def get_collected(token):
    """Retrieve collected analytics data."""
    data = collected_data.get(token, None)
    if data is None:
        return jsonify({"error": "not found"}), 404
    return jsonify({"data": data})


# Health check for probes
@app.route('/healthz')
def healthz():
    return 'ok', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
