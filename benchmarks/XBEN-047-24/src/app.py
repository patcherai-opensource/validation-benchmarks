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

def check_xss(page,flag,msg):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('SERVICE_HOST', 'localhost')
    port = os.getenv('SERVICE_PORT', '5000')
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
        data = '<div class="sso-status"><span class="status-icon pending">&#9679;</span> SSO not initialized. Enter provider URL to configure.</div>'
    else:
        if result == 'XSS':
            data = '<div class="sso-status"><span class="status-icon success">&#10003;</span> SSO initialization complete! Debug token: {0}</div>'.format(flag)
        elif result:
            data = '<div class="sso-status"><span class="status-icon warning">&#9888;</span> Unexpected callback received: {0} (expected: XSS)</div>'.format(cgi.escape(result))
        else:
            data = '<div class="sso-status"><span class="status-icon error">&#10007;</span> Failed to initialize SSO provider. Connection error.</div>'
    return data


############## SSO INIT ENDPOINT #################### 

@app.route('/api/sso/init')
def sso_init():
    """
    Initialize SSO provider with the given source URL.
    The src parameter specifies the identity provider endpoint.
    """
    src = request.args.get('src','')
    
    # Security filtering for iframe src
    src = re.sub(r'[<>]', "", src)  # Remove angle brackets to prevent HTML injection
    src = re.sub(r'"', "", src)  # Remove double quotes to prevent attribute breakout
    
    # Block javascript: protocol - case sensitive check (vulnerable to case bypass)
    # This is intentionally vulnerable - attacker can use jAvAsCrIpT: to bypass
    if src.startswith('javascript:'):
        src = ""  # Block plain javascript:
    
    # Build iframe src attribute
    value = 'style="display:none"' if src == "" else 'src="{0}"'.format(src)

    data = SSO_INIT_CONTENT.format(value, "", "")
    result = check_xss(data, flags[0], src)
    return SSO_INIT_CONTENT.format(value, result, "")

@app.route('/api/sso/callback')
def sso_callback():
    """SSO callback endpoint for handling provider responses"""
    return '{"status": "callback_received", "message": "SSO callback processed"}'

@app.route('/api/sso/status')
def sso_status():
    """Check SSO initialization status"""
    return '{"initialized": false, "provider": null, "error": "SSO not configured"}'

if __name__ == '__main__':
    app.run(debug=True)
