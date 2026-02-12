"""
Jupyter Server - A web-based server for Jupyter notebooks and kernels.

This is the main application module that sets up the REST API
for content management and kernel operations.
"""

import os
import sys
import json
import logging
from flask import Flask, request, jsonify, render_template, redirect, send_from_directory

from filemanager import FileContentsManager
from auth import (
    get_server_token, write_token_file, require_auth, check_token,
    VIEWER_TOKEN
)

# Configuration
ROOT_DIR = os.environ.get("JUPYTER_ROOT_DIR", "/home/jupyter/workspace")
ALLOW_HIDDEN = os.environ.get("JUPYTER_ALLOW_HIDDEN", "false").lower() == "true"
SERVER_PORT = int(os.environ.get("JUPYTER_PORT", "8888"))

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["JSON_SORT_KEYS"] = False

# Suppress default Flask banner
logging.getLogger("werkzeug").setLevel(logging.WARNING)
logger = logging.getLogger("jupyter_server")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "[%(levelname)1.1s %(asctime)s %(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
logger.addHandler(handler)

# Initialize file manager
contents_manager = FileContentsManager(root_dir=ROOT_DIR, allow_hidden=ALLOW_HIDDEN)


@app.before_request
def suppress_server_header():
    pass


@app.after_request
def set_headers(response):
    response.headers["Server"] = "jupyter_server"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


# ─── Health & Info Endpoints ───────────────────────────────────────────

@app.route("/")
def index():
    """Redirect to the tree view or show login page."""
    token = request.args.get("token") or request.cookies.get("_xsrf_token")
    if token and check_token(token):
        return redirect("/tree")
    return redirect("/login")


@app.route("/login")
def login_page():
    """Render the login page."""
    return render_template("login.html")


@app.route("/tree")
@app.route("/tree/<path:subpath>")
def tree_view(subpath=""):
    """Render the file tree view."""
    token = request.args.get("token") or request.cookies.get("_xsrf_token")
    if not token or not check_token(token):
        return redirect(f"/login?next=/tree/{subpath}")
    return render_template("tree.html", path=subpath, token=token)


@app.route("/notebooks/<path:notebook_path>")
def notebook_view(notebook_path):
    """Render a notebook viewer."""
    token = request.args.get("token") or request.cookies.get("_xsrf_token")
    if not token or not check_token(token):
        return redirect(f"/login?next=/notebooks/{notebook_path}")
    return render_template("notebook.html", path=notebook_path, token=token)


@app.route("/ping")
def ping():
    """Health check endpoint."""
    return "pong", 200


@app.route("/api/status")
def api_status():
    """Server status information."""
    return jsonify({
        "started": True,
        "last_activity": None,
        "connections": 0,
        "kernels": 0,
    })


# ─── Contents API ─────────────────────────────────────────────────────

@app.route("/api/contents", defaults={"path": ""}, methods=["GET"])
@app.route("/api/contents/<path:path>", methods=["GET"])
@require_auth
def get_contents(path):
    """Get contents of file or directory.

    Returns a model representing the file or directory at the given path.
    For directories, the model includes a listing of contents.

    Query parameters:
        content (int): Whether to include file content (default: 1)
        type (str): Expected type ('file', 'directory', 'notebook')
    """
    include_content = request.args.get("content", "1") != "0"
    type_filter = request.args.get("type")

    model = contents_manager.get(path, content=include_content, type=type_filter)
    if model is None:
        return jsonify({
            "message": f"No such file or directory: '{path}'",
            "reason": "Not Found"
        }), 404

    return jsonify(model)


@app.route("/api/contents", defaults={"path": ""}, methods=["PUT"])
@app.route("/api/contents/<path:path>", methods=["PUT"])
@require_auth
def save_contents(path):
    """Save file contents.

    Create or update a file at the given path. The request body
    should include 'type', 'format', and 'content' fields.
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({
            "message": "Request body required",
            "reason": "Bad Request"
        }), 400

    model, error = contents_manager.save(path, body)
    if error:
        return jsonify({"message": error, "reason": "Bad Request"}), 400

    return jsonify(model), 201


@app.route("/api/contents/<path:path>", methods=["DELETE"])
@require_auth
def delete_contents(path):
    """Delete a file or directory."""
    error = contents_manager.delete_file(path)
    if error:
        status = 404 if "not found" in error.lower() else 400
        return jsonify({"message": error, "reason": "Error"}), status

    return "", 204


@app.route("/api/contents/<path:path>", methods=["PATCH"])
@require_auth
def rename_contents(path):
    """Rename a file or directory.

    The request body should contain a 'path' field with the new path.
    """
    body = request.get_json(silent=True)
    if not body or "path" not in body:
        return jsonify({
            "message": "New path required",
            "reason": "Bad Request"
        }), 400

    new_path = body["path"]
    error = contents_manager.rename_file(path, new_path)
    if error:
        status = 404 if "not found" in error.lower() else 400
        return jsonify({"message": error, "reason": "Error"}), status

    model = contents_manager.get(new_path, content=False)
    return jsonify(model)


# ─── Kernels API (stub) ───────────────────────────────────────────────

@app.route("/api/kernels", methods=["GET"])
@require_auth
def list_kernels():
    """List running kernels."""
    return jsonify([])


@app.route("/api/kernelspecs", methods=["GET"])
@require_auth
def list_kernelspecs():
    """List available kernel specs."""
    return jsonify({
        "default": "python3",
        "kernelspecs": {
            "python3": {
                "name": "python3",
                "spec": {
                    "display_name": "Python 3",
                    "language": "python",
                },
                "resources": {}
            }
        }
    })


# ─── Sessions API (stub) ──────────────────────────────────────────────

@app.route("/api/sessions", methods=["GET"])
@require_auth
def list_sessions():
    """List active sessions."""
    return jsonify([])


# ─── Config API (stub) ────────────────────────────────────────────────

@app.route("/api/config/<section>", methods=["GET"])
@require_auth
def get_config(section):
    """Get configuration for a section."""
    configs = {
        "notebook": {
            "CodeCell": {"cm_config": {"indentUnit": 4}},
        },
        "tree": {
            "sort_order": "name",
        },
    }
    return jsonify(configs.get(section, {}))


# ─── Error Handlers ───────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"message": "Not Found", "reason": "Not Found"}), 404
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"message": "Internal Server Error", "reason": "Error"}), 500
    return "Internal Server Error", 500


# ─── Startup ──────────────────────────────────────────────────────────

_initialized = False


def initialize():
    """Initialize the server - write token files, log startup info."""
    global _initialized
    if _initialized:
        return
    _initialized = True

    pid = os.getpid()
    token = get_server_token()

    # Write token to a well-known hidden location for local auth
    token_dir = os.path.join(ROOT_DIR, ".jupyter")
    token_file = write_token_file(token, token_dir, pid)

    logger.info("Jupyter Server %s is running at:", "2.4.0")
    logger.info("    http://0.0.0.0:%d/?token=%s", SERVER_PORT, token)
    logger.info("  or http://127.0.0.1:%d/?token=%s", SERVER_PORT, token)
    logger.info("Token file: %s", token_file)
    logger.info("Shared viewer link: http://0.0.0.0:%d/?token=%s", SERVER_PORT, VIEWER_TOKEN)
    logger.info("Use Control-C to stop this server.")


# Initialize on module load (works with both direct run and gunicorn)
initialize()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVER_PORT, debug=False)
