"""
ML Experiment Tracking Service
A simplified experiment tracking service similar to MLflow.
"""
import os
import json
import uuid
from flask import Flask, request, jsonify, render_template_string
from urllib.parse import urlparse, unquote
from pathlib import Path

app = Flask(__name__)

# In-memory storage for experiments and model versions
experiments = {}
model_versions = {}

# Default artifact root for local file storage
ARTIFACT_ROOT = "/artifacts"

# Get flag from environment variable (set at runtime from build)
FLAG = os.environ.get('FLAG', 'FLAG_PLACEHOLDER')

# HTML template for the main page
INDEX_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>ML Experiment Tracking Service</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #007bff; }
        .method { color: #28a745; font-weight: bold; }
        code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
        pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 4px; overflow-x: auto; }
        .description { color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 ML Experiment Tracking Service</h1>
        <p>A lightweight experiment tracking API for machine learning workflows.</p>
        
        <h2>API Endpoints</h2>
        
        <div class="endpoint">
            <span class="method">POST</span> <code>/api/2.0/mlflow/experiments/create</code>
            <p class="description">Create a new experiment with a custom artifact location.</p>
            <pre>curl -X POST http://localhost:8080/api/2.0/mlflow/experiments/create \\
  -H "Content-Type: application/json" \\
  -d '{"name": "my-experiment", "artifact_location": "file:///artifacts/exp1"}'</pre>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/2.0/mlflow/experiments/get?experiment_id=ID</code>
            <p class="description">Get experiment details including artifact contents.</p>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <code>/api/2.0/mlflow/model-versions/create</code>
            <p class="description">Create a new model version with a source artifact path.</p>
            <pre>curl -X POST http://localhost:8080/api/2.0/mlflow/model-versions/create \\
  -H "Content-Type: application/json" \\
  -d '{"name": "my-model", "source": "file:///artifacts/models/v1"}'</pre>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/2.0/mlflow/model-versions/get?name=NAME&amp;version=VERSION</code>
            <p class="description">Get model version details including source contents.</p>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/2.0/mlflow/experiments/list</code>
            <p class="description">List all experiments.</p>
        </div>
        
        <h2>Artifact Storage</h2>
        <p>Artifacts are stored in <code>/artifacts</code> by default. Custom artifact locations can be specified using <code>file://</code> URIs.</p>
    </div>
</body>
</html>
'''

def validate_artifact_uri(uri):
    """
    Validate that the artifact URI is a local file URI.
    
    VULNERABILITY: This function validates the query string but NOT the fragment
    component of the URI. An attacker can use the fragment (#) to bypass path
    restrictions.
    
    CVE-inspired: Similar to MLflow path traversal vulnerability where fragment
    component was not validated.
    """
    if not uri:
        return True, None
    
    parsed = urlparse(uri)
    
    # Only allow file:// scheme or relative paths
    if parsed.scheme and parsed.scheme != 'file':
        return False, "Only file:// URIs are supported for local artifact storage"
    
    # Check for query string manipulation (but NOT fragment!)
    if parsed.query:
        return False, "Query parameters are not allowed in artifact URIs"
    
    # The vulnerability: fragment component is NOT validated
    # parsed.path will be /etc/passwd even if URI is file:///etc/passwd#foo
    # This allows bypassing path validation
    
    return True, None


def resolve_artifact_path(uri):
    """
    Resolve an artifact URI to a file system path.
    
    VULNERABILITY: Uses the path component from urlparse which strips fragments,
    allowing path traversal attacks like file:///etc/passwd#foo
    """
    if not uri:
        return ARTIFACT_ROOT
    
    parsed = urlparse(uri)
    
    if parsed.scheme == 'file':
        # VULNERABLE: Fragment is stripped by urlparse, so file:///etc/passwd#foo
        # becomes /etc/passwd
        path = unquote(parsed.path)
    else:
        # Treat as relative path
        path = os.path.join(ARTIFACT_ROOT, uri)
    
    return path


def read_artifact_content(path, max_size=4096):
    """Read content from an artifact file."""
    try:
        if os.path.isfile(path):
            with open(path, 'r') as f:
                return f.read(max_size)
        elif os.path.isdir(path):
            return f"[Directory: {os.listdir(path)}]"
        else:
            return None
    except Exception as e:
        return f"[Error reading artifact: {str(e)}]"


@app.route('/')
def index():
    return render_template_string(INDEX_HTML)


@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


@app.route('/api/2.0/mlflow/experiments/create', methods=['POST'])
def create_experiment():
    """
    Create a new experiment.
    
    Accepts JSON body with:
    - name: Experiment name (required)
    - artifact_location: Custom artifact storage location (optional)
    """
    data = request.get_json() or {}
    
    name = data.get('name')
    if not name:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", 
                                   "message": "Missing required parameter: name"}}), 400
    
    artifact_location = data.get('artifact_location', '')
    
    # Validate URI (vulnerable - doesn't check fragment)
    valid, error = validate_artifact_uri(artifact_location)
    if not valid:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": error}}), 400
    
    # Create experiment
    experiment_id = str(uuid.uuid4())[:8]
    
    experiment = {
        "experiment_id": experiment_id,
        "name": name,
        "artifact_location": artifact_location or f"file://{ARTIFACT_ROOT}/{experiment_id}",
        "lifecycle_stage": "active",
        "creation_time": 1700000000000,
        "last_update_time": 1700000000000
    }
    
    experiments[experiment_id] = experiment
    
    return jsonify({"experiment_id": experiment_id})


@app.route('/api/2.0/mlflow/experiments/get', methods=['GET'])
def get_experiment():
    """
    Get experiment by ID.
    
    Includes artifact contents if artifact_location points to a readable file.
    This is where the path traversal becomes exploitable - we read the file
    that the artifact_location resolves to.
    """
    experiment_id = request.args.get('experiment_id')
    
    if not experiment_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "Missing required parameter: experiment_id"}}), 400
    
    experiment = experiments.get(experiment_id)
    if not experiment:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST",
                                   "message": f"Experiment {experiment_id} not found"}}), 404
    
    # Resolve artifact path and read contents (VULNERABLE)
    artifact_path = resolve_artifact_path(experiment['artifact_location'])
    artifact_content = read_artifact_content(artifact_path)
    
    response = {
        "experiment": experiment,
        "artifact_preview": artifact_content
    }
    
    return jsonify(response)


@app.route('/api/2.0/mlflow/experiments/list', methods=['GET'])
def list_experiments():
    """List all experiments."""
    return jsonify({"experiments": list(experiments.values())})


@app.route('/api/2.0/mlflow/model-versions/create', methods=['POST'])
def create_model_version():
    """
    Create a new model version.
    
    Accepts JSON body with:
    - name: Model name (required)
    - source: Source artifact URI (required)
    """
    data = request.get_json() or {}
    
    name = data.get('name')
    source = data.get('source')
    
    if not name:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "Missing required parameter: name"}}), 400
    
    if not source:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "Missing required parameter: source"}}), 400
    
    # Validate URI (vulnerable - doesn't check fragment)
    valid, error = validate_artifact_uri(source)
    if not valid:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": error}}), 400
    
    # Get or create model
    if name not in model_versions:
        model_versions[name] = []
    
    version = len(model_versions[name]) + 1
    
    model_version = {
        "name": name,
        "version": str(version),
        "source": source,
        "status": "READY",
        "creation_timestamp": 1700000000000
    }
    
    model_versions[name].append(model_version)
    
    return jsonify({"model_version": model_version})


@app.route('/api/2.0/mlflow/model-versions/get', methods=['GET'])
def get_model_version():
    """
    Get model version by name and version.
    
    Includes source contents if source points to a readable file.
    This is where the path traversal becomes exploitable.
    """
    name = request.args.get('name')
    version = request.args.get('version')
    
    if not name:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "Missing required parameter: name"}}), 400
    
    if not version:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE",
                                   "message": "Missing required parameter: version"}}), 400
    
    if name not in model_versions:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST",
                                   "message": f"Model {name} not found"}}), 404
    
    version_idx = int(version) - 1
    if version_idx < 0 or version_idx >= len(model_versions[name]):
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST",
                                   "message": f"Version {version} of model {name} not found"}}), 404
    
    model_version = model_versions[name][version_idx]
    
    # Resolve source path and read contents (VULNERABLE)
    source_path = resolve_artifact_path(model_version['source'])
    source_content = read_artifact_content(source_path)
    
    response = {
        "model_version": model_version,
        "source_preview": source_content
    }
    
    return jsonify(response)


if __name__ == '__main__':
    # Ensure artifact directory exists
    os.makedirs(ARTIFACT_ROOT, exist_ok=True)
    
    # Create some sample artifacts
    sample_artifact = os.path.join(ARTIFACT_ROOT, "sample_model.txt")
    with open(sample_artifact, 'w') as f:
        f.write("Sample model artifact content\n")
    
    app.run(host='0.0.0.0', port=80, debug=False)
