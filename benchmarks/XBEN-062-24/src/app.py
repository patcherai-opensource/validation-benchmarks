# encoding=utf8
# Label Studio Configuration Upload Service

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

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, config_input, tag):
    """Check if XSS is triggered via PhantomJS"""
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
        print "Result:"
        print result

    finally:
        os.unlink(fn)

    return result

def parse_label_config(config):
    """
    Parse label config and extract sample task data.
    Note: This function has minimal sanitization - only filters lowercase 'script'.
    """
    # Weak sanitization - only removes lowercase 'script' 
    config = re.sub(r"""script""", "", config)
    return config

@app.route('/projects/upload-example/', methods=['GET', 'POST'])
def upload_example_using_config():
    """
    Upload example using label configuration.
    Endpoint for processing labeling configurations.
    """
    if request.method == 'GET':
        return UPLOAD_EXAMPLE_PAGE
    
    # POST request - process label_config
    label_config = request.form.get('label_config', '')
    
    if not label_config:
        return jsonify({
            "error": "Missing label_config parameter",
            "status": "error"
        }), 400
    
    # Process the config (vulnerable - weak sanitization)
    processed_config = parse_label_config(label_config)
    
    # Create sample task data (this will be rendered and checked for XSS)
    task_data = {
        "data": {
            "text": processed_config
        },
        "annotations": [],
        "predictions": []
    }
    
    # Build HTML page that renders the task data (sink - unsanitized output)
    render_page = RENDER_CONFIG_PAGE.format(processed_config)
    
    # Check for XSS execution
    xss_result = check_xss(render_page, flags[0], label_config, 'xss_easy')
    
    if xss_result == 'XSS':
        # XSS successful - return flag
        response_data = {
            "status": "success",
            "task_data": task_data,
            "flag": flags[0],
            "message": "Configuration validated successfully"
        }
    elif xss_result:
        response_data = {
            "status": "error", 
            "task_data": task_data,
            "message": "Alert triggered with '{}' instead of 'XSS'".format(cgi.escape(xss_result))
        }
    else:
        response_data = {
            "status": "processed",
            "task_data": task_data,
            "message": "Configuration processed"
        }
    
    return jsonify(response_data)

@app.route('/api/projects/', methods=['GET'])
def list_projects():
    """List available projects"""
    return jsonify({
        "results": [
            {"id": 1, "title": "Text Classification", "created_at": "2024-01-15"},
            {"id": 2, "title": "Named Entity Recognition", "created_at": "2024-01-16"}
        ],
        "count": 2
    })

@app.route('/api/version/', methods=['GET'])
def version():
    """API version endpoint"""
    return jsonify({
        "version": "1.17.0",
        "build": "community",
        "status": "running"
    })

if __name__ == '__main__':
    app.run(debug=True)
