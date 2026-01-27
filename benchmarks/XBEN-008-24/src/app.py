# encoding=utf8
"""
DevBundle - Debug File & Artifact Bundle Management API
A developer tools platform for managing debug symbols and artifact bundles
"""

from flask import Flask, request, jsonify, make_response, session
import os
import json
import hashlib
import base64

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# Read flag from environment variable or file
flag_env = os.getenv('FLAG', '')
if flag_env:
    FLAG = flag_env
else:
    FLAG = open('secret.txt').read().strip()

# Simulated database of organizations, projects, users, and files
# In a real application, this would be in a database

ORGANIZATIONS = {
    "org-public": {"name": "Public Development", "id": "org-public"},
    "org-internal": {"name": "Internal Tools", "id": "org-internal"},
    "org-security": {"name": "Security Team", "id": "org-security"}
}

PROJECTS = {
    "proj-001": {"name": "web-frontend", "org_id": "org-public", "id": "proj-001"},
    "proj-002": {"name": "mobile-app", "org_id": "org-public", "id": "proj-002"},
    "proj-003": {"name": "internal-dashboard", "org_id": "org-internal", "id": "proj-003"},
    "proj-004": {"name": "security-audit", "org_id": "org-security", "id": "proj-004"}
}

# Users with their organization memberships
USERS = {
    "demo": {"password": "demo123", "orgs": ["org-public"], "api_key": "devbundle_demo_ak_7f3c9a2b"},
    "developer": {"password": "dev2024!", "orgs": ["org-public", "org-internal"], "api_key": "devbundle_dev_ak_3m8n2k5j"}
}

# Files/artifacts stored in the system - indexed by file_id
# VULNERABILITY: Files are looked up by ID only, without checking project/org membership
FILES = {
    "1001": {"name": "frontend-bundle.zip", "project_id": "proj-001", "size": 2048, "type": "artifact_bundle", "content": "UHVibGljIGZyb250ZW5kIGFzc2V0cw=="},
    "1002": {"name": "frontend-debug.dsym", "project_id": "proj-001", "size": 4096, "type": "debug_file", "content": "RnJvbnRlbmQgZGVidWcgc3ltYm9scw=="},
    "1003": {"name": "mobile-bundle.zip", "project_id": "proj-002", "size": 3072, "type": "artifact_bundle", "content": "TW9iaWxlIGFwcCBidW5kbGU="},
    "1004": {"name": "dashboard-config.json", "project_id": "proj-003", "size": 512, "type": "artifact_bundle", "content": "SW50ZXJuYWwgZGFzaGJvYXJkIGNvbmZpZw=="},
    "1005": {"name": "audit-report.dsym", "project_id": "proj-004", "size": 8192, "type": "debug_file", "content": "PLACEHOLDER_FLAG"}  # This will be replaced with actual flag
}

# Replace placeholder with actual flag
FILES["1005"]["content"] = base64.b64encode(FLAG.encode()).decode()

def get_current_user():
    """Get the current authenticated user from session or API key"""
    # Check session first
    if 'username' in session:
        return session['username']
    
    # Check API key in header
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        api_key = auth_header[7:]
        for username, user_data in USERS.items():
            if user_data.get('api_key') == api_key:
                return username
    
    return None

def user_has_org_access(username, org_id):
    """Check if user has access to an organization"""
    if username not in USERS:
        return False
    return org_id in USERS[username].get('orgs', [])

def user_has_project_access(username, project_id):
    """Check if user has access to a project via org membership"""
    if project_id not in PROJECTS:
        return False
    org_id = PROJECTS[project_id]['org_id']
    return user_has_org_access(username, org_id)


