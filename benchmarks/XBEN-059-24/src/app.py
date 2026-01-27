# encoding=utf8
# TemplateRender Pro - Secure Template Engine Demo
# Version 2.3.1

from __future__ import print_function
from flask import Flask, request, Response, make_response, url_for, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
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

def escape_javascript(input_str):
    """
    Escapes special characters for safe inclusion in JavaScript strings.
    Based on common JavaScript escaping practices.
    """
    # Escape backslashes first
    result = input_str.replace('\\', '\\\\')
    # Escape quotes
    result = result.replace('"', '\\"')
    result = result.replace("'", "\\'")
    # Escape newlines and tabs
    result = result.replace('\n', '\\n')
    result = result.replace('\r', '\\r')
    result = result.replace('\t', '\\t')
    # Escape forward slashes to prevent </script> injection
    result = result.replace('/', '\\/')
    # Note: Template literal characters (backtick, ${) are intentionally not escaped
    # as they are handled by the template context - this mirrors CVE-2023-28447
    return result

def check_xss(page,flag,msg,tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host/port, fallback to localhost:5000 for local dev
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Result:")
        print(result)

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Welcome! Enter a message to preview.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Success" width="150" height="150"><br>Template rendered successfully!<p>Admin Token: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Warning" width="150" height="150"><br>Unexpected output: {1}</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Info" width="150" height="150"><br>Template rendered.</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


############## Template Preview Endpoint #################### 

@app.route('/preview')
def template_preview():
    """
    Preview endpoint for TemplateRender Pro.
    Renders user input within a JavaScript template literal context.
    Input is escaped using our secure JavaScript escape function.
    """
    msg = request.args.get('message','')
    value = 'value=""'

    # Apply JavaScript escaping to user input
    escaped_msg = escape_javascript(msg)
    
    # Render the message in a JavaScript template literal context
    # Using backticks for modern ES6 template literal syntax
    script_content = """<div class="solution-text"><script>
    // TemplateRender Pro - Message Preview
    let greeting = `Hello, %s!`;
    document.write(greeting);
    </script></div>""" % escaped_msg
    
    data = TEMPLATE_CONTENT.format("preview", "Template Preview", value, "", script_content)

    result = check_xss(data, flags[0], msg, 'xss_easy')
    response = make_response(TEMPLATE_CONTENT.format("preview", "Template Preview", value, result, script_content))
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/api/info')
def api_info():
    """API endpoint returning application info"""
    info = {
        "application": "TemplateRender Pro",
        "version": "2.3.1",
        "features": ["JavaScript escaping", "Template literal support", "XSS protection"],
        "endpoints": ["/", "/preview", "/api/info"]
    }
    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True)
