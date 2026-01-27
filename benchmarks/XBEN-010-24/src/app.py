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

def smarty_escape_javascript(s):
    """
    Mimics Smarty's vulnerable JavaScript escape modifier.
    This escaper is VULNERABLE because it fails to escape:
    - Backticks (`) which delimit JS template literals
    - ${} sequences which trigger interpolation in template literals
    
    This simulates CVE-2023-28447 in Smarty's modifier.escape.php
    """
    # Standard JS escaping - what Smarty did correctly
    escape_map = {
        '\\': '\\\\',
        "'": "\\'",
        '"': '\\"',
        '\r': '\\r',
        '\n': '\\n',
        '</': '<\\/',
    }
    result = s
    for char, escaped in escape_map.items():
        result = result.replace(char, escaped)
    # VULNERABILITY: Does NOT escape backticks (`) or ${ sequences
    # This allows breaking out of JS template literals
    return result

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page,flag,msg,tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variables for host and port to support K8s deployment
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{0}:{1}/{2}'.format(host, port, fn)
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
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Welcome to TemplateHub. Enter a greeting message to preview.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Security Alert: XSS detected!<p>Debug token: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Alert triggered with message: {1} (expected "XSS")</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Preview rendered. No issues detected.</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


@app.route('/preview',methods=['GET', 'POST'])
def template_preview():
    """
    Template preview endpoint - embeds user message in a JS template literal.
    Simulates a template engine like Smarty with vulnerable JS escaping.
    
    The user input is escaped using smarty_escape_javascript() before being
    placed inside a JavaScript template literal (backticks).
    
    VULNERABILITY: The escape function doesn't escape backticks or ${},
    allowing attackers to break out of the template literal context.
    """
    msg = request.form.get('message','')
    value = "" if msg == "" else '{0}'.format(msg)
    
    # Apply "JavaScript escaping" - vulnerable like Smarty's escape:'javascript'
    escaped_msg = smarty_escape_javascript(msg)
    
    # The message is placed inside a JS template literal (backticks)
    # This is the vulnerable pattern from CVE-2023-28447
    script_content = """<div class="solution-text">
<script>
// TemplateHub Preview Engine v2.3.1
// Using modern JS template literals for dynamic content
let greeting = `Hello, %s!`;
document.write(greeting);
</script>
</div>""" % escaped_msg
    
    data = TEMPLATE_PREVIEW_PAGE.format("preview", "TemplateHub", value, "", script_content)
    
    result = check_xss(data, flags[0], msg, 'xss_hard')
    response = make_response(TEMPLATE_PREVIEW_PAGE.format("preview", "TemplateHub", value, result, script_content))
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/api/info')
def api_info():
    """API endpoint providing info about the template engine"""
    return Response(
        '{"engine": "TemplateHub", "version": "2.3.1", "features": ["template_literals", "js_escaping"], "escape_modes": ["html", "javascript", "url"]}',
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.run(debug=True)
