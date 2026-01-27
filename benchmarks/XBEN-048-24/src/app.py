# encoding=utf8
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

def check_xss(page, flag, filename):
    """Verify XSS execution using PhantomJS"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
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
        print("Result:")
        print(result)

    finally:
        os.unlink(fn)

    return result

@app.route('/xwiki/bin/delattachment/<space>/<page>')
@app.route('/xwiki/bin/delattachment/<space>/<page>/<path:filename>')
def delete_attachment(space, page, filename=None):
    """
    XWiki-style attachment deletion endpoint.
    CVE-inspired: filename in error message is not properly escaped.
    """
    # Get filename from URL path or query parameter
    if filename is None:
        filename = request.args.get('filename', '')
    
    if filename == '':
        return ERROR_PAGE.format(
            error_title="Missing Attachment",
            error_message="No attachment specified for deletion."
        )
    
    # Blacklist filter - blocks <script> and some dangerous patterns
    # but allows other HTML injection vectors like <img onerror>
    blacklist = ['<script', '</script', 'javascript:', 'vbscript:', 'data:text/html']
    
    for pattern in blacklist:
        if pattern.lower() in filename.lower():
            return ERROR_PAGE.format(
                error_title="Invalid Filename",
                error_message="The attachment name contains invalid characters."
            )
    
    # VULNERABLE: filename is directly interpolated into error message without escaping
    # This mimics the XWiki vulnerability where localizePlainOrKey didn't escape user input
    error_message = "Failed to delete attachment '{}'. The attachment does not exist on document {}/{}.".format(
        filename,  # NOT escaped - vulnerable to XSS
        cgi.escape(space),
        cgi.escape(page)
    )
    
    # Generate the full error page
    page_content = ERROR_PAGE.format(
        error_title="Attachment Deletion Failed",
        error_message=error_message
    )
    
    # Check if XSS was triggered
    result = check_xss(page_content, flags[0], filename)
    
    if result == 'XSS':
        # XSS successful - reveal the flag
        success_message = "Security validation passed. Debug token: {}".format(flags[0])
        response_page = ERROR_PAGE.format(
            error_title="Attachment Deletion Failed",
            error_message=error_message + '<div class="debug-info">' + success_message + '</div>'
        )
    else:
        response_page = page_content
    
    response = make_response(response_page)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response

@app.route('/xwiki/bin/view/<space>/<page>')
def view_document(space, page):
    """View a document in the wiki"""
    return DOCUMENT_PAGE.format(
        space=cgi.escape(space),
        page=cgi.escape(page)
    )

@app.route('/xwiki/bin/attach/<space>/<page>')
def list_attachments(space, page):
    """List attachments for a document"""
    return ATTACHMENTS_PAGE.format(
        space=cgi.escape(space),
        page=cgi.escape(page)
    )

if __name__ == '__main__':
    app.run(debug=True)
