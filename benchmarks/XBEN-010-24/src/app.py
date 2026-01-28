# encoding=utf8
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# Simulated projects database
PROJECTS = {
    "1": {"id": 1, "title": "Image Classification", "status": "active", "tasks": 42},
    "2": {"id": 2, "title": "Text Sentiment", "status": "draft", "tasks": 0},
    "3": {"id": 3, "title": "Named Entity Recognition", "status": "completed", "tasks": 156}
}

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/health')
def api_health():
    return jsonify({"status": "ok", "version": "1.17.0", "service": "label-studio"})

@app.route('/api/projects/')
def list_projects():
    """List all labeling projects"""
    return jsonify({"count": len(PROJECTS), "results": list(PROJECTS.values())})

@app.route('/api/projects/<project_id>/')
def get_project(project_id):
    """Get project details"""
    if project_id in PROJECTS:
        return jsonify(PROJECTS[project_id])
    return jsonify({"error": "Project not found"}), 404

@app.route('/api/users/me/')
def current_user():
    """Get current user info"""
    return jsonify({"id": 1, "email": "admin@labelstudio.local", "is_staff": True})

@app.route('/projects/')
def projects_list():
    """Projects listing page"""
    return PROJECTS_PAGE

@app.route('/projects/create/')
def create_project_page():
    """Project creation page"""
    return CREATE_PROJECT_PAGE

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variables for host and port to support K8s deployment
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{0}:{1}/{2}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        logging.info("Page: %s", page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        logging.info("Result: %s", result)

    finally:
        os.unlink(fn)

    return result

def extract_sample_data(label_config):
    """
    Extract sample task data from label config.
    This mimics Label Studio's behavior of parsing config and generating sample data.
    """
    task_data = {}
    
    # Try to extract value attributes from XML-like config
    # This is intentionally vulnerable - values are extracted and returned without sanitization
    try:
        # Simple regex to extract value="..." attributes
        values = re.findall(r'value="([^"]*)"', label_config)
        for i, val in enumerate(values):
            # Decode HTML entities - this is part of the vulnerability
            val = val.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"')
            task_data['field_{}'.format(i)] = val
    except:
        pass
    
    # Also extract name attributes for field identification
    try:
        names = re.findall(r'name="([^"]*)"', label_config)
        for i, name in enumerate(names):
            task_data['name_{}'.format(i)] = name
    except:
        pass
    
    if not task_data:
        task_data = {"error": "Could not parse label config"}
    
    return task_data

@app.route('/projects/upload-example/', methods=['GET', 'POST'])
def upload_example_using_config():
    """
    Upload example task using label configuration.
    This endpoint parses XML label config and returns sample task data.
    
    Vulnerable to XSS - label_config content is included in response without proper sanitization.
    """
    if request.method == 'GET':
        return UPLOAD_EXAMPLE_PAGE
    
    # POST request - process the label config
    label_config = request.form.get('label_config', '')
    
    if not label_config:
        return jsonify({"error": "label_config parameter is required"}), 400
    
    # Extract sample task data from the config
    task_data = extract_sample_data(label_config)
    
    # Generate preview page that includes the task data
    # VULNERABILITY: task_data values are embedded without proper escaping
    preview_content = PREVIEW_PAGE_TEMPLATE.format(
        json_data=json.dumps(task_data),
        raw_config=label_config
    )
    
    # Check for XSS in the rendered page
    result = check_xss(preview_content, flags[0], label_config, 'xss_hard')
    
    if result == 'XSS':
        # XSS detected - return flag
        response_data = {
            "status": "success",
            "task_data": task_data,
            "message": "Configuration validated successfully!",
            "flag": flags[0]
        }
    elif result:
        response_data = {
            "status": "partial",
            "task_data": task_data,
            "message": "Alert detected but expected 'XSS', got: {}".format(result)
        }
    else:
        response_data = {
            "status": "preview",
            "task_data": task_data,
            "message": "Sample task data extracted from configuration"
        }
    
    response = make_response(jsonify(response_data))
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Type"] = "application/json"
    return response

@app.route('/api/import/validate/', methods=['POST'])
def validate_import():
    """Validate import data format - decoy endpoint"""
    data = request.get_json(silent=True) or {}
    if 'format' not in data:
        return jsonify({"error": "format field required"}), 400
    return jsonify({"valid": True, "format": data.get('format'), "message": "Format is supported"})

@app.route('/api/tasks/export/', methods=['GET'])
def export_tasks():
    """Export tasks - decoy endpoint"""
    return jsonify({"tasks": [], "total": 0, "format": "JSON"})

@app.route('/api/ml/models/')
def ml_models():
    """List ML models - decoy endpoint"""
    return jsonify({"count": 0, "results": []})

if __name__ == '__main__':
    app.run(debug=True)
