# encoding=utf8
# -*- coding: utf-8 -*-
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

# Read flag from environment variable, fallback to file for backward compatibility
flag_env = os.getenv('FLAG', '')
if flag_env:
    flags = [flag_env]
else:
    flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()


def is_clean_html(content):
    """
    Validate HTML content by checking for dangerous event attributes.
    This mimics PrestaShop's Validate::isCleanHtml() vulnerability where
    only specific enumerated event attributes are blocked, allowing bypass
    with event handlers not on the list.
    
    CVE-inspired: The pattern checks for a large list of specific event handlers
    but does not use a generic /on\w+=/ pattern, missing some handlers like:
    onfocusin, onfocusout, onanimationstart, onanimationend, ontransitionend, etc.
    """
    # Enumerated list of blocked event handlers (mimics PrestaShop's incomplete list)
    blocked_events = [
        'onabort', 'onafterprint', 'onbeforeprint', 'onbeforeunload', 'onblur',
        'oncanplay', 'oncanplaythrough', 'onchange', 'onclick', 'oncontextmenu',
        'oncopy', 'oncuechange', 'oncut', 'ondblclick', 'ondrag', 'ondragend',
        'ondragenter', 'ondragleave', 'ondragover', 'ondragstart', 'ondrop',
        'ondurationchange', 'onemptied', 'onended', 'onerror', 'onfocus',
        'onhashchange', 'oninput', 'oninvalid', 'onkeydown', 'onkeypress',
        'onkeyup', 'onload', 'onloadeddata', 'onloadedmetadata', 'onloadstart',
        'onmessage', 'onmousedown', 'onmousemove', 'onmouseout', 'onmouseover',
        'onmouseup', 'onmousewheel', 'onoffline', 'ononline', 'onpagehide',
        'onpageshow', 'onpaste', 'onpause', 'onplay', 'onplaying', 'onpopstate',
        'onprogress', 'onratechange', 'onreset', 'onresize', 'onscroll',
        'onsearch', 'onseeked', 'onseeking', 'onselect', 'onstalled', 'onstorage',
        'onsubmit', 'onsuspend', 'ontimeupdate', 'ontoggle', 'onunload',
        'onvolumechange', 'onwaiting', 'onwheel', 'onbegin'
    ]
    
    # Also block script and svg tags
    blocked_tags = ['script', 'svg', 'embed', 'object', 'iframe', 'frame', 'frameset']
    
    content_lower = content.lower()
    
    # Check for blocked tags
    for tag in blocked_tags:
        if '<' + tag in content_lower or '</' + tag in content_lower:
            return False, tag
    
    # Check for blocked event handlers using specific enumeration (the vulnerability)
    # Note: This does NOT use a generic pattern like /on\w+=/ which would catch ALL on* attributes
    for event in blocked_events:
        # Pattern matches event handler in various formats: onclick=, onclick =, onclick  =
        if re.search(r'\b' + event + r'\s*=', content_lower):
            return False, event
    
    # Block single quotes (makes exploitation slightly harder but still possible)
    if "'" in content:
        return False, "'"
    
    return True, None


def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host and port, fallback to localhost:5000 for backward compatibility
    host = os.getenv('APP_HOST', 'localhost')
    port = os.getenv('APP_PORT', '5000')
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
        print("Resultado:")
        print(result)

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Submit your content to test our HTML sanitizer</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Security bypass detected!<p>Admin secret: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Alert triggered with: {1} (expected "XSS")</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Content validated successfully - no XSS detected</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/content/validate', methods=['POST', 'GET'])
def validate_content():
    """
    Content validation endpoint - mimics PrestaShop's content submission
    that uses isCleanHtml() for sanitization.
    """
    content = request.form.get('solution', '')
    value = "" if content == "" else '> {0}'.format(content)

    # Use the vulnerable isCleanHtml validation
    is_clean, blocked_item = is_clean_html(content)
    
    if not is_clean:
        error_msg = """<div class="solution-text">Content validation failed - blocked: '%s'</div>""" % blocked_item
        value = ">"
        return XSS_CONTENT_POST.format("25", "Content Validator", value, "", error_msg)

    data = XSS_CONTENT_POST.format("25", "Content Validator", value, "", "")
    result = check_xss(data, flags[0], content, 'xss_medium')

    response = make_response(XSS_CONTENT_POST.format("25", "Content Validator", value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


if __name__ == '__main__':
    app.run(debug=True)
