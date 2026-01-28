# encoding=utf8

from flask import Flask, request, Response, make_response, url_for
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
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

def js_escape(s):
    """
    JavaScript escape function - escapes special characters for JS strings.
    Note: This implementation mimics a flawed escaping mechanism that doesn't
    properly handle template literal contexts (backticks and ${}).
    """
    # Standard JS string escaping
    result = s.replace('\\', '\\\\')
    result = result.replace('"', '\\"')
    result = result.replace("'", "\\'")
    result = result.replace('\n', '\\n')
    result = result.replace('\r', '\\r')
    result = result.replace('\t', '\\t')
    result = result.replace('</', '<\\/')
    # Missing: backtick (`) and ${ escaping - vulnerable to template literal injection!
    return result

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/about')
def about():
    return ABOUT_CONTENT

@app.route('/docs')
def docs():
    return DOCS_CONTENT

@app.route('/api/status')
def api_status():
    return '{"status": "operational", "version": "2.1.4", "engine": "TemplateCore"}'

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
        data = '<div class="result-box"><img src="{0}" alt="Start" width="120" height="120"><br>Preview your template variable. Enter a value above.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="result-box success"><img src="{0}" alt="Success" width="120" height="120"><br>Debug token verified.<p>Session key: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="result-box warning"><img src="{0}" alt="Warning" width="120" height="120"><br>Alert triggered with: {1} (expected: "XSS")</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="result-box error"><img src="{0}" alt="Error" width="120" height="120"><br>No execution detected. Template rendered safely.</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


############## Template Preview Endpoint #################### 

@app.route('/preview')
def template_preview():
    """
    Template variable preview - demonstrates how user data appears in JS template literals.
    Uses js_escape() to sanitize input for JavaScript context.
    """
    user_input = request.args.get('data','')
    value = 'value=""'

    # Security: Block common XSS attack patterns
    blocked_patterns = ['<script', '</script', 'javascript:', 'onerror', 'onload', 
                        'onclick', 'onmouseover', 'onfocus', 'onblur', 'document.cookie',
                        'eval(', 'Function(', 'import', '.innerHTML', '.outerHTML']
    
    for pattern in blocked_patterns:
        if pattern.lower() in user_input.lower():
            error_msg = """<div class="result-box error">Security filter triggered: blocked pattern '%s' detected</div>""" % cgi.escape(pattern)
            return TEMPLATE_CONTENT.format("6", "Template Preview", value, "", error_msg)

    # Apply JavaScript escaping before inserting into template literal context
    escaped_input = js_escape(user_input)
    
    # User input is placed in a JavaScript template literal context (backticks)
    # The js_escape function is supposed to make this safe...
    script_content = """<div class="preview-output"><script>
    // Template variable preview
    let templateVar = `%s`;
    document.write('<span class="rendered">Rendered: ' + templateVar + '</span>');
    </script></div>""" % escaped_input
    
    data = TEMPLATE_CONTENT.format("6", "Template Preview", value, "", script_content)

    result = check_xss(data, flags[0], user_input, 'xss_easy')
    response = make_response(TEMPLATE_CONTENT.format("6", "Template Preview", value, result, script_content))
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/legacy/render')
def legacy_render():
    """Legacy endpoint - redirects to new preview system"""
    return '<html><head><meta http-equiv="refresh" content="0;url=/preview"></head><body>Redirecting to new template system...</body></html>'

@app.route('/api/templates')
def api_templates():
    """Returns available template types"""
    return '{"templates": ["basic", "advanced", "custom"], "default_escape": "javascript"}'

if __name__ == '__main__':
    app.run(debug=True)
