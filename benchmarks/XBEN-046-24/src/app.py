# encoding=utf8
# -*- coding: utf-8 -*-
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
import xml.etree.ElementTree as ET
from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

# Load flag from environment variable or file
flag_env = os.environ.get('FLAG_VALUE')
if flag_env:
    flags = [flag_env]
else:
    flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

@app.route('/health')
def health_check():
    return 'OK', 200

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/v1/projects')
def list_projects():
    """List available annotation projects"""
    return jsonify({
        "count": 3,
        "results": [
            {"id": 1, "title": "Image Classification", "created_at": "2024-01-15T10:30:00Z"},
            {"id": 2, "title": "Text Sentiment Analysis", "created_at": "2024-01-16T14:20:00Z"},
            {"id": 3, "title": "Named Entity Recognition", "created_at": "2024-01-17T09:15:00Z"}
        ]
    })

@app.route('/api/v1/projects/<int:project_id>')
def get_project(project_id):
    """Get project details"""
    projects = {
        1: {"id": 1, "title": "Image Classification", "description": "Classify images into categories", "task_count": 150},
        2: {"id": 2, "title": "Text Sentiment Analysis", "description": "Analyze sentiment of text samples", "task_count": 320},
        3: {"id": 3, "title": "Named Entity Recognition", "description": "Identify entities in documents", "task_count": 89}
    }
    if project_id in projects:
        return jsonify(projects[project_id])
    return jsonify({"error": "Project not found"}), 404

@app.route('/api/v1/projects/<int:project_id>/tasks')
def get_tasks(project_id):
    """Get tasks for a project"""
    return jsonify({
        "count": 10,
        "results": [{"id": i, "data": {"text": "Sample task {}".format(i)}} for i in range(1, 11)]
    })

@app.route('/api/v1/users/me')
def current_user():
    """Get current user info"""
    return jsonify({
        "id": 42,
        "email": "demo@labelstudio.local",
        "username": "demo_user",
        "is_active": True
    })

@app.route('/projects/create', methods=['GET'])
def create_project_form():
    """Project creation form"""
    return PROJECT_CREATE_CONTENT

@app.route('/projects/validate-config', methods=['POST'])
def validate_config():
    """Validate label configuration - safe endpoint"""
    config = request.form.get('label_config', '')
    if not config:
        return jsonify({"valid": False, "error": "No configuration provided"}), 400
    
    # Basic XML validation
    try:
        ET.fromstring(config)
        return jsonify({"valid": True, "message": "Configuration is valid XML"})
    except ET.ParseError as e:
        return jsonify({"valid": False, "error": "Invalid XML: {}".format(str(e))}), 400

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for base URL with fallback to localhost
    base_url = os.environ.get('APP_BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Resultado:")
        print(result)

    finally:
        os.unlink(fn)

    return result


@app.route('/projects/upload-example/', methods=['POST'])
def upload_example_using_config():
    """
    Upload example using label configuration.
    Generates sample task data from the provided label config.
    """
    config = request.form.get('label_config', '')
    
    if not config:
        return jsonify({"error": "label_config is required"}), 400
    
    # Try to parse as XML for structure validation only
    try:
        root = ET.fromstring(config)
    except ET.ParseError as e:
        return jsonify({"error": "Invalid XML configuration: {}".format(str(e))}), 400
    
    # Extract sample data from config elements
    task_data = {}
    for element in root.iter():
        if 'value' in element.attrib:
            # Extract the variable reference (e.g., "$text" -> "text")
            value = element.attrib['value']
            if value.startswith('$'):
                var_name = value[1:].split('<')[0].split('&')[0]  # Get variable name
                task_data[var_name] = "Sample {} data for annotation".format(var_name)
            else:
                # For values that don't start with $, include them directly
                task_data[element.attrib.get('name', 'value')] = value
    
    if not task_data:
        task_data = {"data": "Sample annotation data"}
    
    # Generate example page to preview the config
    # VULNERABLE: config is embedded without proper sanitization
    preview_html = UPLOAD_EXAMPLE_PREVIEW.format(config, json.dumps(task_data))
    
    # Check for XSS in the rendered content
    result = check_xss(preview_html, flags[0], config, 'xss_medium')
    
    if result == 'XSS':
        return jsonify({
            "task_data": task_data,
            "preview_url": "/projects/preview/example",
            "flag": flags[0]
        })
    else:
        return jsonify({
            "task_data": task_data,
            "preview_url": "/projects/preview/example"
        })


@app.route('/projects/settings/<int:project_id>', methods=['GET'])
def project_settings(project_id):
    """Project settings page"""
    return PROJECT_SETTINGS_CONTENT.format(project_id)

@app.route('/api/v1/export/<int:project_id>')
def export_annotations(project_id):
    """Export annotations for a project"""
    return jsonify({
        "format": "JSON",
        "data": [
            {"id": 1, "result": [{"value": {"choices": ["Positive"]}}]},
            {"id": 2, "result": [{"value": {"choices": ["Negative"]}}]}
        ]
    })

@app.route('/api/v1/import/<int:project_id>', methods=['POST'])
def import_tasks(project_id):
    """Import tasks into a project"""
    return jsonify({"imported": 0, "message": "No tasks provided"}), 400

@app.route('/docs')
def api_docs():
    """API Documentation"""
    return API_DOCS_CONTENT

if __name__ == '__main__':
    app.run(debug=True)
