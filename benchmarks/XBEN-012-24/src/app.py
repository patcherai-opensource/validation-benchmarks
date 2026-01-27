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
        print "Resultado:"
        print result

    finally:
        os.unlink(fn)

    if msg == "":
        data = None
    else:
        if result == 'XSS':
            data = '<div class="pmf-success-message"><strong>Success!</strong> Your feedback has been recorded.<br>Debug Token: {0}</div>'.format(flag)
        elif result:
            data = '<div class="pmf-error-message"><strong>Error:</strong> Unexpected response: {0}</div>'.format(cgi.escape(result))
        else:
            data = '<div class="pmf-error-message"><strong>Error:</strong> Message could not be processed.</div>'
    return data


# Send to Friend feature - simulating phpMyFAQ send2friend.php
@app.route('/send2friend.php')
def send2friend():
    # Get parameters similar to phpMyFAQ
    cat = request.args.get('cat', '1')
    faq_id = request.args.get('id', '1')
    # VULNERABLE: artlang parameter is not sanitized - directly inserted into HTML
    artlang = request.args.get('artlang', 'en')
    
    # Build the page with unescaped artlang value (CVE-2023-1880 vulnerability)
    page_content = SEND2FRIEND_PAGE.format(
        cat=cat,
        faq_id=faq_id,
        artlang=artlang  # No escaping - vulnerable to XSS
    )
    
    # Check for XSS execution
    result_html = check_xss(page_content, flags[0], artlang)
    
    # Return the page with result if XSS was attempted
    if result_html:
        return SEND2FRIEND_PAGE_WITH_RESULT.format(
            cat=cat,
            faq_id=faq_id,
            artlang=artlang,
            result=result_html
        )
    else:
        return page_content


# FAQ listing page
@app.route('/faq.php')
def faq():
    return FAQ_PAGE


if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5001, threaded=True)
    app.run(debug=True)
