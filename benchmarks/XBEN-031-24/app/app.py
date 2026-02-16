import json
import os
import pathlib
import time
import urllib.parse
import uuid

from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# Internal data storage
_projects = {}
_runs = {}
_model_registry = {}
_model_versions = {}

DEFAULT_STORAGE_ROOT = os.environ.get(
    "_TRACKER_STORAGE_ROOT", "/opt/platform/data/storage"
)


# ---------------------------------------------------------------------------
# URI / path validation helpers
# ---------------------------------------------------------------------------

def _decode_uri(url):
    for _ in range(10):
        decoded = urllib.parse.unquote(url)
        if decoded == url:
            return url
        url = decoded
    raise ValueError("Failed to decode url")


def _check_query_string(query):
    """Block query strings that contain traversal sequences."""
    query = _decode_uri(query)
    if ".." in query:
        raise ValueError("Invalid query string")


def _check_path_is_safe(path):
    """Validate that a relative artifact path does not escape its root."""
    path = _decode_uri(path)
    if "#" in path:
        raise ValueError("Invalid path")
    if (
        any((s in path) for s in ("\\",))
        or ".." in path.split("/")
        or pathlib.PurePosixPath(path).is_absolute()
    ):
        raise ValueError("Invalid path")
    return path


def _is_local_uri(uri):
    parsed = urllib.parse.urlparse(uri)
    if parsed.scheme == "" or parsed.scheme == "file":
        return True
    return False


def _local_file_uri_to_path(uri):
    parsed = urllib.parse.urlparse(uri)
    path = urllib.parse.unquote(parsed.path)
    return path


def _validate_non_local_origin_paths(origin):
    """Ensure remote origins don't contain relative path traversal."""
    invalid_msg = (
        f"Invalid model snapshot origin: '{origin}'. "
        "An absolute path must be provided without relative path references."
    )
    while (unquoted := urllib.parse.unquote_plus(origin)) != origin:
        origin = unquoted
    origin_path = urllib.parse.urlparse(origin).path.rstrip("/")
    import re
    origin_path = re.sub(r"/+", "/", origin_path)
    if "\x00" in origin_path:
        raise ValueError(invalid_msg)
    resolved = pathlib.Path(origin_path).resolve().as_posix()
    _, resolved_path = os.path.splitdrive(resolved)
    if resolved_path != origin_path:
        raise ValueError(invalid_msg)


def _validate_origin(origin, run_id):
    if _is_local_uri(origin):
        if run_id:
            run = _runs.get(run_id)
            if run:
                origin_resolved = pathlib.Path(
                    _local_file_uri_to_path(origin)
                ).resolve()
                run_artifact_dir = pathlib.Path(run["artifact_uri"]).resolve()
                if run_artifact_dir in [origin_resolved, *origin_resolved.parents]:
                    return
        raise ValueError(
            f"Invalid model snapshot origin: '{origin}'. "
            "To use a local path, the run_id parameter must be specified and "
            "the path must be within the run's artifact directory."
        )
    _validate_non_local_origin_paths(origin)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TrackerException(Exception):
    def __init__(self, message, error_code="INVALID_PARAMETER_VALUE"):
        super().__init__(message)
        self.error_code = error_code


@app.errorhandler(TrackerException)
def handle_tracker_exception(e):
    return jsonify({"error_code": e.error_code, "message": str(e)}), 400


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error_code": "BAD_REQUEST", "message": str(e)}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error_code": "RESOURCE_NOT_FOUND", "message": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error_code": "INTERNAL_ERROR", "message": "An internal error occurred"}), 500


# ---------------------------------------------------------------------------
# Health / version endpoints
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return Response(
        "<html><head><title>ML Tracker</title></head>"
        "<body><h1>ML Experiment Tracker</h1>"
        "<p>API available at /api/2.0/tracker/</p></body></html>",
        mimetype="text/html",
    )


@app.route("/health")
def health():
    return "OK", 200


@app.route("/version")
def version():
    return "2.9.1", 200


# ---------------------------------------------------------------------------
# Project (Experiment) APIs
# ---------------------------------------------------------------------------

