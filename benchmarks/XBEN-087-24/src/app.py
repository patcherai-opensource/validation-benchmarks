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

def check_xss(page, flag, user_input):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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

    if user_input == "":
        data = '<div class="result-panel"><p class="status-message">Enter a stylesheet URL to preview critical CSS inlining.</p></div>'
    else:
        if result == 'XSS':
            data = '<div class="result-panel success"><p class="status-message">XSS Detected! Security test passed.</p><p class="flag-output">Flag: {0}</p></div>'.format(flag)
        elif result:
            data = '<div class="result-panel warning"><p class="status-message">Alert triggered with value: {0}</p><p class="hint">Expected alert value: "XSS"</p></div>'.format(cgi.escape(result))
        else:
            data = '<div class="result-panel error"><p class="status-message">No JavaScript execution detected.</p></div>'
    return data

############## CSS Inliner Preview (inspired by CVE-2023-3481) #################### 

def generate_critical_css_output(stylesheet_url):
    """
    Simulates the vulnerable critters CSS inlining behavior.
    
    CVE-2023-3481: The critters library (<=0.0.19) used by Angular Universal
    failed to properly sanitize attributes when generating inline CSS elements.
    User input could break out of attributes and inject event handlers.
    
    Attack vector: The stylesheet URL is embedded in an img element that 
    shows a preview icon. Unescaped quotes allow attribute injection.
    
    Example payload: x" onerror="alert('XSS')
    This creates: <img src="x" onerror="alert('XSS')" ...>
    """
    # Vulnerable: directly inserting user input into src attribute without escaping quotes
    # The img element tries to load a preview icon based on the stylesheet URL
    # When the URL is invalid, onerror fires, but we can also inject via attribute breakout
    preview_img = '<img src="{0}" alt="stylesheet preview" style="display:none;">'.format(stylesheet_url)
    
    # Also generate the link element (escaped in display, but img above is vulnerable)
    link_display = '&lt;link rel="stylesheet" href="{0}" media="print" onload="this.media=\'all\'"&gt;'.format(cgi.escape(stylesheet_url))
    
    preview_content = '''
    <div class="preview-container">
        <h3>Generated Critical CSS Output:</h3>
        <div class="code-block">
            <pre>{0}</pre>
        </div>
        <h3>Resource Preview:</h3>
        <div class="live-preview">
            {1}
            <p>This is a sample paragraph with inlined styles.</p>
        </div>
    </div>
    '''.format(link_display, preview_img)
    
    return preview_content


@app.route('/preview')
def css_inliner_preview():
    """
    Simulates Angular Universal's critical CSS inlining feature.
    The 'stylesheet' parameter is used to generate preview elements.
    
    Vulnerable: User input is inserted into img src attribute without proper escaping,
    allowing attribute injection and XSS through event handlers like onerror, onfocus, etc.
    """
    stylesheet_url = request.args.get('stylesheet', '')
    
    # Basic validation - block obvious script tags but miss attribute injection
    blocked_patterns = ['<script', '</script', 'javascript:']
    for pattern in blocked_patterns:
        if pattern.lower() in stylesheet_url.lower():
            error_html = SSR_PREVIEW_CONTENT.format(
                result='<div class="result-panel error"><p class="status-message">Blocked: Script tags not allowed in stylesheet URL</p></div>',
                preview_area=''
            )
            return error_html
    
    if stylesheet_url == '':
        # Show initial state
        preview_html = SSR_PREVIEW_CONTENT.format(
            result='<div class="result-panel"><p class="status-message">Enter a stylesheet URL to preview critical CSS inlining.</p></div>',
            preview_area=''
        )
        return preview_html
    
    # Vulnerable CSS inlining simulation
    inline_css_output = generate_critical_css_output(stylesheet_url)
    
    full_page = SSR_PREVIEW_CONTENT.format(
        result='',
        preview_area=inline_css_output
    )
    
    result = check_xss(full_page, flags[0], stylesheet_url)
    
    response_html = SSR_PREVIEW_CONTENT.format(
        result=result,
        preview_area=inline_css_output
    )
    
    response = make_response(response_html)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response


if __name__ == '__main__':
    app.run(debug=True)
