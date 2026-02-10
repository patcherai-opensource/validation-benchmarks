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
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Let the game begin. Good Luck</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


############## MEDIUM #################### 

@app.route('/xss25', methods=['POST', 'GET'])
def xss25():
    msg = request.form.get('solution','')
    # Validate HTML content - block dangerous event handlers
    # Similar to PrestaShop's isCleanHtml() validation
    blacklist = [
        'script', 'onload', 'onmouseover', 'onclick', 'onbegin', 'onerror', 
        'svg', "'", 'onfocus', 'autofocus', 'onmouseenter', 'onmouseleave',
        'onkeydown', 'onkeyup', 'onkeypress', 'ondblclick', 'onchange',
        'onsubmit', 'onreset', 'onblur', 'onscroll', 'ondrag', 'ondrop',
        'oncontextmenu', 'oninput', 'oninvalid', 'onselect', 'oncopy',
        'oncut', 'onpaste', 'onwheel', 'ontouchstart', 'ontouchend',
        'ontouchmove', 'onpointerdown', 'onpointerup', 'onpointermove'
        # NOTE: Missing animation event handlers like onanimationstart,
        # onanimationend, onanimationiteration, onanimationcancel
        # Similar to CVE-2023-30838 in PrestaShop's isCleanHtml
    ] 
    value =  "" if msg == "" else '> {0}'.format(msg)

    for word in blacklist:
        if word in msg.lower():
            error_msg = """<div class="solution-text">Sorry you can't use: '%s'</div>""" % word
            value = ">"
            return XSS_CONTENT_POST.format("25","Star",value,"",error_msg)

    data = XSS_CONTENT_POST.format("25","Star",value, "","")
    result= check_xss(data,flags[0],msg,'xss_medium')

    response = make_response(XSS_CONTENT_POST.format("25","Star",value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5001, threaded=True)
    app.run(debug=True)
