import mimetypes
import os
from pathlib import Path

from flask import (Flask, Response, abort, render_template, request,
                   redirect, send_from_directory, url_for, jsonify)

from app import app
from app.lib import asset_proxy

CACHE_DIR = Path("/var/lib/vizboard/cache/assets")
WIDGET_STATIC_DIR = Path("/var/www/vizboard/app/static")
COMPONENT_DIR = Path("/var/www/vizboard/app/components")


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/readyz")
def readyz():
    return jsonify({"status": "ok", "ready": True}), 200


@app.route("/static/components/<path:path>")
def serve_components(path):
    safe_path = os.path.normpath(path)
    if safe_path.startswith("..") or safe_path.startswith("/"):
        abort(403)
    full = COMPONENT_DIR / safe_path
    if not full.exists():
        abort(404)
    return send_from_directory(str(COMPONENT_DIR), safe_path)


@app.route("/static/widgets/<path:path>")
def serve_widgets(path):
    widget_dir = WIDGET_STATIC_DIR / "widgets"
    safe_path = os.path.normpath(path)
    if safe_path.startswith("..") or safe_path.startswith("/"):
        abort(403)
    full = widget_dir / safe_path
    if not full.exists():
        abort(404)
    return send_from_directory(str(widget_dir), safe_path)


@app.route("/_platform/cache/<path:path>")
def proxy_cache(path):
    content = asset_proxy.resolve_asset(CACHE_DIR, path)
    if content is None:
        abort(404)
    mime = mimetypes.guess_type(path)
    return Response(content, mimetype=mime[0] if mime[0] else "application/octet-stream")


@app.errorhandler(403)
def forbidden(e):
    return Response("Forbidden", status=403)


@app.errorhandler(404)
def not_found(e):
    return Response("Not Found", status=404)


@app.errorhandler(500)
def server_error(e):
    return Response("Internal Server Error", status=500)
