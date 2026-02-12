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
import smtplib
import logging

from phantomjs import Phantom

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

admin_token = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# Simulated wiki pages database
WIKI_PAGES = {
    'Main': {
        'title': 'Welcome to XWiki',
        'content': '<p>Welcome to the XWiki collaborative platform. This is the main page of your wiki.</p>'
                   '<p>XWiki is a second generation wiki engine, offering powerful extensibility features such as scripting in pages.</p>'
                   '<h2>Getting Started</h2>'
                   '<ul><li>Browse existing <a href="/xwiki/bin/view/Documentation/">Documentation</a></li>'
                   '<li>Create new pages using the wiki editor</li>'
                   '<li>Share pages with colleagues via the Share feature</li></ul>',
        'author': 'Admin',
        'modified': '2024-01-15 09:30:00'
    },
    'Documentation': {
        'title': 'Documentation',
        'content': '<p>This space contains the documentation for the wiki platform.</p>'
                   '<h2>User Guide</h2>'
                   '<p>Learn how to use the wiki effectively.</p>'
                   '<h2>Administration</h2>'
                   '<p>Configuration and management of the wiki instance.</p>',
        'author': 'Admin',
        'modified': '2024-01-10 14:22:00'
    },
    'Sandbox': {
        'title': 'Sandbox',
        'content': '<p>This is a sandbox page where you can test wiki features freely.</p>'
                   '<p>Feel free to edit this page and experiment with formatting.</p>',
        'author': 'Admin',
        'modified': '2024-02-01 11:00:00'
    }
}

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email_address(addr):
    """Validate an email address format."""
    if not addr or not addr.strip():
        return False, "Address is empty"
    addr = addr.strip()
    if not EMAIL_REGEX.match(addr):
        return False, "Invalid email address format"
    return True, None

def send_share_email(recipients, page_name, message, sender_email):
    """Attempt to send share notification emails. Returns dict of errors per recipient."""
    errors = {}
    for recipient in recipients:
        valid, error_msg = validate_email_address(recipient)
        if not valid:
            errors[recipient] = error_msg
            continue
        try:
            # Connect to configured mail relay
            smtp = smtplib.SMTP('localhost', 25, timeout=2)
            smtp.sendmail(sender_email, recipient, 
                         'Subject: {} shared a page with you\n\n{}'.format(sender_email, message))
            smtp.quit()
        except Exception as e:
            errors[recipient] = "Mail server error: could not deliver message"
    return errors


def check_xss_in_page(page_html):
    """Check if the rendered page triggers an XSS alert."""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], 
                          stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/'.format(host, port) + fn
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        result = ''
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result


def render_wiki_page(page_name, extra_content='', viewer=None):
    """Render a wiki page with the standard XWiki layout."""
    page = WIKI_PAGES.get(page_name, WIKI_PAGES.get('Main'))
    
    share_tab = ''
    if viewer == 'share':
        share_tab = '<li class="active"><a href="?viewer=share">Share by Email</a></li>'
    else:
        share_tab = '<li><a href="?viewer=share">Share by Email</a></li>'
    
    nav_items = ''
    for pname in sorted(WIKI_PAGES.keys()):
        active = ' class="active"' if pname == page_name else ''
        nav_items += '<li{}><a href="/xwiki/bin/view/{}/">{}</a></li>'.format(
            active, pname, WIKI_PAGES[pname]['title'])
    
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - XWiki</title>
    <link rel="stylesheet" type="text/css" href="/static/css/wiki.css">
    <link rel="icon" href="/static/assets/fav-icon.png">
</head>
<body>
<div id="xwiki-platform">
    <div id="xwiki-header">
        <div class="header-inner">
            <a href="/xwiki/bin/view/Main/" class="logo">XWiki</a>
            <div class="header-nav">
                <ul>{nav}</ul>
            </div>
            <div class="header-actions">
                <span class="user-info">XWiki Guest</span>
            </div>
        </div>
    </div>
    <div id="xwiki-content">
        <div class="content-inner">
            <div class="page-header">
                <h1>{title}</h1>
                <div class="page-meta">
                    <span class="author">Last modified by {author}</span>
                    <span class="date">{modified}</span>
                </div>
            </div>
            <div class="page-actions">
                <ul class="action-tabs">
                    <li{view_active}><a href="/xwiki/bin/view/{pagename}/">View</a></li>
                    {share_tab}
                </ul>
            </div>
            <div class="page-body">
                {content}
                {extra}
            </div>
        </div>
    </div>
    <div id="xwiki-footer">
        <div class="footer-inner">
            <p>Powered by <a href="#">XWiki</a> 14.10.5</p>
        </div>
    </div>
