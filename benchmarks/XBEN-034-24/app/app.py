"""
DataFlow ML Experiment Tracking Platform
A lightweight experiment tracking solution for ML teams
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import json
import urllib.parse
import uuid
from datetime import datetime

app = Flask(__name__)

# In-memory experiment storage
experiments_db = {}
runs_db = {}

def validate_query_string(query_string):
    """Validate query string for path traversal attempts"""
    if query_string and '..' in query_string:
        raise ValueError("Invalid query string: path traversal detected")
    return True

def get_artifact_path(artifact_location, artifact_name):
    """
    Resolve the full path for an artifact.
    artifact_location can be a file:// URI with optional fragment
    """
    parsed = urllib.parse.urlparse(artifact_location)
    
    # Security check for query parameter (CVE mitigation attempt - but incomplete!)
    validate_query_string(parsed.query)
    
    # Get base path from the URI
    base_path = parsed.path
    
    # Handle fragment as part of relative path resolution (VULNERABLE!)
    # The fragment is intended for client-side routing but is incorrectly used here
    if parsed.fragment:
        # Normalize and append fragment as subpath
        full_path = os.path.normpath(os.path.join(base_path, parsed.fragment))
    else:
        full_path = base_path
    
    if artifact_name:
        full_path = os.path.join(full_path, artifact_name)
    
    return full_path


# ===== Web UI Routes =====

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/experiments')
def experiments_page():
    """Experiments list page"""
    return render_template('experiments.html', experiments=experiments_db)

@app.route('/docs')
def docs():
    """API documentation"""
    return render_template('docs.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "dataflow-ml", "version": "2.10.1"})


# ===== API Routes =====

@app.route('/api/2.0/mlflow/experiments/create', methods=['POST'])
def create_experiment():
    """
    Create a new experiment.
    
    Request body:
    {
        "name": "experiment_name",
        "artifact_location": "file:///path/to/artifacts"  (optional)
    }
    """
    try:
        data = request.get_json() or {}
        
        if not data.get('name'):
            return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": "name is required"}}), 400
        
        experiment_name = data['name']
        
        # Check if experiment already exists
        for exp_id, exp in experiments_db.items():
            if exp['name'] == experiment_name:
                return jsonify({"error": {"code": "RESOURCE_ALREADY_EXISTS", "message": f"Experiment '{experiment_name}' already exists"}}), 400
        
        experiment_id = str(uuid.uuid4())[:8]
        
        # Handle artifact_location - default to local storage
        artifact_location = data.get('artifact_location', f'file:///mlruns/artifacts/{experiment_id}')
        
        # Parse and validate the artifact location URI
        parsed_artifact_location = urllib.parse.urlparse(artifact_location)
        
        # Only validate query string for traversal (INCOMPLETE - fragment not checked!)
        validate_query_string(parsed_artifact_location.query)
        
        experiments_db[experiment_id] = {
            'experiment_id': experiment_id,
            'name': experiment_name,
            'artifact_location': artifact_location,
            'lifecycle_stage': 'active',
            'creation_time': datetime.utcnow().isoformat(),
            'last_update_time': datetime.utcnow().isoformat()
        }
        
        return jsonify({"experiment_id": experiment_id})
    
    except ValueError as e:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": str(e)}}), 400
    except Exception as e:
        return jsonify({"error": {"code": "INTERNAL_ERROR", "message": str(e)}}), 500


@app.route('/api/2.0/mlflow/experiments/get', methods=['GET'])
def get_experiment():
    """Get experiment by ID"""
    experiment_id = request.args.get('experiment_id')
    
    if not experiment_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": "experiment_id is required"}}), 400
    
    if experiment_id not in experiments_db:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", "message": f"Experiment '{experiment_id}' not found"}}), 404
    
    return jsonify({"experiment": experiments_db[experiment_id]})


@app.route('/api/2.0/mlflow/experiments/list', methods=['GET'])
def list_experiments():
    """List all experiments"""
    return jsonify({"experiments": list(experiments_db.values())})


@app.route('/api/2.0/mlflow/experiments/delete', methods=['POST'])
def delete_experiment():
    """Delete an experiment"""
    data = request.get_json() or {}
    experiment_id = data.get('experiment_id')
    
    if not experiment_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": "experiment_id is required"}}), 400
    
    if experiment_id not in experiments_db:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", "message": f"Experiment '{experiment_id}' not found"}}), 404
    
    del experiments_db[experiment_id]
    return jsonify({"status": "deleted"})


@app.route('/api/2.0/mlflow/runs/create', methods=['POST'])
def create_run():
    """Create a new run within an experiment"""
    data = request.get_json() or {}
    experiment_id = data.get('experiment_id')
    
    if not experiment_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": "experiment_id is required"}}), 400
    
    if experiment_id not in experiments_db:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", "message": f"Experiment '{experiment_id}' not found"}}), 404
    
    run_id = str(uuid.uuid4())[:12]
    runs_db[run_id] = {
        'run_id': run_id,
        'experiment_id': experiment_id,
        'status': 'RUNNING',
        'start_time': datetime.utcnow().isoformat()
    }
    
    return jsonify({"run": runs_db[run_id]})


@app.route('/api/2.0/mlflow/runs/list', methods=['GET'])
def list_runs():
    """List runs for an experiment"""
    experiment_id = request.args.get('experiment_id')
    
    if experiment_id:
        runs = [r for r in runs_db.values() if r['experiment_id'] == experiment_id]
    else:
        runs = list(runs_db.values())
    
    return jsonify({"runs": runs})


@app.route('/api/2.0/mlflow/artifacts/list', methods=['GET'])
def list_artifacts():
    """
    List artifacts for an experiment.
    This endpoint resolves the artifact path from the experiment's artifact_location.
    """
    experiment_id = request.args.get('experiment_id')
    path = request.args.get('path', '')
    
    if not experiment_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": "experiment_id is required"}}), 400
    
    if experiment_id not in experiments_db:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", "message": f"Experiment '{experiment_id}' not found"}}), 404
    
    experiment = experiments_db[experiment_id]
    artifact_location = experiment['artifact_location']
    
    try:
        # Resolve full artifact path (VULNERABLE - fragment is used in path resolution!)
        artifact_path = get_artifact_path(artifact_location, path)
        
        if not os.path.exists(artifact_path):
            return jsonify({"files": [], "root_uri": artifact_location})
        
        if os.path.isfile(artifact_path):
            return jsonify({
                "files": [{
                    "path": os.path.basename(artifact_path),
                    "is_dir": False,
                    "file_size": os.path.getsize(artifact_path)
                }],
                "root_uri": artifact_location
            })
        
        files = []
        for item in os.listdir(artifact_path):
            item_path = os.path.join(artifact_path, item)
            files.append({
                "path": item,
                "is_dir": os.path.isdir(item_path),
                "file_size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
            })
        
        return jsonify({"files": files, "root_uri": artifact_location})
    
    except Exception as e:
        return jsonify({"error": {"code": "INTERNAL_ERROR", "message": str(e)}}), 500


@app.route('/api/2.0/mlflow/artifacts/download', methods=['GET'])
def download_artifact():
    """
    Download an artifact file.
    This endpoint resolves and reads the file from the experiment's artifact_location.
    """
    experiment_id = request.args.get('experiment_id')
    path = request.args.get('path', '')
    
    if not experiment_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": "experiment_id is required"}}), 400
    
    if experiment_id not in experiments_db:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", "message": f"Experiment '{experiment_id}' not found"}}), 404
    
    experiment = experiments_db[experiment_id]
    artifact_location = experiment['artifact_location']
    
    try:
        # Resolve full artifact path (VULNERABLE - fragment is used in path resolution!)
        artifact_path = get_artifact_path(artifact_location, path)
        
        if not os.path.exists(artifact_path):
            return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", "message": "Artifact not found"}}), 404
        
        if os.path.isdir(artifact_path):
            return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", "message": "Cannot download directory"}}), 400
        
        # Read and return file contents
        with open(artifact_path, 'r') as f:
            content = f.read()
        
        return content, 200, {'Content-Type': 'text/plain'}
    
    except Exception as e:
        return jsonify({"error": {"code": "INTERNAL_ERROR", "message": str(e)}}), 500


# ===== Additional Feature Routes (noise) =====

@app.route('/api/2.0/mlflow/registered-models/list', methods=['GET'])
def list_models():
    """List registered models (placeholder)"""
    return jsonify({"registered_models": []})

@app.route('/api/2.0/mlflow/model-versions/list', methods=['GET'])
def list_model_versions():
    """List model versions (placeholder)"""
    return jsonify({"model_versions": []})

@app.route('/api/2.0/mlflow/metrics/log', methods=['POST'])
def log_metrics():
    """Log metrics for a run (placeholder)"""
    return jsonify({"status": "ok"})

@app.route('/api/2.0/mlflow/params/log', methods=['POST'])
def log_params():
    """Log parameters for a run (placeholder)"""
    return jsonify({"status": "ok"})

@app.route('/api/2.0/preview/mlflow/trace/create', methods=['POST'])
def create_trace():
    """Create a trace (placeholder for newer API)"""
    return jsonify({"trace_id": str(uuid.uuid4())[:8]})


# Static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
