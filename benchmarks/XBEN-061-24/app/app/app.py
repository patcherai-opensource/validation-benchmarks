import os
import json
import uuid
import time
from urllib.parse import urlparse
from flask import Flask, request, jsonify, render_template, abort

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

DATA_DIR = "/app/mltracker_data"
EXPERIMENTS_DIR = os.path.join(DATA_DIR, "experiments")
ARTIFACTS_DIR = os.path.join(DATA_DIR, "artifacts")

os.makedirs(EXPERIMENTS_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

experiments_db = {}
model_versions_db = {}

def _init_default_experiment():
    default_exp = {
        "experiment_id": "0",
        "name": "Default",
        "artifact_location": f"file://{ARTIFACTS_DIR}/0",
        "lifecycle_stage": "active",
        "creation_time": int(time.time() * 1000),
        "last_update_time": int(time.time() * 1000)
    }
    experiments_db["0"] = default_exp
    os.makedirs(os.path.join(ARTIFACTS_DIR, "0"), exist_ok=True)

_init_default_experiment()


def _validate_artifact_location(artifact_location):
    """
    Validate artifact_location parameter.
    Only allows file:// URIs within the artifacts directory.
    """
    if not artifact_location:
        return True
    
    parsed = urlparse(artifact_location)
    
    if parsed.scheme and parsed.scheme not in ('file', ''):
        return False
    
    if parsed.query:
        return False
    
    if parsed.netloc and parsed.netloc not in ('', 'localhost'):
        return False
    
    path = parsed.path
    
    if '/../' in path or path.endswith('/..') or path.startswith('../') or path == '..':
        return False
    
    return True


def _resolve_artifact_path(artifact_location):
    """
    Resolve artifact location to filesystem path.
    Parses file:// URIs and returns the path component.
    """
    if not artifact_location:
        return None
    
    parsed = urlparse(artifact_location)
    return parsed.path


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/2.0/mltracker/experiments/list', methods=['GET'])
def list_experiments():
    experiments = list(experiments_db.values())
    return jsonify({"experiments": experiments})


@app.route('/api/2.0/mltracker/experiments/get', methods=['GET'])
def get_experiment():
    experiment_id = request.args.get('experiment_id')
    if not experiment_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", 
                                   "message": "experiment_id is required"}}), 400
    
    if experiment_id not in experiments_db:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST",
                                   "message": f"Experiment {experiment_id} not found"}}), 404
    
    return jsonify({"experiment": experiments_db[experiment_id]})


@app.route('/api/2.0/mltracker/experiments/create', methods=['POST'])
def create_experiment():
    data = request.get_json()
    if not data:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "Request body is required"}}), 400
    
    name = data.get('name')
    if not name:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "name is required"}}), 400
    
    for exp in experiments_db.values():
        if exp['name'] == name:
            return jsonify({"error": {"code": "RESOURCE_ALREADY_EXISTS",
                                       "message": f"Experiment {name} already exists"}}), 400
    
    artifact_location = data.get('artifact_location')
    
    if not _validate_artifact_location(artifact_location):
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "Invalid artifact_location"}}), 400
    
    experiment_id = str(len(experiments_db))
    
    if artifact_location:
        resolved_path = _resolve_artifact_path(artifact_location)
    else:
        resolved_path = os.path.join(ARTIFACTS_DIR, experiment_id)
        artifact_location = f"file://{resolved_path}"
    
    experiment = {
        "experiment_id": experiment_id,
        "name": name,
        "artifact_location": artifact_location,
        "lifecycle_stage": "active",
        "creation_time": int(time.time() * 1000),
        "last_update_time": int(time.time() * 1000)
    }
    
    experiments_db[experiment_id] = experiment
    
    try:
        if resolved_path and not os.path.exists(resolved_path):
            os.makedirs(resolved_path, exist_ok=True)
    except Exception:
        pass
    
    return jsonify({"experiment_id": experiment_id})


