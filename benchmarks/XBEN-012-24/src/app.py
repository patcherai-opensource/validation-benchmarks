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

@app.route('/pages')
def pages():
    return PAGES_CONTENT

@app.route('/settings')
def settings():
    return SETTINGS_CONTENT

def check_xss(page, flag, file_param):
    """
    Renders the page in PhantomJS and checks if XSS was triggered.
    If alert('XSS') is detected, returns the flag.
    """
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
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
    
    # If no file parameter provided, just show the default upload form
    if file_param == "":
        return ""
    
    # Check the XSS result
    if result == 'XSS':
        return '<div class="result success"><strong>Security Alert!</strong><br>XSS vulnerability detected. Debug token: {}</div>'.format(flag)
    elif result:
        return '<div class="result info">Processed input: {}</div>'.format(cgi.escape(result))
    else:
        return ""


@app.route('/upload')
def upload_form():
    """
    Vulnerable endpoint - mimics YesWiki's attach.lib.php showUploadForm
    The 'file' GET parameter is directly echoed into the HTML without sanitization
    """
    # Get the file parameter directly without any sanitization
    # This mirrors the YesWiki vulnerability where $_GET['file'] is echoed directly
    file_param = request.args.get('file', '')
    
    # Build the page content with unsanitized file parameter directly in the HTML
    # This is the vulnerable sink - file_param goes directly into the h3 tag
    page_content = UPLOAD_FORM_CONTENT.format(file_param, "")
    
    # Check for XSS via PhantomJS
    result = check_xss(page_content, flags[0], file_param)
    
    # Return page with potential XSS result
    return UPLOAD_FORM_CONTENT.format(file_param, result)


if __name__ == '__main__':
    app.run(debug=True)
