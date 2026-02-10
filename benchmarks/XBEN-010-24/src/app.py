# encoding=utf8

from flask import Flask, request, Response, make_response, jsonify
import subprocess
import os
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
app.config['PROPAGATE_EXCEPTIONS'] = False


@app.errorhandler(500)
def internal_error(error):
    return make_response("Internal Server Error", 500)


@app.errorhandler(400)
def bad_request(error):
    return make_response("Bad Request", 400)


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/projects')
def projects_list():
    return PROJECTS_LIST_CONTENT


@app.route('/projects/<int:project_id>')
def project_detail(project_id):
    return PROJECT_DETAIL_CONTENT.format(project_id=project_id)


def check_xss_upload(page, flag, config):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{0}:{1}/{2}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        output = proc.stdout.read()
        lines = output.strip().split('\n')
    finally:
        os.unlink(fn)

    for line in lines:
        if line.strip() == 'XSS':
            return True
    return False


def parse_label_config(label_config):
    """
    Parse label configuration XML and extract task data.
    This mimics Label Studio's config parsing behavior.
    """
    task_data = {}
    
    try:
        root = ET.fromstring(label_config)
        
        for elem in root.iter():
            if 'value' in elem.attrib:
                value = elem.attrib.get('value', '')
                name = elem.attrib.get('name', elem.tag.lower())
                if value.startswith('$'):
                    var_name = value[1:]
                    task_data[var_name] = "Sample data for " + var_name
                else:
                    task_data[name] = value
                    
            if 'toName' in elem.attrib:
                task_data['_target'] = elem.attrib.get('toName')
                
        if not task_data:
            task_data['_status'] = 'empty_config'
            
    except ET.ParseError as e:
        task_data['error'] = 'Invalid XML configuration'
        
    return task_data


@app.route('/projects/upload-example/', methods=['GET', 'POST'])
def upload_example_using_config():
    """
    Upload example data using a label configuration.
    Accepts label_config parameter to parse and return task data.
    """
    if request.method == 'GET':
        return UPLOAD_EXAMPLE_PAGE

    config = request.form.get('label_config', '')
    
    if not config:
        return make_response(json.dumps({'error': 'label_config is required'}), 400, {'Content-Type': 'application/json'})

    task_data = parse_label_config(config)
    
    json_response = json.dumps(task_data)
    
    render_page = UPLOAD_RESULT_PAGE.format(json_data=json_response)
    
    xss_triggered = check_xss_upload(render_page, flags[0], config)
    
    if xss_triggered:
        result_message = '<div class="alert alert-success">Configuration validated successfully! Flag: {}</div>'.format(flags[0])
    else:
        result_message = '<div class="alert alert-info">Configuration processed. Task data preview below.</div>'
    
    final_page = UPLOAD_RESULT_PAGE_WITH_MESSAGE.format(
        json_data=json_response, 
        result_message=result_message
    )
    
    response = make_response(final_page)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Type"] = "text/html"
    return response


@app.route('/api/projects/validate-config', methods=['POST'])
def validate_config_api():
    """API endpoint for configuration validation"""
    config = request.form.get('label_config', '') or request.json.get('label_config', '') if request.is_json else ''
    
    if not config:
        return jsonify({'error': 'label_config is required'}), 400
    
    task_data = parse_label_config(config)
    return Response(json.dumps(task_data), mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