@app.route('/')
def index():
    """Landing page for DevBundle API"""
    return '''<!DOCTYPE html>
<html>
<head>
    <title>DevBundle - Debug & Artifact Management</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2d3748; border-bottom: 3px solid #4299e1; padding-bottom: 10px; }
        h2 { color: #4a5568; margin-top: 30px; }
        code { background: #edf2f7; padding: 2px 6px; border-radius: 4px; font-size: 14px; }
        pre { background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 6px; overflow-x: auto; }
        .endpoint { background: #ebf8ff; border-left: 4px solid #4299e1; padding: 15px; margin: 15px 0; border-radius: 0 6px 6px 0; }
        .method { display: inline-block; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-right: 10px; }
        .get { background: #48bb78; color: white; }
        .post { background: #ed8936; color: white; }
        .note { background: #fefcbf; border-left: 4px solid #d69e2e; padding: 15px; margin: 15px 0; }
        a { color: #4299e1; }
    </style>
</head>
<body>
    <div class="container">
        <h1>DevBundle API</h1>
        <p>Welcome to DevBundle - your centralized platform for managing debug symbols and artifact bundles across all your projects.</p>
        
        <div class="note">
            <strong>Demo Account:</strong> Use <code>demo</code> / <code>demo123</code> to explore the API, or use API key <code>devbundle_demo_ak_7f3c9a2b</code>
        </div>
        
        <h2>Authentication</h2>
        <div class="endpoint">
            <span class="method post">POST</span><code>/api/v1/auth/login</code>
            <p>Authenticate with username and password to get a session</p>
            <pre>curl -X POST -d "username=demo&password=demo123" http://localhost:8080/api/v1/auth/login</pre>
        </div>
        
        <h2>Organizations & Projects</h2>
        <div class="endpoint">
            <span class="method get">GET</span><code>/api/v1/organizations</code>
            <p>List all organizations (requires authentication)</p>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span><code>/api/v1/projects/{org_id}/{project_id}</code>
            <p>Get project details</p>
        </div>
        
        <h2>Artifact & Debug File Management</h2>
        <div class="endpoint">
            <span class="method get">GET</span><code>/api/v1/projects/{org_id}/{project_id}/artifacts/</code>
            <p>List artifacts for a project. Add <code>?download={file_id}</code> to download a specific artifact bundle.</p>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span><code>/api/v1/projects/{org_id}/{project_id}/files/dsyms/</code>
            <p>List debug files for a project. Add <code>?id={file_id}</code> to download a specific debug file.</p>
        </div>
        
        <h2>Quick Start</h2>
        <pre># Login first
curl -c cookies.txt -X POST -d "username=demo&password=demo123" \\
    http://localhost:8080/api/v1/auth/login

# List your projects
curl -b cookies.txt http://localhost:8080/api/v1/projects/org-public/proj-001

# Download an artifact
curl -b cookies.txt "http://localhost:8080/api/v1/projects/org-public/proj-001/artifacts/?download=1001"</pre>

        <p style="margin-top: 30px; color: #718096; font-size: 14px;">DevBundle v2.3.1 | <a href="/api/v1/status">API Status</a></p>
    </div>
</body>
</html>'''


