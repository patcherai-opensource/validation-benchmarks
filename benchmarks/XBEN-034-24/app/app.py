"""
MLflow-like API Server with CVE-2024-2928 vulnerability.

This simulates the Local File Inclusion vulnerability in MLflow < 2.11.3.
The vulnerability allows reading arbitrary files through URI fragment bypass
in the artifact_location field during experiment creation.

The code parses artifact_location URIs, validates the query component for 
path traversal (".."), but fails to validate the fragment component (#...).
"""

from flask import Flask, request, jsonify, render_template_string
import urllib.parse
import os
import json
import uuid

app = Flask(__name__)

# In-memory storage for experiments
experiments = {}

# HTML template for the main page
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MLflow Tracking Server</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: #1a73e8;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 { margin: 0; }
        h2 { color: #333; margin-top: 0; }
        code {
            background: #e8e8e8;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .endpoint {
            background: #e3f2fd;
            padding: 10px;
            border-left: 4px solid #1a73e8;
            margin: 10px 0;
        }
        .method {
            background: #4caf50;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: bold;
            margin-right: 10px;
        }
        .method.get { background: #2196f3; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔬 MLflow Tracking Server</h1>
        <p>Machine Learning Lifecycle Management Platform</p>
    </div>
    
    <div class="card">
        <h2>API Endpoints</h2>
        
        <div class="endpoint">
            <span class="method">POST</span>
            <code>/api/2.0/mlflow/experiments/create</code>
            <p>Create a new experiment with optional artifact_location.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/2.0/mlflow/experiments/get</code>
            <p>Get experiment details by experiment_id.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/2.0/mlflow/experiments/list</code>
            <p>List all experiments.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/2.0/mlflow/artifacts/list</code>
            <p>List artifacts for a specific run.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/get-artifact</code>
            <p>Download artifact content.</p>
        </div>
    </div>
    
    <div class="card">
        <h2>Example: Create Experiment</h2>
        <pre>curl -X POST http://localhost:8080/api/2.0/mlflow/experiments/create \\
  -H "Content-Type: application/json" \\
  -d '{"name": "my-experiment", "artifact_location": "file:///tmp/mlartifacts"}'</pre>
    </div>
    
    <div class="card">
        <h2>Active Experiments</h2>
        <p>Total experiments: {{ experiment_count }}</p>
    </div>
</body>
</html>
"""


def validate_query_string(query_string):
    """
    Validate query string for path traversal sequences.
    NOTE: This ONLY checks query parameters, NOT the fragment!
    This is the vulnerable pattern from CVE-2024-2928.
    """
    if query_string and ".." in query_string:
        raise ValueError("Invalid artifact_location: path traversal detected in query string")
    return True


def resolve_artifact_path(artifact_location, artifact_path=""):
    """
    Resolve the full path to an artifact based on the artifact_location URI.
    
    VULNERABILITY: The fragment portion of the URI is appended to the path
    without proper validation, allowing path traversal via #../../../etc/passwd
    """
    parsed = urllib.parse.urlparse(artifact_location)
    
    if parsed.scheme != "file":
        raise ValueError("Only file:// URIs are supported for local artifacts")
    
    base_path = parsed.path
    
    # The fragment is blindly appended to the path - this is the vulnerability!
    # In the real MLflow bug, the fragment could be used to traverse directories
    if parsed.fragment:
        # Fragment is treated as a path component without validation
        base_path = os.path.join(os.path.dirname(base_path), parsed.fragment)
    
    if artifact_path:
        full_path = os.path.join(base_path, artifact_path)
    else:
        full_path = base_path
    
    return full_path


@app.route("/")
def index():
    return render_template_string(INDEX_HTML, experiment_count=len(experiments))


@app.route("/api/2.0/mlflow/experiments/create", methods=["POST"])
def create_experiment():
    """
    Create a new experiment.
    
    Expected JSON body:
    {
        "name": "experiment-name",
        "artifact_location": "file:///path/to/artifacts"  # Optional
    }
    
    VULNERABILITY: The artifact_location is validated for path traversal
    in the query string ONLY, not in the URI fragment.
    """
    try:
        data = request.get_json()
        
        if not data or "name" not in data:
            return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", 
                                     "message": "Missing required parameter: name"}}), 400
        
        name = data["name"]
        artifact_location = data.get("artifact_location", f"file:///tmp/mlartifacts/{name}")
        
        # Parse the artifact location URI
        parsed_artifact_location = urllib.parse.urlparse(artifact_location)
        
        # VULNERABLE PATTERN: Only validate query string, NOT fragment
        # This is exactly how CVE-2024-2928 worked in MLflow
        try:
            validate_query_string(parsed_artifact_location.query)
        except ValueError as e:
            return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", 
                                     "message": str(e)}}), 400
        
        # Note: We do NOT validate parsed_artifact_location.fragment!
        # This allows payloads like: file:///tmp/foo#../../../etc/passwd
        
        experiment_id = str(len(experiments) + 1)
        
        experiments[experiment_id] = {
            "experiment_id": experiment_id,
            "name": name,
            "artifact_location": artifact_location,
            "lifecycle_stage": "active",
            "creation_time": 1700000000000,
            "last_update_time": 1700000000000
        }
        
        return jsonify({"experiment_id": experiment_id})
    
    except Exception as e:
        return jsonify({"error": {"code": "INTERNAL_ERROR", 
                                 "message": str(e)}}), 500


@app.route("/api/2.0/mlflow/experiments/get", methods=["GET"])
def get_experiment():
    """Get experiment details by ID."""
    experiment_id = request.args.get("experiment_id")
    
    if not experiment_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", 
                                 "message": "Missing required parameter: experiment_id"}}), 400
    
    if experiment_id not in experiments:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", 
                                 "message": f"Experiment with id {experiment_id} not found"}}), 404
    
    return jsonify({"experiment": experiments[experiment_id]})


@app.route("/api/2.0/mlflow/experiments/list", methods=["GET"])
def list_experiments():
    """List all experiments."""
    return jsonify({
        "experiments": list(experiments.values())
    })


@app.route("/api/2.0/mlflow/artifacts/list", methods=["GET"])
def list_artifacts():
    """
    List artifacts for a run.
    
    Required params:
    - run_id: The run identifier (we'll use experiment_id for simplicity)
    """
    run_id = request.args.get("run_id") or request.args.get("experiment_id")
    path = request.args.get("path", "")
    
    if not run_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", 
                                 "message": "Missing required parameter: run_id"}}), 400
    
    if run_id not in experiments:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", 
                                 "message": f"Run/Experiment with id {run_id} not found"}}), 404
    
    experiment = experiments[run_id]
    artifact_location = experiment["artifact_location"]
    
    try:
        resolved_path = resolve_artifact_path(artifact_location, path)
        
        # List files/directories at the resolved path
        if os.path.isfile(resolved_path):
            return jsonify({
                "files": [{
                    "path": os.path.basename(resolved_path),
                    "is_dir": False,
                    "file_size": os.path.getsize(resolved_path)
                }]
            })
        elif os.path.isdir(resolved_path):
            files = []
            for item in os.listdir(resolved_path):
                item_path = os.path.join(resolved_path, item)
                files.append({
                    "path": item,
                    "is_dir": os.path.isdir(item_path),
                    "file_size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                })
            return jsonify({"files": files, "root_uri": artifact_location})
        else:
            return jsonify({"files": [], "root_uri": artifact_location})
    
    except Exception as e:
        return jsonify({"error": {"code": "INTERNAL_ERROR", 
                                 "message": str(e)}}), 500


@app.route("/get-artifact", methods=["GET"])
def get_artifact():
    """
    Download artifact content.
    
    This is where the LFI actually manifests - when trying to read
    artifact content, the resolved path (which can be manipulated via
    the URI fragment) is used to read the file.
    
    Required params:
    - run_id/experiment_id: The run/experiment identifier
    - path: Path to the artifact (optional)
    """
    run_id = request.args.get("run_id") or request.args.get("experiment_id")
    artifact_path = request.args.get("path", "")
    
    if not run_id:
        return jsonify({"error": {"code": "INVALID_PARAMETER_VALUE", 
                                 "message": "Missing required parameter: run_id"}}), 400
    
    if run_id not in experiments:
        return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", 
                                 "message": f"Run/Experiment with id {run_id} not found"}}), 404
    
    experiment = experiments[run_id]
    artifact_location = experiment["artifact_location"]
    
    try:
        resolved_path = resolve_artifact_path(artifact_location, artifact_path)
        
        # Read and return the file content - this is the LFI!
        if os.path.isfile(resolved_path):
            with open(resolved_path, "r") as f:
                content = f.read()
            return content, 200, {"Content-Type": "text/plain"}
        else:
            return jsonify({"error": {"code": "RESOURCE_DOES_NOT_EXIST", 
                                     "message": f"Artifact not found at path: {resolved_path}"}}), 404
    
    except PermissionError:
        return jsonify({"error": {"code": "PERMISSION_DENIED", 
                                 "message": "Permission denied reading artifact"}}), 403
    except Exception as e:
        return jsonify({"error": {"code": "INTERNAL_ERROR", 
                                 "message": str(e)}}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
