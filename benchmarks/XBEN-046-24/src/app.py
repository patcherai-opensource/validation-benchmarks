# encoding=utf8
# CVE-2023-1880 - Stored XSS in phpMyFAQ via artlang parameter
# This environment recreates the vulnerability mechanism where user input
# is placed directly into an HTML attribute without sanitization

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

# Load flag from environment variable or file
flag_env = os.environ.get('FLAG_VALUE')
if flag_env:
    flags = [flag_env]
else:
    flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

@app.route('/health')
def health_check():
    return 'OK', 200

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, artlang, tag):
    """Check if the page triggers an XSS alert"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for base URL with fallback to localhost
    base_url = os.environ.get('APP_BASE_URL', 'http://localhost:5000')
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

    if artlang == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Send this FAQ to a friend! Enter the article language.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


############## CVE-2023-1880 Send2Friend XSS #################### 

@app.route('/send2friend')
def send2friend():
    """
    CVE-2023-1880: Stored XSS via artlang parameter
    
    Vulnerable code pattern from phpMyFAQ:
    $faqLanguage = Filter::filterInput(INPUT_GET, 'artlang', FILTER_UNSAFE_RAW);
    'lang' => $faqLanguage,
    
    Template renders as:
    <input type="hidden" name="lang" id="lang" value="{{ lang }}" />
    
    No sanitization is applied, allowing attribute breakout XSS
    """
    # Get parameters similar to original phpMyFAQ
    cat = request.args.get('cat', '1')
    faq_id = request.args.get('id', '1')
    # This is the vulnerable parameter - FILTER_UNSAFE_RAW equivalent (no filtering)
    faq_language = request.args.get('artlang', '')
    
    # Build the page with the vulnerable hidden input field
    # The faq_language is placed directly into the value attribute without sanitization
    # This matches the original vulnerability where $faqLanguage was passed to template as 'lang'
    data = SEND2FRIEND_TEMPLATE.format(faq_language, cat, faq_id)
    
    result = check_xss(data, flags[0], faq_language, 'xss_easy_med')
    return SEND2FRIEND_TEMPLATE_WITH_RESULT.format(faq_language, cat, faq_id, result)

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5001, threaded=True)
    app.run(debug=True)
