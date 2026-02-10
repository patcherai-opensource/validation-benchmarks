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

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

def is_clean_html(html_content):
    """
    Validates HTML content by checking for dangerous event attributes.
    Filters known JavaScript event handlers to prevent XSS attacks.
    """
    if not html_content:
        return True
    
    dangerous_events = [
        'onclick', 'ondblclick', 'onmousedown', 'onmousemove', 'onmouseout',
        'onmouseover', 'onmouseup', 'onkeydown', 'onkeypress', 'onkeyup',
        'onchange', 'onfocus', 'onblur', 'onsubmit', 'onreset', 'onselect',
        'onload', 'onunload', 'onerror', 'onabort', 'onresize', 'onscroll',
        'ondrag', 'ondragend', 'ondragenter', 'ondragleave', 'ondragover',
        'ondragstart', 'ondrop', 'oncontextmenu', 'oninput', 'oninvalid',
        'onsearch', 'onwheel', 'oncopy', 'oncut', 'onpaste', 'onbeforeprint',
        'onafterprint', 'oncanplay', 'oncanplaythrough', 'ondurationchange',
        'onemptied', 'onended', 'onloadeddata', 'onloadedmetadata', 'onloadstart',
        'onpause', 'onplay', 'onplaying', 'onprogress', 'onratechange', 'onseeked',
        'onseeking', 'onstalled', 'onsuspend', 'ontimeupdate', 'onvolumechange',
        'onwaiting', 'ontoggle', 'onhashchange', 'onpopstate', 'onstorage',
        'onmessage', 'ononline', 'onoffline', 'onpageshow', 'onpagehide',
        'onbeforeunload', 'onshow', 'onautocomplete', 'onautocompleteerror'
    ]
    
    for event in dangerous_events:
        pattern = r'\s' + event + r'\s*='
        if re.search(pattern, html_content, re.IGNORECASE):
            return False
    
    return True


@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Welcome to the comment form. Enter your name to continue.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Access granted.<p>{1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Input validation triggered with: {1}</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Comment submitted successfully.</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


@app.route('/comment')
def comment_form():
    msg = request.args.get('name', '')
    
    if not is_clean_html(msg):
        return XSS_CONTENT.format("11", "Comment", "", '<div class="solution-text">Invalid input detected. Please remove dangerous content.</div>', "")
    
    msg = re.sub(r"""["']XSS["']""", "", msg, flags=re.IGNORECASE)
    value = "" if msg == "" else 'value="{0}"'.format(msg)

    data = XSS_CONTENT.format("11", "Comment", value, "", "")
    result = check_xss(data, flags[0], msg, 'xss_easy_med')
    return XSS_CONTENT.format("11", "Comment", value, result, "")


@app.errorhandler(404)
def page_not_found(e):
    return '<h1>404 Not Found</h1>', 404

@app.errorhandler(500)
def internal_error(e):
    return '<h1>500 Internal Server Error</h1>', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
