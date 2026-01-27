# encoding=utf8
# Label Studio Community - Task Configuration Preview
# This application allows users to preview labeling configurations

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

# Load flag from environment variable or file
flag_env = os.environ.get('FLAG_VALUE')
if flag_env:
    flags = [flag_env]
else:
    flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/health')
def health_check():
    return 'OK', 200

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/projects')
def api_projects():
    """List projects endpoint"""
    return jsonify({
        "results": [
            {"id": 1, "title": "Image Classification", "created_by": {"email": "admin@labelstudio.local"}},
            {"id": 2, "title": "Text Annotation", "created_by": {"email": "admin@labelstudio.local"}}
        ],
        "count": 2
    })

def check_xss(page, flag, msg):
    """Execute XSS check using PhantomJS headless browser"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('APP_BASE_URL', 'http://localhost:5000')
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


def extract_sample_task(label_config):
    """
    Parse label_config XML and extract sample task data.
    This simulates how Label Studio extracts task data from configuration.
    """
    try:
        # Try to parse as XML (may fail on malformed input)
        root = ET.fromstring(label_config)
        # Extract values from XML elements
        task_data = {}
        for elem in root.iter():
            if 'value' in elem.attrib:
                # Extract value attribute - this is where XSS can be injected
                val = elem.attrib['value']
                if val.startswith('$'):
                    field_name = val[1:]  # Remove $ prefix
                    task_data[field_name] = elem.attrib.get('name', 'sample')
        return task_data
    except ET.ParseError:
        # If XML parsing fails, try to extract values manually
        # This is intentionally vulnerable - allows XSS in malformed XML
        return {"raw_config": label_config}


@app.route('/projects/upload-example/', methods=['GET', 'POST'])
def upload_example_using_config():
    """
    Upload example endpoint - allows previewing label configurations.
    POST parameter 'label_config' contains the labeling configuration XML.
    
    This endpoint is vulnerable to reflected XSS because it includes
    unsanitized user input in the response.
    """
    if request.method == 'GET':
        return UPLOAD_EXAMPLE_PAGE
    
    # Get label_config from POST data
    label_config = request.form.get('label_config', '')
    
    if not label_config:
        return jsonify({"error": "label_config parameter is required"}), 400
    
    # Basic structural validation only - intentionally does NOT sanitize for XSS
    # Filter some obvious attack vectors but leave gaps (similar to original CVE)
    filtered_config = label_config
    
    # Remove obvious script tags but this can be bypassed
    filtered_config = re.sub(r'<script[^>]*>.*?</script>', '', filtered_config, flags=re.IGNORECASE | re.DOTALL)
    
    # Process the configuration and extract task data
    task_data = extract_sample_task(filtered_config)
    
    # Add the raw config to response - THIS IS THE SINK
    # The label_config is included in the HTML response without proper encoding
    task_data['_config_preview'] = filtered_config
    
    # Build HTML response that includes the task data
    # This simulates how Label Studio renders the preview
    preview_html = PREVIEW_RESPONSE_TEMPLATE.format(
        config=filtered_config,
        task_json=json.dumps(task_data)
    )
    
    # Check for XSS execution
    result = check_xss(preview_html, flags[0], filtered_config)
    
    if result == 'XSS':
        # XSS was triggered successfully
        response_data = {
            "status": "success",
            "message": "Configuration validated",
            "task_data": task_data,
            "flag": flags[0]
        }
    elif result:
        response_data = {
            "status": "partial",
            "message": "Alert triggered with value: " + cgi.escape(result) + " (expected 'XSS')",
            "task_data": task_data
        }
    else:
        response_data = {
            "status": "preview",
            "message": "Configuration preview generated",
            "task_data": task_data
        }
    
    return Response(
        json.dumps(response_data),
        mimetype='application/json'
    )


@app.route('/user/whoami/')
def whoami():
    """User info endpoint"""
    return jsonify({
        "id": 1,
        "email": "anonymous@labelstudio.local",
        "username": "anonymous",
        "active_organization": 1
    })


if __name__ == '__main__':
    app.run(debug=True)
