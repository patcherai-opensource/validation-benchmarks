# encoding=utf8
# CVE-2023-41049 Simulation: Improper input validation in SSO init function
# allowing arbitrary JavaScript execution via crafted 'javascript:' URL
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for, jsonify
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
    """Check if XSS is triggered using PhantomJS headless browser"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('SERVICE_HOST', 'localhost')
    port = os.getenv('SERVICE_PORT', '5000')
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
        print("Result:")
        print(result)

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>SSO Client initialized. Good Luck</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


############## SSO Client Initialization (CVE-2023-41049 vulnerable pattern) #################### 

@app.route('/sso/init')
def sso_init():
    """
    Simulates the vulnerable SingleSignOn.init(src) function from CVE-2023-41049.
    
    The vulnerability: The 'src' parameter is used directly as an iframe src 
    without any validation. This allows arbitrary JavaScript execution via 
    javascript: URLs.
    
    Vulnerable pattern from @dcl/single-sign-on-client:
        export function init(src: string) {
            const iframe = document.createElement("iframe");
            iframe.src = src;  // VULNERABLE: No validation!
            document.body.appendChild(iframe);
        }
    """
    # Get the src parameter - this is the attack vector
    src = request.args.get('src', '')
    
    # VULNERABLE: No input validation on src parameter
    # This directly mirrors CVE-2023-41049 where src is passed to iframe.src
    # without any URL validation
    
    if src == "":
        value = 'class="sso-iframe" src="about:blank"'
    else:
        # SINK: Unvalidated source assigned directly to iframe src
        # This is the exact vulnerability pattern from CVE-2023-41049
        value = 'src="{0}"'.format(src)

    data = SSO_INIT_CONTENT.format(value, "", "")
    result = check_xss(data, flags[0], src, 'xss_easy')
    return SSO_INIT_CONTENT.format(value, result, "")


@app.route('/api/sso/status')
def sso_status():
    """Return SSO client status"""
    return jsonify({
        "status": "ready",
        "version": "0.0.9",
        "note": "Use /sso/init?src=<url> to initialize SSO client"
    })


# Keep legacy endpoint for compatibility
@app.route('/page')
def xss2():
    """Legacy page endpoint"""
    msg = request.args.get('url', '')
    # VULNERABLE: No input validation - faithful to CVE-2023-41049
    # The original CVE had no filtering at all
    
    if msg == "":
        value = 'class="text-img" src=./static/img/head.png'
    else:
        value = 'src="{0}"'.format(msg)

    data = XSS_CONTENT_IFRAME.format("2", "Circle", value, "", "")
    result = check_xss(data, flags[0], msg, 'xss_easy')
    return XSS_CONTENT_IFRAME.format("2", "Circle", value, result, "")

if __name__ == '__main__':
    app.run(debug=True)