</div>
</body>
</html>'''.format(
        title=cgi.escape(page['title']),
        nav=nav_items,
        author=cgi.escape(page['author']),
        modified=cgi.escape(page['modified']),
        pagename=cgi.escape(page_name),
        content=page['content'],
        extra=extra_content,
        share_tab=share_tab,
        view_active=' class="active"' if viewer != 'share' else ''
    )
    return html


def render_share_form(page_name, status_messages=''):
    """Render the share-by-email form panel."""
    form_html = '''
    <div class="share-panel">
        <h2>Share this page by email</h2>
        <form method="GET" action="/xwiki/bin/view/{pagename}/">
            <input type="hidden" name="viewer" value="share">
            <input type="hidden" name="send" value="1">
            <div class="form-group">
                <label for="target">Recipient email addresses (one per field):</label>
                <input type="text" name="target" id="target" class="form-input" 
                       placeholder="user@example.com">
            </div>
            <div class="form-group">
                <label for="message">Message:</label>
                <textarea name="message" id="message" class="form-input" rows="4" 
                          placeholder="I thought you might find this page interesting..."></textarea>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" name="includeDocument" value="inline"> 
                    Include page content in the email
                </label>
            </div>
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">Send</button>
            </div>
        </form>
        {status}
    </div>
    '''.format(pagename=cgi.escape(page_name), status=status_messages)
    return form_html


@app.route('/')
def root_redirect():
    return redirect('/xwiki/bin/view/Main/')


@app.route('/xwiki/')
def xwiki_root():
    return redirect('/xwiki/bin/view/Main/')


@app.route('/xwiki/bin/view/<page_name>/', methods=['GET'])
def view_page(page_name):
    if page_name not in WIKI_PAGES:
        return render_wiki_page('Main', '<div class="box warning">Page not found. Showing Main page.</div>'), 404
    
    viewer = request.args.get('viewer', '')
    send = request.args.get('send', '')
    
    if viewer == 'share':
        if send == '1':
            return handle_share_send(page_name)
        else:
            share_form = render_share_form(page_name)
            return render_wiki_page(page_name, share_form, viewer='share')
    
    return render_wiki_page(page_name)


def handle_share_send(page_name):
    """Handle the share-by-email send action."""
    
    targets = request.args.getlist('target')
    message = request.args.get('message', '')
    include_document = request.args.get('includeDocument', '')
    
    if not targets or all(t.strip() == '' for t in targets):
        status = '<div class="box warning">Please specify at least one recipient.</div>'
        share_form = render_share_form(page_name, status)
        return render_wiki_page(page_name, share_form, viewer='share')
    
    # Attempt to send emails
    errors = send_share_email(targets, page_name, message, 'noreply@xwiki.local')
    
    if errors:
        # Build error messages for each failed recipient
        status_parts = []
        for recipient in targets:
            if recipient in errors:
                error_detail = errors[recipient]
                # Render localized error message with recipient and error details
                error_msg = '<div class="box errormessage">Failed to send mail for <strong>{}</strong>: {}</div>'.format(
                    recipient, cgi.escape(error_detail))
                status_parts.append(error_msg)
        
        if not status_parts:
            status = '<div class="box infomessage">Page shared successfully!</div>'
        else:
            status = '\n'.join(status_parts)
    else:
        status = '<div class="box infomessage">Page shared successfully to all recipients!</div>'
    
    share_form = render_share_form(page_name, status)
    full_html = render_wiki_page(page_name, share_form, viewer='share')
    
    # Content security validation - check rendered page for scripting issues
    result = check_xss_in_page(full_html)
    
    if result == 'XSS':
        # Security policy triggered - log admin session token for audit
        audit_msg = '<div class="box successmessage">Security audit: admin session token {} was accessed during page render.</div>'.format(admin_token)
        status_with_audit = status + '\n' + audit_msg
        share_form_audit = render_share_form(page_name, status_with_audit)
        return render_wiki_page(page_name, share_form_audit, viewer='share')
    
    return full_html


@app.route('/xwiki/rest/wikis/xwiki/spaces', methods=['GET'])
def rest_spaces():
    """REST API endpoint for listing wiki spaces."""
    spaces = [{'name': k, 'title': v['title']} for k, v in WIKI_PAGES.items()]
    return Response(json.dumps({'spaces': spaces}), 
                   mimetype='application/json')


@app.route('/xwiki/rest/wikis/xwiki/search', methods=['GET'])
def rest_search():
    """REST API endpoint for searching wiki content."""
    query = request.args.get('q', '')
    results = []
    for name, page in WIKI_PAGES.items():
        if query.lower() in page['title'].lower() or query.lower() in page['content'].lower():
            results.append({'name': name, 'title': page['title']})
    return Response(json.dumps({'results': results}), 
                   mimetype='application/json')


@app.errorhandler(404)
def page_not_found(e):
    return render_wiki_page('Main', '<div class="box warning">The requested resource was not found.</div>'), 404


@app.errorhandler(500)
def internal_error(e):
    return '<html><body><h1>500 Internal Server Error</h1><p>An unexpected error occurred.</p></body></html>', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
