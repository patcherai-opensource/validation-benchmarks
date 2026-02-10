# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, render_template_string, jsonify
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

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()


@app.errorhandler(500)
def internal_error(error):
    return Response("Internal Server Error", status=500, mimetype='text/plain')


@app.errorhandler(404)
def not_found(error):
    return Response("Not Found", status=404, mimetype='text/plain')


@app.errorhandler(400)
def bad_request(error):
    return Response("Bad Request", status=400, mimetype='text/plain')


@app.route('/')
def index():
    return INDEX_CONTENT


def check_xss_in_response(response_content, flag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
    
    html_page = """
    <!DOCTYPE html>
    <html>
    <head><title>Task Preview</title></head>
    <body>
    <div id="task-data">{0}</div>
    </body>
    </html>
    """.format(response_content)
    
    try:
        of = open(fn, 'w')
        of.write(html_page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    if result == 'XSS':
        return flag
    return None


def parse_label_config(config_str):
    """
    Parse label configuration XML and extract sample task data.
    This simulates Label Studio's config parsing behavior.
    """
    task_data = {}
    
    try:
        root = ET.fromstring(config_str)
        
        for elem in root.iter():
            if 'name' in elem.attrib:
                name = elem.attrib.get('name', '')
                value = elem.attrib.get('value', '')
                
                if value.startswith('$'):
                    var_name = value[1:]
                    task_data[var_name] = "Sample data for " + var_name
                else:
                    task_data[name] = value
            
            if elem.tag in ['Text', 'Image', 'Audio', 'Video', 'HyperText']:
                name = elem.attrib.get('name', elem.tag.lower())
                value = elem.attrib.get('value', '')
                if value:
                    task_data[name] = value
                    
    except ET.ParseError:
        pass
    
    return task_data


@app.route('/projects/')
def projects_list():
    return PROJECTS_PAGE


@app.route('/projects/create/', methods=['GET', 'POST'])
def create_project():
    if request.method == 'GET':
        return CREATE_PROJECT_PAGE
    
    project_name = request.form.get('name', 'Untitled Project')
    return Response(
        json.dumps({"status": "created", "name": project_name, "id": 1}),
        mimetype='application/json'
    )


@app.route('/projects/upload-example/', methods=['GET', 'POST'])
def upload_example_using_config():
    """
    Upload example endpoint - processes label_config and returns sample task data.
    """
    if request.method == 'GET':
        return UPLOAD_EXAMPLE_PAGE
    
    config = request.form.get('label_config', '')
    
    if not config:
        return Response(
            json.dumps({"error": "label_config is required"}),
            status=400,
            mimetype='application/json'
        )
    
    task_data = parse_label_config(config)
    
    response_json = json.dumps(task_data)
    
    xss_result = check_xss_in_response(response_json, flags[0])
    if xss_result:
        task_data['_flag'] = xss_result
        response_json = json.dumps(task_data)
    
    return Response(response_json, mimetype='application/json')


@app.route('/api/projects/', methods=['GET'])
def api_projects():
    return Response(
        json.dumps([
            {"id": 1, "title": "Text Classification", "task_count": 150},
            {"id": 2, "title": "Image Labeling", "task_count": 89},
            {"id": 3, "title": "NER Annotation", "task_count": 243}
        ]),
        mimetype='application/json'
    )


@app.route('/api/projects/<int:project_id>/', methods=['GET'])
def api_project_detail(project_id):
    return Response(
        json.dumps({
            "id": project_id,
            "title": "Sample Project",
            "description": "A sample labeling project",
            "task_count": 100,
            "label_config": "<View><Text name=\"text\" value=\"$text\"/></View>"
        }),
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run(debug=False)
