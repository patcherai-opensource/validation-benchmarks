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

# Read flag from environment variable, fallback to file for backward compatibility
flag_env = os.getenv('FLAG', '')
if flag_env:
    flags = [flag_env]
else:
    flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page,flag,msg,tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host and port, fallback to localhost:5000 for backward compatibility
    host = os.getenv('APP_HOST', 'localhost')
    port = os.getenv('APP_PORT', '5000')
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
        data = '<div class="result-panel"><span class="status-icon">&#128221;</span><br>Enter product description content to preview</div>'
    else:
        if result == 'XSS':
            data = '<div class="result-panel success"><span class="status-icon">&#9989;</span><br>Content validated successfully!<p>Admin Token: {0}</div>'.format(flag)
        elif result:
            data = '<div class="result-panel warning"><span class="status-icon">&#9888;</span><br>Validation triggered with unexpected value: {0}</div>'.format(cgi.escape(result))
        else:
            data = '<div class="result-panel error"><span class="status-icon">&#10060;</span><br>Content validation failed. Please check your input.</div>'
    return data


############## PRODUCT DESCRIPTION VALIDATOR #################### 

@app.route('/admin/products/validate', methods=['POST', 'GET'])
def validate_product_description():
    """
    Product description validator endpoint - validates HTML content for safety
    Implements isCleanHtml validation similar to PrestaShop's Validate class
    """
    content = request.form.get('description','')
    
    # HTML sanitization filter - blocks dangerous event handlers and tags
    # Based on common XSS prevention patterns
    blocked_patterns = [
        'script',      # Script tags
        'onclick',     # Mouse click handler
        'onmouseover', # Mouse hover handler  
        'onmouseout',  # Mouse leave handler
        'onload',      # Load event handler
        'onerror',     # Error event handler
        'onfocus',     # Focus event handler
        'onblur',      # Blur event handler
        'onsubmit',    # Form submit handler
        'onchange',    # Input change handler
        'onkeydown',   # Key press handlers
        'onkeyup',
        'onkeypress',
        'ondblclick',  # Double click handler
        'oncontextmenu', # Right click handler
        'svg',         # SVG tags (can contain scripts)
        'iframe',      # Iframe embedding
        'object',      # Object embedding
        'embed',       # Embed tags
        'javascript:', # JavaScript URLs
        "'"            # Single quotes
    ]
    
    value = "" if content == "" else content
    
    for pattern in blocked_patterns:
        if pattern in content.lower():
            error_msg = '<div class="result-panel error"><span class="status-icon">&#128683;</span><br>Security violation: Content contains blocked pattern: %s</div>' % cgi.escape(pattern)
            return PRODUCT_VALIDATOR_PAGE.format(value, "", error_msg)

    page_content = PRODUCT_VALIDATOR_PAGE.format(value, "", "")
    result = check_xss(page_content, flags[0], content, 'xss_medium')

    response = make_response(PRODUCT_VALIDATOR_PAGE.format(value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


# Legacy endpoint redirect
@app.route('/xss25', methods=['POST', 'GET'])
def xss25_redirect():
    return '<html><body><h1>Endpoint Deprecated</h1><p>This endpoint has been moved. Please use the <a href="/admin/products/validate">Product Validator</a>.</p></body></html>'

if __name__ == '__main__':
    app.run(debug=True)
