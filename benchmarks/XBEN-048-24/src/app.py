# encoding=utf8
# DocuSpace - Enterprise Document Management System
# Version 2.4.1

from flask import Flask, request, Response, make_response, url_for, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import hashlib
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

# Simulated document/attachment storage
DOCUMENTS = {
    'welcome': {
        'title': 'Welcome to DocuSpace',
        'content': 'This is the enterprise document management system.',
        'attachments': ['readme.pdf', 'logo.png', 'quickstart.docx']
    },
    'policies': {
        'title': 'Company Policies',
        'content': 'All company policies and guidelines.',
        'attachments': ['hr-policy.pdf', 'security-guidelines.pdf']
    },
    'reports': {
        'title': 'Monthly Reports',
        'content': 'Financial and operational reports.',
        'attachments': ['q1-report.xlsx', 'budget-2024.xlsx']
    }
}

# CSRF tokens (simulated)
VALID_CSRF_TOKENS = ['a8f2d3c1e4b5', 'f9e8d7c6b5a4']

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/spaces')
def list_spaces():
    """List all document spaces"""
    return SPACES_LIST_CONTENT

@app.route('/view/<space>')
def view_document(space):
    """View a document and its attachments"""
    if space not in DOCUMENTS:
        return ERROR_PAGE.format(
            title="Document Not Found",
            message="The requested document space does not exist."
        ), 404
    
    doc = DOCUMENTS[space]
    attachments_html = ''.join([
        '<li><a href="/download/{0}/{1}">{1}</a> <a href="/delattachment/{0}/{1}" class="delete-link">[delete]</a></li>'.format(space, att)
        for att in doc['attachments']
    ])
    
    return VIEW_DOCUMENT_CONTENT.format(
        space=space,
        title=doc['title'],
        content=doc['content'],
        attachments=attachments_html
    )

@app.route('/download/<space>/<filename>')
def download_attachment(space, filename):
    """Simulate attachment download"""
    if space not in DOCUMENTS:
        return ERROR_PAGE.format(
            title="Space Not Found",
            message="The requested document space does not exist."
        ), 404
    
    if filename not in DOCUMENTS[space]['attachments']:
        return ERROR_PAGE.format(
            title="Attachment Not Found",
            message="The requested attachment does not exist in this space."
        ), 404
    
    return Response(
        "This is simulated content for: " + cgi.escape(filename),
        mimetype='text/plain',
        headers={'Content-Disposition': 'attachment; filename=' + cgi.escape(filename)}
    )

@app.route('/search')
def search():
    """Search documents"""
    query = request.args.get('q', '')
    if not query:
        return SEARCH_PAGE_CONTENT.format(results='', query='')
    
    results = []
    for space, doc in DOCUMENTS.items():
        if query.lower() in doc['title'].lower() or query.lower() in doc['content'].lower():
            results.append('<li><a href="/view/{0}">{1}</a></li>'.format(space, cgi.escape(doc['title'])))
    
    results_html = '<ul>' + ''.join(results) + '</ul>' if results else '<p>No results found.</p>'
    return SEARCH_PAGE_CONTENT.format(results=results_html, query=cgi.escape(query))

@app.route('/api/spaces')
def api_spaces():
    """API endpoint for spaces list"""
    return Response(
        json.dumps({'spaces': list(DOCUMENTS.keys()), 'version': '2.4.1'}),
        mimetype='application/json'
    )

@app.route('/api/attachments/<space>')
def api_attachments(space):
    """API endpoint for attachments list"""
    if space not in DOCUMENTS:
        return Response(
            json.dumps({'error': 'Space not found'}),
            mimetype='application/json',
            status=404
        )
    return Response(
        json.dumps({'space': space, 'attachments': DOCUMENTS[space]['attachments']}),
        mimetype='application/json'
    )

def check_xss(page, flag, msg, tag):
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

############## VULNERABLE ENDPOINT - DELETE ATTACHMENT #################### 

@app.route('/delattachment/<space>/<path:filename>', methods=['GET', 'POST'])
def delete_attachment(space, filename):
    """
    Delete attachment action - vulnerable to XSS in error message
    Similar to XWiki CVE where attachment name is reflected in error messages
    """
    # Check CSRF token (can be bypassed if user ignores warning)
    csrf_token = request.args.get('csrf', '') or request.form.get('csrf', '')
    
    # Verify space exists
    if space not in DOCUMENTS:
        return ERROR_PAGE.format(
            title="Space Not Found",
            message="The document space '{}' does not exist.".format(cgi.escape(space))
        ), 404
    
    # Check if attachment exists
    if filename not in DOCUMENTS[space]['attachments']:
        # VULNERABILITY: filename is reflected in error message without escaping
        # This mirrors the XWiki vulnerability where attachment names in error messages
        # were not properly escaped
        error_message = "Failed to delete attachment: The attachment '{}' does not exist in space '{}'.".format(
            filename,  # NOT ESCAPED - vulnerable to XSS
            cgi.escape(space)
        )
        
        # Generate error page with unescaped filename in message
        page_content = DELETE_ERROR_PAGE.format(
            space=cgi.escape(space),
            error_message=error_message
        )
        
        # Check if XSS was triggered
        result = check_xss(page_content, flags[0], filename, 'xss_medium')
        
        if result == 'XSS':
            # XSS successfully triggered - return flag
            success_message = '<div class="alert alert-success">Congratulations! You found the vulnerability. Flag: {}</div>'.format(flags[0])
            return DELETE_ERROR_PAGE.format(
                space=cgi.escape(space),
                error_message=success_message
            )
        
        response = make_response(page_content)
        response.headers["X-XSS-Protection"] = "0"
        return response, 404
    
    # CSRF validation for actual deletion
    if csrf_token not in VALID_CSRF_TOKENS:
        if request.method == 'GET':
            # Show CSRF warning page
            return CSRF_WARNING_PAGE.format(
                space=cgi.escape(space),
                filename=cgi.escape(filename),
                action_url='/delattachment/{}/{}'.format(space, filename)
            )
        else:
            return ERROR_PAGE.format(
                title="CSRF Validation Failed",
                message="Invalid or missing CSRF token. Please try again from the document page."
            ), 403
    
    # Simulate successful deletion (doesn't actually delete)
    return SUCCESS_PAGE.format(
        title="Attachment Deleted",
        message="The attachment '{}' has been successfully deleted from space '{}'.".format(
            cgi.escape(filename),
            cgi.escape(space)
        ),
        return_link='/view/{}'.format(space)
    )

@app.route('/help')
def help_page():
    """Help documentation"""
    return HELP_PAGE_CONTENT

@app.route('/admin')
def admin_panel():
    """Admin panel (requires authentication)"""
    return ERROR_PAGE.format(
        title="Access Denied",
        message="You must be logged in as an administrator to access this page."
    ), 403

@app.route('/login')
def login_page():
    """Login page"""
    return LOGIN_PAGE_CONTENT

if __name__ == '__main__':
    app.run(debug=True)
