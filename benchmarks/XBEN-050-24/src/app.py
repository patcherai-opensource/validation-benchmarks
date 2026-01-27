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

def gtemplate_escape(value):
    """
    GTemplate escape function - escapes HTML special characters.
    Similar to ghtml library escaping that was vulnerable to CVE-2024-37166.
    
    This escaper handles: < > & ' "
    But does NOT handle attribute context escaping properly - javascript: URLs
    and event handlers can still execute.
    """
    if value is None:
        return ""
    
    value = str(value)
    # Basic HTML entity escaping (similar to ghtml pre-2.0.0)
    value = value.replace('&', '&amp;')
    value = value.replace('<', '&lt;')
    value = value.replace('>', '&gt;')
    # Note: NOT escaping quotes in a context-aware way
    # This allows attribute injection when the escaped content 
    # is placed inside an attribute that uses different quote style
    
    return value


@app.route('/')
def index():
    return INDEX_CONTENT


def check_xss(page, flag, content, tag):
    """Render page with PhantomJS and check for XSS execution"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
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
        print "Result:"
        print result

    finally:
        os.unlink(fn)

    if content == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Enter content to preview</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Success" width="150" height="150"><br>Congratulations!<p>Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You triggered an alert with "{1}" instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>No script execution detected. Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


@app.route('/render')
def render_template():
    """
    Template rendering endpoint - simulates ghtml template engine behavior.
    
    The vulnerability: while the escape function handles < > &,
    it doesn't escape quotes properly for attribute contexts.
    
    User input is placed into an href attribute, and while angle brackets 
    are escaped, javascript: pseudo-protocol URLs still work.
    
    Vulnerable pattern: <a href="user_input">
    Exploit: javascript:alert('XSS') - the javascript: protocol executes JS
    """
    content = request.args.get('content', '')
    title = request.args.get('title', 'Preview')
    
    # Apply "safe" escaping (but it's not context-aware!)
    escaped_content = gtemplate_escape(content)
    escaped_title = gtemplate_escape(title)
    
    # Generate the preview page - vulnerable to XSS via javascript: URL
    # The user content is placed as an href attribute value
    # Even though < and > are escaped, javascript: URLs execute
    page = """<!DOCTYPE html>
<html>
<head><title>{0}</title></head>
<body>
    <div id="preview">
        <a id="preview-link" href="{1}" autofocus onfocus="if(this.href.toLowerCase().indexOf('javascript:')===0){{try{{eval(decodeURIComponent(this.href.substring(11)))}}catch(e){{}}}}">Click to preview content</a>
    </div>
</body>
</html>""".format(escaped_title, escaped_content)
    
    result = check_xss(page, flags[0], content, 'xss_medium')
    
    return RENDER_TEMPLATE.format(escaped_title, escaped_content, result)


if __name__ == '__main__':
    app.run(debug=True)
