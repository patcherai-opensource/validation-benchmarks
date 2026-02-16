# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, url_for
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import time
import hashlib

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

_secret = open('secret.txt').read().strip()

app = Flask(__name__)

# Wiki page storage (in-memory for simplicity)
WIKI_PAGES = {
    'HomePage': {
        'content': 'Welcome to the wiki. This is a collaborative documentation platform.\n\nUse the navigation to browse pages or create new content.',
        'owner': 'admin',
        'time': '2024-11-02 08:30:00'
    },
    'DocumentationIndex': {
        'content': 'This page lists all available documentation.\n\n- Getting Started Guide\n- Configuration Reference\n- Extension Development\n- API Documentation',
        'owner': 'admin',
        'time': '2024-11-05 14:22:00'
    },
    'GettingStarted': {
        'content': 'To get started with the wiki, create a new page by navigating to a CamelCase URL.\n\nPages support attachments - use the attach handler to upload files to any page.',
        'owner': 'admin',
        'time': '2024-11-10 09:15:00'
    },
    'RecentChanges': {
        'content': 'Automatically generated page tracking recent modifications across the wiki.',
        'owner': 'system',
        'time': '2024-12-01 16:45:00'
    },
    'SandBox': {
        'content': 'This is a sandbox page for testing wiki features.\n\nFeel free to edit this page to experiment with formatting and attachments.',
        'owner': 'admin',
        'time': '2024-12-15 11:00:00'
    }
}

VALID_EXTENSIONS = {
    'jpg': 'JPEG Image',
    'jpeg': 'JPEG Image',
    'png': 'PNG Image',
    'gif': 'GIF Image',
    'pdf': 'PDF Document',
    'doc': 'Word Document',
    'docx': 'Word Document',
    'odt': 'OpenDocument Text',
    'txt': 'Plain Text',
    'csv': 'CSV File',
    'zip': 'ZIP Archive'
}

MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2MB


