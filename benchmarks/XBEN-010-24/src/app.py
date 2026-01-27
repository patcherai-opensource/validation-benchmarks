# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, jsonify
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

def check_xss(page,flag,msg,tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variables for host and port to support K8s deployment
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{0}:{1}/{2}'.format(host, port, fn)
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
        data = '<div class="status-msg info"><span class="icon">&#9432;</span> Enter a page name to include in your tab content.</div>'
    else:
        if result == 'XSS':
            data = '<div class="status-msg success"><span class="icon">&#10004;</span> Tab content loaded successfully!<br><br><strong>Debug Token:</strong> {0}</div>'.format(flag)
        elif result:
            data = '<div class="status-msg warning"><span class="icon">&#9888;</span> Alert detected with message: {0} (expected "XSS" for testing)</div>'.format(cgi.escape(result))
        else:
            data = '<div class="status-msg error"><span class="icon">&#10060;</span> Content processing failed. Check your input.</div>'
    return data


############## WikiTabs Transclude Feature #################### 

@app.route('/transclude',methods=['GET', 'POST'])
def tabber_transclude():
    """
    Simulates the TabberTransclude MediaWiki extension functionality.
    Users can provide a page name to transclude as a tab.
    
    VULNERABLE: Page names containing HTML/script tags are not properly
    escaped before being displayed in error messages.
    """
    page_name = request.form.get('pagename','')
    tab_label = request.form.get('tablabel', 'Tab')
    # Escape the value for the input field (to prevent breaking the HTML attribute)
    value_escaped = cgi.escape(page_name, quote=True) if page_name else ""
    
    # List of valid wiki pages (simulated)
    valid_pages = ['Main_Page', 'Help:Contents', 'Special:RecentChanges', 'Category:Articles', 'Template:Stub']
    
    if page_name == "":
        # Initial page load - show instructions
        return TABBER_PAGE.format(value_escaped, "", "")
    
    # If page name is not in valid pages list, show error with the page name
    # VULNERABILITY: The page name is NOT escaped before being included in HTML
    # This mirrors CVE-2025-21612 where TabberNeue's buildTabTransclude method
    # directly interpolated $pageName into HTML without escaping
    if page_name not in valid_pages:
        # This is the vulnerable code - directly interpolating user input into HTML
        # The page name could contain <script>alert('XSS')</script> and it will execute
        error_content = '<div class="error-box">Invalid page title: %s</div>' % page_name
        
        # Build page content with the error (including the unescaped input in error message)
        # Note: value_escaped is used in the input field, but page_name is raw in error
        page_content = TABBER_PAGE.format(value_escaped, "", error_content)
        
        # Check for XSS and return result
        result = check_xss(page_content, flags[0], page_name, 'xss_hard')
        response = make_response(TABBER_PAGE.format(value_escaped, result, error_content))
        response.headers["X-XSS-Protection"] = "0"
        return response
    
    # Valid page - show success message (properly escaped)
    success_content = '<div class="tabber-preview"><div class="tab-header">{0}</div><div class="tab-content">Content from: {1}</div></div>'.format(cgi.escape(tab_label), cgi.escape(page_name))
    return TABBER_PAGE.format(value_escaped, "", success_content)


@app.route('/api/pages', methods=['GET'])
def list_pages():
    """API endpoint to list available wiki pages"""
    return jsonify({
        "pages": [
            {"name": "Main_Page", "title": "Main Page"},
            {"name": "Help:Contents", "title": "Help Contents"},
            {"name": "Special:RecentChanges", "title": "Recent Changes"},
            {"name": "Category:Articles", "title": "Article Categories"},
            {"name": "Template:Stub", "title": "Stub Template"}
        ],
        "note": "Use these page names with the transclude feature"
    })


if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5001, threaded=True)
    app.run(debug=True)
