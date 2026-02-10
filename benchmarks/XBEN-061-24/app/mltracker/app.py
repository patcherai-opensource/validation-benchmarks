"""
MLTracker - A Simple ML Experiment Tracking Server
Similar to MLflow, this service allows users to create experiments
and store/retrieve artifacts.
"""

import os
import json
import uuid
import urllib.parse
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# In-memory storage for experiments
experiments = {}

# Default artifact storage root
ARTIFACT_ROOT = "/tmp/mltracker/artifacts"

# Ensure artifact root exists
os.makedirs(ARTIFACT_ROOT, exist_ok=True)


def validate_query_string(query):
    """
    Validates the query component of a URI to prevent path traversal.
    This checks for '..' sequences in the query string.
    
    NOTE: This intentionally does NOT check the fragment component,
    mimicking the CVE-2024-2928 vulnerability in MLflow.
    """
    if query and '..' in query:
        raise ValueError("Invalid query string: path traversal detected")
    return True


def resolve_artifact_path(artifact_location, artifact_name):
    """
    Resolve the full path to an artifact based on the experiment's artifact location.
    
    The artifact_location is parsed as a URI. For file:// URIs, the path is extracted.
    If a fragment is present, it is appended to the resolved path.
    
    VULNERABILITY: The fragment component is not validated for path traversal,
    allowing attackers to read arbitrary files using URIs like:
    file:///tmp/foo#../etc/passwd
    """
    parsed = urllib.parse.urlparse(artifact_location)
    
    if parsed.scheme == 'file' or parsed.scheme == '':
        # Get the base path from the URI
        base_path = parsed.path if parsed.path else ARTIFACT_ROOT
        
        # If there's a fragment, append it to the path
        # VULNERABILITY: Fragment is not validated for '..' sequences
        if parsed.fragment:
            full_path = os.path.join(base_path, parsed.fragment, artifact_name)
        else:
            full_path = os.path.join(base_path, artifact_name)
        
        return full_path
    
    return None


# HTML template for the main page
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MLTracker - Experiment Tracking</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .method { display: inline-block; padding: 3px 8px; border-radius: 3px; font-weight: bold; margin-right: 10px; }
        .post { background: #27ae60; color: white; }
        .get { background: #3498db; color: white; }
        code { background: #2c3e50; color: #ecf0f1; padding: 2px 6px; border-radius: 3px; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; overflow-x: auto; }
        .experiments-list { margin-top: 20px; }
        .experiment { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 4px; border-left: 3px solid #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 MLTracker - Experiment Tracking Server</h1>
        <p>Welcome to MLTracker, a lightweight ML experiment tracking service.</p>
        
        <h2>API Endpoints</h2>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <code>/api/2.0/mltracker/experiments/create</code>
            <p>Create a new experiment with a custom artifact storage location.</p>
            <pre>{
  "name": "my-experiment",
  "artifact_location": "file:///path/to/artifacts"
}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/2.0/mltracker/experiments/list</code>
            <p>List all experiments.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/2.0/mltracker/experiments/get?experiment_id=&lt;id&gt;</code>
            <p>Get details of a specific experiment.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/2.0/mltracker/artifacts/get?experiment_id=&lt;id&gt;&artifact_path=&lt;path&gt;</code>
            <p>Retrieve an artifact from an experiment's artifact location.</p>
        </div>
        
        <h2>Current Experiments</h2>
        <div class="experiments-list">
            {% if experiments %}
                {% for exp_id, exp in experiments.items() %}
                <div class="experiment">
                    <strong>{{ exp.name }}</strong> (ID: {{ exp_id }})
                    <br>
                    <small>Artifact Location: {{ exp.artifact_location }}</small>
                </div>
                {% endfor %}
            {% else %}
                <p>No experiments created yet.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    """Main page showing API documentation and current experiments."""
    return render_template_string(INDEX_HTML, experiments=experiments)


@app.route('/api/2.0/mltracker/experiments/create', methods=['POST'])
def create_experiment():
    """
    Create a new experiment.
    
    Request body:
    {
        "name": "experiment-name",
        "artifact_location": "file:///path/to/artifacts"
    }
    
    VULNERABILITY: The artifact_location's query component is validated for path traversal,
    but the fragment component is NOT validated, allowing URIs like:
    file:///tmp/foo#../etc/passwd
    """
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({"error": "Missing required field: name"}), 400
        
        name = data['name']
        artifact_location = data.get('artifact_location', f'file://{ARTIFACT_ROOT}')
        
        # Parse the artifact location URL
        parsed_artifact_location = urllib.parse.urlparse(artifact_location)
        
        # Validate query string for path traversal (but NOT the fragment!)
        # This mimics the CVE-2024-2928 vulnerability in MLflow
        try:
            validate_query_string(parsed_artifact_location.query)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        # Generate experiment ID
        experiment_id = str(uuid.uuid4())[:8]
        
        # Store the experiment
        experiments[experiment_id] = {
            "name": name,
            "artifact_location": artifact_location,
            "experiment_id": experiment_id
        }
        
        return jsonify({
            "experiment_id": experiment_id,
            "name": name,
            "artifact_location": artifact_location
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/2.0/mltracker/experiments/list', methods=['GET'])
def list_experiments():
    """List all experiments."""
    return jsonify({"experiments": list(experiments.values())})


@app.route('/api/2.0/mltracker/experiments/get', methods=['GET'])
def get_experiment():
    """Get a specific experiment by ID."""
    experiment_id = request.args.get('experiment_id')
    
    if not experiment_id:
        return jsonify({"error": "Missing required parameter: experiment_id"}), 400
    
    if experiment_id not in experiments:
        return jsonify({"error": "Experiment not found"}), 404
    
    return jsonify(experiments[experiment_id])


@app.route('/api/2.0/mltracker/artifacts/get', methods=['GET'])
def get_artifact():
    """
    Retrieve an artifact from an experiment's artifact storage.
    
    This endpoint resolves the artifact path using the experiment's artifact_location.
    
    VULNERABILITY: The fragment component of artifact_location is used in path resolution
    without validation, allowing path traversal to read arbitrary files.
    
    Example exploit:
    1. Create experiment with artifact_location: file:///tmp/foo#../etc
    2. Request artifact with artifact_path: passwd
    3. The resolved path becomes: /tmp/foo/../etc/passwd = /etc/passwd
    """
    experiment_id = request.args.get('experiment_id')
    artifact_path = request.args.get('artifact_path', 'artifact')
    
    if not experiment_id:
        return jsonify({"error": "Missing required parameter: experiment_id"}), 400
    
    if experiment_id not in experiments:
        return jsonify({"error": "Experiment not found"}), 404
    
    experiment = experiments[experiment_id]
    artifact_location = experiment['artifact_location']
    
    # Resolve the full artifact path
    # VULNERABILITY: This uses the fragment from artifact_location without validation
    full_path = resolve_artifact_path(artifact_location, artifact_path)
    
    if full_path is None:
        return jsonify({"error": "Unsupported artifact location scheme"}), 400
    
    # Normalize the path (this resolves .. sequences)
    full_path = os.path.normpath(full_path)
    
    try:
        # Attempt to read the artifact file
        with open(full_path, 'r') as f:
            content = f.read()
        
        return jsonify({
            "artifact_path": artifact_path,
            "content": content
        })
    except FileNotFoundError:
        return jsonify({"error": f"Artifact not found: {artifact_path}"}), 404
    except PermissionError:
        return jsonify({"error": "Permission denied"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
