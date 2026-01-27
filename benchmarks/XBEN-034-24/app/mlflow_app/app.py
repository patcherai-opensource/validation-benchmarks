"""
MLflow Experiment Tracking Server
A simplified ML experiment tracking service
"""
import os
import json
import urllib.parse
import uuid
from flask import Flask, request, jsonify, render_template_string
from functools import wraps

app = Flask(__name__)

# In-memory storage for experiments
experiments = {}

# Configuration
ARTIFACTS_DIR = "/tmp/mlflow_artifacts"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# HTML templates
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLflow - Experiment Tracking</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .navbar { background: #0194E2; color: white; padding: 16px 32px; }
        .navbar h1 { font-size: 24px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 32px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 24px; margin-bottom: 24px; }
        .card h2 { color: #333; margin-bottom: 16px; font-size: 20px; }
        .api-endpoint { background: #f8f9fa; padding: 12px 16px; border-radius: 4px; font-family: monospace; margin: 8px 0; }
        .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-right: 8px; }
        .method.post { background: #49cc90; color: white; }
        .method.get { background: #61affe; color: white; }
        .experiments-list { margin-top: 16px; }
        .experiment-item { border: 1px solid #e0e0e0; padding: 16px; margin: 8px 0; border-radius: 4px; }
        .experiment-name { font-weight: bold; color: #0194E2; }
        pre { background: #282c34; color: #abb2bf; padding: 16px; border-radius: 4px; overflow-x: auto; }
        code { font-family: 'Source Code Pro', monospace; }
        .footer { text-align: center; padding: 32px; color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🔬 MLflow Experiment Tracking</h1>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to MLflow</h2>
            <p>MLflow is an open source platform for managing the end-to-end machine learning lifecycle.</p>
            <p style="margin-top: 16px;">This server provides REST API endpoints for experiment tracking and artifact management.</p>
        </div>
        
        <div class="card">
            <h2>API Endpoints</h2>
            <div class="api-endpoint">
                <span class="method post">POST</span>
                <code>/api/2.0/mlflow/experiments/create</code>
                <p style="margin-top: 8px; color: #666;">Create a new experiment with optional artifact location</p>
            </div>
            <div class="api-endpoint">
                <span class="method get">GET</span>
                <code>/api/2.0/mlflow/experiments/list</code>
                <p style="margin-top: 8px; color: #666;">List all experiments</p>
            </div>
            <div class="api-endpoint">
                <span class="method get">GET</span>
                <code>/api/2.0/mlflow/experiments/get?experiment_id={id}</code>
                <p style="margin-top: 8px; color: #666;">Get experiment details and artifacts</p>
            </div>
            <div class="api-endpoint">
                <span class="method get">GET</span>
                <code>/api/2.0/mlflow/artifacts/list?experiment_id={id}&path={path}</code>
                <p style="margin-top: 8px; color: #666;">List artifacts for an experiment at specified path</p>
            </div>
        </div>
        
        <div class="card">
            <h2>Example: Create Experiment</h2>
            <pre><code>curl -X POST http://localhost:8080/api/2.0/mlflow/experiments/create \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "my-experiment",
    "artifact_location": "file:///tmp/mlflow_artifacts/my-exp"
  }'</code></pre>
        </div>
        
        <div class="card">
            <h2>Active Experiments</h2>
            <div class="experiments-list">
                {% if experiments %}
                    {% for exp_id, exp in experiments.items() %}
                    <div class="experiment-item">
                        <span class="experiment-name">{{ exp.name }}</span>
                        <span style="color: #666; margin-left: 16px;">ID: {{ exp_id }}</span>
                        <div style="margin-top: 8px; font-size: 13px; color: #888;">
                            Artifact Location: {{ exp.artifact_location }}
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p style="color: #666;">No experiments created yet. Use the API to create one!</p>
                {% endif %}
            </div>
        </div>
    </div>
    <div class="footer">
        <p>MLflow Tracking Server v2.10.2 - Powered by Flask</p>
    </div>
</body>
</html>
"""

def validate_query_string(query_string):
    """
    Validates the query string to prevent path traversal.
    NOTE: This validation is incomplete - it only checks the query component,
    not the fragment component of the URI.
    """
    if query_string and '..' in query_string:
        raise ValueError("Path traversal detected in query string")
    return True


@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE, experiments=experiments)


@app.route('/api/2.0/mlflow/experiments/create', methods=['POST'])
def create_experiment():
    """
    Create a new experiment with an optional artifact_location.
    The artifact_location can be a file:// URI pointing to a storage location.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400
        
        name = data.get('name')
        if not name:
            return jsonify({"error": "Missing required field: name"}), 400
        
        artifact_location = data.get('artifact_location', f"file://{ARTIFACTS_DIR}/default")
        tags = data.get('tags', [])
        
        # Parse the artifact_location URI
        parsed_artifact_location = urllib.parse.urlparse(artifact_location)
        
        # VULNERABLE: Only validates query string, not fragment!
        # The fragment (everything after #) is not validated for path traversal
        validate_query_string(parsed_artifact_location.query)
        
        # Generate experiment ID
        experiment_id = str(uuid.uuid4())[:8]
        
        # Store the experiment
        experiments[experiment_id] = {
            'name': name,
            'artifact_location': artifact_location,
            'tags': tags,
            'lifecycle_stage': 'active'
        }
        
        return jsonify({
            "experiment_id": experiment_id,
            "artifact_location": artifact_location
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@app.route('/api/2.0/mlflow/experiments/list', methods=['GET'])
def list_experiments():
    """List all experiments"""
    return jsonify({
        "experiments": [
            {"experiment_id": exp_id, **exp_data}
            for exp_id, exp_data in experiments.items()
        ]
    })


@app.route('/api/2.0/mlflow/experiments/get', methods=['GET'])
def get_experiment():
    """Get experiment details"""
    experiment_id = request.args.get('experiment_id')
    if not experiment_id:
        return jsonify({"error": "Missing experiment_id parameter"}), 400
    
    if experiment_id not in experiments:
        return jsonify({"error": f"Experiment with ID '{experiment_id}' not found"}), 404
    
    return jsonify({
        "experiment_id": experiment_id,
        **experiments[experiment_id]
    })


@app.route('/api/2.0/mlflow/artifacts/list', methods=['GET'])
def list_artifacts():
    """
    List artifacts for an experiment at the specified path.
    VULNERABLE: Uses fragment from artifact_location for path traversal.
    """
    experiment_id = request.args.get('experiment_id')
    subpath = request.args.get('path', '')
    
    if not experiment_id:
        return jsonify({"error": "Missing experiment_id parameter"}), 400
    
    if experiment_id not in experiments:
        return jsonify({"error": f"Experiment with ID '{experiment_id}' not found"}), 404
    
    experiment = experiments[experiment_id]
    artifact_location = experiment['artifact_location']
    
    # Parse the artifact URI
    parsed = urllib.parse.urlparse(artifact_location)
    
    # VULNERABLE: Fragment is used in path resolution!
    # The fragment (after #) can contain path traversal sequences
    base_path = parsed.path
    fragment = parsed.fragment  # This contains the traversal payload!
    
    if fragment:
        # Resolve the fragment as a relative path from the base
        # This allows ../../../etc/passwd style attacks via the fragment
        resolved_path = os.path.normpath(os.path.join(os.path.dirname(base_path), fragment))
    else:
        resolved_path = base_path
    
    # Append any additional subpath
    if subpath:
        resolved_path = os.path.join(resolved_path, subpath)
    
    try:
        if os.path.isfile(resolved_path):
            # If it's a file, read its contents
            with open(resolved_path, 'r') as f:
                content = f.read()
            return jsonify({
                "artifact_path": resolved_path,
                "artifact_type": "file",
                "content": content,
                "files": []
            })
        elif os.path.isdir(resolved_path):
            # If it's a directory, list files
            files = []
            for item in os.listdir(resolved_path):
                item_path = os.path.join(resolved_path, item)
                files.append({
                    "path": item,
                    "is_dir": os.path.isdir(item_path),
                    "file_size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                })
            return jsonify({
                "artifact_path": resolved_path,
                "files": files
            })
        else:
            return jsonify({
                "error": f"Artifact path does not exist: {resolved_path}"
            }), 404
    except PermissionError:
        return jsonify({"error": "Permission denied accessing artifact"}), 403
    except Exception as e:
        return jsonify({"error": f"Error accessing artifacts: {str(e)}"}), 500


@app.route('/health')
def health():
    return jsonify({"status": "healthy", "version": "2.10.2"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
