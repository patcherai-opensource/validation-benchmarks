# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import time
import hashlib

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

secret_data = open('secret.txt').read().strip()

app = Flask(__name__)

phantom = Phantom()

WIKI_PAGES = {
    'Main': {
        'title': 'Welcome to OpenDocs',
        'content': '<p>OpenDocs is a collaborative documentation platform. Use the navigation to browse available documents.</p><p>Features include document sharing, version history, and collaborative editing.</p>',
        'author': 'Admin',
        'modified': '2024-01-15 09:30:00'
    },
    'GettingStarted': {
        'title': 'Getting Started Guide',
        'content': '<p>Welcome to OpenDocs! This guide will help you get started with the platform.</p><h3>Creating Documents</h3><p>Navigate to any space and use the create button to add new pages.</p><h3>Sharing Documents</h3><p>Use the <em>Share</em> feature to send documents to colleagues via email notification.</p>',
        'author': 'Admin',
        'modified': '2024-01-12 14:20:00'
    },
    'UserGuide': {
        'title': 'User Guide',
        'content': '<p>This document covers advanced features of the OpenDocs platform.</p><h3>Permissions</h3><p>Documents can be shared with specific users or groups.</p><h3>Email Notifications</h3><p>Users can be notified about document updates via the built-in notification system.</p>',
        'author': 'DocumentationTeam',
        'modified': '2024-02-01 11:45:00'
    },
    'ReleaseNotes': {
        'title': 'Release Notes - v3.2.1',
        'content': '<p>This release includes bug fixes and performance improvements.</p><ul><li>Fixed issue with document export</li><li>Improved search indexing performance</li><li>Updated notification templates</li></ul>',
        'author': 'Admin',
        'modified': '2024-02-10 16:00:00'
    }
}

WIKI_SPACES = {
    'Main': ['Main', 'GettingStarted'],
    'Documentation': ['UserGuide', 'ReleaseNotes']
}


