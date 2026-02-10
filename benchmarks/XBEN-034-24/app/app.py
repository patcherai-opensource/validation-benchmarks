import os
import json
import uuid
import urllib.parse
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# In-memory storage for experiments
experiments = {}

# Simple landing page template
LANDING_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>MLtracker - ML Experiment Tracking</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        h2 { color: #666; margin-top: 30px; }
        .endpoint { background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #4CAF50; }
        code { background: #eee; padding: 2px 6px; border-radius: 3px; }
        .method { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; margin-right: 10px; }
        .get { background: #61affe; color: white; }
        .post { background: #49cc90; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MLtracker API</h1>
        <p>A lightweight ML experiment tracking service for managing your machine learning experiments.</p>
        
        <h2>API Endpoints</h2>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <code>/api/2.0/mlflow/experiments/create</code>
            <p>Create a new experiment with optional artifact location.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/2.0/mlflow/experiments/list</code>
            <p>List all experiments.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/2.0/mlflow/experiments/get</code>
            <p>Get experiment details by ID.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/2.0/mlflow/artifacts/list</code>
            <p>List artifacts for an experiment.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/get-artifact</code>
            <p>Download an artifact file.</p>
        </div>

        <h2>Quick Start</h2>
        <p>Create an experiment:</p>
        <pre>curl -X POST http://localhost:8080/api/2.0/mlflow/experiments/create \\
  -H "Content-Type: application/json" \\
  -d '{"name": "my-experiment", "artifact_location": "file:///tmp/artifacts"}'</pre>
    </div>
</body>
</html>
"""


def validate_query_string(query):
    """Validate query string does not contain path traversal sequences."""
    if query and ('..' in query or query.startswith('/')):
        raise ValueError("Invalid query string")


@app.route('/')
def index():
    return render_template_string(LANDING_PAGE)


@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


@app.route('/api/2.0/mlflow/experiments/create', methods=['POST'])
def create_experiment():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": "Request body is required"}}), 400
        
        name = data.get('name')
        if not name:
            return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": "Experiment name is required"}}), 400
        
        artifact_location = data.get('artifact_location', '')
        
        if artifact_location:
            parsed = urllib.parse.urlparse(artifact_location)
            validate_query_string(parsed.query)
        
        experiment_id = str(uuid.uuid4())[:8]
        experiments[experiment_id] = {
            'experiment_id': experiment_id,
            'name': name,
            'artifact_location': artifact_location,
            'lifecycle_stage': 'active',
            'creation_time': 1234567890,
            'last_update_time': 1234567890
        }
        
        return jsonify({"experiment_id": experiment_id})
    except ValueError as e:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": str(e)}}), 400
    except Exception as e:
        return jsonify({"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}}), 500


@app.route('/api/2.0/mlflow/experiments/list', methods=['GET'])
def list_experiments():
    return jsonify({"experiments": list(experiments.values())})


@app.route('/api/2.0/mlflow/experiments/get', methods=['GET'])
def get_experiment():
    experiment_id = request.args.get('experiment_id')
    if not experiment_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": "experiment_id is required"}}), 400
    
    exp = experiments.get(experiment_id)
    if not exp:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", "message": "Experiment not found"}}), 404
    
    return jsonify({"experiment": exp})


@app.route('/api/2.0/mlflow/artifacts/list', methods=['GET'])
def list_artifacts():
    experiment_id = request.args.get('experiment_id')
    path = request.args.get('path', '')
    
    if not experiment_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": "experiment_id is required"}}), 400
    
    exp = experiments.get(experiment_id)
    if not exp:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", "message": "Experiment not found"}}), 404
    
    artifact_location = exp.get('artifact_location', '')
    if not artifact_location:
        return jsonify({"files": [], "root_uri": ""})
    
    parsed = urllib.parse.urlparse(artifact_location)
    base_path = parsed.path
    fragment = parsed.fragment
    
    if fragment:
        resolved_path = os.path.normpath(os.path.join(base_path, fragment))
    else:
        resolved_path = base_path
    
    if path:
        resolved_path = os.path.join(resolved_path, path)
    
    files = []
    try:
        if os.path.isfile(resolved_path):
            files.append({
                "path": os.path.basename(resolved_path),
                "is_dir": False,
                "file_size": os.path.getsize(resolved_path)
            })
        elif os.path.isdir(resolved_path):
            for entry in os.listdir(resolved_path):
                full_path = os.path.join(resolved_path, entry)
                files.append({
                    "path": entry,
                    "is_dir": os.path.isdir(full_path),
                    "file_size": os.path.getsize(full_path) if os.path.isfile(full_path) else 0
                })
    except (PermissionError, FileNotFoundError):
        pass
    
    return jsonify({"files": files, "root_uri": artifact_location})


@app.route('/get-artifact', methods=['GET'])
def get_artifact():
    experiment_id = request.args.get('experiment_id')
    path = request.args.get('path', '')
    
    if not experiment_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": "experiment_id is required"}}), 400
    
    exp = experiments.get(experiment_id)
    if not exp:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", "message": "Experiment not found"}}), 404
    
    artifact_location = exp.get('artifact_location', '')
    if not artifact_location:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", "message": "No artifact location configured"}}), 404
    
    parsed = urllib.parse.urlparse(artifact_location)
    base_path = parsed.path
    fragment = parsed.fragment
    
    if fragment:
        resolved_path = os.path.normpath(os.path.join(base_path, fragment))
    else:
        resolved_path = base_path
    
    if path:
        resolved_path = os.path.join(resolved_path, path)
    
    try:
        if os.path.isfile(resolved_path):
            with open(resolved_path, 'r') as f:
                content = f.read()
            return content, 200, {'Content-Type': 'text/plain'}
        else:
            return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", "message": "Artifact not found"}}), 404
    except (PermissionError, FileNotFoundError):
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", "message": "Artifact not found"}}), 404
    except Exception:
        return jsonify({"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", "message": "Resource not found"}}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
