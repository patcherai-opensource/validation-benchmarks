"""
MLflow Tracking Server - lightweight implementation
"""
import os
import json
import time
import uuid
import urllib.parse
import logging
import re

from flask import Flask, request, jsonify, Response, render_template, send_from_directory
from store import FileStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mlflow.server")

app = Flask(__name__, static_folder="static", template_folder="templates")

ARTIFACT_ROOT = os.environ.get("MLFLOW_ARTIFACT_ROOT", "./mlruns")
BACKEND_STORE_URI = os.environ.get("MLFLOW_BACKEND_STORE_URI", "./mlruns")

_tracking_store = None


def _get_tracking_store():
    global _tracking_store
    if _tracking_store is None:
        _tracking_store = FileStore(BACKEND_STORE_URI, ARTIFACT_ROOT)
    return _tracking_store


def _validate_query_string(query_string):
    """Validate that query string doesn't contain path traversal sequences."""
    if query_string and ".." in query_string:
        raise ValueError(
            "Invalid query string: query string must not contain '..' sequences"
        )


# ========================
# REST API Endpoints
# ========================

@app.route("/api/2.0/mlflow/experiments/create", methods=["POST"])
def create_experiment():
    """Create an experiment with optional artifact_location."""
    try:
        req = request.get_json(force=True)
    except Exception:
        return jsonify({"error_code": "INVALID_PARAMETER_VALUE",
                        "message": "Request body must be valid JSON"}), 400

    name = req.get("name")
    if not name:
        return jsonify({"error_code": "INVALID_PARAMETER_VALUE",
                        "message": "Missing value for required parameter 'name'"}), 400

    artifact_location = req.get("artifact_location", "")
    tags = req.get("tags", [])

    # Validate artifact_location if provided
    if artifact_location:
        parsed_artifact_location = urllib.parse.urlparse(artifact_location)
        _validate_query_string(parsed_artifact_location.query)

    try:
        store = _get_tracking_store()
        experiment_id = store.create_experiment(name, artifact_location, tags)
    except ValueError as e:
        return jsonify({"error_code": "RESOURCE_ALREADY_EXISTS",
                        "message": str(e)}), 400

    return jsonify({"experiment_id": str(experiment_id)})


@app.route("/api/2.0/mlflow/experiments/get", methods=["GET"])
def get_experiment():
    """Get experiment details by ID."""
    experiment_id = request.args.get("experiment_id")
    if not experiment_id:
        return jsonify({"error_code": "INVALID_PARAMETER_VALUE",
                        "message": "Missing value for required parameter 'experiment_id'"}), 400

    store = _get_tracking_store()
    experiment = store.get_experiment(experiment_id)
    if experiment is None:
        return jsonify({"error_code": "RESOURCE_DOES_NOT_EXIST",
                        "message": f"Could not find experiment with ID {experiment_id}"}), 404

    return jsonify({"experiment": experiment})


@app.route("/api/2.0/mlflow/experiments/search", methods=["POST", "GET"])
def search_experiments():
    """List/search experiments."""
    store = _get_tracking_store()
    experiments = store.list_experiments()
    return jsonify({"experiments": experiments})


@app.route("/api/2.0/mlflow/experiments/delete", methods=["POST"])
def delete_experiment():
    """Delete an experiment."""
    try:
        req = request.get_json(force=True)
    except Exception:
        return jsonify({"error_code": "INVALID_PARAMETER_VALUE",
                        "message": "Request body must be valid JSON"}), 400

    experiment_id = req.get("experiment_id")
    if not experiment_id:
        return jsonify({"error_code": "INVALID_PARAMETER_VALUE",
                        "message": "Missing value for required parameter 'experiment_id'"}), 400

    store = _get_tracking_store()
    if store.delete_experiment(experiment_id):
        return jsonify({})
    return jsonify({"error_code": "RESOURCE_DOES_NOT_EXIST",
                    "message": f"Could not find experiment with ID {experiment_id}"}), 404


