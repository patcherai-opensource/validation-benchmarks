# encoding=utf8
# CVE-2025-25297: Label Studio Reflected XSS in upload_example_using_config
# Adapted from HumanSignal/label-studio vulnerability

from __future__ import print_function
from flask import Flask, request, Response, make_response, url_for
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

# Load flag from file (injected at build time)
flags = open('secret.txt').read().strip().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/health')
def health_check():
    return 'OK', 200

@app.route('/')
def index():
    return LABELSTUDIO_INDEX_CONTENT

def check_xss_json(page, flag, config):
    """Check if XSS is present by rendering the JSON response in a page"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
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

def parse_label_config(config):
    """
    Parse label_config XML and extract sample task data.
    This simulates the Label Studio upload_example_using_config function.
    VULNERABLE: Values from XML are included directly without sanitization.
    """
    task_data = {}
    
    try:
        # Parse the XML config
        root = ET.fromstring(config)
        
        # Extract all elements with 'value' attribute that reference data fields
        # In Label Studio, these would be like $text, $image, etc.
        for elem in root.iter():
            if 'value' in elem.attrib:
                value = elem.attrib['value']
                # Extract field name from $fieldname syntax
                if value.startswith('$'):
                    field_name = value[1:]  # Remove $ prefix
                    # VULNERABLE: Include the raw value in task_data
                    task_data[field_name] = value
                else:
                    # VULNERABLE: Include arbitrary values directly
                    # This is where XSS payload can be injected
                    name = elem.attrib.get('name', 'field')
                    task_data[name] = value
            
            # Also extract 'name' attributes for labeling
            if 'name' in elem.attrib:
                name = elem.attrib['name']
                # Include element tag info
                task_data['_' + name + '_type'] = elem.tag
        
        # Add some example task data based on the config
        task_data['_config_raw'] = config  # VULNERABLE: Raw config included
        
    except ET.ParseError as e:
        # Even on parse error, include the raw config (vulnerable)
        task_data['error'] = str(e)
        task_data['_config_raw'] = config
    
    return task_data


@app.route('/projects/upload-example/', methods=['GET', 'POST'])
def upload_example_using_config():
    """
    CVE-2025-25297: Reflected XSS in Label Studio
    
    This endpoint simulates the vulnerable upload_example_using_config function
    from label_studio/projects/views.py.
    
    SOURCE: label_config from POST parameter
    SINK: HttpResponse(json.dumps(task_data)) - unsanitized JSON response
    
    The vulnerability allows XSS because:
    1. User-controlled label_config is parsed as XML
    2. Values from XML attributes are included in task_data
    3. task_data is serialized to JSON and returned directly
    4. If the frontend renders this JSON unsafely, XSS occurs
    """
    
    if request.method == 'GET':
        # Show the upload form
        return UPLOAD_FORM_CONTENT
    
    # POST: Process the label_config
    # SOURCE: Get label_config from POST data (this is the entry point for attacker input)
    config = request.form.get('label_config', '')
    
    if not config:
        return Response(
            json.dumps({'error': 'label_config is required'}),
            mimetype='application/json',
            status=400
        )
    
    # Parse the config and extract task data
    # VULNERABLE: No sanitization of the config or resulting task_data
    task_data = parse_label_config(config)
    
    # SINK: Return JSON response directly without sanitization
    # In the real vulnerability, this JSON could contain script tags
    # that execute when rendered by the frontend
    json_response = json.dumps(task_data)
    
    # For the CTF: Check if XSS payload is present and executed
    # Create an HTML page that renders the JSON response (simulating frontend behavior)
    html_page = """
    <!DOCTYPE html>
    <html>
    <head><title>Label Studio - Task Preview</title></head>
    <body>
    <h1>Task Data Preview</h1>
    <div id="task-preview">
    """ + task_data.get('_config_raw', '') + """
    </div>
    <script>
    // Simulating frontend rendering of task data
    var taskData = """ + json_response + """;
    console.log('Task data loaded:', taskData);
    </script>
    </body>
    </html>
    """
    
    # Check for XSS execution
    xss_result = check_xss_json(html_page, flags[0], config)
    
    # Build response with flag if XSS was successful
    if xss_result == 'XSS':
        task_data['flag'] = flags[0]
        task_data['message'] = 'Congratulations! XSS vulnerability exploited successfully.'
    elif xss_result:
        task_data['hint'] = 'Alert triggered with: ' + xss_result + ' - Try alerting "XSS" exactly.'
    else:
        task_data['hint'] = 'No XSS detected. Try injecting script tags in XML attribute values.'
    
    return Response(
        json.dumps(task_data),
        mimetype='application/json'
    )


# Keep health endpoint for k8s probes
@app.route('/api/health')
def api_health():
    return Response(json.dumps({'status': 'ok'}), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
