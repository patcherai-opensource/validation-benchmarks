# encoding=utf8
# Simulates CVE-2025-21612: TabberNeue XSS vulnerability
# User input in tabbertransclude tag is directly embedded without escaping

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

def check_xss(page, flag, msg, tag):
    """Check if the page triggers an XSS alert"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variables for host and port to support K8s deployment
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{0}:{1}/{2}'.format(host, port, fn)
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
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Submit a tabbertransclude tag to render content.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You triggered alert with "{1}" instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Content rendered. No XSS detected.</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


def is_valid_page_title(title):
    """
    Simulates MediaWiki title validation.
    MediaWiki rejects titles with certain characters like < > # { } [ ] etc.
    Titles containing HTML tags like <script> are invalid.
    This simulates how invalid page names trigger the error path in TabberNeue.
    """
    # MediaWiki rejects titles with these characters
    # Note: < and > make the title invalid, which is crucial for the XSS vulnerability
    # When a title like "<script>alert(1)</script>" is used, it's invalid
    # and gets reflected in the error message without escaping
    invalid_chars = ['<', '>', '#', '{', '}', '[', ']']
    for char in invalid_chars:
        if char in title:
            return False
    # Also reject empty titles
    if not title or title.isspace():
        return False
    return True


def parse_tabbertransclude(content):
    """
    Parse tabbertransclude content similar to TabberNeue extension.
    Format: <tabbertransclude> pagename | label </tabbertransclude>
    Returns list of (pagename, label) tuples
    """
    tabs = []
    # Split by newlines for multiple tabs
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Parse format: pagename | label
        if '|' in line:
            parts = line.split('|', 1)
            pagename = parts[0].strip()
            label = parts[1].strip() if len(parts) > 1 else pagename
        else:
            pagename = line.strip()
            label = pagename
        tabs.append((pagename, label))
    return tabs


def build_tab_transclude(pagename, label):
    """
    Simulates TabberNeue's buildTabTransclude method.
    VULNERABLE: When page title is invalid, the pagename is embedded
    directly into HTML without escaping (CVE-2025-21612).
    """
    if is_valid_page_title(pagename):
        # Valid title - would normally transclude the page content
        # Here we just show a placeholder for the page content
        tab_body = '<div class="tabber-tab">Content of page: {}</div>'.format(cgi.escape(pagename))
    else:
        # VULNERABLE: Invalid title is embedded without escaping
        # This is exactly the vulnerability from CVE-2025-21612
        # Before the fix: sprintf('<div class="error">Invalid title: %s</div>', $pageName)
        tab_body = '<div class="error">Invalid title: %s</div>' % pagename
    
    return '''
    <div class="tabber-tab-panel" data-title="{label}">
        {body}
    </div>
    '''.format(label=cgi.escape(label), body=tab_body)


def render_tabbertransclude(content):
    """
    Render a tabbertransclude tag similar to MediaWiki's TabberNeue extension.
    """
    tabs = parse_tabbertransclude(content)
    if not tabs:
        return '<div class="error">No tabs defined</div>'
    
    rendered_tabs = []
    for pagename, label in tabs:
        rendered_tabs.append(build_tab_transclude(pagename, label))
    
    return '''
    <div class="tabber-wrapper">
        <div class="tabber-tabs">
            {tabs}
        </div>
    </div>
    '''.format(tabs=''.join(rendered_tabs))


@app.route('/wiki', methods=['GET', 'POST'])
def wiki_editor():
    """
    Simulates a wiki editor that processes tabbertransclude tags.
    This is the main entry point for the CVE-2025-21612 vulnerability.
    """
    wikitext = request.form.get('wikitext', '')
    value = "" if wikitext == "" else wikitext
    
    rendered_content = ""
    result_message = ""
    
    if wikitext:
        # Parse and process tabbertransclude tags
        # Look for <tabbertransclude>...</tabbertransclude> pattern
        pattern = r'<tabbertransclude>(.*?)</tabbertransclude>'
        matches = re.findall(pattern, wikitext, re.DOTALL | re.IGNORECASE)
        
        if matches:
            for match in matches:
                rendered_content += render_tabbertransclude(match)
        else:
            # If no tabbertransclude tag, just show the raw content escaped
            rendered_content = '<div class="wiki-content">{}</div>'.format(cgi.escape(wikitext))
        
        # Build the full page for XSS checking
        full_page = WIKI_PAGE_TEMPLATE.format(
            title="Wiki Preview",
            content=rendered_content,
            wikitext=cgi.escape(value)
        )
        
        # Check for XSS
        result_message = check_xss(full_page, flags[0], wikitext, 'xss_hard')
    
    response_page = WIKI_EDITOR_TEMPLATE.format(
        wikitext=cgi.escape(value),
        rendered=rendered_content,
        result=result_message
    )
    
    response = make_response(response_page)
    response.headers["X-XSS-Protection"] = "0"
    return response


# Legacy endpoint for backward compatibility
@app.route('/page', methods=['GET', 'POST'])
def page_redirect():
    """Redirect to the new wiki endpoint"""
    return '''
    <html>
    <head><meta http-equiv="refresh" content="0; url=/wiki"></head>
    <body>Redirecting to <a href="/wiki">/wiki</a>...</body>
    </html>
    '''


if __name__ == '__main__':
    app.run(debug=True)