@app.route("/api/2.0/tracker/projects/create", methods=["POST"])
def create_project():
    try:
        data = request.get_json(force=True)
    except Exception:
        raise TrackerException("Invalid JSON payload")

    name = data.get("name")
    if not name or not isinstance(name, str):
        raise TrackerException("Missing or invalid required parameter 'name'")

    storage_path = data.get("storage_path", "")
    tags = data.get("tags", [])

    if storage_path:
        # Validate the storage path to prevent malicious inputs
        parsed_storage = urllib.parse.urlparse(storage_path)

        # Reject non-local schemes except file://
        if parsed_storage.scheme and parsed_storage.scheme not in ("file", ""):
            raise TrackerException(
                f"Unsupported storage scheme: '{parsed_storage.scheme}'. "
                "Only local file paths and file:// URIs are supported."
            )

        # Validate query string to prevent path traversal attacks
        _check_query_string(parsed_storage.query)


    project_id = str(len(_projects) + 1)
    if not storage_path:
        storage_path = os.path.join(DEFAULT_STORAGE_ROOT, project_id)

    project = {
        "project_id": project_id,
        "name": name,
        "storage_path": storage_path,
        "lifecycle_stage": "active",
        "creation_time": int(time.time() * 1000),
        "last_update_time": int(time.time() * 1000),
        "tags": tags,
    }
    _projects[project_id] = project

    return jsonify({"project_id": project_id})


@app.route("/api/2.0/tracker/projects/get", methods=["GET"])
def get_project():
    project_id = request.args.get("project_id")
    if not project_id:
        raise TrackerException("Missing required parameter 'project_id'")

    project = _projects.get(project_id)
    if not project:
        raise TrackerException(
            f"Project with id '{project_id}' not found",
            error_code="RESOURCE_DOES_NOT_EXIST",
        )

    return jsonify({"project": project})


@app.route("/api/2.0/tracker/projects/search", methods=["POST", "GET"])
def search_projects():
    results = []
    for p in _projects.values():
        if p["lifecycle_stage"] == "active":
            results.append(p)
    return jsonify({"projects": results})


@app.route("/api/2.0/tracker/projects/update", methods=["POST"])
def update_project():
    try:
        data = request.get_json(force=True)
    except Exception:
        raise TrackerException("Invalid JSON payload")

    project_id = data.get("project_id")
    if not project_id:
        raise TrackerException("Missing required parameter 'project_id'")

    project = _projects.get(project_id)
    if not project:
        raise TrackerException(
            f"Project with id '{project_id}' not found",
            error_code="RESOURCE_DOES_NOT_EXIST",
        )

    new_name = data.get("new_name")
    if new_name:
        project["name"] = new_name
        project["last_update_time"] = int(time.time() * 1000)

    return jsonify({})


@app.route("/api/2.0/tracker/projects/delete", methods=["POST"])
def delete_project():
    try:
        data = request.get_json(force=True)
    except Exception:
        raise TrackerException("Invalid JSON payload")

    project_id = data.get("project_id")
    if not project_id:
        raise TrackerException("Missing required parameter 'project_id'")

    project = _projects.get(project_id)
    if not project:
        raise TrackerException(
            f"Project with id '{project_id}' not found",
            error_code="RESOURCE_DOES_NOT_EXIST",
        )

    project["lifecycle_stage"] = "deleted"
    return jsonify({})


# ---------------------------------------------------------------------------
# Run APIs
# ---------------------------------------------------------------------------

@app.route("/api/2.0/tracker/runs/create", methods=["POST"])
def create_run():
    try:
        data = request.get_json(force=True)
    except Exception:
        raise TrackerException("Invalid JSON payload")

    project_id = data.get("project_id", "0")
    project = _projects.get(project_id)

    run_id = str(uuid.uuid4()).replace("-", "")
    artifact_uri = os.path.join(
        DEFAULT_STORAGE_ROOT, project_id if project else "0", run_id, "artifacts"
    )

    run = {
        "run_id": run_id,
        "project_id": project_id,
        "status": "RUNNING",
        "start_time": int(time.time() * 1000),
        "end_time": 0,
        "artifact_uri": artifact_uri,
        "lifecycle_stage": "active",
        "metrics": [],
        "params": [],
        "tags": [],
    }
    _runs[run_id] = run

    return jsonify({"run": {"info": {
        "run_id": run_id,
        "project_id": project_id,
        "status": "RUNNING",
        "artifact_uri": artifact_uri,
    }}})


@app.route("/api/2.0/tracker/runs/get", methods=["GET"])
def get_run():
    run_id = request.args.get("run_id")
    if not run_id:
        raise TrackerException("Missing required parameter 'run_id'")

    run = _runs.get(run_id)
    if not run:
        raise TrackerException(
            f"Run with id '{run_id}' not found",
            error_code="RESOURCE_DOES_NOT_EXIST",
        )

    return jsonify({"run": run})


