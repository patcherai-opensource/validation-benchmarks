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

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flag_content = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/projects/')
def projects_list():
    return PROJECTS_LIST_CONTENT


@app.route('/projects/create/', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        project_name = request.form.get('project_name', 'Untitled')
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Label Studio - Project Created</title>
            <link rel="stylesheet" href="/static/css/label-studio.css">
        </head>
        <body>
            <div class="container">
                <h1>Project Created Successfully</h1>
                <p>Project "{}" has been created.</p>
                <a href="/projects/">Back to Projects</a>
            </div>
        </body>
        </html>
        '''.format(cgi.escape(project_name))
    return CREATE_PROJECT_CONTENT


def parse_label_config(config):
    """Parse label config XML and extract sample task data."""
    task_data = {}
    
    try:
        root = ET.fromstring(config)
        
        for elem in root.iter():
            if 'value' in elem.attrib:
                value = elem.attrib.get('value', '')
                if value.startswith('$'):
                    var_name = value[1:]
                    task_data[var_name] = "Sample " + var_name + " content"
                else:
                    name = elem.attrib.get('name', elem.tag.lower())
                    task_data[name] = value
            
            if 'name' in elem.attrib and 'value' not in elem.attrib:
                name = elem.attrib.get('name')
                task_data[name + '_label'] = elem.tag
    except ET.ParseError:
        task_data['raw_config'] = config
    
    return task_data


def check_xss_in_response(html_content, label_config):
    """Check if XSS payload in response triggers alert."""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    
    return result


@app.route('/projects/upload-example/', methods=['POST', 'GET'])
def upload_example_using_config():
    """
    Upload example endpoint that processes label_config and returns task data.
    This endpoint parses the label configuration and generates sample task data.
    """
    if request.method == 'GET':
        return UPLOAD_EXAMPLE_FORM
    
    label_config = request.form.get('label_config', '')
    
    if not label_config:
        return Response(
            json.dumps({"error": "label_config parameter is required"}),
            status=400,
            mimetype='application/json'
        )
    
    task_data = parse_label_config(label_config)
    
    json_response = json.dumps(task_data)
    
    preview_html = TASK_PREVIEW_TEMPLATE.format(label_config, json_response)
    
    xss_result = check_xss_in_response(preview_html, label_config)
    
    if xss_result == 'XSS':
        task_data['_debug_flag'] = flag_content
        json_response = json.dumps(task_data)
    
    return Response(json_response, mimetype='application/json')


@app.route('/api/projects/', methods=['GET'])
def api_projects():
    """API endpoint listing projects."""
    projects = [
        {"id": 1, "title": "Text Classification", "created_at": "2024-01-15"},
        {"id": 2, "title": "Image Annotation", "created_at": "2024-01-20"},
        {"id": 3, "title": "NER Task", "created_at": "2024-02-01"}
    ]
    return jsonify(projects)


@app.route('/user/account/')
def user_account():
    return USER_ACCOUNT_CONTENT


@app.errorhandler(404)
def not_found(e):
    return Response("Not Found", status=404)


@app.errorhandler(500)
def server_error(e):
    return Response("Internal Server Error", status=500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
