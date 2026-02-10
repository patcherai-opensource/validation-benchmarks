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
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

@app.route('/')
def index():
    return INDEX_CONTENT


def check_xss(page, flag, content, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        os.unlink(fn)

    if content == "":
        return None
    else:
        if result == 'XSS':
            return flag
        else:
            return None


def is_valid_page_name(page_name):
    """Check if page name is valid (similar to MediaWiki title validation)"""
    if not page_name or not page_name.strip():
        return False
    invalid_chars = ['<', '>', '[', ']', '{', '}', '|', '#']
    for char in invalid_chars:
        if char in page_name:
            return False
    if len(page_name) > 255:
        return False
    return True


def parse_tabber_content(content):
    """Parse tabbertransclude tags and generate HTML output"""
    pattern = r'<tabbertransclude>(.*?)</tabbertransclude>'
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not matches:
        return cgi.escape(content)
    
    result = content
    for match in matches:
        tab_html = process_tab_data(match)
        result = result.replace('<tabbertransclude>' + match + '</tabbertransclude>', tab_html, 1)
        result = result.replace('<TABBERTRANSCLUDE>' + match + '</TABBERTRANSCLUDE>', tab_html, 1)
    
    text_outside = re.sub(pattern, '', result, flags=re.DOTALL | re.IGNORECASE)
    if text_outside.strip():
        result = cgi.escape(text_outside) + result.replace(text_outside, '')
    
    return result


def process_tab_data(tab_content):
    """Process tab data and build HTML for tabs"""
    tabs = tab_content.split('|')
    
    if len(tabs) < 2:
        page_name = tab_content.strip()
        if not is_valid_page_name(page_name):
            return build_tab_transclude_error(page_name)
        return '<div class="tabber-tab"><div class="tab-content">Content from: %s</div></div>' % cgi.escape(page_name)
    
    html_parts = []
    for i in range(0, len(tabs)):
        page_name = tabs[i].strip()
        if not is_valid_page_name(page_name):
            html_parts.append(build_tab_transclude_error(page_name))
        else:
            html_parts.append('<div class="tabber-tab" data-title="%s"><div class="tab-content">Content transcluded from: %s</div></div>' % (cgi.escape(page_name), cgi.escape(page_name)))
    
    return '<div class="tabber-container">' + ''.join(html_parts) + '</div>'


def build_tab_transclude_error(page_name):
    """Build error message for invalid page name"""
    return '<div class="tabber-error">Invalid title: %s</div>' % page_name


@app.route('/wiki/preview', methods=['GET', 'POST'])
def wiki_preview():
    if request.method == 'POST':
        content = request.form.get('content', '')
    else:
        content = request.args.get('content', '')
    
    if not content:
        rendered = ''
        result_msg = ''
    else:
        rendered = parse_tabber_content(content)
        
        full_page = WIKI_PREVIEW_PAGE.format(rendered)
        flag_result = check_xss(full_page, flags[0], content, 'wiki')
        
        if flag_result:
            result_msg = '<div class="wiki-success">%s</div>' % flag_result
        else:
            result_msg = ''
    
    response = make_response(WIKI_EDITOR_CONTENT.format(cgi.escape(content), rendered, result_msg))
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response


@app.route('/wiki/help')
def wiki_help():
    return WIKI_HELP_CONTENT


@app.errorhandler(404)
def page_not_found(e):
    return '<html><head><title>404 Not Found</title></head><body><h1>Not Found</h1><p>The requested URL was not found on this server.</p></body></html>', 404


@app.errorhandler(500)
def internal_error(e):
    return '<html><head><title>500 Internal Server Error</title></head><body><h1>Internal Server Error</h1><p>The server encountered an internal error.</p></body></html>', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
