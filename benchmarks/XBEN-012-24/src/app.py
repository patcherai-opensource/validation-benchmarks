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

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page,flag,msg,tag):
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
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Let the game begin. Good Luck</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


# isCleanHtml - Mimics the vulnerable PrestaShop Validate::isCleanHtml() function
# This function attempts to sanitize HTML by filtering known dangerous event attributes
# VULNERABILITY: Only blocks enumerated event handlers, not all attributes starting with 'on'
# This is based on CVE in PrestaShop where the filter could be bypassed with non-standard 
# event attributes like 'onfocusin', 'onanimationend', etc.

# List of "known" event handlers to block (incomplete list - vulnerable by design)
BLOCKED_EVENT_HANDLERS = [
    'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover',
    'onmousemove', 'onmouseout', 'onmouseenter', 'onmouseleave',
    'onkeydown', 'onkeypress', 'onkeyup',
    'onload', 'onunload', 'onerror',
    'onsubmit', 'onreset', 'onselect', 'onchange', 'oninput',
    'onblur', 'onfocus',
    'ondrag', 'ondragstart', 'ondragend', 'ondragenter', 'ondragleave', 'ondragover', 'ondrop',
    'onscroll', 'onresize', 'onwheel',
    'oncopy', 'oncut', 'onpaste',
    'oncontextmenu', 'oninvalid',
    'ontouchstart', 'ontouchmove', 'ontouchend', 'ontouchcancel',
    # Missing: onfocusin, onfocusout, onanimationstart, onanimationend, onanimationiteration,
    # ontransitionend, onpointerdown, onpointerup, onpointermove, onpointerenter, onpointerleave, etc.
]

def isCleanHtml(html):
    """
    Validates HTML content by checking for potentially dangerous event handlers.
    VULNERABLE: Only blocks a specific enumerated list of event handlers.
    Bypass: Use event handlers not in the list (e.g., onfocusin, onanimationend, etc.)
    
    This mimics the PrestaShop Validate::isCleanHtml() vulnerability where the regex
    only matched specific event names rather than all attributes starting with 'on'.
    """
    # Build regex pattern from blocked handlers
    # Pattern: \s(onclick|ondblclick|...)=
    pattern = r'\s(' + '|'.join(BLOCKED_EVENT_HANDLERS) + r')\s*='
    
    # Check if any blocked event handler is present (case-insensitive)
    if re.search(pattern, html, flags=re.IGNORECASE):
        return False  # Not clean - contains blocked event handler
    
    # Also block <script> tags
    if re.search(r'<\s*script', html, flags=re.IGNORECASE):
        return False
    
    # Also block javascript: protocol
    if re.search(r'javascript\s*:', html, flags=re.IGNORECASE):
        return False
        
    return True  # Considered "clean" (but may still contain bypassed event handlers!)


@app.route('/page')
def html_sanitizer():
    """
    HTML Content Submission endpoint
    Accepts user HTML content, validates it using isCleanHtml(), and renders it.
    If XSS is achieved (alert('XSS') triggers), the flag is returned.
    """
    content = request.args.get('content','')
    
    # Remove direct 'XSS' string references to make it slightly harder
    content = re.sub(r"""[\"']XSS[\"']""", "", content, flags=re.IGNORECASE)
    
    # Validate using the vulnerable isCleanHtml function
    if not isCleanHtml(content):
        return XSS_CONTENT_SANITIZER.format("Sanitizer", 
            '<div class="solution-text error-text"><br>Content blocked by isCleanHtml filter. Detected potentially dangerous HTML attribute or tag.</div>',
            "", "")
    
    # Content passed validation - render it (potentially vulnerable!)
    # Build the page with user-supplied content
    data = XSS_CONTENT_SANITIZER.format("Sanitizer", "", content, "")
    result = check_xss(data, flags[0], content, 'xss_easy_med')
    return XSS_CONTENT_SANITIZER.format("Sanitizer", result, content, "")


if __name__ == '__main__':
    app.run(debug=True)
