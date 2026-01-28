# encoding=utf8

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

# Simulated projects data
projects_db = [
    {"id": 1, "title": "Sentiment Analysis", "created_at": "2024-01-15", "task_count": 150},
    {"id": 2, "title": "Image Classification", "created_at": "2024-02-20", "task_count": 89},
    {"id": 3, "title": "Named Entity Recognition", "created_at": "2024-03-10", "task_count": 234}
]

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/projects/')
def api_projects():
    """List all projects - API endpoint"""
    return jsonify({"results": projects_db, "count": len(projects_db)})

@app.route('/api/projects/<int:project_id>/')
def api_project_detail(project_id):
    """Get project details"""
    for p in projects_db:
        if p['id'] == project_id:
            return jsonify(p)
    return jsonify({"error": "Project not found"}), 404

@app.route('/projects/')
def projects_list():
    """Projects listing page"""
    return PROJECTS_LIST_CONTENT

@app.route('/projects/create/', methods=['GET', 'POST'])
def create_project():
    """Create new project page"""
    if request.method == 'POST':
        title = request.form.get('title', '')
        if not title:
            return jsonify({"error": "Title is required"}), 400
        return jsonify({"status": "created", "project_id": len(projects_db) + 1})
    return CREATE_PROJECT_CONTENT

@app.route('/docs/')
def docs():
    """Documentation page"""
    return DOCS_CONTENT

@app.route('/api/health/')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "version": "1.17.0"})

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print "Page:"
        print page
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print "Resultado:"
        print result

    finally:
        os.unlink(fn)

    return result

def parse_label_config(config):
    """
    Parse label config XML and extract sample task data.
    This is a simplified parser that extracts value attributes from elements.
    """
    # Simple regex-based extraction of value attributes (mimics Label Studio behavior)
    values = re.findall(r'value="([^"]*)"', config)
    text_values = re.findall(r'<Text[^>]*name="([^"]*)"[^>]*>', config)
    
    task_data = {}
    for name in text_values:
        task_data[name] = "Sample text content"
    
    # Include the raw config snippets in the response (vulnerable!)
    # Only filter obvious script tags (case-sensitive)
    filtered_config = re.sub(r'<script>', '', config)
    filtered_config = re.sub(r'</script>', '', filtered_config)
    
    return {
        "task_data": task_data,
        "preview": filtered_config
    }

@app.route('/projects/upload-example/', methods=['GET', 'POST'])
def upload_example_using_config():
    """
    Upload example using label config.
    Vulnerable endpoint that reflects label_config in the response.
    """
    if request.method == 'GET':
        return UPLOAD_EXAMPLE_CONTENT
    
    # POST request handling - CVE-inspired vulnerability
    label_config = request.form.get('label_config', '')
    
    if not label_config:
        return jsonify({"error": "label_config is required"}), 400
    
    # Parse the config (vulnerable - unsanitized output)
    parsed = parse_label_config(label_config)
    
    # Generate preview HTML with the parsed config (VULNERABLE - XSS sink)
    preview_html = PREVIEW_CONTENT.format(parsed['preview'])
    
    # Check for XSS - if alert('XSS') is triggered, return the flag
    result = check_xss(preview_html, flags[0], label_config, 'config_preview')
    
    if result == 'XSS':
        return jsonify({
            "status": "success",
            "task_data": parsed['task_data'],
            "flag": flags[0],
            "message": "XSS detected! Here is your flag."
        })
    elif result:
        return jsonify({
            "status": "processed",
            "task_data": parsed['task_data'],
            "preview_result": "Alert triggered with: " + result
        })
    else:
        return jsonify({
            "status": "processed",
            "task_data": parsed['task_data']
        })

@app.route('/api/import/', methods=['POST'])
def api_import():
    """Import tasks endpoint (decoy)"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    return jsonify({"imported": 0, "status": "success"})

@app.route('/api/export/<int:project_id>/')
def api_export(project_id):
    """Export project data (decoy)"""
    return jsonify({"project_id": project_id, "format": "JSON", "data": []})

if __name__ == '__main__':
    app.run(debug=True)
