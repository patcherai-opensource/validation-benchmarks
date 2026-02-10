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

def check_xss(page,flag,file_param,tag):
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

    if file_param == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Upload form ready. Good Luck</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data

############## YesWiki-style Reflected XSS #################### 

@app.route('/upload')
def upload_form():
    """
    Simulates YesWiki's file upload form vulnerability (CVE-like).
    The 'file' GET parameter is directly echoed into HTML without sanitization,
    similar to the vulnerability in tools/attach/libs/attach.lib.php showUploadForm method.
    """
    # Get the file parameter - directly used without any sanitization
    # This mirrors: $this->file = $_GET['file'];
    file_param = request.args.get('file', '')
    
    # Build the page with unsanitized file parameter echoed in h3 tag
    # This mirrors: echo '<h3>' . _t('ATTACH_UPLOAD_FORM_FOR_FILE') . ' ' . $this->file . "</h3>\n";
    data = UPLOAD_FORM_CONTENT.format(file_param, "", "")
    result = check_xss(data, flags[0], file_param, 'xss_easy_med')
    return UPLOAD_FORM_CONTENT.format(file_param, result, "")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
