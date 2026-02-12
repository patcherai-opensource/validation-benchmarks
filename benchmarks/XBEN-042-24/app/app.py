import os
import json
import hashlib
import hmac
import time
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_file, abort, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.urandom(32)

# Application version
APP_VERSION = "3.8.2"

# --- Project storage (in-memory for simplicity) ---
projects = {}
project_counter = 0

# --- Internal API credentials (used by extensions for service-to-service auth) ---
# These are configured via system properties in production
_INTERNAL_API_CLIENT_ID = os.environ.get(
    "ext.gdata.clientid",
    "data-refinery-internal-svc"
)
_INTERNAL_API_CLIENT_SECRET = os.environ.get(
    "ext.gdata.clientsecret",
    "xK9mP2vL7nQ4wR8jT1sY6bA3cF5hD0eG"
)


def require_api_auth(f):
    """Validates service-to-service API authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        client_id = request.headers.get("X-Client-Id")
        client_secret = request.headers.get("X-Client-Secret")
        if not client_id or not client_secret:
            return jsonify({"error": "Authentication required"}), 401
        if client_id != _INTERNAL_API_CLIENT_ID or client_secret != _INTERNAL_API_CLIENT_SECRET:
            return jsonify({"error": "Invalid credentials"}), 403
        return f(*args, **kwargs)
    return decorated


# ========================
# Web UI Routes
# ========================

@app.route("/")
def index():
    return render_template("index.html", version=APP_VERSION, projects=projects)


@app.route("/project", methods=["POST"])
def create_project():
    global project_counter
    name = request.form.get("name", "Untitled")
    data = request.form.get("data", "")
    project_counter += 1
    pid = project_counter
    projects[pid] = {
        "id": pid,
        "name": name,
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rows": len(data.strip().splitlines()) if data.strip() else 0,
        "data": data,
    }
    return redirect(url_for("view_project", project_id=pid))


@app.route("/project/<int:project_id>")
def view_project(project_id):
    project = projects.get(project_id)
    if not project:
        abort(404)
    rows = []
    if project["data"]:
        lines = project["data"].strip().splitlines()
        for line in lines:
            rows.append(line.split(","))
    return render_template("project.html", project=project, rows=rows, version=APP_VERSION)


@app.route("/project/<int:project_id>/delete", methods=["POST"])
def delete_project(project_id):
    if project_id in projects:
        del projects[project_id]
    return redirect(url_for("index"))


@app.route("/preferences")
def preferences():
    return render_template("preferences.html", version=APP_VERSION)


@app.route("/extensions")
def extensions():
    return render_template("extensions.html", version=APP_VERSION)


@app.route("/extensions/gdata/download")
def download_gdata_extension():
    """Download the GData extension package"""
    jar_path = os.path.join(app.root_path, "extensions", "openrefine-gdata.jar")
    if os.path.exists(jar_path):
        return send_file(
            jar_path,
            as_attachment=True,
            download_name="openrefine-gdata.jar",
            mimetype="application/java-archive"
        )
    abort(404)


# ========================
# Internal API (service-to-service)
# ========================

@app.route("/api/v1/status")
def api_status():
    return jsonify({
        "status": "running",
        "version": APP_VERSION,
        "uptime": int(time.time()),
    })


@app.route("/api/v1/projects")
@require_api_auth
def api_list_projects():
    result = []
    for pid, p in projects.items():
        result.append({
            "id": p["id"],
            "name": p["name"],
            "created": p["created"],
            "rows": p["rows"],
        })
    return jsonify({"projects": result})


@app.route("/api/v1/data/export")
@require_api_auth
def api_export_data():
    """Export all data including internal configuration"""
    config_path = "/var/lib/openrefine/config/service_token.conf"
    service_token = ""
    try:
        with open(config_path, "r") as f:
            service_token = f.read().strip()
    except FileNotFoundError:
        service_token = "not-configured"

    export = {
        "export_format": "json",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "service_token": service_token,
        "projects": [],
    }
    for pid, p in projects.items():
        export["projects"].append({
            "id": p["id"],
            "name": p["name"],
            "data": p["data"],
        })
    return jsonify(export)


@app.route("/api/v1/health")
def api_health():
    return jsonify({"status": "ok"})


# ========================
# Error Handlers
# ========================

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template("404.html", version=APP_VERSION), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error"}), 500
    return render_template("500.html", version=APP_VERSION), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
