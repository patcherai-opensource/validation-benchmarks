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

@app.route('/pages')
def pages():
    return PAGES_CONTENT

@app.route('/pages/<page_name>')
def page_view(page_name):
    # Sanitized page view - safe endpoint
    safe_name = cgi.escape(page_name)
    content_map = {
        'MainPage': 'Welcome to OpenWiki! This is the main page of your wiki. You can edit this page to add content.',
        'GettingStarted': 'To get started with OpenWiki, first create your user account, then start creating and editing pages.',
        'Installation': 'Installation requires Python 2.7+ and a web server. Follow the setup instructions in the documentation.',
        'Configuration': 'Configuration is done via the config.yaml file. See the API documentation for available options.',
        'APIReference': 'The API provides RESTful endpoints for managing wiki content programmatically.',
        'Troubleshooting': 'If you encounter issues, check the logs at /var/log/openwiki/ or contact support.',
        'RecentChanges': 'No recent changes to display.'
    }
    page_content = content_map.get(safe_name, 'Page not found.')
    return PAGE_VIEW_CONTENT.format(safe_name, page_content)

@app.route('/api/status')
def api_status():
    return Response(API_STATUS_CONTENT, mimetype='application/json')

@app.route('/api/pages')
def api_pages():
    pages_data = {
        "pages": [
            {"name": "MainPage", "modified": "2024-01-15"},
            {"name": "GettingStarted", "modified": "2024-01-14"},
            {"name": "Installation", "modified": "2024-01-12"}
        ],
        "total": 3
    }
    return jsonify(pages_data)

@app.route('/api/attachments')
def api_attachments():
    attachments_data = {
        "attachments": [
            {"name": "readme.pdf", "size": "125 KB"},
            {"name": "logo.png", "size": "45 KB"}
        ],
        "total": 2
    }
    return jsonify(attachments_data)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # Sanitized search - safe endpoint
    safe_query = cgi.escape(query)
    if safe_query:
        result = 'No results found for: ' + safe_query
    else:
        result = 'Enter a search query above.'
    return SEARCH_CONTENT.format(result)

@app.route('/help')
def help_page():
    return HELP_CONTENT

@app.route('/tools/attach')
def attach_list():
    return ATTACH_LIST_CONTENT

# Vulnerable endpoint - mimics YesWiki attach.lib.php showUploadForm
# The 'file' parameter is reflected directly into the HTML without proper sanitization
@app.route('/tools/attach/upload')
def upload_form():
    # Get the 'file' parameter - this is the vulnerable sink
    file_param = request.args.get('file', '')
    
    # Weak filtering attempt - only removes script tags (can be bypassed with event handlers)
    file_param = re.sub(r'<script[^>]*>.*?</script>|<script[^>]*>', '', file_param, flags=re.IGNORECASE | re.DOTALL)
    
    # Value attribute for the input field
    value_attr = "" if file_param == "" else 'value="{0}"'.format(file_param)
    
    # Build the page with the reflected parameter in the h3 tag (similar to YesWiki CVE)
    data = UPLOAD_FORM_CONTENT.format(file_param, "", value_attr)
    result = check_xss(data, flags[0], file_param, 'xss_easy_med')
    return UPLOAD_FORM_CONTENT.format(file_param, result, value_attr)

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host, fallback to localhost for local development
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

    if msg == "":
        data = '<div class="result-box" style="background: #e8f4f8;"><p>Ready to upload files. Specify a filename to begin.</p></div>'
    else:
        if result == 'XSS':
            data = '<div class="result-box" style="background: #d4edda;"><p style="color: #155724;"><strong>Security Test Passed!</strong></p><p>Flag: {0}</p></div>'.format(flag)
        elif result:
            data = '<div class="result-box" style="background: #fff3cd;"><p style="color: #856404;">Alert detected with content: {0}</p></div>'.format(cgi.escape(result))
        else:
            data = '<div class="result-box" style="background: #f8d7da;"><p style="color: #721c24;">No XSS detected. Try again.</p></div>'
    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
