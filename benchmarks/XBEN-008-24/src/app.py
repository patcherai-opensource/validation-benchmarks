# encoding=utf8
# CVE-2025-21612 - TabberNeue XSS Simulation
# This simulates the stored XSS vulnerability in MediaWiki's TabberNeue extension
# where page names in <tabbertransclude> tags were not properly escaped in error messages

from __future__ import print_function
from flask import Flask, request, Response, make_response, url_for
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
from constants import *

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True


@app.route('/')
def index():
    return INDEX_CONTENT


def check_xss(page, flag, wikitext, tag):
    """Check if the rendered page triggers XSS via PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Result:")
        print(result)

    finally:
        os.unlink(fn)

    if wikitext == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Welcome to the Wiki Editor. Try using the tabbertransclude tag!</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>No XSS detected. Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


def is_valid_page_title(title):
    """
    Check if a page title is valid.
    In MediaWiki, page titles containing certain characters like < > are invalid.
    This simulates the validation logic from TabberNeue.
    """
    # Invalid characters in MediaWiki page titles
    invalid_chars = ['<', '>', '[', ']', '{', '}', '|']
    for char in invalid_chars:
        if char in title:
            return False
    return True


def build_tab_transclude(page_name, tab_label):
    """
    Build the HTML for a tabbertransclude element.
    VULNERABLE: If the page name is invalid, it's inserted into the error message
    without proper escaping - exactly like CVE-2025-21612.
    """
    page_name = page_name.strip()
    tab_label = tab_label.strip() if tab_label else page_name
    
    if not is_valid_page_title(page_name):
        # VULNERABLE CODE - CVE-2025-21612
        # The page name is not escaped before being inserted into HTML
        # This matches the vulnerable code in TabberNeue before the fix:
        # sprintf('<div class="error">Invalid title: %s</div>', $pageName)
        tab_body = '<div class="tabber-error">Invalid title: %s</div>' % page_name
    else:
        # Valid page - would normally transclude content
        tab_body = '<div class="tabber-content">Content for: %s</div>' % cgi.escape(page_name)
    
    return '''
    <div class="tabber-tab">
        <div class="tabber-tab-label">%s</div>
        %s
    </div>
    ''' % (cgi.escape(tab_label), tab_body)


def parse_tabbertransclude(wikitext):
    """
    Parse tabbertransclude tags from wikitext.
    Format: <tabbertransclude> page_name | tab_label </tabbertransclude>
    
    This simulates the parsing in TabberNeue's parserHook function.
    """
    output = wikitext
    
    # Find all tabbertransclude tags
    pattern = r'<tabbertransclude>(.*?)</tabbertransclude>'
    matches = re.findall(pattern, wikitext, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        # Split by | to get page name and tab label
        parts = match.split('|', 1)
        page_name = parts[0] if parts else ''
        tab_label = parts[1] if len(parts) > 1 else ''
        
        # Build the tab HTML (this is where the vulnerability is)
        tab_html = build_tab_transclude(page_name, tab_label)
        
        # Replace the original tag with rendered HTML
        original_tag = '<tabbertransclude>%s</tabbertransclude>' % match
        output = output.replace(original_tag, tab_html, 1)
    
    return output


def render_wikitext(wikitext):
    """
    Render wikitext to HTML.
    This is a simplified version of MediaWiki's parser.
    """
    # Parse tabbertransclude tags (vulnerable)
    html = parse_tabbertransclude(wikitext)
    
    return html


@app.route('/wiki')
def wiki_page():
    """
    Wiki page editor - simulates MediaWiki's Special:ExpandTemplates
    or wiki page editing functionality.
    
    This endpoint accepts wikitext and renders it, similar to how
    MediaWiki processes user-submitted content.
    """
    wikitext = request.args.get('wikitext', '')
    
    # Render the wikitext (this processes tabbertransclude tags)
    rendered_content = render_wikitext(wikitext) if wikitext else ''
    
    # Build the full page HTML
    page_html = WIKI_CONTENT.format(cgi.escape(wikitext), rendered_content)
    
    # Check for XSS
    result = check_xss(page_html, flags[0], wikitext, 'xss_medium')
    
    # Return the page with the result
    response = make_response(WIKI_CONTENT_WITH_RESULT.format(cgi.escape(wikitext), rendered_content, result))
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/preview', methods=['POST'])
def wiki_preview():
    """
    Preview endpoint for wiki editing - simulates the preview functionality
    where users can see their wikitext rendered before saving.
    """
    wikitext = request.form.get('wikitext', '')
    
    # Render the wikitext (this processes tabbertransclude tags)
    rendered_content = render_wikitext(wikitext) if wikitext else ''
    
    # Build the full page HTML
    page_html = WIKI_CONTENT.format(cgi.escape(wikitext), rendered_content)
    
    # Check for XSS
    result = check_xss(page_html, flags[0], wikitext, 'xss_medium')
    
    # Return the page with the result
    response = make_response(WIKI_CONTENT_WITH_RESULT.format(cgi.escape(wikitext), rendered_content, result))
    response.headers["X-XSS-Protection"] = "0"
    return response


if __name__ == '__main__':
    app.run(debug=True)
