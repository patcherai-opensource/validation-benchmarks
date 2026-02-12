import os
import json
import uuid
import hashlib
import threading
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

from flask import (
    Flask, request, Response, make_response,
    redirect, url_for, render_template, session, jsonify, abort
)

from bot import visit_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

# In-memory storage for projects and users
USERS = {
    "admin": {
        "password_hash": hashlib.sha256(os.urandom(32)).hexdigest(),
        "email": "admin@label-studio.local",
        "is_superuser": True,
        "token": None,
    }
}

PROJECTS = {}
PROJECT_COUNTER = 0

ADMIN_TOKEN = hashlib.sha256(os.urandom(32)).hexdigest()
USERS["admin"]["token"] = ADMIN_TOKEN


def get_flag():
    try:
        with open("/app/data/flag.txt", "r") as f:
            return f.read().strip()
    except Exception:
        return "FLAG{placeholder}"


def get_current_user():
    # Check Flask session first
    token = session.get("token")
    if token:
        for username, user in USERS.items():
            if user.get("token") == token:
                return username, user
    # Check session_token cookie (used by API clients)
    token = request.cookies.get("session_token")
    if token:
        for username, user in USERS.items():
            if user.get("token") == token:
                return username, user
    # Check Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Token "):
        token = auth_header[6:]
        for username, user in USERS.items():
            if user.get("token") == token:
                return username, user
    return None, None


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        username, user = get_current_user()
        if not username:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"detail": "Authentication credentials were not provided."}), 401
            return redirect(url_for("user_login"))
        request.current_user = username
        request.current_user_data = user
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        username, user = get_current_user()
        if not username or not user.get("is_superuser"):
            return jsonify({"detail": "You do not have permission to perform this action."}), 403
        request.current_user = username
        request.current_user_data = user
        return f(*args, **kwargs)
    return decorated


# ==================== Health ====================

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ==================== Auth ====================

@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        for username, user in USERS.items():
            if user["email"] == email:
                pw_hash = hashlib.sha256(password.encode()).hexdigest()
                if pw_hash == user["password_hash"]:
                    if not user.get("token"):
                        user["token"] = hashlib.sha256(os.urandom(32)).hexdigest()
                    session["token"] = user["token"]
                    return redirect(url_for("projects_list"))
                else:
                    error = "Invalid credentials."
                    break
        else:
            error = "Invalid credentials."
    return render_template("login.html", error=error)


@app.route("/user/signup", methods=["GET", "POST"])
def user_signup():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        if not email or not password:
            error = "Email and password are required."
        else:
            username = email.split("@")[0]
            if username in USERS:
                error = "User already exists."
            else:
                token = hashlib.sha256(os.urandom(32)).hexdigest()
                USERS[username] = {
                    "password_hash": hashlib.sha256(password.encode()).hexdigest(),
                    "email": email,
                    "is_superuser": False,
                    "token": token,
                }
                session["token"] = token
                return redirect(url_for("projects_list"))
    return render_template("signup.html", error=error)


@app.route("/user/logout")
def user_logout():
    session.pop("token", None)
    return redirect(url_for("user_login"))


# ==================== API: Current User ====================

@app.route("/api/current-user/whoami")
@login_required
def api_whoami():
    user = request.current_user_data
    return jsonify({
        "id": 1,
        "username": request.current_user,
        "email": user["email"],
        "is_superuser": user.get("is_superuser", False),
    })


# ==================== Projects ====================

@app.route("/")
def index():
    username, user = get_current_user()
    if username:
        return redirect(url_for("projects_list"))
    return redirect(url_for("user_login"))


@app.route("/projects/", methods=["GET"])
@login_required
def projects_list():
    user_projects = {
        pid: p for pid, p in PROJECTS.items()
        if p["created_by"] == request.current_user
    }
    return render_template("projects.html", projects=user_projects, user=request.current_user)


@app.route("/projects/create", methods=["GET", "POST"])
@login_required
def project_create():
    global PROJECT_COUNTER
    error = None
    if request.method == "POST":
        title = request.form.get("title", "")
        description = request.form.get("description", "")
        label_config = request.form.get("label_config", "")
        if not title:
            error = "Project title is required."
        else:
            PROJECT_COUNTER += 1
            pid = PROJECT_COUNTER
            PROJECTS[pid] = {
                "id": pid,
                "title": title,
                "description": description,
                "label_config": label_config,
                "created_by": request.current_user,
                "created_at": datetime.utcnow().isoformat(),
                "task_number": 0,
            }
            return redirect(url_for("project_detail", project_id=pid))
    return render_template("project_create.html", error=error)


@app.route("/projects/<int:project_id>/", methods=["GET"])
@login_required
def project_detail(project_id):
    project = PROJECTS.get(project_id)
    if not project or project["created_by"] != request.current_user:
        abort(404)
    return render_template("project_detail.html", project=project, user=request.current_user)


@app.route("/projects/<int:project_id>/settings", methods=["GET", "POST"])
@login_required
def project_settings(project_id):
    project = PROJECTS.get(project_id)
    if not project or project["created_by"] != request.current_user:
        abort(404)
    if request.method == "POST":
        project["title"] = request.form.get("title", project["title"])
        project["description"] = request.form.get("description", project["description"])
        project["label_config"] = request.form.get("label_config", project["label_config"])
        return redirect(url_for("project_detail", project_id=project_id))
    return render_template("project_settings.html", project=project)


# ==================== Upload Example ====================

