# encoding=utf8
# ShopWave CMS - Content Management System
# Product Description Editor with HTML Sanitization

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

def is_clean_html(html_input):
    """
    Validates HTML input by checking for dangerous event handlers.
    Based on PrestaShop-style validation - blocks specific known event attributes.
    Note: This mimics the vulnerable pattern from CVE where only specific event 
    handlers are enumerated rather than generically blocking all 'on*' attributes.
    """
    # Enumerated list of dangerous event handlers (like the vulnerable PrestaShop pattern)
    # This list is incomplete - it doesn't catch ALL event handlers starting with 'on'
    blocked_events = [
        'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover',
        'onmousemove', 'onmouseout', 'onkeydown', 'onkeypress', 'onkeyup',
        'onload', 'onunload', 'onerror', 'onsubmit', 'onreset', 'onselect',
        'onchange', 'onblur', 'onabort', 'onresize', 'onscroll'
    ]
    
    # Also block dangerous tags
    blocked_tags = ['script', 'iframe', 'object', 'embed', 'applet', 'form', 'base', 'svg']
    
    html_lower = html_input.lower()
    
    # Check for blocked tags
    for tag in blocked_tags:
        if '<' + tag in html_lower or '</' + tag in html_lower:
            return False, tag
    
    # Check for blocked event handlers (enumerated list - the vulnerability)
    for event in blocked_events:
        if event in html_lower:
            return False, event
    
    return True, None

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
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

    if msg == "":
        data = '<div class="result-panel"><div class="preview-info">Enter product description HTML above and click Preview to see the rendered output.</div></div>'
    else:
        if result == 'XSS':
            data = '<div class="result-panel success"><div class="preview-info">Security Alert! XSS Detected.<br>Admin Token: {0}</div></div>'.format(flag)
        elif result:
            data = '<div class="result-panel warning"><div class="preview-info">Alert triggered with content: {0}<br>Expected: XSS</div></div>'.format(cgi.escape(result))
        else:
            data = '<div class="result-panel"><div class="preview-info">Preview rendered successfully. No script execution detected.</div></div>'
    return data

############## Product Description Preview ####################

@app.route('/admin/product/preview')
def product_preview():
    """
    Product description preview endpoint.
    Uses is_clean_html() to sanitize user-provided HTML before rendering.
    """
    description = request.args.get('description', '')
    
    if description == "":
        value = ""
    else:
        # Validate HTML using our sanitization function
        is_valid, blocked_item = is_clean_html(description)
        
        if not is_valid:
            error_msg = """<div class="result-panel error"><div class="preview-info">HTML Validation Error: Blocked element detected: '%s'<br>This content is not allowed for security reasons.</div></div>""" % blocked_item
            return PREVIEW_CONTENT.format("Product Preview", "", "", error_msg)
        
        value = description

    preview_html = PREVIEW_CONTENT.format("Product Preview", value, "", "")
    result = check_xss(preview_html, flags[0], description, 'xss_medium')

    response = make_response(PREVIEW_CONTENT.format("Product Preview", value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/api/validate', methods=['POST'])
def api_validate():
    """
    API endpoint for validating HTML content.
    Returns JSON response indicating if content passes sanitization.
    """
    content = request.form.get('content', '')
    is_valid, blocked_item = is_clean_html(content)
    
    if is_valid:
        return '{"valid": true, "message": "Content passed validation"}'
    else:
        return '{"valid": false, "message": "Blocked: %s", "blocked_element": "%s"}' % (blocked_item, blocked_item)

if __name__ == '__main__':
    app.run(debug=True)