@app.route("/api/2.0/tracker/runs/search", methods=["POST"])
def search_runs():
    try:
        data = request.get_json(force=True)
    except Exception:
        data = {}

    project_ids = data.get("project_ids", [])
    results = []
    for r in _runs.values():
        if not project_ids or r["project_id"] in project_ids:
            results.append(r)
    return jsonify({"runs": results})


@app.route("/api/2.0/tracker/runs/log-metric", methods=["POST"])
def log_metric():
    try:
        data = request.get_json(force=True)
    except Exception:
        raise TrackerException("Invalid JSON payload")

    run_id = data.get("run_id")
    if not run_id:
        raise TrackerException("Missing required parameter 'run_id'")

    run = _runs.get(run_id)
    if not run:
        raise TrackerException(
            f"Run with id '{run_id}' not found",
            error_code="RESOURCE_DOES_NOT_EXIST",
        )

    metric = {
        "key": data.get("key", ""),
        "value": data.get("value", 0),
        "timestamp": data.get("timestamp", int(time.time() * 1000)),
        "step": data.get("step", 0),
    }
    run["metrics"].append(metric)
    return jsonify({})


@app.route("/api/2.0/tracker/runs/log-parameter", methods=["POST"])
def log_param():
    try:
        data = request.get_json(force=True)
    except Exception:
        raise TrackerException("Invalid JSON payload")

    run_id = data.get("run_id")
    if not run_id:
        raise TrackerException("Missing required parameter 'run_id'")

    run = _runs.get(run_id)
    if not run:
        raise TrackerException(
            f"Run with id '{run_id}' not found",
            error_code="RESOURCE_DOES_NOT_EXIST",
        )

    param = {"key": data.get("key", ""), "value": data.get("value", "")}
    run["params"].append(param)
    return jsonify({})


# ---------------------------------------------------------------------------
# Artifacts APIs
# ---------------------------------------------------------------------------

@app.route("/api/2.0/tracker/artifacts/list", methods=["GET"])
def list_artifacts():
    project_id = request.args.get("project_id")
    run_id = request.args.get("run_id")
    path = request.args.get("path", "")
    root_uri = ""

    if run_id:
        run = _runs.get(run_id)
        if not run:
            raise TrackerException(
                f"Run with id '{run_id}' not found",
                error_code="RESOURCE_DOES_NOT_EXIST",
            )
        base_path = run["artifact_uri"]
        root_uri = base_path
    elif project_id:
        project = _projects.get(project_id)
        if not project:
            raise TrackerException(
                f"Project with id '{project_id}' not found",
                error_code="RESOURCE_DOES_NOT_EXIST",
            )
        storage = project["storage_path"]
        parsed = urllib.parse.urlparse(storage)
        base_path = parsed.path
        root_uri = storage
    else:
        raise TrackerException("Either 'project_id' or 'run_id' is required")

    if path:
        try:
            path = _check_path_is_safe(path)
        except ValueError:
            raise TrackerException("Invalid artifact path")
        full_path = os.path.join(base_path, path)
    else:
        full_path = base_path

    full_path = os.path.abspath(full_path)

    files = []
    if os.path.isdir(full_path):
        try:
            for entry in os.listdir(full_path):
                entry_path = os.path.join(full_path, entry)
                is_dir = os.path.isdir(entry_path)
                file_size = os.path.getsize(entry_path) if not is_dir else 0
                files.append({
                    "path": entry,
                    "is_dir": is_dir,
                    "file_size": file_size,
                })
        except PermissionError:
            pass
    elif os.path.isfile(full_path):
        files.append({
            "path": os.path.basename(full_path),
            "is_dir": False,
            "file_size": os.path.getsize(full_path),
        })

    return jsonify({
        "root_uri": root_uri,
        "files": files,
    })


@app.route("/api/2.0/tracker/artifacts/download", methods=["GET"])
def download_artifact():
    project_id = request.args.get("project_id")
    run_id = request.args.get("run_id")
    path = request.args.get("path", "")

    if run_id:
        run = _runs.get(run_id)
        if not run:
            raise TrackerException(
                f"Run with id '{run_id}' not found",
                error_code="RESOURCE_DOES_NOT_EXIST",
            )
        base_path = run["artifact_uri"]
    elif project_id:
        project = _projects.get(project_id)
        if not project:
            raise TrackerException(
                f"Project with id '{project_id}' not found",
                error_code="RESOURCE_DOES_NOT_EXIST",
            )
        storage = project["storage_path"]
        parsed = urllib.parse.urlparse(storage)
        base_path = parsed.path
    else:
        raise TrackerException("Either 'project_id' or 'run_id' is required")

    if path:
        try:
            path = _check_path_is_safe(path)
        except ValueError:
            raise TrackerException("Invalid artifact path")
        full_path = os.path.join(base_path, path)
    else:
        full_path = base_path

    full_path = os.path.abspath(full_path)

    if os.path.isfile(full_path):
        try:
            with open(full_path, "r") as f:
                content = f.read()
            return Response(content, mimetype="text/plain")
        except Exception:
            raise TrackerException("Failed to read artifact")
    else:
        raise TrackerException(
            "Artifact not found or is a directory",
            error_code="RESOURCE_DOES_NOT_EXIST",
        )


