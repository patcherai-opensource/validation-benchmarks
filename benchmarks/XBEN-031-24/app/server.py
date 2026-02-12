"""
MLflow Tracking Server - REST API
"""
import json
import os
import time
import uuid
import logging
from urllib.parse import urlparse

from flask import Flask, request, jsonify, Response

from store import FileStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mlflow.server")

app = Flask(__name__)

_artifact_root = os.environ.get("MLFLOW_ARTIFACT_ROOT", "/data/mlartifacts")
_file_store = FileStore(root_directory="/data/mlruns", artifact_root=_artifact_root)


def _get_request_json():
    return request.get_json(force=True, silent=True) or {}


def _validate_tag_name(tag_name):
    if not tag_name or not isinstance(tag_name, str):
        raise ValueError("Invalid tag name")
    return tag_name.strip()


# Health endpoints
@app.route("/health")
def health():
    return jsonify({"status": "OK"})


@app.route("/")
def index():
    return jsonify({
        "service": "mlflow-tracking",
        "version": "2.9.2",
        "status": "running"
    })


@app.route("/version")
def version():
    return Response("2.9.2\n", content_type="text/plain")


# REST API 2.0 endpoints

@app.route("/api/2.0/mlflow/experiments/create", methods=["POST"])
def create_experiment():
    req = _get_request_json()
    name = req.get("name")
    if not name:
        return jsonify({
            "error_code": "INVALID_PARAMETER_VALUE",
            "message": "No experiment name provided."
        }), 400

    artifact_location = req.get("artifact_location")
    tags = req.get("tags", [])

    try:
        experiment_id = _file_store.create_experiment(
            name=name,
            artifact_location=artifact_location,
            tags=tags
        )
    except ValueError as e:
        return jsonify({
            "error_code": "INVALID_PARAMETER_VALUE",
            "message": str(e)
        }), 400
    except FileExistsError:
        return jsonify({
            "error_code": "RESOURCE_ALREADY_EXISTS",
            "message": f"Experiment(name={name}) already exists."
        }), 409

    return jsonify({"experiment_id": str(experiment_id)})


@app.route("/api/2.0/mlflow/experiments/get", methods=["GET"])
def get_experiment():
    experiment_id = request.args.get("experiment_id")
    if not experiment_id:
        return jsonify({
            "error_code": "INVALID_PARAMETER_VALUE",
            "message": "No experiment_id provided."
        }), 400

    experiment = _file_store.get_experiment(experiment_id)
    if experiment is None:
        return jsonify({
            "error_code": "RESOURCE_DOES_NOT_EXIST",
            "message": f"Could not find experiment with ID {experiment_id}"
        }), 404

    return jsonify({"experiment": experiment})


@app.route("/api/2.0/mlflow/experiments/search", methods=["POST", "GET"])
def search_experiments():
    experiments = _file_store.search_experiments()
    return jsonify({"experiments": experiments})


@app.route("/api/2.0/mlflow/experiments/delete", methods=["POST"])
def delete_experiment():
    req = _get_request_json()
    experiment_id = req.get("experiment_id")
    if not experiment_id:
        return jsonify({
            "error_code": "INVALID_PARAMETER_VALUE",
            "message": "No experiment_id provided."
        }), 400

    success = _file_store.delete_experiment(experiment_id)
    if not success:
        return jsonify({
            "error_code": "RESOURCE_DOES_NOT_EXIST",
            "message": f"Could not find experiment with ID {experiment_id}"
        }), 404

    return jsonify({})


@app.route("/api/2.0/mlflow/runs/create", methods=["POST"])
def create_run():
    req = _get_request_json()
    experiment_id = req.get("experiment_id", "0")
    user_id = req.get("user_id", "")
    run_name = req.get("run_name", "")
    start_time = req.get("start_time", int(time.time() * 1000))
    tags = req.get("tags", [])

    experiment = _file_store.get_experiment(experiment_id)
    if experiment is None:
        return jsonify({
            "error_code": "RESOURCE_DOES_NOT_EXIST",
            "message": f"Could not find experiment with ID {experiment_id}"
        }), 404

    run = _file_store.create_run(
        experiment_id=experiment_id,
        user_id=user_id,
        run_name=run_name,
        start_time=start_time,
        tags=tags
    )
    return jsonify({"run": run})


@app.route("/api/2.0/mlflow/runs/get", methods=["GET"])
def get_run():
    run_id = request.args.get("run_id")
    if not run_id:
        return jsonify({
            "error_code": "INVALID_PARAMETER_VALUE",
            "message": "No run_id provided."
        }), 400

    run = _file_store.get_run(run_id)
    if run is None:
        return jsonify({
            "error_code": "RESOURCE_DOES_NOT_EXIST",
            "message": f"Run with id={run_id} not found"
        }), 404

    return jsonify({"run": run})