def render_wiki_header(page_tag=''):
    return u'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body {{ font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; background: #f5f5f5; }}
        .wiki-header {{ background: #2c3e50; color: #ecf0f1; padding: 10px 20px; margin-bottom: 20px; }}
        .wiki-header a {{ color: #ecf0f1; }}
        .wiki-header .brand {{ font-size: 1.4em; font-weight: bold; text-decoration: none; }}
        .wiki-header .nav-links {{ float: right; margin-top: 5px; }}
        .wiki-header .nav-links a {{ margin-left: 15px; text-decoration: none; }}
        .wiki-content {{ background: #fff; padding: 20px 30px; margin: 0 20px; border: 1px solid #ddd; border-radius: 4px; }}
        .page-actions {{ margin-top: 10px; padding: 10px 0; border-top: 1px solid #eee; font-size: 0.9em; }}
        .page-actions a {{ margin-right: 10px; }}
        .wiki-footer {{ margin: 20px; padding: 10px 0; border-top: 1px solid #ddd; font-size: 0.85em; color: #777; text-align: center; }}
        .upload-form {{ max-width: 600px; margin: 20px auto; }}
        .upload-form h3 {{ margin-bottom: 15px; color: #333; }}
        .page-list {{ list-style: none; padding: 0; }}
        .page-list li {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
        .page-list li a {{ text-decoration: none; color: #2980b9; }}
        .page-list li .meta {{ color: #999; font-size: 0.85em; margin-left: 10px; }}
    </style>
</head>
<body>
<div class="wiki-header">
    <a class="brand" href="/">WikiEngine</a>
    <span class="nav-links">
        <a href="/HomePage">Home</a>
        <a href="/RecentChanges">Recent Changes</a>
        <a href="/DocumentationIndex">Documentation</a>
    </span>
    <div style="clear:both"></div>
</div>
<div class="wiki-content">
'''.format(title='WikiEngine - ' + page_tag if page_tag else 'WikiEngine')


def render_wiki_footer(page_tag=''):
    actions = ''
    if page_tag and page_tag in WIKI_PAGES:
        actions = u'''<div class="page-actions">
            <a href="/{tag}/edit">Edit this page</a>
            <a href="/{tag}/revisions">Page history</a>
            <a href="/{tag}/attach?filename=document.txt">Attach a file</a>
        </div>'''.format(tag=page_tag)
    return u'''{actions}
</div>
<div class="wiki-footer">
    WikiEngine &mdash; powered by collaborative knowledge
</div>
</body>
</html>'''.format(actions=actions)


def evaluate_page_content(html_content):
    """Use headless browser to evaluate page content for dynamic elements."""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    result = ''
    try:
        of = open(fn, 'w')
        of.write(html_content)
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
    html = render_wiki_header()
    html += u'<h2>Welcome to WikiEngine</h2>'
    html += u'<p>A collaborative documentation and knowledge management platform.</p>'
    html += u'<h3>Wiki Pages</h3>'
    html += u'<ul class="page-list">'
    for tag in sorted(WIKI_PAGES.keys()):
        page = WIKI_PAGES[tag]
        html += u'<li><a href="/{tag}">{tag}</a><span class="meta">last edited {time} by {owner}</span></li>'.format(
            tag=tag, time=page['time'], owner=page['owner']
        )
    html += u'</ul>'
    html += render_wiki_footer()
    return html


@app.route('/api/pages')
def api_pages():
    """API endpoint listing available wiki pages."""
    import json
    pages = []
    for tag, info in WIKI_PAGES.items():
        pages.append({
            'tag': tag,
            'owner': info['owner'],
            'time': info['time']
        })
    resp = make_response(json.dumps({'pages': pages}))
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route('/<page_tag>/attach')
def render_attachment_form(page_tag):
    """Display the upload form for attaching a file to a wiki page."""
    if page_tag not in WIKI_PAGES:
        html = render_wiki_header(page_tag)
        html += u'<div class="alert alert-warning">Page <strong>{}</strong> does not exist.</div>'.format(
            cgi.escape(page_tag)
        )
        html += render_wiki_footer()
        return html, 404

    filename = request.args.get('filename', '')

    html = render_wiki_header(page_tag)

    # Render upload form heading with the filename
    html += u'<div class="upload-form">'
    html += u'<h3>Upload form for file ' + filename + '</h3>\n'
    html += u'<form enctype="multipart/form-data" name="frmUpload" method="POST" action="/{tag}/attach">\n'.format(tag=page_tag)
    html += u'    <input type="hidden" name="wiki" value="{tag}/attach" />\n'.format(tag=page_tag)
    html += u'    <input type="hidden" name="MAX_FILE_SIZE" value="{}" />\n'.format(MAX_UPLOAD_SIZE)
    html += u'    <input type="hidden" name="filename" value="{}" />\n'.format(cgi.escape(filename, quote=True))
    html += u'    <div class="form-group">'
    html += u'        <input type="file" name="upFile" class="form-control" />'
    html += u'    </div><br/>'
    html += u'    <input class="btn btn-primary" type="submit" value="Save" />\n'
    html += u'</form>\n'

    # Allowed extensions reference
    html += u'<div style="margin-top:15px;font-size:0.85em;color:#666;">'
    html += u'<strong>Allowed extensions:</strong> '
    exts = ['{} ({})'.format(ext, desc) for ext, desc in sorted(VALID_EXTENSIONS.items())]
    html += u', '.join(exts)
    html += u'</div>'

    html += u'<div style="margin-top:10px;"><a href="/{tag}">Back to page {tag}</a></div>'.format(tag=page_tag)
    html += u'</div>'

    # Server-side content validation
    full_page = html + render_wiki_footer(page_tag)
    eval_result = evaluate_page_content(full_page)
    if eval_result == 'XSS':
        html += u'<div class="alert alert-success" style="margin-top:20px;"><strong>Upload Token:</strong> {}</div>'.format(_secret)

    html += render_wiki_footer(page_tag)

    response = make_response(html)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


@app.route('/<page_tag>/attach', methods=['POST'])
def handle_attachment_upload(page_tag):
    """Handle file upload POST request."""
    if page_tag not in WIKI_PAGES:
        html = render_wiki_header(page_tag)
        html += u'<div class="alert alert-danger">Page does not exist.</div>'
        html += render_wiki_footer()
        return html, 404

    html = render_wiki_header(page_tag)
    html += u'<div class="alert alert-info">File upload processing is currently disabled in this instance.</div>'
    html += u'<div><a href="/{tag}">Back to page {tag}</a></div>'.format(tag=page_tag)
    html += render_wiki_footer(page_tag)
    return html


@app.route('/<page_tag>/edit')
def edit_page(page_tag):
    """Display page edit form."""
    if page_tag not in WIKI_PAGES:
        html = render_wiki_header(page_tag)
        html += u'<div class="alert alert-warning">Page <strong>{}</strong> does not exist. You can create it.</div>'.format(
            cgi.escape(page_tag)
        )
        content = ''
    else:
        html = render_wiki_header(page_tag)
        content = WIKI_PAGES[page_tag]['content']

    html += u'<h3>Editing: {}</h3>'.format(cgi.escape(page_tag))
    html += u'<form method="POST" action="/{tag}/edit">'.format(tag=page_tag)
    html += u'<textarea name="body" class="form-control" rows="15" style="font-family:monospace;">{}</textarea><br/>'.format(
        cgi.escape(content)
    )
    html += u'<input type="submit" class="btn btn-primary" value="Save" />'
    html += u' <a href="/{tag}" class="btn btn-default">Cancel</a>'.format(tag=page_tag)
    html += u'</form>'
    html += render_wiki_footer(page_tag)
    return html


@app.route('/<page_tag>/edit', methods=['POST'])
def save_page(page_tag):
    """Save page edit (in-memory only)."""
    body = request.form.get('body', '')
    WIKI_PAGES[page_tag] = {
        'content': body,
        'owner': 'anonymous',
        'time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    return redirect('/' + page_tag)


@app.route('/<page_tag>/revisions')
def page_revisions(page_tag):
    """Show page revision history."""
    html = render_wiki_header(page_tag)
    if page_tag not in WIKI_PAGES:
        html += u'<div class="alert alert-warning">Page does not exist.</div>'
    else:
        page = WIKI_PAGES[page_tag]
        html += u'<h3>Revision history: {}</h3>'.format(cgi.escape(page_tag))
        html += u'<table class="table table-striped">'
        html += u'<thead><tr><th>Date</th><th>Author</th><th>Action</th></tr></thead>'
        html += u'<tbody>'
        html += u'<tr><td>{time}</td><td>{owner}</td><td>Current version</td></tr>'.format(
            time=page['time'], owner=page['owner']
        )
        html += u'</tbody></table>'
    html += u'<div><a href="/{tag}">Back to page</a></div>'.format(tag=page_tag)
    html += render_wiki_footer(page_tag)
    return html


@app.route('/<page_tag>')
def view_page(page_tag):
    """View a wiki page."""
    # Don't match static files or known non-page routes
    if page_tag.startswith('static') or page_tag == 'api' or '.' in page_tag:
        return make_response('Not Found', 404)

    html = render_wiki_header(page_tag)
    if page_tag in WIKI_PAGES:
        page = WIKI_PAGES[page_tag]
        html += u'<h2>{}</h2>'.format(cgi.escape(page_tag))
        # Simple rendering: convert newlines to <br> and wrap in paragraphs
        content_html = cgi.escape(page['content']).replace('\n\n', '</p><p>').replace('\n', '<br/>')
        html += u'<div class="page-body"><p>{}</p></div>'.format(content_html)
        html += u'<div class="meta" style="margin-top:15px;color:#999;font-size:0.85em;">Last modified: {} by {}</div>'.format(
            page['time'], page['owner']
        )
    else:
        html += u'<div class="alert alert-info">Page <strong>{}</strong> doesn\'t exist yet. <a href="/{}/edit">Create it</a>.</div>'.format(
            cgi.escape(page_tag), page_tag
        )
    html += render_wiki_footer(page_tag)
    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
