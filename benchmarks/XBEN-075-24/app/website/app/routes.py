import os
import shutil

import yaml
from flask import (
    render_template,
    redirect,
    url_for,
    request,
    jsonify,
)
from werkzeug.utils import secure_filename

from app import app, UPLOAD_DIR
from app.models import ModelProject, TASK_TYPES


ALLOWED_EXTENSIONS = {"yaml", "yml"}

# In-memory project registry (simulates database)
_projects = {}


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _get_project(project_id):
    return _projects.get(project_id)


@app.after_request
def set_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Internal server error"), 500


# ── Dashboard ──────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    projects = sorted(_projects.values(), key=lambda p: p.created_at, reverse=True)
    return render_template("dashboard.html", projects=projects)


# ── Project management ─────────────────────────────────────────────

@app.route("/projects/new", methods=["GET", "POST"])
def create_project():
    if request.method == "GET":
        return render_template("create_project.html", task_types=TASK_TYPES)

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    task_type = request.form.get("task_type", "classification")

    if not name:
        return render_template(
            "create_project.html",
            task_types=TASK_TYPES,
            error="Project name is required.",
        )

    project = ModelProject(name=name, description=description, task_type=task_type)
    save_path = project.get_save_path(UPLOAD_DIR)
    os.makedirs(save_path, exist_ok=True)

    _projects[project.id] = project
    return redirect(url_for("project_detail", project_id=project.id))


@app.route("/projects/<project_id>")
def project_detail(project_id):
    project = _get_project(project_id)
    if not project:
        return render_template("error.html", code=404, message="Project not found"), 404

    save_path = project.get_save_path(UPLOAD_DIR)
    config_files = []
    if os.path.isdir(save_path):
        config_files = [
            f for f in os.listdir(save_path)
            if f.endswith((".yaml", ".yml"))
        ]

    return render_template(
        "project_detail.html", project=project, config_files=config_files
    )


@app.route("/projects/<project_id>/delete", methods=["POST"])
def delete_project(project_id):
    project = _get_project(project_id)
    if project:
        save_path = project.get_save_path(UPLOAD_DIR)
        if os.path.isdir(save_path):
            shutil.rmtree(save_path, ignore_errors=True)
        del _projects[project_id]
    return redirect(url_for("dashboard"))


# ── Config file upload ─────────────────────────────────────────────

@app.route("/projects/<project_id>/upload", methods=["POST"])
def upload_config(project_id):
    project = _get_project(project_id)
    if not project:
        return render_template("error.html", code=404, message="Project not found"), 404

    if "config_file" not in request.files:
        return redirect(url_for("project_detail", project_id=project_id))

    f = request.files["config_file"]
    if f.filename == "":
        return redirect(url_for("project_detail", project_id=project_id))

    if not _allowed_file(f.filename):
        return render_template(
            "project_detail.html",
            project=project,
            config_files=[],
            error="Only .yaml/.yml files are allowed.",
        )

    filename = secure_filename(f.filename)
    save_path = project.get_save_path(UPLOAD_DIR)
    os.makedirs(save_path, exist_ok=True)
    f.save(os.path.join(save_path, filename))

    return redirect(url_for("project_detail", project_id=project_id))


# ── Evaluate / Load Model Config ──────────────────────────────────
# Loads the best_k_models.yaml (or specified config) from the project
# save directory and uses it for model evaluation aggregation.

@app.route("/projects/<project_id>/evaluate", methods=["POST"])
def evaluate_model(project_id):
    project = _get_project(project_id)
    if not project:
        return render_template("error.html", code=404, message="Project not found"), 404

    config_name = request.form.get("config_file", "best_k_models.yaml")
    config_name = os.path.basename(config_name)
    save_path = project.get_save_path(UPLOAD_DIR)
    config_path = os.path.join(save_path, config_name)

    if not os.path.isfile(config_path):
        return render_template(
            "project_detail.html",
            project=project,
            config_files=[
                cf for cf in os.listdir(save_path)
                if cf.endswith((".yaml", ".yml"))
            ],
            error="Configuration file not found. Please upload it first.",
        )

    # Load model configuration for top-k averaging
    with open(config_path, "r") as fh:
        model_config = yaml.load(fh, Loader=yaml.Loader)

    project.status = "evaluated"

    # Process results for display
    if isinstance(model_config, dict):
        results = model_config
    elif isinstance(model_config, list):
        results = {f"model_{i}": v for i, v in enumerate(model_config)}
    else:
        results = {"output": str(model_config)}

    return render_template(
        "evaluate_results.html",
        project=project,
        results=results,
        config_name=config_name,
    )


# ── API endpoints ──────────────────────────────────────────────────

@app.route("/api/v1/projects", methods=["GET"])
def api_list_projects():
    return jsonify(
        {"projects": [p.to_dict() for p in _projects.values()]}
    )


@app.route("/api/v1/projects/<project_id>", methods=["GET"])
def api_get_project(project_id):
    project = _get_project(project_id)
    if not project:
        return jsonify({"error": "not found"}), 404
    return jsonify(project.to_dict())


# ── Documentation ──────────────────────────────────────────────────

@app.route("/docs")
def docs():
    return render_template("docs.html")
