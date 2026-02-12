import os
import mimetypes
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, abort, Response

from app import app

SOLARA_VERSION = "1.34.0"
CDN_CACHE_DIR = Path(app.root_path) / "cdn_cache"
PUBLIC_DIR = Path(app.root_path) / "static" / "public"
ASSETS_DIR = Path(app.root_path) / "static" / "assets"
NBEXTENSIONS_DIR = Path(app.root_path) / "static" / "nbextensions"


@app.after_request
def add_headers(response):
    response.headers["X-Powered-By"] = "Solara/%s" % SOLARA_VERSION
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route("/")
def index():
    return render_template("index.html", version=SOLARA_VERSION)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == "admin" and password == os.environ.get("ADMIN_PASS", ""):
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html", error=None)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", version=SOLARA_VERSION)


@app.route("/_solara/api/info")
def api_info():
    return jsonify({
        "version": SOLARA_VERSION,
        "platform": "linux",
        "widgets": ["plotly", "ipywidgets", "ipyvuetify"],
        "theme": "light",
    })


@app.route("/_solara/api/health")
def api_health():
    return jsonify({"status": "ok"})


def get_from_cache(base_cache_dir, path):
    """Fetch a file from the CDN cache directory."""
    full_path = base_cache_dir / path
    resolved = full_path.resolve()
    # Serve the file if it exists
    if resolved.is_file():
        content_type = mimetypes.guess_type(str(resolved))[0] or "application/octet-stream"
        with open(resolved, "rb") as f:
            data = f.read()
        return data, content_type
    return None, None


def get_data(base_cache_dir, path):
    """Get data from CDN cache, downloading from upstream if not cached."""
    data, content_type = get_from_cache(base_cache_dir, path)
    if data is not None:
        return data, content_type
    return None, None


@app.route("/_solara/cdn/<path:path>")
def cdn(path):
    """Serve CDN cached resources."""
    data, content_type = get_data(CDN_CACHE_DIR, path)
    if data is None:
        abort(404)
    return Response(data, content_type=content_type)


@app.route("/static/public/<path:path>")
def static_public(path):
    """Serve public static files."""
    full_path = PUBLIC_DIR / path
    resolved = full_path.resolve()
    if resolved.is_file():
        content_type = mimetypes.guess_type(str(resolved))[0] or "application/octet-stream"
        with open(resolved, "rb") as f:
            data = f.read()
        return Response(data, content_type=content_type)
    abort(404)


@app.route("/static/assets/<path:path>")
def static_assets(path):
    """Serve asset files."""
    full_path = ASSETS_DIR / path
    resolved = full_path.resolve()
    if not str(resolved).startswith(str(ASSETS_DIR.resolve())):
        abort(403)
    if resolved.is_file():
        return send_from_directory(str(ASSETS_DIR), path)
    abort(404)


@app.route("/static/nbextensions/<dir>/<filename>")
def static_nbextensions(dir, filename):
    """Serve notebook extension static files."""
    ext_dir = NBEXTENSIONS_DIR / dir
    if not ext_dir.is_dir():
        abort(404)
    resolved = (ext_dir / filename).resolve()
    if not str(resolved).startswith(str(NBEXTENSIONS_DIR.resolve())):
        abort(403)
    if resolved.is_file():
        return send_from_directory(str(ext_dir), filename)
    abort(404)


@app.route("/resource")
def resource():
    filename = request.args.get("filename")
    if not filename:
        abort(400)
    safe_path = Path(filename)
    if ".." in safe_path.parts:
        abort(403)
    return send_from_directory("static", filename)
