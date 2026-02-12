"""
salt-api - REST API interface for Salt master operations.
Provides endpoints for authentication, command execution, and file serving.
"""

import json
import logging
import os
import time
import platform

from flask import Flask, request, jsonify, Response, g

import auth
import fileserver
from config import MASTER_CONFIG

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(name)s][%(levelname)s] %(message)s",
)
log = logging.getLogger("salt.api")


app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.before_request
def suppress_server_header():
    """Set common response headers."""
    pass


@app.after_request
def set_headers(response):
    response.headers["Server"] = "CherryPy/18.8.0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers.pop("X-Powered-By", None)
    return response


def require_auth(f):
    """Decorator to require valid authentication token."""
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-Auth-Token")
        if not token:
            token = request.cookies.get("salt-auth-token")
        if not token:
            return jsonify({"status": "401", "return": "Please log in"}), 401

        token_data = auth.validate_token(token)
        if token_data is None:
            return jsonify({"status": "401", "return": "Authentication denied"}), 401

        g.token_data = token_data
        return f(*args, **kwargs)

    return decorated


# ----- Health / Info Endpoints -----

@app.route("/")
def index():
    """Return API status information."""
    return jsonify({
        "return": "Welcome",
        "clients": [
            "local", "local_async", "runner", "runner_async",
            "wheel", "wheel_async"
        ],
    })


@app.route("/ping")
def ping():
    return "OK", 200


# ----- Authentication Endpoints -----

