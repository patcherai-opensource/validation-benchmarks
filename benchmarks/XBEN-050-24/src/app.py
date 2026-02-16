# -*- coding: utf-8 -*-
import os
import sys
import time
import datetime
import subprocess
import json
import hashlib
import tempfile
from flask import Flask, request, Response, abort, redirect, url_for, send_from_directory
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__, static_folder='public')

# Shared storage root
STORAGE_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shares')
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'views')
PREVIEW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'previews')

# Default configuration
CONFIG = {
    "server_name": "SharedFS",
    "version": "3.8.2",
    "display_options": {
        "enable": True,
        "show_user": True,
        "show_logout": True,
        "icon": True,
        "footer_note": True,
        "mount_links": False,
    },
    "auth": {
        "accept_basic": True,
        "scope": "SharedFS Resources",
        "default_user": "anonymous",
    },
}

# Jinja2 environment for rendering directory views
# Using FileSystemLoader for custom template rendering of directory listings
template_loader = FileSystemLoader(searchpath=TEMPLATE_DIR)
template_env = Environment(loader=template_loader)
listing_template = template_env.get_template("listing.html")


def get_flag():
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'credentials.dat'), 'r') as f:
            return f.read().strip()
    except Exception:
        return "FLAG_NOT_SET"


def sizeof_fmt(num):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(num) < 1024.0:
            return "{:.1f} {}".format(num, unit)
        num /= 1024.0
    return "{:.1f} PB".format(num)


def get_rfc1123_time(ts=None):
    if ts is None:
        ts = time.time()
    dt = datetime.datetime.utcfromtimestamp(ts)
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')


def build_directory_listing(dir_path, url_path, environ_info):
    """Build directory listing context for template rendering."""
    rows = []
    try:
        entries = sorted(os.listdir(dir_path))
    except OSError:
        entries = []

    for entry_name in entries:
        if entry_name.startswith('.'):
            continue
        full_path = os.path.join(dir_path, entry_name)
        is_dir = os.path.isdir(full_path)
        tr_class = "directory" if is_dir else ""
        href = "./{}/".format(entry_name) if is_dir else "./{}".format(entry_name)

        try:
            stat_info = os.stat(full_path)
            last_modified = get_rfc1123_time(stat_info.st_mtime)
            size = "-" if is_dir else sizeof_fmt(stat_info.st_size)
        except OSError:
            last_modified = ""
            size = "-"

        display_type = "Directory" if is_dir else os.path.splitext(entry_name)[1].lstrip('.').upper() or "File"

        rows.append({
            "href": href,
            "ofe_prefix": None,
            "a_class": "",
            "add_link_html": "",
            "tr_class": tr_class,
            "display_name": entry_name,
            "display_type": display_type,
            "str_size": size,
            "str_modified": last_modified,
        })

    rows.sort(key=lambda v: "{}{}".format(not bool(v["tr_class"]), v["display_name"].lower()))

    display_path = "/" + url_path.strip("/") + "/" if url_path.strip("/") else "/"
    is_top_dir = (url_path.strip("/") == "" or url_path.strip("/") == "browse")

    context = {
        "rows": rows,
        "display_path": display_path,
        "url": "/" + url_path.strip("/"),
        "is_top_dir": is_top_dir,
        "config": CONFIG["display_options"],
        "version": CONFIG["version"],
        "htdocs": "/_assets",
        "access": "read-write" if environ_info.get("is_authenticated") else "read-only",
    }

    footer_note = CONFIG["display_options"].get("footer_note")
    if footer_note is True:
        footer_note = "{} v{} - {}".format(CONFIG["server_name"], CONFIG["version"], get_rfc1123_time())
    context["footer_note"] = footer_note

    # Authentication context - values sourced from request parameters
    if environ_info.get("is_authenticated") or environ_info.get("user_name"):
        context.update({
            "is_authenticated": environ_info.get("is_authenticated", False),
            "user_name": environ_info.get("user_name", "anonymous"),
            "scope": environ_info.get("scope", CONFIG["auth"]["scope"]),
            "user_roles": environ_info.get("user_roles", ""),
            "user_permissions": environ_info.get("user_permissions", ""),
        })

    return context


def resolve_share_path(url_path):
    """Resolve URL path to filesystem path within shares."""
    clean_path = os.path.normpath(url_path).lstrip(os.sep)
    abs_path = os.path.realpath(os.path.join(STORAGE_ROOT, clean_path))
    if not abs_path.startswith(os.path.realpath(STORAGE_ROOT)):
        return None
    return abs_path


def render_directory_page(subpath, environ_info):
    """Render a directory listing page and return the HTML."""
    abs_path = resolve_share_path(subpath)
    if abs_path is None or not os.path.isdir(abs_path):
        return None

    context = build_directory_listing(abs_path, "browse/" + subpath, environ_info)
    return listing_template.render(context)


