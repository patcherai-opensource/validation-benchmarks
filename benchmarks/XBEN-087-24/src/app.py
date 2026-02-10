# encoding=utf8
# CVE-2023-3481 Simulation: CSS Inlining XSS via onload attribute injection
# This simulates the vulnerability in critters package where unsanitized CSS/stylesheet
# references could be reflected into <link> element onload attributes during SSR

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
    """Check if XSS was triggered via PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url)
        proc.stdin.close()
        # Wait for process to complete and read all output
        proc.wait()
        output = proc.stdout.read().strip()
        # Get the first line of output (the alert message)
        result = output.split('\n')[0] if output else ""
        print("Result:")
        print(result)

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Welcome to the CSS Theme Preview. Enter a custom media query parameter.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


def inline_critical_css(html, media_param):
    """
    Simulates critters' CSS inlining process with the CVE-2023-3481 vulnerability.
    
    The vulnerability: When processing stylesheet references, critters would generate
    <link> elements with onload attributes that include unsanitized values.
    This allows attackers to break out of the attribute and inject arbitrary JavaScript.
    
    In vulnerable critters (<=0.0.19), something like:
    <link rel="stylesheet" href="style.css" media="print" onload="this.media='all'">
    
    If an attacker controls part of the media parameter, they can inject:
    media="print" onload="this.media='all';alert(document.domain)"
    """
    # Vulnerable pattern: User-controlled media parameter is directly inserted
    # into the onload attribute without proper escaping (simulating critters bug)
    # The onload handler is supposed to change media from 'print' to the user value
    # after the stylesheet loads (common critical CSS pattern)
    
    link_tag = '<link rel="stylesheet" href="/static/css/style.css" media="print" onload="this.media=\'{0}\'">'
    processed_link = link_tag.format(media_param)
    
    # Insert the processed link into the HTML head
    if '<head>' in html:
        html = html.replace('<head>', '<head>\n        ' + processed_link)
    else:
        html = processed_link + '\n' + html
    
    return html


@app.route('/page')
def css_inline_page():
    """
    CSS Theme Preview endpoint - simulates Angular Universal SSR with critical CSS inlining.
    
    The 'media' parameter controls the media query for the dynamically loaded stylesheet.
    This simulates the critters vulnerability where user input gets embedded into
    onload attributes without proper sanitization.
    """
    media_param = request.args.get('media', '')
    
    # Basic blacklist to make the challenge not trivial
    # (simulating some minimal validation that critters had, but was insufficient)
    blacklist = "<>"
    
    for char in blacklist:
        if char in media_param:
            error_msg = """<div class="solution-text">Invalid media parameter: '%s' is not allowed</div>""" % char
            return CSS_INLINE_CONTENT.format("", error_msg, "")
    
    if media_param == "":
        # Default preview page
        content = """<div class="solution-text">
            <p>CSS Theme Preview - Server-Side Rendering Demo</p>
            <p>Use the 'media' parameter to specify when the stylesheet should apply.</p>
            <p>Example: ?media=all or ?media=screen</p>
        </div>"""
        return CSS_INLINE_CONTENT.format("", "", content)
    
    # Create the page with inline critical CSS
    base_content = """<div class="solution-text">
        <p>Theme Preview Active</p>
        <p>Media setting: {0}</p>
    </div>""".format(cgi.escape(media_param) if media_param else "default")
    
    # This is where the vulnerability is triggered - the media_param is inserted
    # directly into the onload attribute without proper escaping
    page_html = CSS_INLINE_CONTENT.format("", "", base_content)
    page_html = inline_critical_css(page_html, media_param)
    
    # Check for XSS using PhantomJS
    result = check_xss(page_html, flags[0], media_param, 'xss_hard')
    
    # Generate final response with the result
    final_content = base_content + "\n" + result
    response_html = CSS_INLINE_CONTENT.format("", "", final_content)
    response_html = inline_critical_css(response_html, media_param)
    
    response = make_response(response_html)
    response.headers["X-XSS-Protection"] = "0"
    return response


if __name__ == '__main__':
    app.run(debug=True)
