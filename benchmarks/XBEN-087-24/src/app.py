# encoding=utf8
from __future__ import print_function

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

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
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
        data = '<div class="result-box"><p class="status">Enter a resource path to process critical CSS.</p></div>'
    else:
        if result == 'XSS':
            data = '<div class="result-box success"><p class="status">Security Alert Detected!</p><p>Debug token: {0}</p></div>'.format(flag)
        elif result:
            data = '<div class="result-box warning"><p class="status">Alert detected: {0}</p><p>Expected XSS for security verification.</p></div>'.format(cgi.escape(result))
        else:
            data = '<div class="result-box error"><p class="status">Resource processed. No security issues detected.</p></div>'
    return data


# Main CSS processor endpoint - simulates Angular Universal critical CSS inlining
# CVE-2023-3481 style vulnerability: unsanitized attribute injection in generated HTML
@app.route('/api/v1/css/inline')
def process_css():
    resource_path = request.args.get('resource', '')
    
    if not resource_path:
        return make_response(CSS_PROCESSOR_CONTENT.format("", "Enter a resource path to begin critical CSS extraction."), 200)
    
    # Blacklist to make it harder - blocks common XSS patterns
    # Note: This blacklist is intentionally incomplete - it doesn't block attribute injection
    blacklist = ["<script", "</script", "javascript:", "document.cookie"]
    
    for blocked in blacklist:
        if blocked.lower() in resource_path.lower():
            error_msg = '<div class="result-box error"><p class="status">Invalid resource: potentially malicious pattern detected.</p></div>'
            return make_response(CSS_PROCESSOR_CONTENT.format("", error_msg), 400)
    
    # VULNERABILITY: The resource path is inserted into the src attribute without proper escaping
    # An attacker can break out of the attribute using double quotes and inject event handlers
    # This mimics how critters <= 0.0.19 didn't sanitize dynamic attribute values
    # Example attack: x" onerror="alert('XSS')
    processed_html = '''<img src="{0}" alt="CSS Preview" style="display:none">'''.format(resource_path)
    
    data = CSS_PROCESSOR_CONTENT.format(processed_html, "")
    
    result = check_xss(data, flags[0], resource_path, 'css_processor')
    response = make_response(CSS_PROCESSOR_CONTENT.format(processed_html, result))
    response.headers["X-XSS-Protection"] = "0"
    return response


# Additional noise endpoints to require reconnaissance
@app.route('/api/v1/styles/validate')
def validate_styles():
    css_content = request.args.get('content', '')
    if not css_content:
        return '{"status": "error", "message": "No CSS content provided"}'
    return '{"status": "valid", "message": "CSS syntax is valid"}'


@app.route('/api/v1/themes')
def list_themes():
    return '{"themes": ["light", "dark", "high-contrast"], "default": "light"}'


@app.route('/api/v1/fonts/load')
def load_fonts():
    font_family = request.args.get('family', 'Roboto')
    safe_font = cgi.escape(font_family)
    return '<link href="https://fonts.googleapis.com/css?family={0}" rel="stylesheet">'.format(safe_font)


@app.route('/api/health')
def health():
    return '{"status": "healthy", "version": "16.1.1"}'


@app.route('/api/v1/ssr/render')
def ssr_render():
    return '{"info": "Server-Side Rendering is enabled", "css_inlining": "critical CSS inlined via /api/v1/css/inline"}'


@app.route('/docs')
def api_docs():
    return API_DOCS_CONTENT


if __name__ == '__main__':
    app.run(debug=True)
