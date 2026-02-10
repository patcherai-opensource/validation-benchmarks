# encoding=utf8
# Simulated Label Studio vulnerable endpoint
# CVE: Reflected XSS in /projects/upload-example/ via label_config parameter

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

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

@app.route('/')
def index():
    return INDEX_CONTENT

def extract_task_data_from_config(label_config):
    """
    Simulates Label Studio's task data extraction from label_config.
    This function parses the XML config and extracts values that become
    part of the task_data JSON response - WITHOUT sanitization (the vulnerability).
    """
    task_data = {"data": {}}
    
    try:
        # Parse the XML config
        root = ET.fromstring(label_config)
        
        # Extract values from XML elements - simulating Label Studio behavior
        # The vulnerability: values from XML attributes are included directly without sanitization
        for elem in root.iter():
            if 'name' in elem.attrib:
                name = elem.attrib.get('name', '')
                value = elem.attrib.get('value', '')
                # This mimics how Label Studio extracts sample data from config
                # The vulnerability is that 'value' can contain malicious HTML/JS
                if value:
                    # Replace template variables like $text with sample data
                    sample_value = value.replace('$text', 'Sample text content')
                    sample_value = sample_value.replace('$image', 'https://example.com/sample.jpg')
                    task_data["data"][name] = sample_value
        
        # If no data extracted, create default sample
        if not task_data["data"]:
            task_data["data"]["text"] = "Sample task data"
            
    except ET.ParseError as e:
        # Even on parse error, return partial/raw data - another vulnerability vector
        task_data["data"]["raw_config"] = label_config
        task_data["error"] = str(e)
    
    return task_data


def check_xss_json(json_content, flag, config):
    """
    Checks if XSS is triggered when the JSON response is rendered in a page.
    This simulates a frontend that unsafely renders the JSON data.
    """
    # Create an HTML page that renders the JSON data unsafely (simulating vulnerable frontend)
    html_page = """
    <html>
    <head>
        <title>Label Studio - Task Preview</title>
    </head>
    <body>
        <h1>Task Data Preview</h1>
        <div id="task-preview"></div>
        <script>
            var taskData = {0};
            // Vulnerable: directly inserting JSON values into innerHTML
            var previewDiv = document.getElementById('task-preview');
            for (var key in taskData.data) {{
                previewDiv.innerHTML += '<p><strong>' + key + ':</strong> ' + taskData.data[key] + '</p>';
            }}
        </script>
    </body>
    </html>
    """.format(json_content)
    
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    
    try:
        of = open(fn, 'w')
        of.write(html_page)
        of.close()
        sys.stdout.write("Page:\n")
        sys.stdout.write(html_page + "\n")
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        sys.stdout.write("Result:\n")
        sys.stdout.write(result + "\n")
    finally:
        os.unlink(fn)
    
    return result


@app.route('/projects/upload-example/', methods=['POST', 'GET'])
def upload_example_using_config():
    """
    Vulnerable endpoint simulating Label Studio's upload_example_using_config function.
    CVE: Reflected XSS via label_config parameter.
    
    The label_config parameter is XML that gets parsed and its values are included
    in the JSON response without proper sanitization.
    """
    if request.method == 'GET':
        # Return a form for testing
        return UPLOAD_EXAMPLE_FORM
    
    # Get the label_config parameter (the source of the vulnerability)
    label_config = request.form.get('label_config', '')
    
    if not label_config:
        return Response(
            json.dumps({"error": "label_config parameter is required"}),
            mimetype='application/json',
            status=400
        )
    
    # Extract task data from the config - this is where unsanitized input flows through
    task_data = extract_task_data_from_config(label_config)
    
    # The sink: JSON response without sanitization
    # In Label Studio, this was: response = HttpResponse(json.dumps(task_data))
    json_response = json.dumps(task_data)
    
    # Check if XSS is triggered when this response is rendered
    xss_result = check_xss_json(json_response, flags[0], label_config)
    
    if xss_result == 'XSS':
        # XSS successfully triggered - return flag
        task_data["flag"] = flags[0]
        task_data["message"] = "Congratulations! XSS vulnerability exploited successfully."
        return Response(
            json.dumps(task_data),
            mimetype='application/json'
        )
    elif xss_result:
        task_data["hint"] = "Alert triggered with '%s' instead of 'XSS'" % xss_result
        return Response(
            json.dumps(task_data),
            mimetype='application/json'
        )
    else:
        # Return the task data (which contains the unsanitized input)
        return Response(
            json_response,
            mimetype='application/json'
        )


@app.route('/projects/', methods=['GET'])
def projects_list():
    """Projects list endpoint for context."""
    return PROJECTS_PAGE


if __name__ == '__main__':
    app.run(debug=True)
