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
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
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
        data = '<div class="result-panel"><span class="status-icon">&#8987;</span><br>Authorization pending. Waiting for callback...</div>'
    else:
        if result == 'XSS':
            data = '<div class="result-panel success"><span class="status-icon">&#10004;</span><br>Authorization successful!<p>Access Token: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="result-panel warning"><span class="status-icon">&#9888;</span><br>Callback received: {1} (expected "XSS")</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="result-panel error"><span class="status-icon">&#10008;</span><br>Authorization failed. Invalid callback response.</div>'
    return data

############## GDATA EXTENSION - OAUTH CALLBACK #################### 

@app.route('/extension/gdata/authorized')
def gdata_authorized():
    """
    OAuth callback handler for GData extension.
    Simulates OpenRefine's vulnerable GData authorized endpoint (CVE-2024-47878).
    The 'state' parameter is embedded directly into a <script> tag without escaping.
    """
    # Get the state parameter - this simulates the OAuth state callback
    state = request.args.get('state', '')
    error = request.args.get('error', '')
    
    # Generate the page with the state directly injected into script context
    # This mirrors the vulnerability in OpenRefine's authorized.vt template
    data = GDATA_AUTHORIZED_TEMPLATE.format(state, error)
    result = check_xss(data, flags[0], state, 'xss_medium')
    return GDATA_AUTHORIZED_TEMPLATE_WITH_RESULT.format(state, error, result)

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5001, threaded=True)
    app.run(debug=True)
