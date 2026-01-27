"""
ModelHub - Machine Learning Model Registry
REST API for managing ML models, experiments, and artifacts
"""
import os
import json
import uuid
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Simulated database
USERS = {
    "admin": {"password": "admin123", "role": "admin", "api_key": "mh-key-admin-001"},
    "analyst": {"password": "analyst456", "role": "user", "api_key": "mh-key-analyst-002"}
}

MODELS = {
    "model-001": {
        "id": "model-001",
        "name": "fraud-detection-v1",
        "description": "Credit card fraud detection model",
        "version": "1.0.0",
        "created_at": "2024-01-15T10:30:00Z",
        "owner": "admin",
        "status": "production"
    },
    "model-002": {
        "id": "model-002",
        "name": "customer-churn-predictor",
        "description": "Customer churn prediction model",
        "version": "2.1.0",
        "created_at": "2024-02-20T14:45:00Z",
        "owner": "analyst",
        "status": "staging"
    }
}

EXPERIMENTS = {
    "exp-001": {
        "id": "exp-001",
        "name": "fraud-detection-training",
        "model_id": "model-001",
        "metrics": {"accuracy": 0.95, "precision": 0.92, "recall": 0.89},
        "created_at": "2024-01-10T09:00:00Z"
    }
}

# Internal system data - contains sensitive information
SYSTEM_CONFIG = {
    "database_url": "postgresql://mluser:secret@localhost/mlhub",
    "storage_path": "/data/artifacts",
    "internal_notes": "System initialized. Check /FLAG.txt for deployment token."
}


def get_flag():
    """Read flag from file or environment variable"""
    # First try environment variable (k8s deployment)
    flag = os.environ.get('FLAG', '')
    if flag and flag != 'PLACEHOLDER_FLAG':
        return flag
    # Then try file (docker build)
    try:
        with open('/FLAG.txt', 'r') as f:
            return f.read().strip()
    except:
        return "FLAG{placeholder}"


