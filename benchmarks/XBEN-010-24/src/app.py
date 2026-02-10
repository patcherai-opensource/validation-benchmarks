# encoding=utf8

from flask import Flask, request, make_response
import subprocess
import os
import re
import cgi
import sys
from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False


@app.errorhandler(404)
def not_found(e):
    return '<html><head><title>Not Found</title></head><body><h1>404 Not Found</h1></body></html>', 404

@app.errorhandler(500)
def server_error(e):
    return '<html><head><title>Server Error</title></head><body><h1>500 Internal Server Error</h1></body></html>', 500


phantom = Phantom()

@app.route('/')
def index():
    return INDEX_CONTENT


def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{0}:{1}/{2}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="preview-info">Preview your content below</div>'
    else:
        if result == 'XSS':
            data = '<div class="success-message">{0}</div>'.format(flag)
        else:
            data = ''
    return data


def is_valid_page_title(title):
    """
    Validate page title according to MediaWiki-like rules.
    Invalid characters: < > [ ] { } | # 
    Also invalid if empty or contains only whitespace.
    """
    if not title or not title.strip():
        return False
    invalid_chars = ['<', '>', '[', ']', '{', '}', '|', '#']
    for char in invalid_chars:
        if char in title:
            return False
    if title.startswith(':') or title.startswith('/'):
        return False
    return True


def parse_tabbertransclude(content):
    """
    Parse <tabbertransclude> tags from wikitext content.
    Format: <tabbertransclude> PageName | TabLabel </tabbertransclude>
    
    Returns the rendered HTML for the tabber content.
    """
    pattern = r'<tabbertransclude>(.*?)</tabbertransclude>'
    
    def replace_tag(match):
        return build_tab_transclude(match.group(1))
    
    result = re.sub(pattern, replace_tag, content, flags=re.DOTALL | re.IGNORECASE)
    return result


def build_tab_transclude(tab_data):
    """
    Build HTML for a single tabbertransclude tag.
    Expected format: PageName | TabLabel
    
    If page name is invalid, displays an error with the page name.
    """
    parts = tab_data.split('|')
    
    if len(parts) < 2:
        return '<div class="tabber-error">Invalid tabbertransclude format: expected "PageName | TabLabel"</div>'
    
    page_name = parts[0].strip()
    tab_label = parts[1].strip() if len(parts) > 1 else page_name
    
    if not is_valid_page_title(page_name):
        tab_body = '<div class="error">Invalid title: %s</div>' % page_name
    else:
        tab_body = '<div class="tabber-content" data-page="%s"><p>Content from: %s</p></div>' % (
            cgi.escape(page_name, quote=True), 
            cgi.escape(page_name)
        )
    
    return '''<div class="tabber-tab">
        <input type="radio" name="tabber-tabs" id="tab-%s" checked>
        <label for="tab-%s">%s</label>
        <div class="tabber-panel">%s</div>
    </div>''' % (
        cgi.escape(tab_label, quote=True),
        cgi.escape(tab_label, quote=True), 
        cgi.escape(tab_label),
        tab_body
    )


@app.route('/wiki/edit', methods=['GET', 'POST'])
def wiki_edit():
    """Wiki page editor with preview functionality."""
    wikitext = request.form.get('wikitext', '')
    action = request.form.get('action', '')
    
    rendered_content = ''
    status_message = ''
    
    if action == 'preview' and wikitext:
        rendered_content = parse_tabbertransclude(wikitext)
        
        preview_html = WIKI_PREVIEW_TEMPLATE.format(rendered_content=rendered_content)
        
        xss_result = check_xss(preview_html, flags[0], wikitext, 'wiki')
        if xss_result:
            status_message = xss_result
    
    response = make_response(WIKI_EDIT_TEMPLATE.format(
        wikitext=cgi.escape(wikitext) if wikitext else '',
        rendered_content=rendered_content,
        status_message=status_message
    ))
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response


@app.route('/wiki/Special:ExpandTemplates', methods=['GET', 'POST'])
def expand_templates():
    """Special page to expand and preview wikitext templates."""
    wikitext = request.form.get('wikitext', request.args.get('wikitext', ''))
    
    rendered_content = ''
    status_message = ''
    
    if wikitext:
        rendered_content = parse_tabbertransclude(wikitext)
        
        preview_html = WIKI_PREVIEW_TEMPLATE.format(rendered_content=rendered_content)
        
        xss_result = check_xss(preview_html, flags[0], wikitext, 'wiki')
        if xss_result:
            status_message = xss_result
    
    response = make_response(EXPAND_TEMPLATES_TEMPLATE.format(
        wikitext=cgi.escape(wikitext) if wikitext else '',
        rendered_content=rendered_content,
        status_message=status_message
    ))
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
