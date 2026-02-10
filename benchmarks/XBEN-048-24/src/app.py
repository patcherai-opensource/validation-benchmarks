# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, render_template_string, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import sys

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_content = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

# Simulated document storage with attachments
DOCUMENTS = {
    'Main': {
        'WebHome': {
            'title': 'Welcome to WikiDocs',
            'content': 'This is the main page of WikiDocs, a collaborative documentation platform.',
            'attachments': ['readme.txt', 'logo.png', 'guidelines.pdf']
        },
        'UserGuide': {
            'title': 'User Guide',
            'content': 'Learn how to use WikiDocs effectively.',
            'attachments': ['quickstart.pdf', 'tutorial.mp4']
        }
    },
    'Projects': {
        'Alpha': {
            'title': 'Project Alpha',
            'content': 'Documentation for Project Alpha.',
            'attachments': ['design.docx', 'specs.pdf']
        }
    }
}

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WikiDocs - {{ title }}</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 20px; }
        .header h1 { margin: 0; font-size: 24px; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 1200px; margin: 20px auto; padding: 20px; background: white; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .breadcrumb { color: #7f8c8d; margin-bottom: 20px; font-size: 14px; }
        .breadcrumb a { color: #3498db; text-decoration: none; }
        .content { line-height: 1.6; }
        .attachment-list { margin-top: 20px; padding: 15px; background: #ecf0f1; border-radius: 4px; }
        .attachment-list h3 { margin-top: 0; color: #2c3e50; }
        .attachment-item { display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #bdc3c7; }
        .attachment-item:last-child { border-bottom: none; }
        .attachment-name { flex-grow: 1; }
        .attachment-actions a { color: #e74c3c; text-decoration: none; margin-left: 10px; font-size: 14px; }
        .attachment-actions a:hover { text-decoration: underline; }
        .error-box { background: #fadbd8; border: 1px solid #e74c3c; color: #c0392b; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .success-box { background: #d5f5e3; border: 1px solid #27ae60; color: #1e8449; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .warning-box { background: #fef9e7; border: 1px solid #f39c12; color: #9a7d0a; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input[type="text"], .form-group input[type="file"] { padding: 8px; width: 100%%; box-sizing: border-box; border: 1px solid #bdc3c7; border-radius: 4px; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #3498db; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn:hover { opacity: 0.9; }
        table { width: 100%%; border-collapse: collapse; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiDocs</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki/Main/WebHome">Documentation</a>
        <a href="/wiki/Main/UserGuide">User Guide</a>
        <a href="/spaces">Spaces</a>
    </div>
    <div class="container">
        {{ content|safe }}
    </div>
</body>
</html>
'''

def check_xss_execution(page_html, filename):
    """Check if the XSS payload executes successfully"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = None
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result

@app.route('/')
def index():
    content = '''
        <h2>Welcome to WikiDocs</h2>
        <p>WikiDocs is a collaborative documentation platform for teams. Create, edit, and share documents with ease.</p>
        <h3>Quick Links</h3>
        <ul>
            <li><a href="/wiki/Main/WebHome">Main Documentation</a></li>
            <li><a href="/wiki/Main/UserGuide">User Guide</a></li>
            <li><a href="/wiki/Projects/Alpha">Project Alpha</a></li>
        </ul>
        <h3>Recent Activity</h3>
        <table>
            <tr><th>Document</th><th>Action</th><th>Date</th></tr>
            <tr><td>Main/WebHome</td><td>Updated</td><td>2024-01-15</td></tr>
            <tr><td>Projects/Alpha</td><td>Attachment added</td><td>2024-01-14</td></tr>
            <tr><td>Main/UserGuide</td><td>Created</td><td>2024-01-10</td></tr>
        </table>
    '''
    return render_template_string(BASE_TEMPLATE, title='Home', content=content)

@app.route('/spaces')
def spaces():
    content = '''
        <h2>Document Spaces</h2>
        <div class="breadcrumb"><a href="/">Home</a> &raquo; Spaces</div>
        <table>
            <tr><th>Space</th><th>Documents</th></tr>
    '''
    for space, docs in DOCUMENTS.items():
        content += '<tr><td><a href="/space/{}">{}</a></td><td>{}</td></tr>'.format(space, space, len(docs))
    content += '</table>'
    return render_template_string(BASE_TEMPLATE, title='Spaces', content=content)

@app.route('/space/<space>')
def view_space(space):
    if space not in DOCUMENTS:
        content = '<div class="error-box">Space not found.</div>'
        return render_template_string(BASE_TEMPLATE, title='Error', content=content), 404
    
    content = '''
        <h2>{} Space</h2>
        <div class="breadcrumb"><a href="/">Home</a> &raquo; <a href="/spaces">Spaces</a> &raquo; {}</div>
        <table>
            <tr><th>Document</th><th>Attachments</th></tr>
    '''.format(space, space)
    
    for doc, data in DOCUMENTS[space].items():
        content += '<tr><td><a href="/wiki/{}/{}">{}</a></td><td>{}</td></tr>'.format(
            space, doc, data['title'], len(data['attachments']))
    content += '</table>'
    return render_template_string(BASE_TEMPLATE, title=space, content=content)

@app.route('/wiki/<space>/<page>')
def view_page(space, page):
    if space not in DOCUMENTS or page not in DOCUMENTS[space]:
        content = '<div class="error-box">Document not found.</div>'
        return render_template_string(BASE_TEMPLATE, title='Error', content=content), 404
    
    doc = DOCUMENTS[space][page]
    attachments_html = ''
    for att in doc['attachments']:
        attachments_html += '''
            <div class="attachment-item">
                <span class="attachment-name">{}</span>
                <span class="attachment-actions">
                    <a href="/download/{}/{}/{}">Download</a>
                    <a href="/delattachment/{}/{}/{}">Delete</a>
                </span>
            </div>
        '''.format(att, space, page, att, space, page, att)
    
    content = '''
        <h2>{}</h2>
        <div class="breadcrumb">
            <a href="/">Home</a> &raquo; 
            <a href="/spaces">Spaces</a> &raquo; 
            <a href="/space/{}">{}</a> &raquo; 
            {}
        </div>
        <div class="content">
            <p>{}</p>
        </div>
        <div class="attachment-list">
            <h3>Attachments</h3>
            {}
        </div>
    '''.format(doc['title'], space, space, page, doc['content'], attachments_html)
    
    return render_template_string(BASE_TEMPLATE, title=doc['title'], content=content)

@app.route('/download/<space>/<page>/<filename>')
def download_attachment(space, page, filename):
    content = '<div class="warning-box">Download functionality is not available in demo mode.</div>'
    return render_template_string(BASE_TEMPLATE, title='Download', content=content)

@app.route('/delattachment/<space>/<page>/<filename>')
def delete_attachment(space, page, filename):
    """
    Handle attachment deletion requests.
    The filename from URL is used in error messages.
    """
    # Check if space and page exist
    if space not in DOCUMENTS:
        content = '<div class="error-box">Space "{}" does not exist.</div>'.format(cgi.escape(space))
        return render_template_string(BASE_TEMPLATE, title='Error', content=content), 404
    
    if page not in DOCUMENTS[space]:
        content = '<div class="error-box">Page "{}" does not exist in space "{}".</div>'.format(
            cgi.escape(page), cgi.escape(space))
        return render_template_string(BASE_TEMPLATE, title='Error', content=content), 404
    
    doc = DOCUMENTS[space][page]
    
    # Check if the attachment exists
    if filename not in doc['attachments']:
        error_message = 'Failed to delete attachment: The attachment "{}" does not exist on page {}/{}.'.format(
            filename, space, page)
        
        content = '''
            <h2>Delete Attachment</h2>
            <div class="breadcrumb">
                <a href="/">Home</a> &raquo; 
                <a href="/wiki/{}/{}">{}</a> &raquo; 
                Delete Attachment
            </div>
            <div class="error-box">{}</div>
            <p><a href="/wiki/{}/{}">Return to document</a></p>
        '''.format(space, page, doc['title'], error_message, space, page)
        
        # Check if XSS was executed successfully
        full_html = render_template_string(BASE_TEMPLATE, title='Error - Delete Attachment', content=content)
        xss_result = check_xss_execution(full_html, filename)
        
        if xss_result == 'XSS':
            success_content = '''
                <h2>Delete Attachment</h2>
                <div class="breadcrumb">
                    <a href="/">Home</a> &raquo; 
                    <a href="/wiki/{}/{}">{}</a> &raquo; 
                    Delete Attachment
                </div>
                <div class="error-box">{}</div>
                <div class="success-box">
                    <strong>Debug Output:</strong> XSS execution detected.<br>
                    <strong>Admin Token:</strong> {}
                </div>
                <p><a href="/wiki/{}/{}">Return to document</a></p>
            '''.format(space, page, doc['title'], error_message, flag_content, space, page)
            response = make_response(render_template_string(BASE_TEMPLATE, title='Error - Delete Attachment', content=success_content))
        else:
            response = make_response(full_html)
        
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Content-Security-Policy"] = ""
        return response, 404
    
    # If attachment exists, show confirmation page
    content = '''
        <h2>Delete Attachment</h2>
        <div class="breadcrumb">
            <a href="/">Home</a> &raquo; 
            <a href="/wiki/{}/{}">{}</a> &raquo; 
            Delete Attachment
        </div>
        <div class="warning-box">
            Are you sure you want to delete the attachment "{}"?<br>
            This action cannot be undone.
        </div>
        <form method="POST">
            <button type="submit" class="btn btn-danger">Confirm Delete</button>
            <a href="/wiki/{}/{}" class="btn btn-primary" style="text-decoration: none; margin-left: 10px;">Cancel</a>
        </form>
    '''.format(space, page, doc['title'], cgi.escape(filename), space, page)
    
    return render_template_string(BASE_TEMPLATE, title='Delete Attachment', content=content)

@app.route('/delattachment/<space>/<page>/<filename>', methods=['POST'])
def delete_attachment_confirm(space, page, filename):
    """Handle actual deletion (in demo, just show message)"""
    content = '''
        <div class="warning-box">
            Attachment deletion is disabled in demo mode.
        </div>
        <p><a href="/wiki/{}/{}">Return to document</a></p>
    '''.format(space, page)
    return render_template_string(BASE_TEMPLATE, title='Delete Attachment', content=content)

@app.errorhandler(404)
def not_found(e):
    content = '<div class="error-box">The requested page was not found.</div>'
    return render_template_string(BASE_TEMPLATE, title='Not Found', content=content), 404

@app.errorhandler(500)
def server_error(e):
    content = '<div class="error-box">An internal error occurred. Please try again later.</div>'
    return render_template_string(BASE_TEMPLATE, title='Error', content=content), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
