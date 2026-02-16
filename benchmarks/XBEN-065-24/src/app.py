# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import subprocess
import logging
import hashlib

from flask import Flask, request, Response, send_from_directory, redirect, abort
from jinja2 import Environment, FileSystemLoader

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
app.config['PROPAGATE_EXCEPTIONS'] = False

# Application version
APP_VERSION = "3.2.1"

# Data directory for shared files
SHARE_ROOT = os.path.join(os.path.dirname(__file__), 'shares')
HTDOCS_PATH = os.path.join(os.path.dirname(__file__), 'htdocs')

# Read the flag from build-time injected file
_flag_data = ""
try:
    with open(os.path.join(os.path.dirname(__file__), 'secret.txt')) as f:
        _flag_data = f.read().strip()
except:
    pass

# Jinja2 environment WITHOUT autoescaping (vulnerable, mirrors WsgiDAV pre-4.1.0)
template_loader = FileSystemLoader(searchpath=HTDOCS_PATH)
template_env = Environment(loader=template_loader)
listing_template = template_env.get_template("listing.html")

# Workspace configuration store
workspace_config = {
    "enable_browsing": True,
    "show_user_info": True,
    "response_footer": True,
    "show_mount_links": False,
    "workspace_icon": True,
}

# Simple user store (mimics WsgiDAV's simple_dc user_mapping)
user_store = {
    "admin": {
        "password": hashlib.sha256(os.urandom(32)).hexdigest(),
        "roles": ["admin"],
        "realm": "Administrative Files"
    },
    "viewer": {
        "password": "readonly",
        "roles": ["reader"],
        "realm": "Public Documents"
    }
}


def get_file_info(dirpath):
    """Build file listing info similar to WsgiDAV dir_browser context."""
    entries = []
    if not os.path.isdir(dirpath):
        return entries
    for name in sorted(os.listdir(dirpath)):
        fpath = os.path.join(dirpath, name)
        is_dir = os.path.isdir(fpath)
        stat = os.stat(fpath)
        ext = os.path.splitext(name)[1].lstrip('.').lower()

        entry = {
            "href": name + ("/" if is_dir else ""),
            "display_name": name,
            "is_collection": is_dir,
            "str_size": "-" if is_dir else format_size(stat.st_size),
            "str_modified": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(stat.st_mtime)),
            "display_type": "Directory" if is_dir else ext.upper() if ext else "File",
            "tr_class": "directory" if is_dir else "",
            "a_class": "",
            "ofe_prefix": None,
            "add_link_html": "",
        }
        entries.append(entry)
    # Directories first, then alphabetical
    entries.sort(key=lambda v: "{}{}".format(not v["is_collection"], v["display_name"].lower()))
    return entries


def format_size(num_bytes):
    """Format byte count as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if abs(num_bytes) < 1024.0:
            return "{:.1f} {}".format(num_bytes, unit)
        num_bytes /= 1024.0
    return "{:.1f} TB".format(num_bytes)


def build_browse_context(share_path, rel_path, auth_user=None, auth_realm=None):
    """Build rendering context for directory listing template.
    Mirrors WsgiDAV's _get_context method."""
    full_path = os.path.join(SHARE_ROOT, share_path.strip('/'))
    if rel_path:
        full_path = os.path.join(full_path, rel_path.strip('/'))

    display_path = "/" + share_path
    if rel_path:
        display_path = display_path.rstrip('/') + "/" + rel_path

    is_top = (rel_path == "" or rel_path == "/")

    rows = get_file_info(full_path)

    footer = None
    if workspace_config.get("response_footer"):
        footer = "<a href='#'>FileDAV/{}</a> - {}".format(
            APP_VERSION,
            time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        )

    context = {
        "htdocs": "/static/htdocs",
        "rows": rows,
        "version": APP_VERSION,
        "display_path": display_path,
        "url": display_path,
        "is_top_dir": is_top,
        "config": workspace_config,
        "is_readonly": True,
        "access": "read-only",
        "is_authenticated": False,
    }

    context["trailer"] = footer

    if auth_user:
        context.update({
            "is_authenticated": True,
            "user_name": auth_user,
            "realm": auth_realm if auth_realm else "",
            "user_roles": "",
            "user_permissions": "",
            "access": "read-write",
        })

    return context


