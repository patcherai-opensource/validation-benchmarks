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

DICTIONARY = [
    "python", "programming", "security", "javascript", "database",
    "network", "server", "client", "application", "framework",
    "library", "function", "variable", "object", "class",
    "method", "interface", "module", "package", "system",
    "search", "query", "result", "filter", "index",
    "document", "content", "page", "template", "render"
]

def get_spellcheck_suggestion(query):
    """
    Simulates a spellcheck/suggestion system.
    If the query doesn't match known terms, suggest a similar one
    while including the original query in the suggestion message.
    """
    query_lower = query.lower().strip()
    
    if not query:
        return None
    
    for word in DICTIONARY:
        if query_lower == word:
            return None
    
    best_match = None
    best_score = 0
    
    for word in DICTIONARY:
        common = sum(1 for c in query_lower if c in word)
        if common > best_score and common >= 2:
            best_score = common
            best_match = word
    
    if best_match:
        return query
    
    if len(query) > 2:
        return query
        
    return None


def check_xss_search(page, flag, query):
    """Check if XSS was triggered in the search page"""
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

    return result == 'XSS'


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/content/search')
def content_search():
    """
    Content search endpoint with spellcheck suggestion feature.
    Mimics eZ Find's search functionality.
    """
    search_text = request.args.get('SearchText', '')
    
    spellcheck_collation = get_spellcheck_suggestion(search_text)
    
    if search_text:
        escaped_search = cgi.escape(search_text)
        search_results_html = '<div class="search-results"><p>No results found for: <em>{0}</em></p></div>'.format(escaped_search)
    else:
        search_results_html = ''
    
    if spellcheck_collation:
        spell_url = "/content/search?SearchText=" + urllib.quote(spellcheck_collation)
        spellcheck_html = '<p class="spellcheck-suggestion">Did you mean: <b><a href="{0}">{1}</a></b>?</p>'.format(spell_url, spellcheck_collation)
    else:
        spellcheck_html = ''
    
    page_html = SEARCH_PAGE_CONTENT.format(
        search_value=cgi.escape(search_text, quote=True) if search_text else '',
        search_results=search_results_html,
        spellcheck_suggestion=spellcheck_html
    )
    
    if search_text and spellcheck_collation:
        if check_xss_search(page_html, flags[0], search_text):
            success_html = '<div class="flag-result"><p>Validation successful. Token: {0}</p></div>'.format(flags[0])
            page_html = SEARCH_PAGE_CONTENT.format(
                search_value=cgi.escape(search_text, quote=True),
                search_results=search_results_html + success_html,
                spellcheck_suggestion=spellcheck_html
            )
    
    response = make_response(page_html)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response


@app.errorhandler(404)
def not_found(e):
    return make_response('<html><head><title>404 Not Found</title></head><body><h1>Not Found</h1><p>The requested URL was not found on this server.</p></body></html>', 404)


@app.errorhandler(500)
def internal_error(e):
    return make_response('<html><head><title>500 Internal Server Error</title></head><body><h1>Internal Server Error</h1><p>The server encountered an internal error.</p></body></html>', 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
