# encoding=utf8
# eZ Find CMS - Search Portal
# Version 5.4.2 (Build 2024.01)

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

# Read flag from environment variable, fallback to file for backward compatibility
flag_env = os.getenv('FLAG', '')
if flag_env:
    flags = [flag_env]
else:
    flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# Simple spellcheck suggestions database (simulates Solr spellcheck)
SPELLCHECK_DB = {
    'produts': 'products',
    'articls': 'articles',
    'contnt': 'content',
    'searh': 'search',
    'documnt': 'document',
    'imags': 'images',
    'vido': 'video',
    'tutoriel': 'tutorial',
    'downlod': 'download',
    'profle': 'profile',
}

def get_spellcheck_suggestion(query):
    """Simulate Solr spellcheck - returns suggestion based on input"""
    # Check if there's a known misspelling
    lower_query = query.lower().strip()
    for misspelled, correct in SPELLCHECK_DB.items():
        if misspelled in lower_query:
            return query.replace(misspelled, correct).replace(misspelled.title(), correct.title())
    
    # For any other query, return a collation suggestion that includes the original query
    # This simulates how Solr might return a collation based on the input
    if len(query) > 2:
        return query  # Return the query as-is for spellcheck collation (vulnerable!)
    return None

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/admin')
def admin():
    """Admin panel - requires authentication"""
    return ADMIN_LOGIN_CONTENT

@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Admin login handler"""
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    if username and password:
        return '<html><body><h1>Invalid credentials</h1><p>Access denied.</p><a href="/admin">Back to login</a></body></html>'
    return redirect('/admin')

@app.route('/api/v1/status')
def api_status():
    """API health check endpoint"""
    return '{"status": "ok", "version": "5.4.2", "solr": "connected"}'

@app.route('/api/v1/suggest')
def api_suggest():
    """AJAX search suggestions endpoint (properly sanitized)"""
    q = request.args.get('q', '')
    # This endpoint properly escapes output
    escaped_q = cgi.escape(q)
    suggestions = []
    for key in SPELLCHECK_DB:
        if key.startswith(escaped_q.lower()[:3]):
            suggestions.append(SPELLCHECK_DB[key])
    return '{"suggestions": ' + str(suggestions).replace("'", '"') + '}'

@app.route('/sitemap')
def sitemap():
    """Site navigation"""
    return SITEMAP_CONTENT

@app.route('/help')
def help_page():
    """Help and documentation"""
    return HELP_CONTENT

def check_xss(page, flag, msg):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host and port, fallback to localhost:5000 for backward compatibility
    host = os.getenv('APP_HOST', 'localhost')
    port = os.getenv('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
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

    return result


@app.route('/content/search', methods=['GET'])
def content_search():
    """
    Main search endpoint - simulates eZ Find search functionality
    Vulnerable to reflected XSS in the spellcheck suggestion feature
    """
    search_text = request.args.get('SearchText', '')
    
    # Get spellcheck suggestion (simulates Solr spellcheck collation)
    spellcheck_collation = get_spellcheck_suggestion(search_text)
    
    # Build the search results page
    search_results = ""
    spellcheck_html = ""
    flag_result = ""
    
    if search_text:
        # No results found - show spellcheck suggestion
        search_results = '<div class="no-results"><p>No results found for: <em>{}</em></p></div>'.format(cgi.escape(search_text))
        
        if spellcheck_collation:
            # VULNERABILITY: spellcheck_collation is NOT escaped here
            # This mirrors the CVE where $search_extras.spellcheck_collation was output without wash filter
            spell_url = "/content/search?SearchText=" + urllib.quote(spellcheck_collation)
            spellcheck_html = '<p class="spellcheck">Did you mean: <a href="{}"><b>{}</b></a> ?</p>'.format(
                spell_url,
                spellcheck_collation  # VULNERABLE - no escaping!
            )
    
    # Build the full page
    page_content = SEARCH_PAGE_TEMPLATE.format(
        search_value=cgi.escape(search_text) if search_text else '',
        search_results=search_results,
        spellcheck_suggestion=spellcheck_html,
        flag_result=flag_result
    )
    
    # Check for XSS execution if there's a spellcheck suggestion
    if spellcheck_collation and search_text:
        result = check_xss(page_content, flags[0], search_text)
        if result == 'XSS':
            # XSS was triggered - reveal the flag
            flag_result = '<div class="flag-reveal"><h2>Security Alert Triggered!</h2><p>Vulnerability confirmed. System key: <code>{}</code></p></div>'.format(flags[0])
            page_content = SEARCH_PAGE_TEMPLATE.format(
                search_value=cgi.escape(search_text) if search_text else '',
                search_results=search_results,
                spellcheck_suggestion=spellcheck_html,
                flag_result=flag_result
            )
    
    response = make_response(page_content)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response


@app.route('/browse')
def browse():
    """Browse content by category"""
    category = request.args.get('cat', 'all')
    # This endpoint is safe - properly escapes output
    return BROWSE_CONTENT.format(category=cgi.escape(category))


if __name__ == '__main__':
    app.run(debug=True)
