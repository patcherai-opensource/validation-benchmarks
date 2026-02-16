"""
Conductor - Configuration Management File Distribution Service

REST API for distributing configuration files and managed content
to registered nodes in the infrastructure.
"""

import json
import logging
import os
import sys

from flask import Flask, request, jsonify, g, render_template

import auth
import config
import content_backend

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("conductor")


def require_auth(f):
    """Decorator to require valid authentication token."""
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-Auth-Token")
        if not token:
            token = request.cookies.get("session_token")
        if not token:
            return jsonify({"status": "error", "message": "Authentication required"}), 401

        token_data = auth.validate_token(token)
        if not token_data:
            return (
                jsonify({"status": "error", "message": "Invalid or expired token"}),
                401,
            )

        g.user = token_data
        return f(*args, **kwargs)

    return decorated


@app.route("/")
def index():
    """Service information page."""
    return render_template("index.html")


@app.route("/ping")
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Authenticate and receive a session token.

    POST with JSON body: {"username": "...", "password": "..."}
    Or with form data: username=...&password=...

    Returns a session token for use with subsequent API requests.
    Include the token in the X-Auth-Token header.
    """
    if request.method == "GET":
        return jsonify(
            {
                "status": "ok",
                "message": "POST credentials to this endpoint to obtain an auth token.",
                "example": {
                    "method": "POST",
                    "content_type": "application/json",
                    "body": {"username": "...", "password": "..."},
                },
                "usage": "Include the returned token in subsequent requests using the X-Auth-Token header.",
            }
        )

    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return (
            jsonify(
                {"status": "error", "message": "Missing username or password"}
            ),
            400,
        )

    token = auth.authenticate(username, password)
    if not token:
        return jsonify({"status": "error", "message": "Authentication failed"}), 401

    return jsonify(
        {
            "status": "ok",
            "token": token,
            "expire": 86400,
            "user": username,
        }
    )


@app.route("/api/v1/environments", methods=["GET"])
@require_auth
def get_environments():
    """
    List available content environments.
    """
    envs = content_backend.list_environments()
    return jsonify({"status": "ok", "environments": envs})


@app.route("/api/v1/content", methods=["GET"])
@require_auth
def list_files():
    """
    List files in a content environment.

    Query parameters:
        content_env: the environment name (default: production)
    """
    content_env = request.args.get("content_env", "production")
    files = content_backend.list_content(content_env)
    return jsonify({"status": "ok", "environment": content_env, "files": files})


@app.route("/api/v1/content/fetch", methods=["POST"])
@require_auth
def fetch_file():
    """
    Fetch content from the file distribution backend.

    JSON body:
        path: relative path to the file within the content root
        content_env: the environment name (default: production)
        loc: byte offset to begin reading from (default: 0)
    """
    if not request.is_json:
        return (
            jsonify({"status": "error", "message": "Request must be JSON"}),
            400,
        )

    data = request.get_json()
    path = data.get("path", "")
    content_env = data.get("content_env", "production")
    loc = data.get("loc", 0)

    if not path:
        return jsonify({"status": "error", "message": "No path specified"}), 400

    fnd = content_backend.locate_content(path, content_env)
    if not fnd.get("path"):
        return jsonify({"status": "error", "message": "File not found"}), 404

    load = {"path": path, "content_env": content_env, "loc": loc}
    result = content_backend.retrieve_content(load, fnd)

    if not result.get("data"):
        return jsonify({"status": "error", "message": "Unable to read file"}), 500

    import base64

    return jsonify(
        {
            "status": "ok",
            "path": result["dest"],
            "data": base64.b64encode(result["data"]).decode("utf-8"),
            "encoding": "base64",
        }
    )


@app.route("/api/v1/content/info", methods=["POST"])
@require_auth
def file_info():
    """
    Get file metadata from the content backend.

    JSON body:
        path: relative path to the file
        content_env: the environment name (default: production)
    """
    if not request.is_json:
        return (
            jsonify({"status": "error", "message": "Request must be JSON"}),
            400,
        )

    data = request.get_json()
    path = data.get("path", "")
    content_env = data.get("content_env", "production")

    if not path:
        return jsonify({"status": "error", "message": "No path specified"}), 400

    fnd = content_backend.locate_content(path, content_env)
    if not fnd.get("path"):
        return jsonify({"status": "error", "message": "File not found"}), 404

    stat_info = fnd.get("stat", [])
    info = {
        "status": "ok",
        "path": fnd["rel"],
        "exists": True,
    }
    if stat_info:
        info["size"] = stat_info[6] if len(stat_info) > 6 else 0
        info["mtime"] = stat_info[8] if len(stat_info) > 8 else 0

    return jsonify(info)


@app.route("/api/v1/status", methods=["GET"])
@require_auth
def system_status():
    """System status information."""
    return jsonify(
        {
            "status": "ok",
            "service": "conductor",
            "version": "3.7.2",
            "content_roots": list(config.CONTENT_ROOTS.keys()),
            "cache_dir": config.CACHE_DIR,
        }
    )


@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"status": "error", "message": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"status": "error", "message": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host=config.LISTEN_HOST, port=config.LISTEN_PORT)
