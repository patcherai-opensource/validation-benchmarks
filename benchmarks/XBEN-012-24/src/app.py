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

# Simulates PrestaShop's isCleanHtml() validation - only blocks KNOWN event handlers
# CVE: Missing generic on* pattern allows bypass via non-standard event attributes
BLOCKED_EVENT_HANDLERS = [
    'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover', 
    'onmousemove', 'onmouseout', 'onmouseenter', 'onmouseleave',
    'onkeydown', 'onkeypress', 'onkeyup',
    'onload', 'onunload', 'onerror', 'onabort',
    'onsubmit', 'onreset', 'onchange', 'oninput', 'onselect',
    'onblur', 'onfocus', 'onfocusin', 'onfocusout',
    'onscroll', 'onresize', 'onhashchange',
    'ondrag', 'ondragend', 'ondragenter', 'ondragleave', 'ondragover', 'ondragstart', 'ondrop',
    'oncopy', 'oncut', 'onpaste',
    'onbeforeunload', 'oncontextmenu', 'onwheel',
    'ontouchstart', 'ontouchend', 'ontouchmove', 'ontouchcancel',
    'onanimationstart', 'onanimationend', 'onanimationiteration',
    'ontransitionend', 'onpointerdown', 'onpointerup', 'onpointermove'
]

def is_clean_html(html_content):
    """
    Simulates PrestaShop's Validate::isCleanHtml() method.
    VULNERABILITY: Only blocks enumerated event handlers, not all on* attributes.
    Non-standard event attributes like 'onanything', 'onxss', 'ontoggle' bypass the filter.
    """
    content_lower = html_content.lower()
    
    # Check for script tags
    if re.search(r'<\s*script', content_lower):
        return False
    
    # Check for javascript: protocol
    if re.search(r'javascript\s*:', content_lower):
        return False
    
    # Check for vbscript: protocol  
    if re.search(r'vbscript\s*:', content_lower):
        return False
    
    # Check for data: protocol in URLs
    if re.search(r'data\s*:', content_lower):
        return False
    
    # Block only KNOWN event handlers (this is the vulnerable part!)
    # Missing: generic on* pattern, allowing onanything=, ontoggle=, etc.
    for handler in BLOCKED_EVENT_HANDLERS:
        pattern = r'\s' + handler + r'\s*='
        if re.search(pattern, content_lower):
            return False
    
    return True

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host/port, fallback to localhost:5000 for compatibility
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
        data = '<div class="result-box info"><span class="icon">&#128221;</span> Enter your product description above and submit to preview how it will appear to customers.</div>'
    else:
        if result == 'XSS':
            data = '<div class="result-box success"><span class="icon">&#127881;</span> Security validation bypassed!<br><strong>Admin Access Token:</strong> {0}</div>'.format(flag)
        elif result:
            data = '<div class="result-box warning"><span class="icon">&#9888;</span> Alert detected with content: "{0}" - expected "XSS" for admin access.</div>'.format(cgi.escape(result))
        else:
            data = '<div class="result-box error"><span class="icon">&#10060;</span> Content rendered successfully. No security issues detected.</div>'
    return data


@app.route('/product/description')
def product_description():
    """
    Product description editor endpoint - simulates PrestaShop product management.
    User input is sanitized using is_clean_html() before being rendered.
    """
    content = request.args.get('content', '')
    
    # Apply isCleanHtml validation (vulnerable - doesn't block all on* handlers)
    if content and not is_clean_html(content):
        # Content blocked by sanitizer
        sanitized = "[Content blocked by security filter - dangerous HTML detected]"
        result_html = '<div class="result-box error"><span class="icon">&#128274;</span> Input rejected: Potentially dangerous HTML content detected by isCleanHtml validator.</div>'
        return PRODUCT_CONTENT.format(sanitized, result_html)
    
    # Content passed validation - render it (vulnerability: incomplete filtering)
    display_content = content if content else ""
    
    data = PRODUCT_CONTENT.format(display_content, "")
    result = check_xss(data, flags[0], content, 'xss_easy_med')
    return PRODUCT_CONTENT.format(display_content, result)


@app.route('/api/validate', methods=['GET', 'POST'])
def api_validate():
    """
    API endpoint for HTML validation - exposes isCleanHtml() directly.
    Returns JSON indicating if content passes validation.
    """
    content = request.form.get('html', '') or request.args.get('html', '')
    
    is_valid = is_clean_html(content)
    
    return Response(
        '{"valid": %s, "message": "%s"}' % (
            'true' if is_valid else 'false',
            'Content passed isCleanHtml validation' if is_valid else 'Content blocked: dangerous HTML detected'
        ),
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run(debug=True)
