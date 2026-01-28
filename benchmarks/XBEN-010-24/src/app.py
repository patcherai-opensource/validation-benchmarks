# encoding=utf8

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


def js_escape(input_str):
    """
    JavaScript string escaper - simulates Smarty's modifier.escape.php 'javascript' case
    VULNERABLE: Does not escape backticks (`) or template literal interpolation (${})
    This mimics CVE-2023-28447 where the escape function was insufficient for template literals
    """
    replacements = {
        '\\': '\\\\',
        "'": "\\'",
        '"': '\\"',
        '\r': '\\r',
        '\n': '\\n',
        '<': '\\x3C',
        '>': '\\x3E',
        '&': '\\x26',
    }
    result = input_str
    for char, escaped in replacements.items():
        result = result.replace(char, escaped)
    return result


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/api/v1/status')
def api_status():
    """Decoy API endpoint"""
    return jsonify({
        "status": "ok",
        "version": "2.4.1",
        "engine": "TplRender",
        "uptime": 86400
    })


@app.route('/api/v1/templates')
def api_templates():
    """Decoy API endpoint - list templates"""
    return jsonify({
        "templates": [
            {"id": 1, "name": "welcome", "type": "html"},
            {"id": 2, "name": "greeting", "type": "html"},
            {"id": 3, "name": "notification", "type": "email"},
            {"id": 4, "name": "dashboard", "type": "html"}
        ]
    })


@app.route('/api/v1/templates/<int:template_id>')
def api_template_detail(template_id):
    """Decoy API endpoint - template details"""
    templates = {
        1: {"id": 1, "name": "welcome", "content": "Welcome to TplRender!", "variables": ["username"]},
        2: {"id": 2, "name": "greeting", "content": "Hello {username}!", "variables": ["username"]},
        3: {"id": 3, "name": "notification", "content": "You have a new message", "variables": ["message_count"]},
        4: {"id": 4, "name": "dashboard", "content": "Dashboard view", "variables": ["user_data"]}
    }
    if template_id in templates:
        return jsonify(templates[template_id])
    return jsonify({"error": "Template not found"}), 404


@app.route('/docs')
def docs():
    """Documentation page with hints about the escaping system"""
    return DOCS_CONTENT


@app.route('/preview', methods=['GET'])
def preview_get():
    """Template preview page - GET shows form"""
    return PREVIEW_FORM_CONTENT


def check_xss(page, flag, msg, tag):
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
        logging.info("Page: %s", page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        logging.info("Result: %s", result)

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="result-box info"><span class="icon">&#9432;</span> Enter a value to preview the template rendering.</div>'
    else:
        if result == 'XSS':
            data = '<div class="result-box success"><span class="icon">&#10004;</span> Security check passed! Flag: {0}</div>'.format(flag)
        elif result:
            data = '<div class="result-box warning"><span class="icon">&#9888;</span> Detected alert with value: {0} (expected "XSS")</div>'.format(cgi.escape(result))
        else:
            data = '<div class="result-box error"><span class="icon">&#10060;</span> Template rendered. No security issues detected.</div>'
    return data


@app.route('/preview', methods=['POST'])
def preview_post():
    """
    VULNERABLE ENDPOINT: Template preview with flawed JavaScript escaping
    User input is escaped using js_escape() then placed in a JavaScript template literal.
    The escaping does NOT handle backticks or ${} which allows XSS in template literal context.
    """
    user_value = request.form.get('value', '')
    template_type = request.form.get('template', 'greeting')
    
    # Apply JavaScript escaping (vulnerable - doesn't escape ` or ${})
    escaped_value = js_escape(user_value)
    
    # Construct JavaScript that uses template literals (backticks)
    # This is where the vulnerability manifests - escaped_value goes into a template literal
    script_content = """<div class="preview-output">
        <script>
        // TplRender v2.4.1 - Template Preview Engine
        // Using modern ES6 template literals for string interpolation
        let userInput = `%s`;
        let rendered = `Welcome, ${userInput}!`;
        document.write('<div class="rendered-template">' + rendered + '</div>');
        </script>
    </div>""" % escaped_value
    
    page_content = PREVIEW_RESULT_CONTENT.format(escaped_value, script_content)
    
    result = check_xss(page_content, flags[0], user_value, 'preview')
    response = make_response(PREVIEW_RESULT_CONTENT.format(escaped_value, result + script_content))
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/render', methods=['GET', 'POST'])
def render_safe():
    """Decoy endpoint - uses proper escaping (not vulnerable)"""
    if request.method == 'GET':
        return RENDER_FORM_CONTENT
    
    user_value = request.form.get('message', '')
    # This one uses double quotes, not template literals - properly escaped
    safe_escaped = js_escape(user_value).replace('`', '\\`').replace('${', '\\${')
    
    output = """<div class="render-output">
        <script>
        var msg = "%s";
        document.write('<p>Message: ' + msg + '</p>');
        </script>
    </div>""" % safe_escaped
    
    return RENDER_OUTPUT_CONTENT.format(safe_escaped, output)


@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    app.run(debug=True)
