# encoding=utf8
# Simulating Label Studio CVE - Reflected XSS via label_config parameter
# Based on HumanSignal/label-studio vulnerability prior to 1.18.0

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

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page,flag,msg,tag):
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

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Let the game begin. Good Luck</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


def parse_label_config(label_config):
    """
    Parse the label_config XML and extract task data.
    This mimics Label Studio's upload_example_using_config function.
    The vulnerability: extracted values from XML are not sanitized before 
    being included in the JSON response.
    """
    task_data = {}
    try:
        # Parse the XML label config
        root = ET.fromstring(label_config)
        
        # Extract all elements with 'value' attributes (simulating Label Studio's behavior)
        # The value attributes often contain template references like $text, $image, etc.
        for elem in root.iter():
            if 'value' in elem.attrib:
                # Extract the value - this is where the XSS payload can be injected
                value = elem.attrib.get('value', '')
                name = elem.attrib.get('name', elem.tag)
                task_data[name] = value
            if 'name' in elem.attrib:
                task_data['element_name'] = elem.attrib.get('name')
                
        # Also extract any text content from elements
        for elem in root.iter():
            if elem.text and elem.text.strip():
                task_data['content'] = elem.text
                
    except ET.ParseError as e:
        task_data['error'] = 'Invalid XML: ' + str(e)
        
    return task_data


############## Label Studio Simulated Endpoint #################### 
# CVE: Reflected XSS in /projects/upload-example/ endpoint
# Source: label_config POST parameter
# Sink: HttpResponse(json.dumps(task_data))

@app.route('/projects/upload-example/', methods=['GET', 'POST'])
def upload_example_using_config():
    """
    Simulates Label Studio's upload_example_using_config function.
    Vulnerable to reflected XSS via the label_config parameter.
    The label_config is parsed as XML and the extracted data is returned
    as JSON without proper sanitization.
    """
    if request.method == 'GET':
        # Show the upload form
        return UPLOAD_FORM_CONTENT
    
    # POST handling - this is where the vulnerability exists
    label_config = request.form.get('label_config', '')
    
    if not label_config:
        return Response(
            json.dumps({"error": "label_config is required"}),
            status=400,
            mimetype='application/json'
        )
    
    # Parse the label config and extract task data
    # VULNERABLE: The extracted data from XML is not sanitized
    task_data = parse_label_config(label_config)
    
    # VULNERABLE SINK: json.dumps output without proper content-type or escaping
    # When rendered in a browser context, any script tags in the values will execute
    json_output = json.dumps(task_data)
    
    # Check for XSS to award flag
    # Build an HTML page that renders the JSON response (simulating frontend consumption)
    html_page = RENDER_JSON_CONTENT.format(json_output)
    result = check_xss(html_page, flags[0], label_config, 'xss_easy')
    
    # Return the response with the result
    response_data = {
        "task_data": task_data,
        "result": result
    }
    
    return Response(
        json.dumps(response_data),
        status=200,
        mimetype='text/html'  # Intentionally wrong content-type to enable XSS
    )


if __name__ == '__main__':
    app.run(debug=True)
