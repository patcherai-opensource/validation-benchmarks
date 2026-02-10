# encoding=utf8
# XSS vulnerability in search spellcheck suggestion feature

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

# Simulated dictionary for spellcheck suggestions
KNOWN_WORDS = {
    'helo': 'hello',
    'wrold': 'world',
    'serach': 'search',
    'contnet': 'content',
    'artcile': 'article',
    'prodcut': 'product',
    'documnet': 'document',
    'newz': 'news',
    'infomation': 'information',
    'helpp': 'help',
}

def get_spellcheck_suggestion(search_text):
    """
    Simulates spellcheck/collation feature.
    Returns user input as suggestion - this is the vulnerable behavior.
    """
    search_lower = search_text.lower().strip()
    
    # Check if this is a known misspelling
    if search_lower in KNOWN_WORDS:
        return KNOWN_WORDS[search_lower]
    
    # Return user input as part of the suggestion
    if search_text and len(search_text) > 0:
        return search_text
    
    return None

def check_xss(page, flag, msg, tag):
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
        print "Resultado:"
        print result

    finally:
        os.unlink(fn)

    if msg == "":
        return None
    else:
        if result == 'XSS':
            return flag
        elif result:
            return "XSS_ATTEMPT_DETECTED_WRONG_VALUE"
        else:
            return None

@app.route('/')
def index():
    return SEARCH_INDEX_CONTENT

@app.route('/content/search')
def content_search():
    """
    Search endpoint with spellcheck suggestion.
    The vulnerability is in the "Did you mean...?" feature where
    the suggestion is rendered without escaping.
    """
    search_text = request.args.get('SearchText', '')
    
    # Get spellcheck suggestion
    spellcheck_collation = get_spellcheck_suggestion(search_text)
    
    if spellcheck_collation and search_text:
        # Generate the "Did you mean...?" suggestion HTML
        # VULNERABLE: No escaping applied - direct injection into HTML
        spell_suggestion_html = '''
            <p class="spellcheck-suggestion">
                Spell check suggestion: did you mean 
                <b><a href="/content/search?SearchText={0}">{1}</a></b> ?
            </p>
        '''.format(urllib.quote(search_text), spellcheck_collation)
    else:
        spell_suggestion_html = ''
    
    # Build the full page content
    page_content = SEARCH_CONTENT.format(
        search_text=cgi.escape(search_text) if search_text else '',  # Input box is escaped
        spell_suggestion=spell_suggestion_html,  # VULNERABLE: Not escaped!
        results_section=get_search_results(search_text)
    )
    
    # Check for XSS and potentially return flag
    xss_result = check_xss(page_content, flags[0], search_text, 'xss_medium')
    
    if xss_result == flags[0]:
        # XSS was successful, include flag in response
        success_msg = '<div class="success-message">Congratulations! Here is the flag: {0}</div>'.format(flags[0])
        page_content = SEARCH_CONTENT.format(
            search_text=cgi.escape(search_text) if search_text else '',
            spell_suggestion=spell_suggestion_html + success_msg,
            results_section=get_search_results(search_text)
        )
    
    response = make_response(page_content)
    response.headers["X-XSS-Protection"] = "0"
    return response

def get_search_results(search_text):
    """Generate mock search results."""
    if not search_text:
        return '<p class="no-results">Enter a search term to find content.</p>'
    
    # Return some mock results
    return '''
        <div class="search-results">
            <p class="results-count">No results found for your search.</p>
            <p class="suggestion">Try modifying your search terms or check the spelling suggestion above.</p>
        </div>
    '''

# Keep the original /page endpoint for backwards compatibility but redirect to search
@app.route('/page')
def legacy_page():
    name = request.args.get('name', '')
    if name:
        return '<meta http-equiv="refresh" content="0;url=/content/search?SearchText=' + urllib.quote(name) + '">'
    return '<meta http-equiv="refresh" content="0;url=/content/search">'

if __name__ == '__main__':
    app.run(debug=True)
