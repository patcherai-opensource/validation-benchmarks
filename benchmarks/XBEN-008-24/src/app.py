# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect
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

# Simulated wiki pages database
WIKI_PAGES = {
    'Main_Page': {
        'title': 'Welcome to WikiBase',
        'content': '<h1>Welcome to WikiBase</h1><p>WikiBase is a simple wiki system for documentation and knowledge sharing.</p><h2>Getting Started</h2><ul><li><a href="/wiki/Help:Editing">Help:Editing</a> - Learn how to edit pages</li><li><a href="/wiki/Help:Templates">Help:Templates</a> - Using templates</li><li><a href="/wiki/Special:Preview">Special:Preview</a> - Preview markup before publishing</li></ul><h2>Featured Articles</h2><ul><li><a href="/wiki/Documentation">Documentation</a></li><li><a href="/wiki/API_Reference">API Reference</a></li></ul>'
    },
    'Help:Editing': {
        'title': 'Help:Editing',
        'content': '<h1>Editing Pages</h1><p>WikiBase uses a simplified markup language similar to MediaWiki.</p><h2>Basic Formatting</h2><ul><li><code>&apos;&apos;&apos;bold&apos;&apos;&apos;</code> - Bold text</li><li><code>&apos;&apos;italic&apos;&apos;</code> - Italic text</li><li><code>[[Page Name]]</code> - Internal link</li></ul><h2>Templates</h2><p>Templates can be included using the <code>&lt;tabinclude&gt;</code> tag:</p><pre>&lt;tabinclude&gt;Template Name | Display Label&lt;/tabinclude&gt;</pre><p>See <a href="/wiki/Help:Templates">Help:Templates</a> for more information.</p>'
    },
    'Help:Templates': {
        'title': 'Help:Templates',
        'content': '<h1>Using Templates</h1><p>Templates allow you to include reusable content across multiple pages.</p><h2>The tabinclude Tag</h2><p>The <code>&lt;tabinclude&gt;</code> tag embeds content from another page:</p><pre>&lt;tabinclude&gt;PageName | Tab Label&lt;/tabinclude&gt;</pre><p><strong>Parameters:</strong></p><ul><li><strong>PageName</strong> - The name of the page to include (must be a valid page title)</li><li><strong>Tab Label</strong> - The display label for the tab</li></ul><h2>Valid Page Names</h2><p>Page names must follow standard naming conventions. Invalid characters will result in an error message being displayed.</p><p>Try the <a href="/wiki/Special:Preview">Preview Tool</a> to test your markup.</p>'
    },
    'Documentation': {
        'title': 'Documentation',
        'content': '<h1>WikiBase Documentation</h1><p>Complete documentation for the WikiBase system.</p><h2>Sections</h2><ul><li>Installation Guide</li><li>Configuration</li><li>API Documentation</li><li>Troubleshooting</li></ul>'
    },
    'API_Reference': {
        'title': 'API Reference',
        'content': '<h1>API Reference</h1><p>WikiBase provides a REST API for programmatic access.</p><h2>Endpoints</h2><ul><li><code>GET /api/pages</code> - List all pages</li><li><code>GET /api/page/{name}</code> - Get page content</li><li><code>POST /api/preview</code> - Preview markup rendering</li></ul>'
    }
}

# Valid template/page names (alphanumeric, underscores, colons)
VALID_PAGE_PATTERN = re.compile(r'^[A-Za-z0-9_:]+$')

@app.route('/')
def index():
    return redirect('/wiki/Main_Page')

@app.route('/wiki/')
@app.route('/wiki/<path:page_name>')
def wiki_page(page_name='Main_Page'):
    page = WIKI_PAGES.get(page_name)
    if page:
        return WIKI_PAGE_TEMPLATE.format(
            title=page['title'],
            content=page['content'],
            page_name=page_name
        )
    else:
        return WIKI_NOT_FOUND_TEMPLATE.format(page_name=cgi.escape(page_name)), 404

@app.route('/api/pages')
def api_pages():
    return {'pages': list(WIKI_PAGES.keys())}

@app.route('/api/page/<path:page_name>')
def api_page(page_name):
    page = WIKI_PAGES.get(page_name)
    if page:
        return {'title': page['title'], 'content': page['content']}
    return {'error': 'Page not found'}, 404

