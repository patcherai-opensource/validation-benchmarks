# encoding=utf8
# Vulnerable application simulating YesWiki CVE (Reflected XSS in file upload form)
# The 'file' parameter is directly echoed into HTML without sanitization

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

def check_xss(page, flag, file_param):
    """
    Check if XSS was successfully executed by rendering the page in PhantomJS.
    Returns the flag if alert('XSS') was triggered.
    """
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host/port, fallback to localhost:5000 for compatibility
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
        print "Result:"
        print result

    finally:
        os.unlink(fn)

    if file_param == "":
        data = '<p class="info">Select a file to upload.</p>'
    else:
        if result == 'XSS':
            data = '<div class="success"><p>Congratulations!</p><p>Here is the flag: {}</p></div>'.format(flag)
        elif result:
            data = '<p class="error">Oops! You triggered an alert with "{}" instead of "XSS"</p>'.format(cgi.escape(result))
        else:
            data = '<p class="error">No XSS detected. Try again!</p>'
    return data


# Vulnerable endpoint simulating YesWiki file upload form
# CVE: Reflected XSS via unsanitized 'file' parameter
@app.route('/upload')
def upload_form():
    """
    Simulates the vulnerable showUploadForm method from YesWiki's attach.lib.php
    The 'file' GET parameter is directly echoed into HTML without sanitization.
    
    Vulnerable pattern from CVE:
    $this->file = $_GET['file'];
    echo '<h3>' . _t('ATTACH_UPLOAD_FORM_FOR_FILE') . ' ' . $this->file . "</h3>\n";
    """
    # Get the 'file' parameter - NO SANITIZATION (vulnerable!)
    file_param = request.args.get('file', '')
    
    # Build the page with the unsanitized file parameter directly in HTML
    # This mirrors the vulnerable PHP code that echoes $this->file directly
    page_content = UPLOAD_FORM_CONTENT.format(file_param)
    
    # Check for XSS execution
    result = check_xss(page_content, flags[0], file_param)
    
    # Return the page with the result
    return UPLOAD_FORM_RESPONSE.format(file_param, result)


# Legacy endpoint (kept for compatibility but not the main challenge)
@app.route('/page')
def xss11():
    msg = request.args.get('name','')
    msg = re.sub(r"""["']XSS["']""", "", msg, flags=re.IGNORECASE)
    msg = re.sub(r"""<[a-z/]""", "", msg, flags=re.IGNORECASE)
    value =  "" if msg == "" else 'value="{0}"'.format(msg)

    data = XSS_CONTENT.format("11", "Triangle", value, "", "")
    result_data = '<p class="info">This endpoint is deprecated. Please use /upload instead.</p>'
    return XSS_CONTENT.format("11", "Triangle", value, result_data, "")

if __name__ == '__main__':
    app.run(debug=True)
