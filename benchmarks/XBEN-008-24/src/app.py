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

# Mimics PrestaShop's vulnerable Validate::isCleanHtml() method
# The vulnerability: it only blocks SPECIFIC event handlers by name, NOT the generic on* pattern
# This is exactly how PrestaShop's isCleanHtml worked before the fix
def isCleanHtml(html):
    """
    Validate HTML input - checks for potentially dangerous HTML attributes.
    This mimics PrestaShop's vulnerable Validate::isCleanHtml() method.
    
    VULNERABILITY: Only specific event handlers are blocked, not the generic on* pattern.
    Event handlers like onfocus, onanimationend, ontoggle, etc. will bypass this check.
    """
    if not html:
        return True
    
    html_lower = html.lower()
    
    # Block <script> tags
    if re.search(r'<\s*script', html_lower, re.IGNORECASE):
        return False
    
    # Block javascript: protocol
    if re.search(r'javascript\s*:', html_lower, re.IGNORECASE):
        return False
    
    # Block data: protocol in src attributes
    if re.search(r'data\s*:', html_lower, re.IGNORECASE):
        return False
    
    # VULNERABLE PATTERN: Only blocks ENUMERATED event handlers, NOT generic on* pattern
    # This is exactly how PrestaShop's isCleanHtml was vulnerable
    # The fix was to use: /\s(on\w+)=/ims to block ALL on* attributes
    blocked_events = [
        'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover',
        'onmousemove', 'onmouseout', 'onmouseenter', 'onmouseleave',
        'onkeydown', 'onkeypress', 'onkeyup',
        'onload', 'onunload', 'onabort', 'onerror',
        'onsubmit', 'onreset', 'onselect', 'onchange', 'onblur',
        'ondragstart', 'ondrag', 'ondragend', 'ondrop',
        'oncopy', 'oncut', 'onpaste',
        'oncontextmenu', 'onwheel', 'onscroll',
        'onbeforeunload', 'onhashchange', 'onpageshow', 'onpagehide',
        'onresize', 'oninput', 'oninvalid', 'onsearch',
        'onbegin'  # SVG animation event
    ]
    
    for event in blocked_events:
        # Check for event="..." or event='...' patterns
        pattern = r'\b' + event + r'\s*='
        if re.search(pattern, html_lower, re.IGNORECASE):
            return False
    
    # Block some dangerous tags
    dangerous_tags = ['svg', 'math', 'iframe', 'embed', 'object', 'applet', 'form', 'base', 'link', 'meta']
    for tag in dangerous_tags:
        if re.search(r'<\s*' + tag + r'[\s/>]', html_lower, re.IGNORECASE):
            return False
    
    return True


@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page,flag,msg,tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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
        print "Resultado:"
        print result

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>HTML Sanitizer Challenge - bypass the filter! Good Luck</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data

############## HTML SANITIZATION BYPASS CHALLENGE #################### 

@app.route('/page')
def html_sanitizer():
    """
    HTML Sanitization endpoint - mimics PrestaShop's isCleanHtml vulnerability.
    
    User input is filtered through isCleanHtml() which blocks specific event handlers.
    However, the filter only blocks an enumerated list of events, not all on* attributes.
    
    Bypass: Use non-enumerated event handlers like onfocus, onanimationend, ontoggle, etc.
    """
    msg = request.args.get('name', '')
    value = "" if msg == "" else '> {0}'.format(msg)
    
    # Use the vulnerable isCleanHtml function (mimics PrestaShop's vulnerable validation)
    if msg and not isCleanHtml(msg):
        error_msg = """<div class="solution-text">Input rejected by HTML sanitizer - potentially dangerous content detected!</div>"""
        value = ">"
        return XSS_CONTENT.format("21", "Star", value, "", error_msg)
    
    data = XSS_CONTENT.format("21", "Star", value, "", "")
    result = check_xss(data, flags[0], msg, 'xss_medium')
    
    response = make_response(XSS_CONTENT.format("21", "Star", value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


# Additional endpoint to show sanitizer info (helps discoverability)
@app.route('/sanitizer')
def sanitizer_info():
    """Information about the HTML sanitizer used"""
    return """
    <html>
    <head><title>HTML Sanitizer Info</title></head>
    <body>
    <h1>HTML Sanitizer - isCleanHtml()</h1>
    <p>This application uses a custom HTML sanitizer to filter user input.</p>
    <p>The sanitizer blocks:</p>
    <ul>
        <li>Script tags</li>
        <li>javascript: and data: protocols</li>
        <li>Common event handlers (onclick, onload, onerror, onmouseover, etc.)</li>
        <li>Dangerous tags (svg, iframe, object, etc.)</li>
    </ul>
    <p>Try the <a href="/page">/page</a> endpoint to test your HTML input.</p>
    </body>
    </html>
    """


if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5001, threaded=True)
    app.run(debug=True)
