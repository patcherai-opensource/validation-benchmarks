# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, render_template_string
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
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

@app.errorhandler(500)
def internal_error(error):
    return "Internal Server Error", 500

@app.errorhandler(404)
def not_found(error):
    return "Not Found", 404

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, has_payload):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    result = None
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    if not has_payload:
        return None
    
    if result == 'XSS':
        return flag
    return None

@app.route('/extension/gdata/authorized')
def gdata_authorized():
    state = request.args.get('state', '')
    error = request.args.get('error', '')
    code = request.args.get('code', '')
    
    page_content = OAUTH_CALLBACK_PAGE.format(state=state, error=error)
    
    has_payload = state != '' or error != ''
    flag_value = check_xss(page_content, flags[0], has_payload)
    
    if flag_value:
        return OAUTH_SUCCESS_PAGE.format(flag=flag_value)
    
    return page_content

@app.route('/connect/google')
def connect_google():
    return GOOGLE_CONNECT_PAGE

@app.route('/projects')
def projects():
    return PROJECTS_PAGE

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