@app.route("/api/2.0/mlflow/runs/search", methods=["POST"])
def search_runs():
    req = _get_request_json()
    experiment_ids = req.get("experiment_ids", ["0"])
    runs = _file_store.search_runs(experiment_ids)
    return jsonify({"runs": runs})


@app.route("/api/2.0/mlflow/registered-models/create", methods=["POST"])
def create_registered_model():
    req = _get_request_json()
    name = req.get("name")
    if not name:
        return jsonify({
            "error_code": "INVALID_PARAMETER_VALUE",
            "message": "No registered model name provided."
        }), 400

    tags = req.get("tags", [])
    description = req.get("description", "")

    try:
        model = _file_store.create_registered_model(
            name=name, tags=tags, description=description
        )
    except FileExistsError:
        return jsonify({
            "error_code": "RESOURCE_ALREADY_EXISTS",
            "message": f"Registered Model (name={name}) already exists."
        }), 409

    return jsonify({"registered_model": model})


@app.route("/api/2.0/mlflow/registered-models/get", methods=["GET"])
def get_registered_model():
    name = request.args.get("name")
    if not name:
        return jsonify({
            "error_code": "INVALID_PARAMETER_VALUE",
            "message": "No name provided."
        }), 400

    model = _file_store.get_registered_model(name)
    if model is None:
        return jsonify({
            "error_code": "RESOURCE_DOES_NOT_EXIST",
            "message": f"Registered Model with name={name} not found."
        }), 404

    return jsonify({"registered_model": model})


@app.route("/api/2.0/mlflow/model-versions/create", methods=["POST"])
def create_model_version():
    req = _get_request_json()
    name = req.get("name")
    source = req.get("source")

    if not name:
        return jsonify({
            "error_code": "INVALID_PARAMETER_VALUE",
            "message": "No name provided."
        }), 400

    if not source:
        return jsonify({
            "error_code": "INVALID_PARAMETER_VALUE",
            "message": "No source provided."
        }), 400

    run_id = req.get("run_id", "")
    description = req.get("description", "")
    tags = req.get("tags", [])

    try:
        model_version = _file_store.create_model_version(
            name=name,
            source=source,
            run_id=run_id,
            description=description,
            tags=tags
        )
    except ValueError as e:
        return jsonify({
            "error_code": "INVALID_PARAMETER_VALUE",
            "message": str(e)
        }), 400
    except FileNotFoundError:
        return jsonify({
            "error_code": "RESOURCE_DOES_NOT_EXIST",
            "message": f"Registered Model with name={name} not found."
        }), 404

    return jsonify({"model_version": model_version})


@app.route("/api/2.0/mlflow/model-versions/get", methods=["GET"])
def get_model_version():
    name = request.args.get("name")
    version = request.args.get("version")

    if not name or not version:
        return jsonify({
            "error_code": "INVALID_PARAMETER_VALUE",
            "message": "Both name and version are required."
        }), 400

    mv = _file_store.get_model_version(name, version)
    if mv is None:
        return jsonify({
            "error_code": "RESOURCE_DOES_NOT_EXIST",
            "message": f"Model Version (name={name}, version={version}) not found."
        }), 404

    return jsonify({"model_version": mv})


@app.route("/api/2.0/mlflow/artifacts/list", methods=["GET"])
def list_artifacts():
    run_id = request.args.get("run_id")
    path = request.args.get("path", "")

    if not run_id:
        return jsonify({
            "error_code": "INVALID_PARAMETER_VALUE",
            "message": "No run_id provided."
        }), 400

    artifacts = _file_store.list_artifacts(run_id, path)
    return jsonify(artifacts)


@app.route("/api/2.0/mlflow/artifacts/get", methods=["GET"])
def get_artifact():
    run_id = request.args.get("run_id")
    path = request.args.get("path", "")

    if not run_id:
        return jsonify({
            "error_code": "INVALID_PARAMETER_VALUE",
            "message": "No run_id provided."
        }), 400

    content = _file_store.get_artifact(run_id, path)
    if content is None:
        return jsonify({
            "error_code": "RESOURCE_DOES_NOT_EXIST",
            "message": "Artifact not found."
        }), 404

    return Response(content, content_type="application/octet-stream")


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error_code": "ENDPOINT_NOT_FOUND",
        "message": "The requested endpoint was not found."
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error_code": "INTERNAL_ERROR",
        "message": "An internal error occurred."
    }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
