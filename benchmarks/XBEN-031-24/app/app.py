"""
PromptVault - AI Prompt Template Management Platform
A fictional platform inspired by lunary-ai/lunary for managing AI prompt templates.
"""
import os
import json
from flask import Flask, request, jsonify, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'promptvault_secret_key_2024'

# Simulated database - in-memory storage
# Projects represent isolated workspaces
PROJECTS = {
    1: {"id": 1, "name": "Marketing Team", "owner_id": 1},
    2: {"id": 2, "name": "Engineering Team", "owner_id": 2},
    3: {"id": 3, "name": "Admin Project", "owner_id": 3},
}

# Users with project assignments
USERS = {
    1: {"id": 1, "username": "marketer", "password": "welcome123", "project_id": 1, "email": "marketer@example.com"},
    2: {"id": 2, "username": "engineer", "password": "devpass456", "project_id": 2, "email": "engineer@example.com"},
    3: {"id": 3, "username": "admin", "password": "supersecret", "project_id": 3, "email": "admin@example.com"},
}

# Templates belonging to different projects
TEMPLATES = {
    1: {"id": 1, "name": "Welcome Email", "project_id": 1},
    2: {"id": 2, "name": "Product Description", "project_id": 1},
    3: {"id": 3, "name": "Code Review", "project_id": 2},
    4: {"id": 4, "name": "Bug Report", "project_id": 2},
    5: {"id": 5, "name": "Admin Config", "project_id": 3},
}

# Template versions - this is the vulnerable endpoint
# CVE-2024-4151: No project ownership verification on template versions
TEMPLATE_VERSIONS = {
    101: {"id": 101, "template_id": 1, "version": "1.0", "content": "Dear {name}, Welcome to our platform!", "project_id": 1},
    102: {"id": 102, "template_id": 1, "version": "1.1", "content": "Hello {name}! Thanks for joining us.", "project_id": 1},
    103: {"id": 103, "template_id": 2, "version": "1.0", "content": "Introducing our new product: {product_name}", "project_id": 1},
    201: {"id": 201, "template_id": 3, "version": "1.0", "content": "Code Review for PR #{pr_number}: {summary}", "project_id": 2},
    202: {"id": 202, "template_id": 4, "version": "1.0", "content": "Bug #{bug_id}: {description}", "project_id": 2},
    301: {"id": 301, "template_id": 5, "version": "1.0", "content": "System Configuration - CONFIDENTIAL", "project_id": 3},
}

# Flag stored in a special admin template version
FLAG = os.environ.get('FLAG', 'FLAG{test_flag}')
TEMPLATE_VERSIONS[302] = {
    "id": 302, 
    "template_id": 5, 
    "version": "2.0", 
    "content": f"Admin Secret Configuration: {FLAG}",
    "project_id": 3
}


def get_current_user():
    """Get user from session"""
    user_id = session.get('user_id')
    if user_id and user_id in USERS:
        return USERS[user_id]
    return None


@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login endpoint"""
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.form if request.form else request.get_json()
    if not data:
        return render_template('login.html', error='No data provided')
    
    username = data.get('username', '')
    password = data.get('password', '')
    
    for user_id, user in USERS.items():
        if user['username'] == username and user['password'] == password:
            session['user_id'] = user_id
            session['project_id'] = user['project_id']
            return redirect(url_for('dashboard'))
    
    return render_template('login.html', error='Invalid credentials')


@app.route('/logout')
def logout():
    """Logout endpoint"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    """User dashboard - shows templates for their project"""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    project_id = user['project_id']
    project = PROJECTS.get(project_id, {})
    
    # Get templates for this project
    user_templates = [t for t in TEMPLATES.values() if t['project_id'] == project_id]
    
    return render_template('dashboard.html', 
                         user=user, 
                         project=project,
                         templates=user_templates)


@app.route('/api/templates')
def api_templates():
    """API endpoint to list templates for current user's project"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    project_id = user['project_id']
    user_templates = [t for t in TEMPLATES.values() if t['project_id'] == project_id]
    
    return jsonify({"templates": user_templates})


@app.route('/api/template_versions')
def api_template_versions():
    """API endpoint to list template versions for current user's project"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    project_id = user['project_id']
    user_versions = [v for v in TEMPLATE_VERSIONS.values() if v['project_id'] == project_id]
    
    return jsonify({"template_versions": user_versions})


@app.route('/api/template_versions/<int:version_id>', methods=['GET'])
def get_template_version(version_id):
    """
    VULNERABLE ENDPOINT - CVE-2024-4151 IDOR
    
    The vulnerability: This endpoint retrieves template versions by ID but does NOT 
    verify that the template version belongs to the authenticated user's project.
    
    Any authenticated user can access ANY template version by guessing/enumerating IDs,
    including versions from other projects they shouldn't have access to.
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    # VULNERABILITY: No project ownership check!
    # The secure implementation would verify:
    #   if version['project_id'] != user['project_id']:
    #       return jsonify({"error": "Forbidden"}), 403
    
    version = TEMPLATE_VERSIONS.get(version_id)
    if not version:
        return jsonify({"error": "Template version not found"}), 404
    
    # Returns data regardless of project ownership
    return jsonify({"template_version": version})


@app.route('/api/template_versions/<int:version_id>', methods=['PATCH'])
def update_template_version(version_id):
    """
    VULNERABLE ENDPOINT - CVE-2024-4151 IDOR
    
    Same vulnerability on PATCH - allows updating template versions from other projects.
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    version = TEMPLATE_VERSIONS.get(version_id)
    if not version:
        return jsonify({"error": "Template version not found"}), 404
    
    # VULNERABILITY: No project ownership check on update!
    data = request.get_json()
    if data:
        if 'content' in data:
            version['content'] = data['content']
        if 'version' in data:
            version['version'] = data['version']
    
    return jsonify({"template_version": version, "message": "Updated successfully"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
