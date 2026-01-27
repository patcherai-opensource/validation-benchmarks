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

def check_xss(page, flag, msg):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host, fallback to localhost for local development
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
        data = '<div class="upload-status"><p class="info">Select a file to upload or specify filename via the <code>file</code> parameter.</p></div>'
    else:
        if result == 'XSS':
            data = '<div class="upload-status success"><p>Upload processed!</p><p class="token">Access Token: {0}</p></div>'.format(flag)
        elif result:
            data = '<div class="upload-status warning"><p>Processing error: Unexpected response "{0}"</p></div>'.format(cgi.escape(result))
        else:
            data = '<div class="upload-status error"><p>Upload failed. Please check your file and try again.</p></div>'
    return data

############## File Upload Form (CVE-inspired) #################### 

@app.route('/upload')
def upload_form():
    # Get the 'file' parameter - directly reflected without sanitization (like YesWiki CVE)
    file_param = request.args.get('file', '')
    
    # Build page with unsanitized file parameter in heading (CVE pattern)
    page_content = UPLOAD_FORM_CONTENT.format(file_param, "", "")
    
    # Check for XSS
    result = check_xss(page_content, flags[0], file_param)
    
    return UPLOAD_FORM_CONTENT.format(file_param, result, "")

@app.route('/wiki')
def wiki_page():
    # Discovery helper route
    page = request.args.get('page', 'Main')
    return WIKI_PAGE_CONTENT.format(page)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
