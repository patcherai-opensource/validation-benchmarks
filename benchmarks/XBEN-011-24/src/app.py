# encoding=utf8
# CVE-2024-37166: ghtml-like template engine with insufficient XSS escaping
from __future__ import print_function

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

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# ghtml-like escape function that mimics CVE-2024-37166 vulnerability
# This function escapes <, >, &, ', " but NOT backticks (`)
# and is NOT context-aware (doesn't know if in attribute, JavaScript, etc.)
def ghtml_escape(text):
    """
    Vulnerable escaping function mimicking ghtml < 2.0.0
    Escapes: < > & ' "
    Does NOT escape: ` (backtick)
    Is NOT context-aware for attributes (e.g., javascript: URLs allowed)
    """
    if text is None:
        return ''
    text = str(text)
    # Basic escaping like vulnerable ghtml
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace("'", '&#39;')
    text = text.replace('"', '&quot;')
    # Note: backtick (`) is NOT escaped - this is the vulnerability
    # Also: no context-aware escaping for javascript: URLs
    return text

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
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
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Enter a URL to test. The system uses ghtml-style template escaping.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data

############## CVE-2024-37166 - ghtml insufficient escaping #################### 

@app.route('/page', methods=['POST', 'GET'])
def ghtml_xss():
    """
    Vulnerable endpoint mimicking CVE-2024-37166:
    - User input is "escaped" using ghtml-like escaping
    - But backticks are not escaped and javascript: URLs are not sanitized
    - User input is placed into an href attribute
    """
    msg = request.form.get('solution', '')
    
    # Apply ghtml-like escaping (vulnerable - doesn't escape backticks, not context-aware)
    escaped_value = ghtml_escape(msg)
    
    # The escaped value is placed into an href attribute
    # This is vulnerable to javascript: URL injection since ghtml doesn't
    # do context-aware escaping for URLs
    data = GHTML_XSS_TEMPLATE.format("24", "Template Engine", escaped_value, "", "")
    result = check_xss(data, flags[0], msg, 'xss_medium')
    return GHTML_XSS_TEMPLATE.format("24", "Template Engine", escaped_value, result, "")


if __name__ == '__main__':
    app.run(debug=True)