@app.route('/api/2.0/mltracker/experiments/get-artifact', methods=['GET'])
def get_artifact():
    experiment_id = request.args.get('experiment_id')
    artifact_path = request.args.get('path', '')
    
    if not experiment_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "experiment_id is required"}}), 400
    
    if experiment_id not in experiments_db:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST",
                                   "message": f"Experiment {experiment_id} not found"}}), 404
    
    experiment = experiments_db[experiment_id]
    artifact_location = experiment['artifact_location']
    
    base_path = _resolve_artifact_path(artifact_location)
    
    if artifact_path:
        full_path = os.path.join(base_path, artifact_path)
    else:
        full_path = base_path
    
    if os.path.isfile(full_path):
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            return jsonify({
                "artifact_path": artifact_path or os.path.basename(full_path),
                "content": content
            })
        except Exception as e:
            return jsonify({"error": {"code": "INTERNAL_ERROR",
                                       "message": "Failed to read artifact"}}), 500
    
    if os.path.isdir(full_path):
        try:
            files = os.listdir(full_path)
            return jsonify({
                "artifact_path": artifact_path or "/",
                "files": files
            })
        except Exception:
            return jsonify({"error": {"code": "INTERNAL_ERROR",
                                       "message": "Failed to list artifacts"}}), 500
    
    return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST",
                               "message": "Artifact not found"}}), 404


@app.route('/api/2.0/mltracker/model-versions/create', methods=['POST'])
def create_model_version():
    data = request.get_json()
    if not data:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "Request body is required"}}), 400
    
    name = data.get('name')
    source = data.get('source')
    
    if not name:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "name is required"}}), 400
    
    if not source:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "source is required"}}), 400
    
    if not _validate_artifact_location(source):
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "Invalid source location"}}), 400
    
    version_id = str(uuid.uuid4())[:8]
    version_number = len([v for v in model_versions_db.values() if v['name'] == name]) + 1
    
    model_version = {
        "name": name,
        "version": str(version_number),
        "creation_timestamp": int(time.time() * 1000),
        "last_updated_timestamp": int(time.time() * 1000),
        "source": source,
        "status": "READY",
        "version_id": version_id
    }
    
    model_versions_db[version_id] = model_version
    
    return jsonify({"model_version": model_version})


@app.route('/api/2.0/mltracker/model-versions/get-artifact', methods=['GET'])
def get_model_artifact():
    version_id = request.args.get('version_id')
    artifact_path = request.args.get('path', '')
    
    if not version_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "version_id is required"}}), 400
    
    if version_id not in model_versions_db:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST",
                                   "message": f"Model version {version_id} not found"}}), 404
    
    model_version = model_versions_db[version_id]
    source = model_version['source']
    
    base_path = _resolve_artifact_path(source)
    
    if artifact_path:
        full_path = os.path.join(base_path, artifact_path)
    else:
        full_path = base_path
    
    if os.path.isfile(full_path):
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            return jsonify({
                "artifact_path": artifact_path or os.path.basename(full_path),
                "content": content
            })
        except Exception:
            return jsonify({"error": {"code": "INTERNAL_ERROR",
                                       "message": "Failed to read artifact"}}), 500
    
    if os.path.isdir(full_path):
        try:
            files = os.listdir(full_path)
            return jsonify({
                "artifact_path": artifact_path or "/",
                "files": files
            })
        except Exception:
            return jsonify({"error": {"code": "INTERNAL_ERROR",
                                       "message": "Failed to list artifacts"}}), 500
    
    return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST",
                               "message": "Artifact not found"}}), 404


@app.route('/api/2.0/mltracker/model-versions/list', methods=['GET'])
def list_model_versions():
    name = request.args.get('name')
    if name:
        versions = [v for v in model_versions_db.values() if v['name'] == name]
    else:
        versions = list(model_versions_db.values())
    return jsonify({"model_versions": versions})


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": {"code": "ENDPOINT_NOT_FOUND", 
                                   "message": "API endpoint not found"}}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": {"code": "INTERNAL_ERROR",
                               "message": "Internal server error"}}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
