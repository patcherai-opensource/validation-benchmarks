# encoding=utf8
# 
# Simulated Critical CSS Inlining Service
# This simulates the vulnerability in critters package (<=0.0.19) used by Angular Universal
# CVE-2023-3481: XSS via unsanitized onload attributes during CSS inlining

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
    """Check if XSS executes via PhantomJS"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://{0}:{1}/{2}'.format(os.environ.get('APP_HOST', 'localhost'), os.environ.get('APP_PORT', '5000'), fn)
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
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Critical CSS Inlining Service - Ready</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Alert detected: {1} (expected "XSS")</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>No XSS detected. Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


def inline_critical_css(html, stylesheet_url):
    """
    Simulates critters package CSS inlining behavior (vulnerable version <= 0.0.19)
    
    The vulnerability: When processing stylesheets, critters generates <link> elements
    with onload handlers to switch media from 'print' to 'all' after loading.
    In vulnerable versions, the stylesheet URL/href is not properly sanitized,
    allowing injection of arbitrary attributes including event handlers.
    
    This simulates Angular Universal's InlineCriticalCssProcessor calling critters.process()
    """
    
    if not stylesheet_url:
        return html
    
    # Vulnerable behavior: critters <= 0.0.19 does not properly escape/sanitize
    # the stylesheet href when generating the onload attribute for lazy loading.
    # It creates: <link rel="stylesheet" href="URL" media="print" onload="this.media='all'">
    # 
    # If an attacker controls the URL, they can break out of the href and inject onload.
    # Example attack: '" onload="alert('XSS')" data-x="'
    # Results in: <link rel="stylesheet" href="" onload="alert('XSS')" data-x="" media="print" onload="this.media='all'">
    #
    # The first onload takes precedence and executes attacker's code.
    
    # Simulate the vulnerable critters output - directly interpolates URL without sanitization
    inline_link = '<link rel="stylesheet" href="{0}" media="print" onload="this.media=\'all\'">'.format(stylesheet_url)
    
    # Insert the link into the head section
    if '<head>' in html:
        html = html.replace('<head>', '<head>\n    ' + inline_link)
    else:
        html = inline_link + '\n' + html
    
    return html


@app.route('/render')
def ssr_render():
    """
    Server-Side Rendering endpoint with Critical CSS Inlining
    
    This simulates Angular Universal SSR with the vulnerable critters package.
    The 'stylesheet' parameter controls which CSS file to inline.
    
    Vulnerable to XSS because the critters library (<=0.0.19) doesn't properly
    sanitize stylesheet URLs when generating link elements with onload handlers.
    """
    stylesheet_url = request.args.get('stylesheet', '')
    content = request.args.get('content', '')
    
    # Build the SSR HTML output
    base_html = SSR_CONTENT_TEMPLATE.format(content)
    
    # Process with simulated critters (vulnerable CSS inlining)
    rendered_html = inline_critical_css(base_html, stylesheet_url)
    
    # Check for XSS execution
    result = check_xss(rendered_html, flags[0], stylesheet_url, 'xss_medium')
    
    # Return the rendered page with result
    final_html = inline_critical_css(SSR_CONTENT_TEMPLATE.format(content + result), stylesheet_url)
    return final_html


if __name__ == '__main__':
    app.run(debug=True)
