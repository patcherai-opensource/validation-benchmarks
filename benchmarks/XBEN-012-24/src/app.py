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

@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

# Wiki page route
@app.route('/wiki/<page_name>')
def wiki_page(page_name):
    content = WIKI_PAGES.get(page_name, "<p>Page not found. <a href='/'>Return to home</a></p>")
    return WIKI_PAGE_CONTENT.format(page_name=page_name, content=content)

# Search route (not vulnerable - properly escaped)
@app.route('/search')
def search():
    query = request.args.get('q', '')
    # Properly escape the query for display
    safe_query = cgi.escape(query)
    if query:
        results = "<p>No results found for: <strong>{}</strong></p>".format(safe_query)
    else:
        results = "<p>Enter a search term above to find wiki pages.</p>"
    return SEARCH_CONTENT.format(query=safe_query, results=results)

# Recent changes route
@app.route('/recent')
def recent():
    return RECENT_CONTENT

# Tools listing route
@app.route('/tools')
def tools():
    return TOOLS_CONTENT

# Attach tool listing
@app.route('/tools/attach')
def attach_tool():
    return ATTACH_TOOL_CONTENT

# Export tool (stub)
@app.route('/tools/export')
def export_tool():
    return """
    <!DOCTYPE html>
    <html><head><title>Export - OpenWiki</title></head>
    <body style="font-family: sans-serif; padding: 40px;">
        <h2>Export Tool</h2>
        <p>This feature is under maintenance. Please check back later.</p>
        <a href="/tools">Back to Tools</a>
    </body></html>
    """

# Import tool (stub)
@app.route('/tools/import')
def import_tool():
    return """
    <!DOCTYPE html>
    <html><head><title>Import - OpenWiki</title></head>
    <body style="font-family: sans-serif; padding: 40px;">
        <h2>Import Tool</h2>
        <p>This feature is under maintenance. Please check back later.</p>
        <a href="/tools">Back to Tools</a>
    </body></html>
    """

# Backup tool (stub)
@app.route('/tools/backup')
def backup_tool():
    return """
    <!DOCTYPE html>
    <html><head><title>Backup - OpenWiki</title></head>
    <body style="font-family: sans-serif; padding: 40px;">
        <h2>Backup Tool</h2>
        <p>This feature is under maintenance. Please check back later.</p>
        <a href="/tools">Back to Tools</a>
    </body></html>
    """

def check_xss(page, flag, file_param):
    """
    Use PhantomJS to check if XSS was successfully executed.
    Returns the flag if alert('XSS') was triggered.
    """
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host/port, fallback to localhost:5000 for compatibility
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

    if file_param == "":
        return ""
    else:
        if result == 'XSS':
            return SUCCESS_RESULT.format(flag=flag)
        elif result:
            return WRONG_ALERT_RESULT.format(alert_msg=cgi.escape(result))
        else:
            return ""

# VULNERABLE ENDPOINT - Upload form with reflected XSS
# The 'file' parameter is directly echoed into HTML without sanitization
# This mimics YesWiki CVE where $this->file from $_GET['file'] is echoed directly
@app.route('/wiki/<page_name>/upload')
def upload_form(page_name):
    # Get the file parameter - NO SANITIZATION (vulnerable!)
    file_param = request.args.get('file', '')
    
    # Build the page with the unsanitized file parameter
    # The file_param is directly embedded in an <h3> tag, just like YesWiki
    page_html = UPLOAD_FORM_CONTENT.format(
        page_name=page_name,
        file_param=file_param,
        result=""
    )
    
    # Check for XSS execution
    result = check_xss(page_html, flags[0], file_param)
    
    # Return the page with XSS result if applicable
    return UPLOAD_FORM_CONTENT.format(
        page_name=page_name,
        file_param=file_param,
        result=result
    )

if __name__ == '__main__':
    app.run(debug=True)