# VULNERABLE: Content-Type validation that can be bypassed
def require_json_content_type(f):
    """
    Decorator to validate Content-Type header.
    VULNERABILITY: Only checks if header starts with specific values,
    allowing bypass with non-standard content types.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        content_type = request.headers.get('Content-Type', '')
        
        # Vulnerable validation - only checks for exact match with common types
        # Does NOT reject unknown/malicious content types
        allowed_types = ['application/json', 'application/x-www-form-urlencoded']
        
        # The bug: if content-type is NOT in allowed list AND NOT empty,
        # we still process it (should reject instead)
        if content_type and content_type.split(';')[0].strip() in allowed_types:
            # Normal processing
            pass
        elif not content_type:
            # Missing content-type - reject
            return jsonify({"error": "Missing Content-Type header"}), 400
        else:
            # VULNERABILITY: Non-standard content types are processed anyway!
            # Should reject here but instead falls through
            pass
        
        return f(*args, **kwargs)
    return decorated_function


def parse_request_json():
    """
    Parse JSON from request body.
    VULNERABILITY: Uses force=True which parses JSON regardless of Content-Type
    """
    try:
        # VULNERABLE: force=True ignores Content-Type header
        return request.get_json(force=True, silent=True) or {}
    except:
        return {}


# HTML templates
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ModelHub - ML Model Registry</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 0; }
        .api-card { border-radius: 8px; transition: transform 0.2s; }
        .api-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="hero text-center">
        <h1><i class="fas fa-cube"></i> ModelHub</h1>
        <p class="lead">Enterprise Machine Learning Model Registry</p>
        <p>Version 2.8.1</p>
    </div>
    
    <div class="container my-5">
        <div class="row">
            <div class="col-md-8 offset-md-2">
                <h2>REST API Documentation</h2>
                <p class="text-muted">Manage your ML models, experiments, and artifacts through our API.</p>
                
                <div class="card api-card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">GET /api/v1/models</h5>
                        <p class="card-text">List all registered models</p>
                    </div>
                </div>
                
                <div class="card api-card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">POST /api/v1/models/search</h5>
                        <p class="card-text">Search models with filters. Requires <code>Content-Type: application/json</code></p>
                    </div>
                </div>
                
                <div class="card api-card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">GET /api/v1/experiments</h5>
                        <p class="card-text">List experiments</p>
                    </div>
                </div>
                
                <div class="card api-card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">POST /api/v1/experiments/search</h5>
                        <p class="card-text">Search experiments with filters</p>
                    </div>
                </div>
                
                <div class="card api-card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">POST /api/v1/system/diagnostics</h5>
                        <p class="card-text">Internal endpoint for system diagnostics (restricted access)</p>
                        <small class="text-muted">Requires proper authentication and Content-Type validation</small>
                    </div>
                </div>
                
                <hr>
                <h4>Authentication</h4>
                <p>Protected endpoints require an API key in the <code>X-API-Key</code> header or proper session authentication.</p>
                
                <h4>Content-Type Requirements</h4>
                <p>POST endpoints must include <code>Content-Type: application/json</code> header with a valid JSON body.</p>
            </div>
        </div>
    </div>
    
    <footer class="bg-light py-3 text-center">
        <small class="text-muted">ModelHub &copy; 2024 - ML Infrastructure Platform</small>
    </footer>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE)


@app.route('/api/v1/models', methods=['GET'])
def list_models():
    """List all models - public endpoint"""
    return jsonify({
        "models": list(MODELS.values()),
        "total": len(MODELS)
    })


@app.route('/api/v1/models/search', methods=['POST'])
@require_json_content_type
def search_models():
    """Search models with filters"""
    data = parse_request_json()
    
    # Filter models based on search criteria
    results = []
    name_filter = data.get('name', '')
    status_filter = data.get('status', '')
    
    for model in MODELS.values():
        if name_filter and name_filter.lower() not in model['name'].lower():
            continue
        if status_filter and model['status'] != status_filter:
            continue
        results.append(model)
    
    return jsonify({
        "results": results,
        "count": len(results),
        "filters_applied": {"name": name_filter, "status": status_filter}
    })


@app.route('/api/v1/experiments', methods=['GET'])
def list_experiments():
    """List all experiments"""
    return jsonify({
        "experiments": list(EXPERIMENTS.values()),
        "total": len(EXPERIMENTS)
    })


@app.route('/api/v1/experiments/search', methods=['POST'])
@require_json_content_type
def search_experiments():
    """Search experiments with filters"""
    data = parse_request_json()
    
    results = []
    model_id = data.get('model_id', '')
    
    for exp in EXPERIMENTS.values():
        if model_id and exp['model_id'] != model_id:
            continue
        results.append(exp)
    
    return jsonify({
        "results": results,
        "count": len(results)
    })


@app.route('/api/v1/system/diagnostics', methods=['POST'])
@require_json_content_type
def system_diagnostics():
    """
    VULNERABLE ENDPOINT
    
    This endpoint is supposed to be protected by Content-Type validation,
    but the validation can be bypassed by using a non-standard content type
    like 'text/plain' or 'text/html'.
    
    When bypassed, it returns sensitive system information including the flag.
    """
    data = parse_request_json()
    content_type = request.headers.get('Content-Type', '')
    
    # Check if this is a "proper" request with application/json
    if content_type.startswith('application/json'):
        # Normal diagnostic response - no sensitive data
        return jsonify({
            "status": "healthy",
            "version": "2.8.1",
            "uptime": "14 days",
            "message": "System operating normally"
        })
    else:
        # VULNERABILITY: Non-standard content type bypassed the check
        # and reaches here - we return sensitive debug information
        include_secrets = data.get('include_secrets', False)
        debug_level = data.get('debug_level', 0)
        
        response = {
            "status": "healthy",
            "version": "2.8.1",
            "debug_mode": True,
            "config": SYSTEM_CONFIG,
            "internal_endpoints": ["/api/internal/backup", "/api/internal/secrets"],
            "warning": "Debug information exposed - content-type validation bypassed"
        }
        
        # If they request secrets explicitly
        if include_secrets or debug_level > 1:
            response["deployment_token"] = get_flag()
            response["api_keys"] = {user: info["api_key"] for user, info in USERS.items()}
        
        return jsonify(response)


@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = parse_request_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    if username in USERS and USERS[username]['password'] == password:
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {"username": username, "role": USERS[username]['role']}
        })
    
    return jsonify({"success": False, "error": "Invalid credentials"}), 401


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