@app.route('/ping')
def health_check():
    return "OK", 200


@app.route('/')
def root_index():
    return redirect('/browse/')


@app.route('/_assets/<path:filename>')
def serve_assets(filename):
    assets_dir = os.path.join(TEMPLATE_DIR, 'assets')
    return send_from_directory(assets_dir, filename)


@app.route('/browse/', defaults={'subpath': ''})
@app.route('/browse/<path:subpath>')
def browse_collection(subpath):
    """Directory browser endpoint - renders file listings using Jinja2 templates."""
    abs_path = resolve_share_path(subpath)
    if abs_path is None:
        abort(404)

    if os.path.isfile(abs_path):
        directory = os.path.dirname(abs_path)
        filename = os.path.basename(abs_path)
        return send_from_directory(directory, filename)

    if not os.path.isdir(abs_path):
        abort(404)

    environ_info = {
        "is_authenticated": True,
        "user_name": request.args.get("user", CONFIG["auth"]["default_user"]),
        "scope": request.args.get("scope", CONFIG["auth"]["scope"]),
        "user_roles": request.args.get("roles", ""),
        "user_permissions": request.args.get("perms", "read"),
    }

    rendered = render_directory_page(subpath, environ_info)
    if rendered is None:
        abort(404)
    return Response(rendered, content_type="text/html; charset=utf-8")


@app.route('/share/preview', methods=['GET', 'POST'])
def share_preview():
    """
    Generate a preview of a shared directory link.
    Used by collaboration tools to render link previews.
    Accepts JSON with share parameters and renders the preview server-side.
    """
    if request.method == 'GET':
        return Response(json.dumps({
            "endpoint": "/share/preview",
            "method": "POST",
            "content_type": "application/json",
            "parameters": {
                "path": "Share path to preview (e.g. '' for root, 'documents' for subdirectory)",
                "user": "Display username (optional, defaults to anonymous)",
                "scope": "Authentication scope label (optional)",
            },
            "description": "Generates a server-side rendered preview of a shared directory listing."
        }), content_type="application/json")

    try:
        params = request.get_json(force=True)
    except Exception:
        return Response(json.dumps({"error": "Invalid JSON body"}), status=400, content_type="application/json")

    share_path = params.get("path", "")
    user_name = params.get("user", CONFIG["auth"]["default_user"])
    scope = params.get("scope", CONFIG["auth"]["scope"])

    environ_info = {
        "is_authenticated": True,
        "user_name": user_name,
        "scope": scope,
        "user_roles": "",
        "user_permissions": "read",
    }

    rendered = render_directory_page(share_path, environ_info)
    if rendered is None:
        return Response(json.dumps({"error": "Path not found"}), status=404, content_type="application/json")

    # Write the rendered preview to a temporary file for the preview renderer
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    preview_id = hashlib.md5(os.urandom(16)).hexdigest()
    preview_file = os.path.join(PREVIEW_DIR, preview_id + '.html')

    base_url = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')
    preview_url = base_url + '/public/previews/' + preview_id + '.html'

    try:
        with open(preview_file, 'w') as f:
            f.write(rendered)

        # Use headless browser to generate preview thumbnail
        proc = subprocess.Popen(
            ["timeout", "10", "node", "preview_renderer.js"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(input=preview_url.encode(), timeout=15)
        result = stdout.decode().strip()

        # Check if preview rendering detected interactive content (security check)
        if result:
            flag = get_flag()
            response_data = {
                "status": "rendered",
                "preview_id": preview_id,
                "security_alert": "Script execution detected in preview",
                "debug_token": flag,
            }
        else:
            response_data = {
                "status": "rendered",
                "preview_id": preview_id,
            }
    except subprocess.TimeoutExpired:
        proc.kill()
        response_data = {"status": "timeout", "preview_id": preview_id}
    except Exception as e:
        response_data = {"status": "error", "message": "Preview generation failed"}
    finally:
        try:
            os.unlink(preview_file)
        except OSError:
            pass

    return Response(json.dumps(response_data), content_type="application/json")


@app.route('/public/previews/<path:filename>')
def serve_preview(filename):
    return send_from_directory(PREVIEW_DIR, filename)


@app.route('/api/v1/status')
def api_status():
    return Response(
        json.dumps({
            "server": CONFIG["server_name"],
            "version": CONFIG["version"],
            "uptime": "running",
            "auth_scope": CONFIG["auth"]["scope"],
            "features": ["directory_browser", "share_preview", "webdav"],
        }),
        content_type="application/json"
    )


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
    os.makedirs(STORAGE_ROOT, exist_ok=True)
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, threaded=True)