@app.route("/api/2.0/mlflow/runs/create", methods=["POST"])
def create_run():
    """Create a new run within an experiment."""
    try:
        req = request.get_json(force=True)
    except Exception:
        return jsonify({"error_code": "INVALID_PARAMETER_VALUE",
                        "message": "Request body must be valid JSON"}), 400

    experiment_id = req.get("experiment_id", "0")
    store = _get_tracking_store()
    experiment = store.get_experiment(experiment_id)
    if experiment is None:
        return jsonify({"error_code": "RESOURCE_DOES_NOT_EXIST",
                        "message": f"Could not find experiment with ID {experiment_id}"}), 404

    run_id = uuid.uuid4().hex
    artifact_location = experiment.get("artifact_location", "")

    run = {
        "info": {
            "run_id": run_id,
            "run_uuid": run_id,
            "experiment_id": experiment_id,
            "status": "RUNNING",
            "start_time": int(time.time() * 1000),
            "artifact_uri": artifact_location + "/" + run_id + "/artifacts",
            "lifecycle_stage": "active"
        },
        "data": {
            "metrics": [],
            "params": [],
            "tags": req.get("tags", [])
        }
    }

    store.create_run(experiment_id, run_id, run)
    return jsonify({"run": run})


@app.route("/api/2.0/mlflow/runs/get", methods=["GET"])
def get_run():
    """Get run details."""
    run_id = request.args.get("run_id")
    if not run_id:
        return jsonify({"error_code": "INVALID_PARAMETER_VALUE",
                        "message": "Missing value for required parameter 'run_id'"}), 400

    store = _get_tracking_store()
    run = store.get_run(run_id)
    if run is None:
        return jsonify({"error_code": "RESOURCE_DOES_NOT_EXIST",
                        "message": f"Could not find run with ID {run_id}"}), 404

    return jsonify({"run": run})


@app.route("/api/2.0/mlflow/runs/search", methods=["POST"])
def search_runs():
    """Search for runs."""
    try:
        req = request.get_json(force=True)
    except Exception:
        req = {}

    experiment_ids = req.get("experiment_ids", [])
    store = _get_tracking_store()
    runs = store.search_runs(experiment_ids)
    return jsonify({"runs": runs})


@app.route("/api/2.0/mlflow/artifacts/list", methods=["GET"])
def list_artifacts():
    """List artifacts for a run. Resolves artifact paths from experiment artifact_location."""
    run_id = request.args.get("run_id")
    path = request.args.get("path", "")

    if not run_id:
        return jsonify({"error_code": "INVALID_PARAMETER_VALUE",
                        "message": "Missing value for required parameter 'run_id'"}), 400

    store = _get_tracking_store()
    run = store.get_run(run_id)
    if run is None:
        return jsonify({"error_code": "RESOURCE_DOES_NOT_EXIST",
                        "message": f"Could not find run with ID {run_id}"}), 404

    artifact_uri = run["info"]["artifact_uri"]
    artifact_path = _resolve_artifact_path(artifact_uri, path)

    files = []
    if os.path.isdir(artifact_path):
        for entry in os.listdir(artifact_path):
            full = os.path.join(artifact_path, entry)
            files.append({
                "path": entry,
                "is_dir": os.path.isdir(full),
                "file_size": os.path.getsize(full) if os.path.isfile(full) else 0
            })
    elif os.path.isfile(artifact_path):
        files.append({
            "path": os.path.basename(artifact_path),
            "is_dir": False,
            "file_size": os.path.getsize(artifact_path)
        })

    return jsonify({
        "root_uri": artifact_uri,
        "files": files
    })


@app.route("/get-artifact", methods=["GET"])
def get_artifact():
    """Download an artifact file. Resolves the artifact path from the run's artifact_uri."""
    run_id = request.args.get("run_id")
    path = request.args.get("path", "")

    if not run_id:
        return jsonify({"error_code": "INVALID_PARAMETER_VALUE",
                        "message": "Missing value for required parameter 'run_id'"}), 400

    store = _get_tracking_store()
    run = store.get_run(run_id)
    if run is None:
        return jsonify({"error_code": "RESOURCE_DOES_NOT_EXIST",
                        "message": f"Could not find run with ID {run_id}"}), 404

    artifact_uri = run["info"]["artifact_uri"]
    artifact_path = _resolve_artifact_path(artifact_uri, path)

    if os.path.isfile(artifact_path):
        try:
            with open(artifact_path, "r") as f:
                content = f.read()
            return Response(content, mimetype="text/plain")
        except Exception:
            return jsonify({"error_code": "INTERNAL_ERROR",
                            "message": "Failed to read artifact"}), 500

    return jsonify({"error_code": "RESOURCE_DOES_NOT_EXIST",
                    "message": f"Artifact not found: {path}"}), 404