def check_xss(page, flag, msg):
    """Check if XSS was triggered using PhantomJS"""
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
        return None
    else:
        if result == 'XSS':
            return flag
        elif result:
            return "alert_other:" + result
        else:
            return None

def parse_tabinclude(markup):
    """
    Parse tabinclude tags and render them.
    Similar to MediaWiki's TabberTransclude extension.
    
    Syntax: <tabinclude>PageName | Label</tabinclude>
    """
    # Pattern to match tabinclude tags
    pattern = r'<tabinclude>(.*?)</tabinclude>'
    
    def replace_tabinclude(match):
        content = match.group(1).strip()
        
        # Split by | to get page name and label
        parts = content.split('|', 1)
        page_name = parts[0].strip()
        label = parts[1].strip() if len(parts) > 1 else page_name
        
        # Check if page name is valid
        if not page_name or not VALID_PAGE_PATTERN.match(page_name):
            # CVE-2025-21612: Invalid page name is NOT escaped in error output
            # This is the vulnerable sink - page_name is inserted directly into HTML
            return '<div class="tabinclude-error">Invalid page title: %s</div>' % page_name
        
        # Check if page exists
        if page_name not in WIKI_PAGES:
            return '<div class="tabinclude-warning">Page not found: %s</div>' % cgi.escape(page_name)
        
        # Return included content
        page = WIKI_PAGES[page_name]
        return '<div class="tabinclude-content" data-label="%s">%s</div>' % (cgi.escape(label), page['content'])
    
    return re.sub(pattern, replace_tabinclude, markup, flags=re.DOTALL)

def render_markup(markup):
    """Render wiki markup to HTML"""
    # Process tabinclude tags first
    html = parse_tabinclude(markup)
    
    # Basic wiki markup processing (simplified)
    # Bold: '''text'''
    html = re.sub(r"'''(.*?)'''", r'<strong>\1</strong>', html)
    # Italic: ''text''
    html = re.sub(r"''(.*?)''", r'<em>\1</em>', html)
    # Internal links: [[Page Name]]
    html = re.sub(r'\[\[([^\]]+)\]\]', r'<a href="/wiki/\1">\1</a>', html)
    
    return html

@app.route('/wiki/Special:Preview', methods=['GET', 'POST'])
def preview_markup():
    """Preview wiki markup rendering - mirrors Special:ExpandTemplates in MediaWiki"""
    markup = ""
    rendered = ""
    flag_result = None
    
    if request.method == 'POST':
        markup = request.form.get('markup', '')
        
        # Render the markup
        rendered = render_markup(markup)
        
        # Create full page for XSS check
        full_page = PREVIEW_RESULT_PAGE.format(
            markup=cgi.escape(markup),
            rendered=rendered
        )
        
        # Check for XSS
        flag_result = check_xss(full_page, flags[0], markup)
    
    # Build flag message
    flag_message = ""
    if flag_result:
        if not flag_result.startswith('alert_other:'):
            flag_message = '<div class="success-message">Challenge completed! Flag: %s</div>' % flag_result
        else:
            alert_val = cgi.escape(flag_result.replace('alert_other:', ''))
            flag_message = '<div class="info-message">Alert detected with value: %s (expected: "XSS")</div>' % alert_val
    
    response = make_response(PREVIEW_PAGE_TEMPLATE.format(
        markup=cgi.escape(markup),
        rendered=rendered,
        flag_message=flag_message
    ))
    response.headers["X-XSS-Protection"] = "0"
    return response

# Additional decoy endpoints for reconnaissance
@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    # Properly escaped - not vulnerable
    results = []
    for name, page in WIKI_PAGES.items():
        if query.lower() in name.lower() or query.lower() in page['content'].lower():
            results.append({'name': name, 'title': page['title']})
    return {'query': query, 'results': results}

@app.route('/wiki/Special:RecentChanges')
def recent_changes():
    return RECENT_CHANGES_TEMPLATE

@app.route('/wiki/Special:AllPages')
def all_pages():
    pages_list = ''.join(['<li><a href="/wiki/%s">%s</a></li>' % (name, cgi.escape(name)) for name in sorted(WIKI_PAGES.keys())])
    return ALL_PAGES_TEMPLATE.format(pages_list=pages_list)

if __name__ == '__main__':
    app.run(debug=True)
