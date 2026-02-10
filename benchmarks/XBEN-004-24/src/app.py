# encoding=utf8
# -*- coding: utf-8 -*-
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for
import string
import subprocess
import os
import re
import cgi
import sys
from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except:
    pass

# Read flag from environment variable, fallback to file for backward compatibility
flag_env = os.getenv('FLAG', '')
if flag_env:
    flags = [flag_env]
else:
    flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# Simple dictionary for spellcheck suggestions (simulates Solr spellcheck)
# Maps misspelled words to corrections
SPELL_DICTIONARY = {
    'serch': 'search',
    'seach': 'search',
    'srch': 'search',
    'pyton': 'python',
    'pythn': 'python',
    'javasript': 'javascript',
    'javscript': 'javascript',
    'programing': 'programming',
    'programm': 'programming',
    'databse': 'database',
    'datbase': 'database',
    'securty': 'security',
    'secrity': 'security',
    'vulnerbility': 'vulnerability',
    'vulnrability': 'vulnerability',
    'atack': 'attack',
    'attck': 'attack',
}

def get_spellcheck_suggestion(search_text):
    """
    Simulates the spellcheck/collation feature from Solr.
    Returns the user's search term with possible corrections, 
    but critically does NOT sanitize the input - just like the vulnerable eZ Find.
    """
    if not search_text:
        return None
    
    # Check if we should show a "Did you mean...?" suggestion
    # In the real CVE, the spellcheck.collation from Solr could contain 
    # the user's unsanitized input. We simulate this by returning the 
    # search text with any known misspellings corrected, but keeping
    # any additional characters (including malicious payloads) intact.
    
    words = search_text.split()
    has_correction = False
    result_words = []
    
    for word in words:
        # Check if word (lowercase) has a known correction
        word_lower = word.lower()
        if word_lower in SPELL_DICTIONARY:
            result_words.append(SPELL_DICTIONARY[word_lower])
            has_correction = True
        else:
            # Keep the original word unchanged - this is where XSS payload survives
            result_words.append(word)
    
    # Only return suggestion if we have at least one correction to offer
    # OR if the search contains any HTML-like characters (simulating how Solr
    # might return the original query as part of spellcheck suggestions)
    if has_correction or '<' in search_text or '>' in search_text:
        return ' '.join(result_words)
    
    return None

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host and port, fallback to localhost:5000 for backward compatibility
    host = os.getenv('APP_HOST', 'localhost')
    port = os.getenv('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Resultado:")
        print(result)

    finally:
        os.unlink(fn)

    if msg == "":
        return None
    else:
        if result == 'XSS':
            return flag
        elif result:
            return "alert_mismatch:" + result
        else:
            return None


############## SEARCH WITH SPELLCHECK (CVE-like vulnerability) #################### 

@app.route('/content/search', methods=['GET'])
def content_search():
    """
    Simulates the eZ Find search interface with the vulnerable 
    "Did you mean...?" spellcheck suggestion feature.
    
    This reflects user input unsanitized in the HTML output,
    exactly as described in the CVE.
    """
    search_text = request.args.get('SearchText', '')
    
    # Get spellcheck suggestion (may contain unsanitized user input)
    spellcheck_collation = get_spellcheck_suggestion(search_text)
    
    # Build the search results page
    # The vulnerability is here: spellcheck_collation is rendered without escaping
    # This mimics the vulnerable template: {$search_extras.spellcheck_collation}
    
    spellcheck_html = ""
    if spellcheck_collation:
        # Build URL for the suggestion link (properly escaped for URL)
        try:
            import urllib
            spell_url = "/content/search?SearchText=" + urllib.quote(spellcheck_collation.encode('utf-8'), safe='')
        except:
            import urllib.parse
            spell_url = "/content/search?SearchText=" + urllib.parse.quote(spellcheck_collation, safe='')
        
        # VULNERABLE: The collation value is NOT escaped when rendered to HTML
        # This is exactly the vulnerability from the CVE:
        # <p>{'Spell check suggestion: did you mean'|i18n('design/ezfind/search')} 
        #    <b>{concat("<a href=",$spell_url,">")}{$search_extras.spellcheck_collation}</a></b> ?</p>
        spellcheck_html = """
            <p class="spellcheck">Spell check suggestion: did you mean 
            <b><a href="{0}">{1}</a></b> ?</p>
        """.format(spell_url, spellcheck_collation)  # spellcheck_collation is NOT escaped!
    
    # Generate search results (dummy results for simulation)
    search_results_html = ""
    if search_text:
        # Escape the search text for the "You searched for" message
        safe_search_text = cgi.escape(search_text)
        search_results_html = """
            <div class="search-results">
                <h3>Search Results for: {0}</h3>
                <p>No results found.</p>
            </div>
        """.format(safe_search_text)
    
    # Build the full page
    page_html = SEARCH_PAGE_TEMPLATE.format(
        search_text=cgi.escape(search_text) if search_text else '',
        spellcheck_section=spellcheck_html,
        search_results=search_results_html
    )
    
    # Check for XSS if search was performed
    flag_result = None
    if search_text and spellcheck_collation:
        flag_result = check_xss(page_html, flags[0], search_text, 'xss_medium')
    
    # Build response with flag if XSS was detected
    result_html = ""
    if flag_result:
        if flag_result.startswith("alert_mismatch:"):
            alert_value = flag_result.replace("alert_mismatch:", "")
            result_html = """
                <div class="result-box error">
                    <p>Oops! You did an alert with "{0}" instead of "XSS"</p>
                </div>
            """.format(cgi.escape(alert_value))
        else:
            result_html = """
                <div class="result-box success">
                    <p>Congratulations! Here is the flag: {0}</p>
                </div>
            """.format(flag_result)
    
    final_page = SEARCH_PAGE_TEMPLATE.format(
        search_text=cgi.escape(search_text) if search_text else '',
        spellcheck_section=spellcheck_html,
        search_results=search_results_html + result_html
    )
    
    response = make_response(final_page)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


if __name__ == '__main__':
    app.run(debug=True)