@app.route("/api/2.0/mlflow/experiments/get-artifact", methods=["GET"])
def get_experiment_artifact():
    """
    Retrieve an artifact from an experiment's artifact store.
    Resolves path from the experiment's artifact_location.
    """
    experiment_id = request.args.get("experiment_id")
    path = request.args.get("path", "")

    if not experiment_id:
        return jsonify({"error_code": "INVALID_PARAMETER_VALUE",
                        "message": "Missing value for required parameter 'experiment_id'"}), 400

    store = _get_tracking_store()
    experiment = store.get_experiment(experiment_id)
    if experiment is None:
        return jsonify({"error_code": "RESOURCE_DOES_NOT_EXIST",
                        "message": f"Could not find experiment with ID {experiment_id}"}), 404

    artifact_location = experiment.get("artifact_location", "")
    artifact_path = _resolve_artifact_path(artifact_location, path)

    if os.path.isfile(artifact_path):
        try:
            with open(artifact_path, "r") as f:
                content = f.read()
            return Response(content, mimetype="text/plain")
        except Exception:
            return jsonify({"error_code": "INTERNAL_ERROR",
                            "message": "Failed to read artifact"}), 500

    if os.path.isdir(artifact_path):
        files = []
        for entry in os.listdir(artifact_path):
            full = os.path.join(artifact_path, entry)
            files.append({
                "path": entry,
                "is_dir": os.path.isdir(full),
                "file_size": os.path.getsize(full) if os.path.isfile(full) else 0
            })
        return jsonify({"root_uri": artifact_location, "files": files})

    return jsonify({"error_code": "RESOURCE_DOES_NOT_EXIST",
                    "message": f"Artifact not found: {path}"}), 404


def _resolve_artifact_path(artifact_uri, relative_path=""):
    """
    Resolve the local filesystem path for an artifact given an artifact URI.
    Handles file:// URIs and local paths.
    """
    parsed = urllib.parse.urlparse(artifact_uri)
    if parsed.scheme == "file" or parsed.scheme == "":
        # Reconstruct local path from the parsed URI components
        base_path = parsed.path
        if parsed.fragment:
            base_path = os.path.join(base_path, parsed.fragment)
    else:
        base_path = artifact_uri

    if relative_path:
        return os.path.join(base_path, relative_path)
    return base_path


# ========================
# Registered Models API (stubs)
# ========================

@app.route("/api/2.0/mlflow/registered-models/search", methods=["GET"])
def search_models():
    return jsonify({"registered_models": []})


@app.route("/api/2.0/mlflow/registered-models/create", methods=["POST"])
def create_model():
    try:
        req = request.get_json(force=True)
    except Exception:
        return jsonify({"error_code": "INVALID_PARAMETER_VALUE",
                        "message": "Request body must be valid JSON"}), 400
    name = req.get("name", "")
    return jsonify({
        "registered_model": {
            "name": name,
            "creation_timestamp": int(time.time() * 1000),
            "last_updated_timestamp": int(time.time() * 1000),
            "tags": []
        }
    })


# ========================
# Web UI Endpoints
# ========================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "OK"})


@app.route("/version")
def version():
    return "2.11.2"


@app.route("/ajax-api/2.0/mlflow/experiments/search", methods=["GET", "POST"])
def ajax_search_experiments():
    return search_experiments()


@app.route("/ajax-api/2.0/mlflow/runs/search", methods=["POST"])
def ajax_search_runs():
    return search_runs()


@app.route("/ajax-api/2.0/mlflow/artifacts/list", methods=["GET"])
def ajax_list_artifacts():
    return list_artifacts()


@app.route("/ajax-api/2.0/mlflow/registered-models/search", methods=["GET"])
def ajax_search_models():
    return search_models()


# Catch-all for SPA routing
@app.route("/<path:path>")
def catch_all(path):
    # Serve static files if they exist
    if ".." not in path:
        try:
            return send_from_directory(app.static_folder, path)
        except Exception:
            pass
    # Otherwise return the SPA index
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