def generate_sample_task(label_config):
    """Parse label config XML and generate sample task data."""
    task_data = {}
    try:
        root = ET.fromstring(label_config)
        for elem in root.iter():
            value_attr = elem.get("value")
            name_attr = elem.get("name")
            tag_name = elem.tag

            if value_attr and value_attr.startswith("$"):
                field_name = value_attr[1:]
                if tag_name in ("Text", "HyperText", "Header"):
                    task_data[field_name] = value_attr.replace("$", "")
                elif tag_name == "Image":
                    task_data[field_name] = "/static/samples/sample.jpg"
                elif tag_name == "Audio":
                    task_data[field_name] = "/static/samples/sample.mp3"
                elif tag_name == "Video":
                    task_data[field_name] = "/static/samples/sample.mp4"
                elif tag_name == "TimeSeries":
                    task_data[field_name] = "/static/samples/sample.csv"
                else:
                    task_data[field_name] = value_attr.replace("$", "")

            if value_attr and not value_attr.startswith("$"):
                field_name = name_attr if name_attr else tag_name.lower()
                task_data[field_name] = value_attr

    except ET.ParseError:
        return None

    if not task_data:
        task_data = {"text": "Sample text for labeling"}

    return task_data


@app.route("/projects/upload-example/", methods=["POST", "GET"])
def upload_example_using_config():
    """Generate sample task data from a label configuration.

    Accepts label_config as XML and returns generated sample task data
    that can be used to preview the labeling interface.
    """
    if request.method == "GET":
        label_config = request.args.get("label_config", "")
    else:
        label_config = request.form.get("label_config", "")
        if not label_config:
            try:
                data = request.get_json(silent=True)
                if data:
                    label_config = data.get("label_config", "")
            except Exception:
                pass

    if not label_config:
        return Response(
            json.dumps({"error": "label_config is required"}),
            status=400,
            content_type="application/json"
        )

    task_data = generate_sample_task(label_config)
    if task_data is None:
        return Response(
            json.dumps({"error": "Invalid label config XML"}),
            status=400,
            content_type="application/json"
        )

    response = Response(json.dumps(task_data))
    return response


# ==================== API Endpoints ====================

@app.route("/api/projects/", methods=["GET"])
@login_required
def api_projects_list():
    user_projects = [
        p for p in PROJECTS.values()
        if p["created_by"] == request.current_user
    ]
    return jsonify(user_projects)


@app.route("/api/projects/<int:project_id>/", methods=["GET"])
@login_required
def api_project_detail(project_id):
    project = PROJECTS.get(project_id)
    if not project or project["created_by"] != request.current_user:
        return jsonify({"detail": "Not found."}), 404
    return jsonify(project)


@app.route("/api/projects/<int:project_id>/tasks/", methods=["GET"])
@login_required
def api_project_tasks(project_id):
    project = PROJECTS.get(project_id)
    if not project or project["created_by"] != request.current_user:
        return jsonify({"detail": "Not found."}), 404
    return jsonify([])


# ==================== Admin ====================

@app.route("/api/admin/secret", methods=["GET"])
@admin_required
def admin_secret():
    flag = get_flag()
    return jsonify({"secret": flag, "status": "classified"})


# ==================== Bot / Report ====================

@app.route("/projects/report-issue/", methods=["GET", "POST"])
def report_issue():
    """Report an issue with a project configuration.
    An administrator will review the submitted URL.
    """
    message = None
    if request.method == "POST":
        url = request.form.get("url", "")
        if not url:
            message = "Please provide a URL."
        elif not url.startswith("http"):
            message = "Please provide a valid URL."
        else:
            base_url = "http://127.0.0.1:5000"
            admin_token = ADMIN_TOKEN
            thread = threading.Thread(
                target=visit_url,
                args=(url, base_url, admin_token),
                daemon=True
            )
            thread.start()
            message = "Thank you. An administrator will review your report shortly."
    return render_template("report.html", message=message)


@app.route("/api/report/", methods=["POST"])
def api_report_issue():
    """API endpoint to report an issue URL for admin review."""
    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    if not url:
        url = request.form.get("url", "")
    if not url or not url.startswith("http"):
        return jsonify({"error": "Valid URL required"}), 400

    base_url = "http://127.0.0.1:5000"
    admin_token = ADMIN_TOKEN
    thread = threading.Thread(
        target=visit_url,
        args=(url, base_url, admin_token),
        daemon=True
    )
    thread.start()
    return jsonify({"status": "Report submitted. An administrator will review it."})


# ==================== Collector Endpoint ====================

COLLECTED_DATA = {}


@app.route("/api/webhooks/receiver", methods=["POST", "GET"])
def webhook_receiver():
    """Generic webhook receiver for integration testing."""
    token = request.args.get("token", request.form.get("token", ""))
    data = request.args.get("data", request.form.get("data", ""))
    if token:
        COLLECTED_DATA[token] = data
    return jsonify({"status": "received"})


@app.route("/api/webhooks/results/<token>", methods=["GET"])
def webhook_results(token):
    data = COLLECTED_DATA.get(token)
    if data:
        return jsonify({"data": data})
    return jsonify({"data": None}), 404


# ==================== Version / Info ====================

@app.route("/version")
def version_info():
    return jsonify({
        "version": "1.17.0",
        "label-studio-frontend": "1.0.0",
        "label-studio-converter": "0.0.58",
    })


if __name__ == "__main__":
    os.makedirs("/app/data", exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=False)