# ---------------------------------------------------------------------------
# Model Registry APIs
# ---------------------------------------------------------------------------

@app.route("/api/2.0/tracker/registered-models/create", methods=["POST"])
def create_registered_model():
    try:
        data = request.get_json(force=True)
    except Exception:
        raise TrackerException("Invalid JSON payload")

    name = data.get("name")
    if not name or not isinstance(name, str):
        raise TrackerException("Missing or invalid required parameter 'name'")

    if name in _model_registry:
        raise TrackerException(
            f"Registered model '{name}' already exists",
            error_code="RESOURCE_ALREADY_EXISTS",
        )

    model = {
        "name": name,
        "creation_timestamp": int(time.time() * 1000),
        "last_updated_timestamp": int(time.time() * 1000),
        "description": data.get("description", ""),
        "latest_versions": [],
        "tags": data.get("tags", []),
    }
    _model_registry[name] = model

    return jsonify({"registered_model": model})


@app.route("/api/2.0/tracker/registered-models/get", methods=["GET"])
def get_registered_model():
    name = request.args.get("name")
    if not name:
        raise TrackerException("Missing required parameter 'name'")

    model = _model_registry.get(name)
    if not model:
        raise TrackerException(
            f"Registered model '{name}' not found",
            error_code="RESOURCE_DOES_NOT_EXIST",
        )

    return jsonify({"registered_model": model})


@app.route("/api/2.0/tracker/registered-models/search", methods=["GET", "POST"])
def search_registered_models():
    return jsonify({"registered_models": list(_model_registry.values())})


@app.route("/api/2.0/tracker/model-snapshots/create", methods=["POST"])
def create_model_snapshot():
    try:
        data = request.get_json(force=True)
    except Exception:
        raise TrackerException("Invalid JSON payload")

    name = data.get("name")
    origin = data.get("origin")
    if not name or not isinstance(name, str):
        raise TrackerException("Missing or invalid required parameter 'name'")
    if not origin or not isinstance(origin, str):
        raise TrackerException("Missing or invalid required parameter 'origin'")

    if name not in _model_registry:
        raise TrackerException(
            f"Registered model '{name}' not found",
            error_code="RESOURCE_DOES_NOT_EXIST",
        )

    run_id = data.get("run_id", "")
    _validate_origin(origin, run_id)

    version_num = len(_model_versions) + 1
    snapshot = {
        "name": name,
        "version": str(version_num),
        "creation_timestamp": int(time.time() * 1000),
        "last_updated_timestamp": int(time.time() * 1000),
        "origin": origin,
        "run_id": run_id,
        "status": "READY",
        "description": data.get("description", ""),
        "tags": data.get("tags", []),
    }
    _model_versions[f"{name}/{version_num}"] = snapshot
    _model_registry[name]["latest_versions"].append(snapshot)

    return jsonify({"model_snapshot": snapshot})


@app.route("/api/2.0/tracker/model-snapshots/get", methods=["GET"])
def get_model_snapshot():
    name = request.args.get("name")
    version = request.args.get("version")
    if not name or not version:
        raise TrackerException("Missing required parameters 'name' and 'version'")

    key = f"{name}/{version}"
    snapshot = _model_versions.get(key)
    if not snapshot:
        raise TrackerException(
            f"Model snapshot '{name}' version '{version}' not found",
            error_code="RESOURCE_DOES_NOT_EXIST",
        )

    return jsonify({"model_snapshot": snapshot})


@app.route("/api/2.0/tracker/model-snapshots/search", methods=["GET", "POST"])
def search_model_snapshots():
    return jsonify({"model_snapshots": list(_model_versions.values())})


# ---------------------------------------------------------------------------
# GraphQL endpoint (stub - mirrors MLflow's real graphql endpoint)
# ---------------------------------------------------------------------------

@app.route("/graphql", methods=["GET", "POST"])
def graphql_endpoint():
    return jsonify({"errors": [{"message": "GraphQL endpoint is not configured"}]}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
