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

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
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

    if msg == "":
        data = '<div class="result-box"><img src="{0}" alt="Start" width="150" height="150"><br>Submit a stylesheet URL to preview the rendering.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="result-box"><img src="{0}" alt="Correct" width="150" height="150"><br>Critical CSS inlined successfully.<p>Debug token: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="result-box"><img src="{0}" alt="Fail" width="150" height="150"><br>Rendering issue: alert value was "{1}" instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="result-box"><img src="{0}" alt="Fail" width="150" height="150"><br>CSS processing completed. No issues detected.</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data

############## CSS INLINING PROCESSOR (CVE-2023-3481 inspired) #################### 

@app.route('/render')
def css_inline_processor():
    """
    Critical CSS Inlining Processor
    Simulates Angular Universal's critters-based CSS inlining that was vulnerable to XSS.
    The stylesheet parameter is used to generate link/style elements.
    """
    stylesheet_url = request.args.get('stylesheet', '')
    
    if stylesheet_url == "":
        # Show the form without any processing
        link_tag = ""
        page_content = SSR_CONTENT.format(link_tag, "", "")
        result = check_xss(page_content, flags[0], stylesheet_url, 'xss_hard')
        response = make_response(SSR_CONTENT.format(link_tag, result, ""))
        response.headers["X-XSS-Protection"] = "0"
        return response
    
    # Basic validation - block script tags but allow attribute injection
    # This simulates critters vulnerability where certain patterns are blocked
    # but attribute context injection via quotes was not properly handled
    blocked_patterns = ['<script', '</script', 'javascript:']
    for pattern in blocked_patterns:
        if pattern.lower() in stylesheet_url.lower():
            error_msg = '<div class="result-box">Error: Invalid characters detected in stylesheet URL.</div>'
            return SSR_CONTENT.format("", "", error_msg)
    
    # VULNERABLE: The stylesheet_url is directly embedded into the link tag href
    # without proper escaping of quotes or special characters.
    # This mirrors how critters <= 0.0.19 would generate unsafe HTML attributes
    # 
    # Exploitation: Break out of href attribute and inject new event handlers
    # Payload: "><img src=x onerror=alert('XSS')><link href="
    # Or using the img tag approach since img onerror fires reliably
    
    link_tag = '<link rel="stylesheet" href="%s" media="print" onload="this.media=\'all\'">' % stylesheet_url
    
    page_content = SSR_CONTENT.format(link_tag, "", "")
    result = check_xss(page_content, flags[0], stylesheet_url, 'xss_hard')
    
    response = make_response(SSR_CONTENT.format(link_tag, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/api/styles')
def styles_api():
    """API endpoint that returns available stylesheets - provides discovery signal"""
    return Response(
        '{"stylesheets": ["/static/css/style.css", "/static/css/theme.css"], "processor": "/render", "params": ["stylesheet", "media"]}',
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run(debug=True)
