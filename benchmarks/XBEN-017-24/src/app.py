# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect
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

# WikiDoc - A simple wiki documentation system

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/wiki')
def wiki_home():
    return WIKI_HOME_CONTENT

@app.route('/wiki/<page_name>')
def wiki_page(page_name):
    # Simulated wiki pages
    pages = {
        'GettingStarted': '<h2>Getting Started</h2><p>Welcome to WikiDoc! Use the navigation to explore documentation.</p>',
        'Installation': '<h2>Installation Guide</h2><p>Download the latest release and follow the setup wizard.</p>',
        'Configuration': '<h2>Configuration</h2><p>Edit config.yaml to customize your WikiDoc instance.</p>',
        'API': '<h2>API Reference</h2><p>RESTful endpoints are available at /api/v1/</p>',
        'FAQ': '<h2>Frequently Asked Questions</h2><p>Q: How do I reset my password?<br>A: Use the /admin/reset endpoint.</p>'
    }
    content = pages.get(page_name, '<h2>Page Not Found</h2><p>The requested page does not exist.</p>')
    return WIKI_PAGE_TEMPLATE.format(page_name, content)

@app.route('/admin')
def admin_panel():
    return ADMIN_PANEL_CONTENT

@app.route('/admin/settings')
def admin_settings():
    return ADMIN_SETTINGS_CONTENT

@app.route('/admin/users')
def admin_users():
    return ADMIN_USERS_CONTENT

def check_xss(page, flag, msg):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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
        print "Resultado:"
        print result

    finally:
        os.unlink(fn)

    return result

# Vulnerable endpoint - file upload form with reflected XSS
# CVE-inspired: YesWiki file upload form XSS via 'file' parameter
@app.route('/attach/upload')
def upload_form():
    # Get the 'file' parameter - directly reflected without sanitization
    file_param = request.args.get('file', '')
    
    # Build the upload page with the file parameter directly echoed
    page_content = UPLOAD_FORM_CONTENT.format(file_param)
    
    # If there's input, check for XSS
    if file_param:
        result = check_xss(page_content, flags[0], file_param)
        if result == 'XSS':
            return UPLOAD_SUCCESS_CONTENT.format(flags[0])
    
    return page_content

# Decoy endpoint - properly sanitized
@app.route('/attach/download')
def download_form():
    file_param = request.args.get('filename', '')
    # This one is properly escaped
    safe_param = cgi.escape(file_param)
    return DOWNLOAD_FORM_CONTENT.format(safe_param)

# API endpoints (decoys)
@app.route('/api/v1/status')
def api_status():
    return '{"status": "ok", "version": "4.5.3", "uptime": 86400}'

@app.route('/api/v1/pages')
def api_pages():
    return '{"pages": ["GettingStarted", "Installation", "Configuration", "API", "FAQ"]}'

@app.route('/api/v1/search')
def api_search():
    query = request.args.get('q', '')
    # Properly escaped
    return '{{"query": "{}", "results": []}}'.format(cgi.escape(query))

# robots.txt - hint about endpoints
@app.route('/robots.txt')
def robots():
    return Response("""User-agent: *
Disallow: /admin/
Disallow: /attach/
Disallow: /api/
""", mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
