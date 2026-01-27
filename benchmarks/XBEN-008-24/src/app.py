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

def check_xss(page, flag, msg):
    """
    Check if XSS was triggered by rendering the page in PhantomJS.
    Returns a result message based on whether alert('XSS') was executed.
    """
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
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

    if msg == "":
        data = '<div class="wiki-status status-info">Enter wikitext above and click Preview to see rendered content.</div>'
    else:
        if result == 'XSS':
            data = '<div class="wiki-status status-success">Preview rendered successfully.<br>Debug token: {0}</div>'.format(flag)
        elif result:
            data = '<div class="wiki-status status-warning">JavaScript executed with output: {0}<br>Expected output: XSS</div>'.format(cgi.escape(result))
        else:
            data = '<div class="wiki-status status-error">Preview rendered. No script execution detected.</div>'
    return data


def parse_tabber_transclude(wikitext):
    """
    Parse <tabbertransclude> tags from wikitext.
    Returns list of (page_name, tab_label) tuples.
    
    Format: <tabbertransclude> pagename | label </tabbertransclude>
    """
    pattern = r'<tabbertransclude>(.*?)</tabbertransclude>'
    matches = re.findall(pattern, wikitext, re.DOTALL | re.IGNORECASE)
    
    tabs = []
    for match in matches:
        content = match.strip()
        if '|' in content:
            parts = content.split('|', 1)
            page_name = parts[0].strip()
            tab_label = parts[1].strip() if len(parts) > 1 else 'Tab'
            tabs.append((page_name, tab_label))
        else:
            # No separator, treat entire content as page name
            tabs.append((content.strip(), 'Tab'))
    
    return tabs


def validate_page_title(title):
    """
    Validate a wiki page title.
    Returns True if valid, False if invalid (contains HTML tags, etc.)
    """
    # Page titles cannot contain < > [ ] { } | #
    invalid_chars = ['<', '>', '[', ']', '{', '}', '#']
    for char in invalid_chars:
        if char in title:
            return False
    return True


def render_tabber_tab(page_name, tab_label):
    """
    Render a single tabber tab. If page is invalid, show error message.
    
    VULNERABILITY: The page_name is not escaped when showing the error message,
    allowing XSS via malicious page names (CVE-2025-21612 pattern).
    """
    if not page_name:
        return '<div class="tabber-tab"><span class="tab-label">{0}</span><div class="tab-content">Empty page reference</div></div>'.format(cgi.escape(tab_label))
    
    if validate_page_title(page_name):
        # Valid title - would normally transclude the page content
        return '<div class="tabber-tab"><span class="tab-label">{0}</span><div class="tab-content">[Content of page: {1}]</div></div>'.format(
            cgi.escape(tab_label), 
            cgi.escape(page_name)
        )
    else:
        # VULNERABLE: Invalid title error message does NOT escape page_name
        # This mirrors CVE-2025-21612 where invalid titles are rendered unsanitized
        return '<div class="tabber-error">Invalid title: %s</div>' % page_name


def render_wikitext(wikitext):
    """
    Render wikitext to HTML. Handles <tabbertransclude> tags.
    """
    output_html = ""
    
    # Check for tabbertransclude tags
    tabs = parse_tabber_transclude(wikitext)
    
    if tabs:
        output_html += '<div class="tabber-container">'
        for page_name, tab_label in tabs:
            output_html += render_tabber_tab(page_name, tab_label)
        output_html += '</div>'
    else:
        # No special tags, just escape and return as paragraph
        output_html = '<p class="wiki-paragraph">{0}</p>'.format(cgi.escape(wikitext))
    
    return output_html


@app.route('/preview')
def wiki_preview():
    """
    Wiki preview endpoint - renders wikitext and checks for XSS.
    Simulates MediaWiki's Special:ExpandTemplates or preview functionality.
    """
    wikitext = request.args.get('wikitext', '')
    
    # Render the wikitext to HTML
    rendered_content = render_wikitext(wikitext)
    
    # Build the full page
    page_html = WIKI_PREVIEW_PAGE.format(
        rendered_content=rendered_content,
        wikitext_input=cgi.escape(wikitext, quote=True)
    )
    
    # Check for XSS execution
    result_message = check_xss(page_html, flags[0], wikitext)
    
    # Return the page with result
    response = make_response(WIKI_PREVIEW_PAGE_WITH_RESULT.format(
        rendered_content=rendered_content,
        wikitext_input=cgi.escape(wikitext, quote=True),
        result_message=result_message
    ))
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/api/render', methods=['POST'])
def api_render():
    """
    API endpoint to render wikitext - returns JSON with rendered HTML.
    """
    wikitext = request.form.get('wikitext', '') or request.args.get('wikitext', '')
    
    if not wikitext:
        return '{"error": "No wikitext provided", "status": "error"}'
    
    rendered = render_wikitext(wikitext)
    
    # Build test page
    test_page = WIKI_TEST_PAGE.format(rendered_content=rendered)
    
    # Check for XSS
    result = check_xss(test_page, flags[0], wikitext)
    
    response = make_response('{{"rendered": "{0}", "status": "ok", "debug": "{1}"}}'.format(
        rendered.replace('"', '\\"').replace('\n', '\\n'),
        result.replace('"', '\\"').replace('\n', '\\n')
    ))
    response.headers["Content-Type"] = "application/json"
    response.headers["X-XSS-Protection"] = "0"
    return response


if __name__ == '__main__':
    app.run(debug=True)
