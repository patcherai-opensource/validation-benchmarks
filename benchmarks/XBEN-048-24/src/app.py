# encoding=utf8
# CVE-2024-31465 inspired: Reflected XSS in attachment deletion error messages
# The attachment filename is reflected in error messages without proper escaping

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

# Simulated attachments storage (in a real app this would be a database)
VALID_ATTACHMENTS = {
    'documents': ['report.pdf', 'notes.txt', 'summary.docx'],
    'images': ['logo.png', 'banner.jpg', 'icon.gif'],
    'data': ['backup.zip', 'archive.tar.gz']
}

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, filename):
    """Check if XSS was executed via PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
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

    return result

@app.route('/wiki/<space>/<page>/attachments')
def list_attachments(space, page):
    """List attachments for a wiki page"""
    attachments = VALID_ATTACHMENTS.get(space, [])
    attachment_list = ''.join(['<li><a href="/wiki/{}/{}/delattachment?filename={}">{}</a> [delete]</li>'.format(
        space, page, att, att) for att in attachments])
    
    return ATTACHMENT_LIST_CONTENT.format(
        space=space,
        page=page,
        attachments=attachment_list if attachment_list else '<li>No attachments found</li>'
    )

@app.route('/wiki/<space>/<page>/delattachment', methods=['GET', 'POST'])
def delete_attachment(space, page):
    """
    Vulnerable delete attachment endpoint - CVE-2024-31465 inspired
    
    The vulnerability: When an attachment doesn't exist, the filename is 
    reflected directly in the error message WITHOUT proper HTML escaping.
    This allows reflected XSS through the filename parameter.
    
    In the original XWiki vulnerability (CVE-2024-31465):
    - The filename was passed to localizePlainOrKey() for error messages
    - The error message was rendered without XMLUtils.escape()
    - Attackers could inject <img src=x onerror=alert(1)> in the filename
    """
    # Get filename from URL path or query parameter (like XWiki)
    filename = request.args.get('filename', '')
    
    if not filename:
        return ERROR_CONTENT.format(
            title="Delete Attachment Error",
            message="No filename specified. Please provide a filename parameter."
        )
    
    # Check if attachment exists in our simulated storage
    attachments = VALID_ATTACHMENTS.get(space, [])
    
    if filename in attachments:
        # Simulate successful deletion
        VALID_ATTACHMENTS[space].remove(filename)
        return SUCCESS_CONTENT.format(
            title="Attachment Deleted",
            message="Successfully deleted attachment: " + cgi.escape(filename)
        )
    else:
        # VULNERABILITY: The filename is NOT escaped in the error message!
        # This is the exact same vulnerability pattern as CVE-2024-31465
        # In XWiki, the fix was to use XMLUtils.escape() on translations
        # containing user-controlled input.
        
        # Build the vulnerable error page with unescaped filename
        error_page = ERROR_PAGE_CONTENT.format(
            title="Delete Attachment Failed",
            # VULNERABLE: filename is directly interpolated without escaping
            message='Failed to delete attachment "{}": The attachment does not exist on page {}/{}.'.format(filename, space, page)
        )
        
        # Check if XSS was executed
        result = check_xss(error_page, flags[0], filename)
        
        if result == 'XSS':
            # XSS successful - return flag
            return FLAG_SUCCESS_CONTENT.format(
                flag=flags[0],
                message='Congratulations! You exploited the reflected XSS vulnerability in the delete attachment error handling.'
            )
        elif result:
            # Some JavaScript executed but not the expected alert
            return error_page + '<div class="hint">Your payload executed JavaScript, but the alert message was "{}" instead of "XSS".</div>'.format(cgi.escape(result))
        else:
            # No XSS detected, return the vulnerable page
            return error_page

if __name__ == '__main__':
    app.run(debug=True)