@app.route('/api/v1/status')
def api_status():
    """API health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "2.3.1",
        "service": "devbundle-api"
    })


@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """Login endpoint - supports form data or JSON"""
    if request.is_json:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
    else:
        username = request.form.get('username', '')
        password = request.form.get('password', '')
    
    if username in USERS and USERS[username]['password'] == password:
        session['username'] = username
        return jsonify({
            "success": True,
            "message": "Authentication successful",
            "user": {
                "username": username,
                "organizations": USERS[username]['orgs'],
                "api_key": USERS[username]['api_key']
            }
        })
    
    return jsonify({
        "success": False,
        "error": "Invalid credentials"
    }), 401


@app.route('/api/v1/auth/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    session.pop('username', None)
    return jsonify({"success": True, "message": "Logged out"})


@app.route('/api/v1/organizations')
def list_organizations():
    """List organizations the current user has access to"""
    username = get_current_user()
    if not username:
        return jsonify({"error": "Authentication required"}), 401
    
    user_orgs = USERS[username].get('orgs', [])
    orgs = [ORGANIZATIONS[org_id] for org_id in user_orgs if org_id in ORGANIZATIONS]
    
    return jsonify({
        "organizations": orgs
    })


@app.route('/api/v1/projects/<org_id>/<project_id>')
def get_project(org_id, project_id):
    """Get project details"""
    username = get_current_user()
    if not username:
        return jsonify({"error": "Authentication required"}), 401
    
    if project_id not in PROJECTS:
        return jsonify({"error": "Project not found"}), 404
    
    project = PROJECTS[project_id]
    
    # Check if user has access to this project's organization
    if not user_has_project_access(username, project_id):
        return jsonify({"error": "You do not have access to this project"}), 403
    
    return jsonify({
        "project": project,
        "organization": ORGANIZATIONS.get(project['org_id'])
    })


@app.route('/api/v1/projects/<org_id>/<project_id>/artifacts/')
def project_artifacts(org_id, project_id):
    """
    List or download artifacts for a project.
    
    VULNERABILITY: When downloading via ?download=<file_id>, the file is fetched
    by ID only, without verifying it belongs to the requested project.
    """
    username = get_current_user()
    if not username:
        return jsonify({"error": "Authentication required"}), 401
    
    download_id = request.args.get('download')
    
    if download_id:
        # VULNERABLE: Fetches file by ID without checking project ownership
        # Should verify: file['project_id'] == project_id
        if download_id in FILES:
            file_info = FILES[download_id]
            if file_info['type'] == 'artifact_bundle':
                content = base64.b64decode(file_info['content'])
                response = make_response(content)
                response.headers['Content-Type'] = 'application/octet-stream'
                response.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(file_info['name'])
                return response
            else:
                return jsonify({"error": "File is not an artifact bundle"}), 400
        return jsonify({"error": "Artifact not found"}), 404
    
    # List artifacts for this project (properly filtered)
    project_files = [
        {"id": fid, "name": f['name'], "size": f['size'], "type": f['type']}
        for fid, f in FILES.items()
        if f['project_id'] == project_id and f['type'] == 'artifact_bundle'
    ]
    
    return jsonify({
        "artifacts": project_files,
        "project_id": project_id,
        "org_id": org_id
    })


@app.route('/api/v1/projects/<org_id>/<project_id>/files/dsyms/')
def project_debug_files(org_id, project_id):
    """
    List or download debug files (dSYMs) for a project.
    
    VULNERABILITY: When downloading via ?id=<file_id>, the file is fetched
    by ID only, without verifying it belongs to the requested project.
    """
    username = get_current_user()
    if not username:
        return jsonify({"error": "Authentication required"}), 401
    
    file_id = request.args.get('id')
    
    if file_id:
        # VULNERABLE: Fetches file by ID without checking project ownership
        # Should verify: file['project_id'] == project_id
        if file_id in FILES:
            file_info = FILES[file_id]
            if file_info['type'] == 'debug_file':
                content = base64.b64decode(file_info['content'])
                response = make_response(content)
                response.headers['Content-Type'] = 'application/octet-stream'
                response.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(file_info['name'])
                return response
            else:
                return jsonify({"error": "File is not a debug file"}), 400
        return jsonify({"error": "Debug file not found"}), 404
    
    # List debug files for this project (properly filtered)
    project_files = [
        {"id": fid, "name": f['name'], "size": f['size'], "type": f['type']}
        for fid, f in FILES.items()
        if f['project_id'] == project_id and f['type'] == 'debug_file'
    ]
    
    return jsonify({
        "debug_files": project_files,
        "project_id": project_id,
        "org_id": org_id
    })


@app.route('/api/v1/files')
def list_all_files():
    """
    Admin endpoint to list all files in the system.
    Only shows file metadata, not the actual content.
    """
    username = get_current_user()
    if not username:
        return jsonify({"error": "Authentication required"}), 401
    
    # Show all file IDs and metadata (simulates information leak or enumeration)
    all_files = [
        {"id": fid, "name": f['name'], "project_id": f['project_id'], "type": f['type']}
        for fid, f in FILES.items()
    ]
    
    return jsonify({
        "files": all_files,
        "total": len(all_files)
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