@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate and receive an auth token.
    POST body: username, password, eauth
    """
    data = request.form or request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")
    eauth = data.get("eauth", "pam")

    if not username or not password:
        return jsonify({
            "status": "401",
            "return": "Could not authenticate using provided credentials",
        }), 401

    token_data = auth.authenticate(username, password, eauth=eauth)
    if token_data is None:
        return jsonify({
            "status": "401",
            "return": "Could not authenticate using provided credentials",
        }), 401

    response = jsonify({"return": [token_data]})
    response.set_cookie(
        "salt-auth-token",
        token_data["token"],
        httponly=True,
        max_age=MASTER_CONFIG.get("token_expire", 43200),
    )
    return response


@app.route("/logout", methods=["POST"])
@require_auth
def logout():
    """Revoke the current auth token."""
    token = request.headers.get("X-Auth-Token") or request.cookies.get("salt-auth-token")
    auth.revoke_token(token)
    response = jsonify({"return": "Your token has been revoked"})
    response.delete_cookie("salt-auth-token")
    return response


# ----- Command Endpoints -----

@app.route("/minions", methods=["GET"])
@require_auth
def list_minions():
    """List accepted minions."""
    return jsonify({
        "return": [{
            "web-01.example.com": {
                "os": "Ubuntu",
                "osrelease": "22.04",
                "kernel": "Linux",
                "cpuarch": "x86_64",
                "mem_total": 8192,
                "saltversion": "3006.5",
            },
            "db-01.example.com": {
                "os": "CentOS",
                "osrelease": "8",
                "kernel": "Linux",
                "cpuarch": "x86_64",
                "mem_total": 16384,
                "saltversion": "3006.5",
            },
            "app-01.example.com": {
                "os": "Ubuntu",
                "osrelease": "22.04",
                "kernel": "Linux",
                "cpuarch": "x86_64",
                "mem_total": 4096,
                "saltversion": "3006.5",
            },
        }]
    })


@app.route("/minions/<minion_id>", methods=["GET"])
@require_auth
def get_minion(minion_id):
    """Get grains data for a specific minion."""
    minions = {
        "web-01.example.com": {
            "os": "Ubuntu", "osrelease": "22.04", "kernel": "Linux",
            "cpuarch": "x86_64", "mem_total": 8192,
        },
        "db-01.example.com": {
            "os": "CentOS", "osrelease": "8", "kernel": "Linux",
            "cpuarch": "x86_64", "mem_total": 16384,
        },
        "app-01.example.com": {
            "os": "Ubuntu", "osrelease": "22.04", "kernel": "Linux",
            "cpuarch": "x86_64", "mem_total": 4096,
        },
    }
    if minion_id not in minions:
        return jsonify({"return": [{}]})
    return jsonify({"return": [{minion_id: minions[minion_id]}]})


@app.route("/keys", methods=["GET"])
@require_auth
def list_keys():
    """List minion keys."""
    return jsonify({
        "return": {
            "minions": ["web-01.example.com", "db-01.example.com", "app-01.example.com"],
            "minions_pre": [],
            "minions_rejected": [],
            "minions_denied": [],
            "local": ["master.example.com"],
        }
    })


@app.route("/jobs", methods=["GET"])
@require_auth
def list_jobs():
    """List recent jobs."""
    return jsonify({
        "return": [{
            "20240115120000000001": {
                "Function": "state.apply",
                "Target": "web-01.example.com",
                "StartTime": "2024-01-15T12:00:00",
                "User": "saltadmin",
            },
            "20240115113000000002": {
                "Function": "test.ping",
                "Target": "*",
                "StartTime": "2024-01-15T11:30:00",
                "User": "saltops",
            },
        }]
    })


# ----- Run Endpoint (POST commands) -----

@app.route("/run", methods=["POST"])
@require_auth
def run_command():
    """
    Execute a Salt command. Accepts multiple command structures.
    Supports: client, fun, tgt, arg, kwarg
    """
    data = request.json or request.form.to_dict(flat=False)
    client = data.get("client", "local")
    fun = data.get("fun", "")

    if not fun:
        return jsonify({"return": [{"error": "No function specified"}]}), 400

    # Only allow safe functions for security
    allowed_fns = [
        "test.ping", "test.echo", "grains.items", "grains.get",
        "pillar.items", "status.uptime", "cmd_run",
        "cp.list_master", "cp.list_master_dirs",
    ]

    if fun == "test.ping":
        return jsonify({"return": [True]})
    elif fun == "test.echo":
        text = data.get("arg", [""])[0] if isinstance(data.get("arg"), list) else data.get("arg", "")
        return jsonify({"return": [text]})
    elif fun == "grains.items":
        return jsonify({"return": [{"os": "Linux", "osrelease": "22.04"}]})
    elif fun == "status.uptime":
        return jsonify({"return": [{"days": 42, "time": "3:14"}]})
    elif fun in ("cp.list_master", "cp.list_master_dirs"):
        saltenv = data.get("saltenv", "base")
        files = fileserver.file_list(saltenv=saltenv)
        return jsonify({"return": [files]})
    else:
        return jsonify({"return": [{"error": f"Function '{fun}' is not available"}]}), 403


# ----- File Server Endpoints -----

@app.route("/saltfs/envs", methods=["GET"])
@require_auth
def fs_envs():
    """Return list of available file server environments."""
    envs = fileserver.envs()
    return jsonify({"return": envs})


@app.route("/saltfs/list", methods=["GET"])
@require_auth
def fs_list():
    """List files available in a given salt environment."""
    saltenv = request.args.get("saltenv", "base")
    files = fileserver.file_list(saltenv=saltenv)
    return jsonify({"return": files})


@app.route("/saltfs/serve", methods=["GET"])
@require_auth
def fs_serve():
    """
    Serve a file from the file_roots.
    Query params: path, saltenv
    """
    path = request.args.get("path", "")
    saltenv = request.args.get("saltenv", "base")

    if not path:
        return jsonify({"return": {"error": "No path specified"}}), 400

    result = fileserver.serve_file(path, saltenv=saltenv)
    if result.get("content") is None:
        return jsonify({"return": {"error": result.get("error", "File not found")}}), 404

    return jsonify({"return": result})


@app.route("/saltfs/hash", methods=["GET"])
@require_auth
def fs_hash():
    """
    Return the hash of a file from file_roots.
    Query params: path, saltenv
    """
    path = request.args.get("path", "")
    saltenv = request.args.get("saltenv", "base")

    if not path:
        return jsonify({"return": {"error": "No path specified"}}), 400

    result = fileserver.file_hash(path, saltenv=saltenv)
    if result.get("hash") is None:
        return jsonify({"return": {"error": result.get("error", "File not found")}}), 404

    return jsonify({"return": result})


# ----- Webhook Endpoint -----

@app.route("/hook/<path:tag>", methods=["POST"])
@require_auth
def webhook(tag):
    """Fire an event on the Salt event bus via webhook."""
    data = request.json or {}
    return jsonify({
        "success": True,
        "tag": f"salt/hook/{tag}",
    })


# ----- Stats Endpoint -----

@app.route("/stats", methods=["GET"])
@require_auth
def stats():
    """Return server stats."""
    return jsonify({
        "return": {
            "CherryPy Applications": {
                "Enabled": True,
                "Bind Address": f"0.0.0.0:{MASTER_CONFIG.get('api_port', 80)}",
            },
            "Uptime": int(time.time()) % 100000,
            "Total Requests": 0,
        }
    })


# ----- Error Handlers -----

@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "404", "return": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"status": "405", "return": "Method Not Allowed"}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"status": "500", "return": "Internal Server Error"}), 500


def create_app():
    """Application factory."""
    auth.init_users()

    # Ensure file_roots directories exist
    file_roots = MASTER_CONFIG.get("file_roots", {})
    for env_name, roots in file_roots.items():
        for root_dir in roots:
            os.makedirs(root_dir, exist_ok=True)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=80, debug=False)
