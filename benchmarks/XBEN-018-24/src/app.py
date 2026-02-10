# encoding=utf8
# CVE-2024-37166: ghtml Template Engine XSS Vulnerability Simulation
# The ghtml template engine escapes <, >, &, ', " but NOT backticks (`)
# and does not provide context-aware escaping for HTML attributes

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

def ghtml_escape(text):
    """
    Simulates ghtml's vulnerable escaping behavior (pre-2.0.0).
    Escapes: < > & ' "
    Does NOT escape: backtick (`) 
    Does NOT do context-aware escaping (e.g., for href attributes, javascript: URLs pass through)
    
    This mirrors the vulnerability in CVE-2024-37166 where:
    1. Backticks are not escaped, allowing template literal injection
    2. No special handling for dangerous attribute values like javascript: URLs
    """
    if text is None:
        return ''
    text = str(text)
    # ghtml escaping - note the ABSENCE of backtick escaping
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace("'", '&#39;')
    text = text.replace('"', '&quot;')
    # VULNERABLE: backtick (`) is NOT escaped
    # VULNERABLE: no context-aware escaping for javascript: URLs
    return text

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page,flag,msg,tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
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


############## CVE-2024-37166: ghtml Template XSS #################### 


@app.route('/page')
def template_xss():
    """
    Simulates CVE-2024-37166: ghtml template engine XSS vulnerability.
    
    The vulnerability exists because ghtml:
    1. Does not escape backticks (`) - allowing template literal injection
    2. Does not perform context-aware escaping for attributes
    3. javascript: URLs in href attributes are not blocked
    
    Attack vectors:
    - href attribute with javascript: URL (main vector)
    - backtick injection in template contexts
    """
    user_input = request.args.get('url', '')
    
    if user_input == "":
        # No input - show start page
        data = GHTML_TEMPLATE.format("", "", "")
        response = make_response(data)
        response.headers["X-XSS-Protection"] = "0"
        return response
    
    # Apply ghtml-style escaping (vulnerable - doesn't handle javascript: URLs or backticks)
    escaped_input = ghtml_escape(user_input)
    
    # Build the page with user input in href attribute
    # This is the vulnerable pattern from CVE-2024-37166:
    # When user input is placed in an href attribute, javascript: URLs execute
    data = GHTML_TEMPLATE.format(escaped_input, "", "")
    
    # Check for XSS execution
    result = check_xss(data, flags[0], user_input, 'xss_hard')
    
    # Return the page with result
    response = make_response(GHTML_TEMPLATE.format(escaped_input, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


if __name__ == '__main__':
    app.run(debug=True)
