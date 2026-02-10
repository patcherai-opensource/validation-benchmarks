# encoding=utf8

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

def check_xss(page, flag, msg, tag):
    """Check if XSS payload triggers alert('XSS') using PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variables for host and port to support K8s deployment
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{0}:{1}/{2}'.format(host, port, fn)
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


def parse_label_config(config_str):
    """
    Parse a label configuration XML string and extract sample task data.
    This mimics Label Studio's upload_example_using_config functionality.
    
    VULNERABLE: The value attribute content is extracted and included in the
    response without HTML encoding, allowing XSS payloads to be reflected.
    
    In the real CVE, the label_config could contain values like:
    <Text name="text" value="$text<script>alert(1)</script>foo"/>
    
    The XML parser will decode HTML entities, so:
    - Input: value="$text&lt;script&gt;alert(1)&lt;/script&gt;"
    - Parsed: value="$text<script>alert(1)</script>"
    - This is then included in the JSON response and rendered unsafely.
    """
    task_data = {}
    
    try:
        # Parse the XML configuration
        root = ET.fromstring(config_str)
        
        # Extract all text content and attributes from the XML
        for elem in root.iter():
            # Get attributes
            value_attr = elem.get('value', '')
            name_attr = elem.get('name', '')
            
            if value_attr:
                # VULNERABLE: Value is included directly without sanitization
                # The XML parser decodes HTML entities like &lt; to <
                # If the frontend renders this without escaping, XSS occurs
                
                # Extract the actual value (for variable refs like $text, use the rest)
                if value_attr.startswith('$'):
                    # This is a variable reference, extract any suffix after the variable name
                    # e.g., "$text<script>..." -> variable is "text", extra content is "<script>..."
                    parts = value_attr[1:].split('<', 1)  # Split at first <
                    var_name = parts[0].strip()
                    if len(parts) > 1:
                        # There's extra content after the variable name (potential XSS payload)
                        extra_content = '<' + parts[1]
                        task_data[var_name] = "Sample " + var_name + extra_content
                    else:
                        task_data[var_name] = "Sample data for " + var_name
                else:
                    # Direct value (VULNERABLE - no escaping)
                    key = name_attr if name_attr else 'data'
                    task_data[key] = value_attr
            
            # Also include element text content
            if elem.text and elem.text.strip():
                key = name_attr if name_attr else elem.tag
                task_data[key + '_text'] = elem.text.strip()
                
    except ET.ParseError as e:
        task_data['error'] = 'Invalid XML configuration: ' + str(e)
    
    return task_data


@app.route('/projects/upload-example/', methods=['GET', 'POST'])
def upload_example_using_config():
    """
    Endpoint that simulates Label Studio's upload-example functionality.
    
    VULNERABILITY: CVE-like reflected XSS (similar to CVE in HumanSignal/label-studio)
    - Source: label_config POST parameter
    - Sink: JSON data rendered via innerHTML without escaping
    
    The label_config parameter is parsed as XML and values are extracted.
    The XML parser decodes HTML entities, so &lt;script&gt; becomes <script>.
    This is then serialized to JSON and the frontend renders it with innerHTML,
    causing the script to execute.
    
    Exploit: 
    <View><Text name="text" value="$text&lt;script&gt;alert('XSS')&lt;/script&gt;"/></View>
    
    Or directly:
    <View><Text name="xss" value="&lt;script&gt;alert('XSS')&lt;/script&gt;"/></View>
    """
    if request.method == 'GET':
        # Show the upload form
        return UPLOAD_EXAMPLE_FORM
    
    # Get the label_config from POST data
    config = request.form.get('label_config', '')
    
    if not config:
        return make_response(json.dumps({'error': 'label_config parameter is required'}), 400)
    
    # Parse the configuration and extract task data
    # VULNERABLE: Values from XML are not sanitized before being included in response
    task_data = parse_label_config(config)
    
    # Serialize to JSON
    response_data = json.dumps(task_data)
    
    # Create an HTML page that renders the JSON data unsafely
    # This simulates a frontend that renders the response without proper escaping
    html_response = UPLOAD_EXAMPLE_RESULT.format(response_data, cgi.escape(config))
    
    # Check if XSS was triggered
    result = check_xss(html_response, flags[0], config, 'xss_hard')
    
    if result == 'XSS':
        # XSS successful - return the flag
        success_html = UPLOAD_EXAMPLE_SUCCESS.format(flags[0], cgi.escape(response_data))
        response = make_response(success_html)
    else:
        # Return the vulnerable page
        response = make_response(html_response)
    
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


# Keep the original /page endpoint for backward compatibility
@app.route('/page', methods=['GET', 'POST'])
def xss32():
    """Original endpoint - redirects to new vulnerability"""
    return '''
    <html>
    <head><title>Label Studio - Upload Example</title></head>
    <body style="background: #1a1a2e; color: #eee; font-family: Arial;">
    <div style="max-width: 600px; margin: 50px auto; text-align: center;">
    <h1>This endpoint has been updated</h1>
    <p>Please use the <a href="/projects/upload-example/" style="color: #00d4ff;">upload example endpoint</a> instead.</p>
    </div>
    </body>
    </html>
    '''


if __name__ == '__main__':
    app.run(debug=True)