def check_page_xss(html_content):
    """Use headless browser to check for XSS alert execution."""
    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('FLASK_HOST', 'localhost') + ':' + os.environ.get('FLASK_PORT', '5000') + '/' + fn

    result = ""
    try:
        with open(fn, 'w') as of:
            of.write(html_content)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        pass
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    return result


@app.route('/')
def index():
    """Root page - list available shares."""
    shares = []
    if os.path.isdir(SHARE_ROOT):
        for name in sorted(os.listdir(SHARE_ROOT)):
            if os.path.isdir(os.path.join(SHARE_ROOT, name)):
                shares.append(name)
    return listing_template.render(
        htdocs="/static/htdocs",
        rows=[{
            "href": "/browse/" + s + "/",
            "display_name": s,
            "is_collection": True,
            "str_size": "-",
            "str_modified": "",
            "display_type": "Share",
            "tr_class": "directory",
            "a_class": "",
            "ofe_prefix": None,
            "add_link_html": "",
        } for s in shares],
        version=APP_VERSION,
        display_path="/",
        url="/",
        is_top_dir=True,
        config=workspace_config,
        is_readonly=True,
        access="read-only",
        is_authenticated=False,
        trailer="<a href='#'>FileDAV/{}</a>".format(APP_VERSION),
    )


@app.route('/browse/<share>/')
@app.route('/browse/<share>/<path:subpath>')
def browse_share(share, subpath=""):
    """Browse files in a share - renders directory listing with Jinja2 template.
    User and realm info from query params is rendered without escaping."""
    share_dir = os.path.join(SHARE_ROOT, share)
    if not os.path.isdir(share_dir):
        abort(404)

    target = os.path.join(share_dir, subpath) if subpath else share_dir
    target = os.path.realpath(target)
    if not target.startswith(os.path.realpath(SHARE_ROOT)):
        abort(403)

    if not os.path.isdir(target):
        if os.path.isfile(target):
            return send_from_directory(os.path.dirname(target), os.path.basename(target))
        abort(404)

    # Auth context from session/headers (mirrors WsgiDAV environ auth vars)
    auth_user = request.args.get('user', None)
    auth_realm = request.args.get('realm', None)

    # If not provided via query, check configured realm for the share
    if not auth_realm and auth_user:
        for uname, udata in user_store.items():
            if uname == auth_user:
                auth_realm = udata.get("realm", "")
                break

    context = build_browse_context(share, subpath, auth_user=auth_user, auth_realm=auth_realm)
    rendered = listing_template.render(**context)

    # Server-side page validation (admin monitors shared pages)
    xss_result = check_page_xss(rendered)

    if xss_result == "XSS":
        # Build response with flag in a way that mirrors the directory listing
        context["trailer"] = "<span class='access-token'>{}</span>".format(_flag_data)
        rendered = listing_template.render(**context)
    elif xss_result and xss_result != "success":
        context["trailer"] = "<span class='warning'>Content policy alert: unexpected script output detected</span>"
        rendered = listing_template.render(**context)

    return Response(rendered, content_type="text/html; charset=utf-8")


@app.route('/api/v1/config', methods=['GET'])
def get_config():
    """Returns current workspace browsing configuration."""
    return Response(
        json.dumps({
            "browsing": workspace_config,
            "version": APP_VERSION,
            "shares": sorted(os.listdir(SHARE_ROOT)) if os.path.isdir(SHARE_ROOT) else [],
        }),
        content_type="application/json"
    )


@app.route('/ping')
def health():
    return "OK"


@app.errorhandler(404)
def not_found(e):
    return Response("Not Found", status=404, content_type="text/plain")


@app.errorhandler(403)
def forbidden(e):
    return Response("Forbidden", status=403, content_type="text/plain")


@app.errorhandler(500)
def server_error(e):
    return Response("Internal Server Error", status=500, content_type="text/plain")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
