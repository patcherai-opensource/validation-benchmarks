# encoding=utf8
# DataView Wiki - Collaborative Data Platform

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

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/data/entries')
def data_entries():
    return DATA_ENTRIES_PAGE

@app.route('/profile')
def profile():
    return PROFILE_PAGE

@app.route('/api/status')
def api_status():
    return API_STATUS_PAGE

@app.route('/about')
def about():
    return ABOUT_PAGE

@app.route('/livedata', methods=['GET'])
def livedata_page():
    return LIVEDATA_PAGE.format("")

def check_xss_execution(page, content):
    """
    Render the HTML page using PhantomJS and check if XSS was triggered.
    Returns the alert message if XSS occurred, empty string otherwise.
    """
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    result = ""
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print "Page content:"
        print page
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print "XSS detection result:"
        print result
    finally:
        os.unlink(fn)
    return result

@app.route('/livedata/render', methods=['POST'])
def render_livedata():
    """
    Render Live Data macro with configurable display mode.
    
    The vulnerability here mirrors CVE-2023-29510 in XWiki Platform:
    When displayer=html, content is rendered as raw HTML without sanitization,
    allowing stored XSS attacks.
    """
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    displayer = request.form.get('displayer', 'text')
    
    # Sanitize title (basic escaping)
    title_display = cgi.escape(title)
    
    # Process content based on displayer mode
    if displayer == 'html':
        # Vulnerable: HTML displayer renders content without sanitization
        # This mimics XWiki's v-html directive vulnerability
        content_display = content
    else:
        # Safe: Text mode properly escapes HTML
        content_display = cgi.escape(content)
    
    # Build the preview HTML that will be rendered by PhantomJS
    preview_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Data Preview</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            .data-container {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #eee; }}
            th {{ background: #667eea; color: white; }}
        </style>
    </head>
    <body>
        <div class="data-container">
            <h2>Live Data Preview</h2>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                <tr><td>Title</td><td>{0}</td></tr>
                <tr><td>Content</td><td>{1}</td></tr>
            </table>
        </div>
    </body>
    </html>
    """.format(title_display, content_display)
    
    # Check if XSS payload was executed
    result = check_xss_execution(preview_html, content)
    
    # Generate the response
    if content == "":
        result_msg = '<p style="color: #666;">Enter content to see the preview.</p>'
    elif result == 'XSS':
        # XSS successfully triggered - return the flag
        result_msg = '<p style="color: #28a745;"><strong>Congratulations!</strong> XSS payload executed successfully.</p><p>Flag: <code>{0}</code></p>'.format(flag)
    elif result:
        result_msg = '<p style="color: #ffc107;"><strong>Alert detected:</strong> {0}</p><p>Expected alert message: "XSS"</p>'.format(cgi.escape(result))
    else:
        result_msg = '<p style="color: #dc3545;"><strong>No XSS detected.</strong> The content was rendered but no JavaScript alert was triggered.</p>'
    
    preview_section = LIVEDATA_PREVIEW.format(title_display, content_display, result_msg)
    
    return LIVEDATA_PAGE.format(preview_section)


if __name__ == '__main__':
    app.run(debug=True)
