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
import xml.etree.ElementTree as ET
from constants import *

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "version": "1.17.0"})

@app.route('/api/projects')
def list_projects():
    return jsonify({
        "count": 3,
        "results": [
            {"id": 1, "title": "Image Classification", "description": "Classify images into categories"},
            {"id": 2, "title": "Named Entity Recognition", "description": "Tag named entities in text"},
            {"id": 3, "title": "Sentiment Analysis", "description": "Label sentiment in reviews"}
        ]
    })

@app.route('/api/projects/<int:project_id>')
def get_project(project_id):
    projects = {
        1: {"id": 1, "title": "Image Classification", "description": "Classify images", "task_count": 150},
        2: {"id": 2, "title": "Named Entity Recognition", "description": "Tag entities", "task_count": 89},
        3: {"id": 3, "title": "Sentiment Analysis", "description": "Label sentiment", "task_count": 234}
    }
    if project_id in projects:
        return jsonify(projects[project_id])
    return jsonify({"error": "Project not found"}), 404

@app.route('/api/users')
def list_users():
    return jsonify({
        "count": 2,
        "results": [
            {"id": 1, "username": "admin", "email": "admin@labelstudio.local"},
            {"id": 2, "username": "annotator", "email": "annotator@labelstudio.local"}
        ]
    })

def check_xss(page, flag, msg):
    """Execute PhantomJS to check if XSS payload triggers alert('XSS')"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print "Page:"
        print page
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print "Result:"
        print result
    finally:
        os.unlink(fn)
    
    return result

def parse_label_config(config):
    """Parse label config XML and extract task data"""
    try:
        root = ET.fromstring(config)
        task_data = {"data": {}, "parsed": True}
        
        # Extract data from XML elements
        for elem in root.iter():
            if 'value' in elem.attrib:
                val = elem.attrib.get('value', '')
                if val.startswith('$'):
                    task_data["data"][val[1:]] = "sample_value"
                else:
                    task_data["data"][elem.tag.lower()] = val
            if 'name' in elem.attrib:
                task_data["data"]["_" + elem.attrib['name']] = elem.tag
        
        return task_data
    except ET.ParseError as e:
        # Return error but still include the raw config for display
        return {"error": "Invalid XML format", "detail": str(e), "parsed": False}

@app.route('/projects/upload-example/', methods=['POST', 'GET'])
def upload_example_using_config():
    """
    Upload example endpoint - accepts label_config parameter
    VULNERABLE: Reflects user input in HTML response without proper sanitization
    Similar to CVE in HumanSignal/label-studio prior to 1.18.0
    """
    if request.method == 'GET':
        return UPLOAD_EXAMPLE_FORM
    
    # Get label_config from POST data
    label_config = request.form.get('label_config', '')
    
    if not label_config:
        return jsonify({"error": "label_config is required"}), 400
    
    # Parse the label config (may fail for invalid XML)
    task_data = parse_label_config(label_config)
    
    # Generate JSON output
    json_output = json.dumps(task_data, indent=2)
    
    # VULNERABLE: Create HTML page that embeds raw label_config without escaping
    # This allows XSS when the config contains script tags or event handlers
    html_response = UPLOAD_RESPONSE_TEMPLATE.format(json_output, label_config)
    
    # Check if XSS payload executes via PhantomJS
    result = check_xss(html_response, flags[0], label_config)
    
    if result == 'XSS':
        # XSS successfully executed - return flag
        return UPLOAD_SUCCESS_TEMPLATE.format(flags[0])
    elif result:
        # Alert triggered but not with 'XSS'
        return UPLOAD_RESPONSE_TEMPLATE.format(json_output, cgi.escape(label_config)) + \
               '<div class="alert alert-warning">Alert triggered with: {}</div>'.format(cgi.escape(result))
    else:
        # Normal response - show the parsed data (escaped for display)
        return UPLOAD_RESPONSE_TEMPLATE.format(json_output, cgi.escape(label_config))

@app.route('/api/templates')
def list_templates():
    return jsonify({
        "count": 4,
        "results": [
            {"id": 1, "name": "Image Classification", "config": "<View><Image name=\"img\" value=\"$image\"/></View>"},
            {"id": 2, "name": "Text Classification", "config": "<View><Text name=\"text\" value=\"$text\"/></View>"},
            {"id": 3, "name": "Named Entity", "config": "<View><Labels name=\"ner\"><Label value=\"PER\"/></Labels></View>"},
            {"id": 4, "name": "Audio Transcription", "config": "<View><Audio name=\"audio\" value=\"$audio\"/></View>"}
        ]
    })

@app.route('/api/export/<int:project_id>')
def export_project(project_id):
    return jsonify({"message": "Export initiated for project {}".format(project_id), "status": "pending"})

if __name__ == '__main__':
    app.run(debug=True)