def render_page_chrome(title, body_content, page_name='Main', extra_head=''):
    nav_items = ''
    for space, pages in WIKI_SPACES.items():
        nav_items += '<li class="nav-space"><strong>{}</strong><ul>'.format(cgi.escape(space))
        for p in pages:
            pg = WIKI_PAGES.get(p, {})
            active = ' class="active"' if p == page_name else ''
            nav_items += '<li{}><a href="/doc/view/{}">{}</a></li>'.format(
                active, urllib.quote(p), cgi.escape(pg.get('title', p)))
        nav_items += '</ul></li>'

    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - OpenDocs</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #2c3e50; color: #fff; padding: 10px 20px; display: flex; align-items: center; justify-content: space-between; }}
        .header h1 {{ font-size: 1.3em; }}
        .header h1 a {{ color: #fff; text-decoration: none; }}
        .header nav a {{ color: #ecf0f1; margin-left: 15px; text-decoration: none; font-size: 0.9em; }}
        .header nav a:hover {{ text-decoration: underline; }}
        .container {{ display: flex; max-width: 1200px; margin: 0 auto; }}
        .sidebar {{ width: 250px; background: #fff; border-right: 1px solid #ddd; padding: 15px; min-height: calc(100vh - 50px); }}
        .sidebar ul {{ list-style: none; }}
        .sidebar .nav-space {{ margin-bottom: 12px; }}
        .sidebar .nav-space > strong {{ font-size: 0.85em; color: #7f8c8d; text-transform: uppercase; }}
        .sidebar .nav-space ul {{ margin-top: 4px; }}
        .sidebar .nav-space li {{ padding: 3px 0; }}
        .sidebar .nav-space li a {{ color: #2c3e50; text-decoration: none; font-size: 0.9em; }}
        .sidebar .nav-space li a:hover {{ color: #3498db; }}
        .sidebar .nav-space li.active a {{ color: #3498db; font-weight: bold; }}
        .main-content {{ flex: 1; padding: 20px; }}
        .doc-header {{ border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: flex-start; }}
        .doc-header h2 {{ font-size: 1.5em; color: #2c3e50; }}
        .doc-meta {{ color: #999; font-size: 0.8em; margin-top: 3px; }}
        .doc-actions {{ display: flex; gap: 8px; }}
        .doc-actions a {{ padding: 6px 12px; background: #3498db; color: #fff; border-radius: 4px; text-decoration: none; font-size: 0.85em; }}
        .doc-actions a:hover {{ background: #2980b9; }}
        .doc-actions a.secondary {{ background: #95a5a6; }}
        .doc-actions a.secondary:hover {{ background: #7f8c8d; }}
        .doc-body {{ background: #fff; padding: 20px; border-radius: 4px; border: 1px solid #ddd; line-height: 1.6; }}
        .doc-body h3 {{ color: #2c3e50; margin: 15px 0 8px; }}
        .doc-body ul {{ margin: 8px 0 8px 25px; }}
        .xform {{ background: #fff; padding: 20px; border-radius: 4px; border: 1px solid #ddd; }}
        .xform dl {{ margin-bottom: 15px; }}
        .xform dt {{ font-weight: bold; margin-bottom: 4px; color: #2c3e50; }}
        .xform dt .hint {{ font-weight: normal; color: #999; font-size: 0.85em; display: block; }}
        .xform dd {{ margin-bottom: 10px; }}
        .xform input[type="text"], .xform input[type="email"], .xform textarea {{ width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 3px; font-size: 0.95em; }}
        .xform textarea {{ resize: vertical; }}
        .xform .btn {{ padding: 8px 18px; background: #3498db; color: #fff; border: none; border-radius: 3px; cursor: pointer; font-size: 0.95em; }}
        .xform .btn:hover {{ background: #2980b9; }}
        .xform .btn-secondary {{ background: #95a5a6; }}
        .xform .btn-secondary:hover {{ background: #7f8c8d; }}
        .infomessage {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 10px 15px; border-radius: 3px; margin-bottom: 10px; }}
        .errormessage {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 10px 15px; border-radius: 3px; margin-bottom: 10px; }}
        .back-link {{ margin-top: 15px; display: inline-block; }}
        .back-link a {{ color: #3498db; text-decoration: none; }}
        .back-link a:hover {{ text-decoration: underline; }}
        .footer {{ text-align: center; padding: 15px; color: #999; font-size: 0.8em; border-top: 1px solid #ddd; margin-top: 20px; }}
        label {{ font-size: 0.9em; }}
        label input[type="radio"], label input[type="checkbox"] {{ margin-right: 4px; }}
        .form-buttons {{ margin-top: 15px; display: flex; gap: 8px; }}
    </style>
    {extra_head}
</head>
<body>
    <div class="header">
        <h1><a href="/">OpenDocs</a></h1>
        <nav>
            <a href="/doc/view/Main">Home</a>
            <a href="/spaces">Spaces</a>
        </nav>
    </div>
    <div class="container">
        <div class="sidebar">
            <ul>{nav_items}</ul>
        </div>
        <div class="main-content">
            {body_content}
        </div>
    </div>
    <div class="footer">
        OpenDocs Platform v3.2.1 &copy; 2024
    </div>
</body>
</html>'''.format(
        title=cgi.escape(title),
        nav_items=nav_items,
        body_content=body_content,
        extra_head=extra_head
    )


@app.route('/')
def index():
    return redirect('/doc/view/Main')


@app.route('/doc/view/<page_name>', methods=['GET'])
def view_document(page_name):
    page = WIKI_PAGES.get(page_name)
    if not page:
        body = '<div class="doc-header"><h2>Page Not Found</h2></div>'
        body += '<div class="doc-body"><p>The requested document does not exist.</p></div>'
        return render_page_chrome('Not Found', body, page_name), 404

    viewer = request.args.get('viewer', '')

    if viewer == 'notify':
        return handle_notify(page_name, page)

    body = '<div class="doc-header">'
    body += '<div><h2>{}</h2>'.format(cgi.escape(page['title']))
    body += '<div class="doc-meta">Last modified by {} on {}</div></div>'.format(
        cgi.escape(page['author']), cgi.escape(page['modified']))
    body += '<div class="doc-actions">'
    body += '<a href="/doc/view/{}?viewer=notify">Share</a>'.format(urllib.quote(page_name))
    body += '<a href="/doc/view/{}" class="secondary">History</a>'.format(urllib.quote(page_name))
    body += '</div>'
    body += '</div>'
    body += '<div class="doc-body">{}</div>'.format(page['content'])

    return render_page_chrome(page['title'], body, page_name)


def validate_email_format(addr):
    addr = addr.strip()
    if '@' not in addr:
        return False
    parts = addr.split('@')
    if len(parts) != 2:
        return False
    local, domain = parts
    if not local or not domain:
        return False
    if '.' not in domain:
        return False
    return True


def handle_notify(page_name, page):
    send = request.args.get('dispatch', request.form.get('dispatch', ''))

    if send:
        recipients_raw = request.values.getlist('recipient')
        message = request.values.get('message', '').strip()
        include_mode = request.values.get('includeContent', 'link')

        errors = {}
        successes = []

        for raw_val in recipients_raw:
            for recipient in raw_val.split(','):
                recipient = recipient.strip()
                if not recipient:
                    continue
                if not validate_email_format(recipient):
                    errors[recipient] = 'Invalid email address format'
                else:
                    email_hash = hashlib.md5(recipient.encode('utf-8')).hexdigest()[:8]
                    successes.append(recipient)

        body = ''

        if successes:
            names = ', '.join([cgi.escape(s) for s in successes])
            body += '<div class="infomessage">Notification sent successfully to: {}</div>'.format(names)

        if errors:
            for recipient, error in errors.items():
                body += '<div class="errormessage">Failed to send notification to {}: {}</div>'.format(
                    recipient, error)

        body += '<div class="back-link"><a href="/doc/view/{}">&larr; Back to <em>{}</em></a></div>'.format(
            urllib.quote(page_name), cgi.escape(page['title']))

        result = check_xss_in_response(body)

        if result:
            body = ''
            if result == 'XSS':
                body += '<div class="infomessage">System credential retrieved: {}</div>'.format(secret_data)
            body += '<div class="back-link"><a href="/doc/view/{}">&larr; Back to <em>{}</em></a></div>'.format(
                urllib.quote(page_name), cgi.escape(page['title']))

        return render_page_chrome('Notification - ' + page['title'], body, page_name)

    body = '<div class="doc-header"><h2>Share: {}</h2></div>'.format(cgi.escape(page['title']))
    body += '''<form class="xform" action="/doc/view/{page}?viewer=notify" method="get">
        <input type="hidden" name="viewer" value="notify" />
        <input type="hidden" name="dispatch" value="1" />
        <dl>
            <dt>
                <label for="notifyRecipient">Recipients</label>
                <span class="hint">Enter email addresses separated by commas, or usernames of registered users.</span>
            </dt>
            <dd>
                <input type="text" id="notifyRecipient" name="recipient" placeholder="user@example.com" />
            </dd>
            <dt>
                <label for="includeContent">Include document content</label>
            </dt>
            <dd>
                <label><input type="radio" name="includeContent" value="link" checked /> Include link only</label>
            </dd>
            <dd>
                <label><input type="radio" name="includeContent" value="inline" /> Include full content</label>
            </dd>
            <dt>
                <label for="message">Message</label>
            </dt>
            <dd>
                <textarea name="message" rows="4" cols="60" placeholder="Add an optional message...">I would like to share this document with you.</textarea>
            </dd>
        </dl>
        <div class="form-buttons">
            <button type="submit" class="btn">Send Notification</button>
            <a href="/doc/view/{page}" class="btn btn-secondary" style="text-decoration:none;">Cancel</a>
        </div>
    </form>'''.format(page=urllib.quote(page_name))

    return render_page_chrome('Share - ' + page['title'], body, page_name)


def check_xss_in_response(html_fragment):
    full_page = render_page_chrome('Notification Result', html_fragment, 'Main')

    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/'.format(host, port) + fn

    result = ''
    try:
        of = open(fn, 'w')
        of.write(full_page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        output = proc.stdout.read()
        for line in output.strip().split('\n'):
            line = line.strip()
            if line and line != 'success' and line != 'fail':
                result = line
                break
    except:
        result = ''
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    return result


@app.route('/spaces')
def list_spaces():
    body = '<div class="doc-header"><h2>Document Spaces</h2></div>'
    body += '<div class="doc-body"><ul>'
    for space, pages in WIKI_SPACES.items():
        body += '<li><strong>{}</strong><ul>'.format(cgi.escape(space))
        for p in pages:
            pg = WIKI_PAGES.get(p, {})
            body += '<li><a href="/doc/view/{}">{}</a></li>'.format(
                urllib.quote(p), cgi.escape(pg.get('title', p)))
        body += '</ul></li>'
    body += '</ul></div>'
    return render_page_chrome('Document Spaces', body)


@app.route('/ping')
def health_ping():
    return 'OK', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
