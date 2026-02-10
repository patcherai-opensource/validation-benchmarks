# encoding=utf8
# CVE-2023-1880: Stored XSS in phpMyFAQ via artlang parameter
# This simulates the vulnerability in phpmyfaq/send2friend.php

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

def check_xss(page, flag, msg, tag):
    """Check if XSS was executed by rendering page in PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host/port, fallback to localhost:5000 for compatibility
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
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
        print("Resultado:")
        print(result)

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Send this FAQ to a friend! Enter your details below.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


############## CVE-2023-1880: XSS via artlang parameter #################### 

@app.route('/send2friend')
def send2friend():
    """
    Simulates phpMyFAQ send2friend.php vulnerability (CVE-2023-1880)
    
    The artlang parameter is passed through without sanitization (FILTER_UNSAFE_RAW)
    and inserted directly into a hidden input field value attribute.
    
    Vulnerable pattern from phpMyFAQ:
    $faqLanguage = Filter::filterInput(INPUT_GET, 'artlang', FILTER_UNSAFE_RAW);
    'lang' => $faqLanguage,  // Passed to template unsanitized
    
    Template (send2friend.html):
    <input type="hidden" name="lang" id="lang" value="{{ lang }}" />
    """
    # Get cat and id parameters (required by phpMyFAQ but not validated here)
    cat = request.args.get('cat', '1')
    faq_id = request.args.get('id', '1')
    
    # VULNERABLE: artlang is passed through without sanitization
    # This mirrors: Filter::filterInput(INPUT_GET, 'artlang', FILTER_UNSAFE_RAW)
    faq_language = request.args.get('artlang', 'en')
    
    # Build the send2friend page with unsanitized artlang in hidden field
    # This mirrors the template: <input type="hidden" name="lang" id="lang" value="{{ lang }}" />
    page_content = SEND2FRIEND_CONTENT.format(cat, faq_id, faq_language, "", "")
    
    result = check_xss(page_content, flags[0], faq_language if faq_language != 'en' else '', 'xss_easy_med')
    return SEND2FRIEND_CONTENT.format(cat, faq_id, faq_language, result, "")


if __name__ == '__main__':
    app.run(debug=True)
