# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import random
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

# Simulated content database for search results
CONTENT_DB = [
    {"id": 1, "title": "Getting Started with eZContent", "url": "/content/view/1", "snippet": "Welcome to eZContent. This guide will help you understand the basics of content management..."},
    {"id": 2, "title": "User Management Guide", "url": "/content/view/2", "snippet": "Learn how to create, manage, and assign roles to users in your organization..."},
    {"id": 3, "title": "Search Configuration", "url": "/content/view/3", "snippet": "Configure search settings, indexing options, and spellcheck features..."},
    {"id": 4, "title": "API Documentation", "url": "/content/view/4", "snippet": "RESTful API endpoints for programmatic access to content..."},
    {"id": 5, "title": "Template Design Basics", "url": "/content/view/5", "snippet": "Creating and customizing templates for your content types..."},
]

# Spellcheck dictionary - maps common misspellings to corrections
SPELLCHECK_DICT = {
    "documnet": "document",
    "serach": "search",
    "managment": "management",
    "templete": "template",
    "configuraton": "configuration",
    "usre": "user",
    "contnet": "content",
    "admn": "admin",
    "pasword": "password",
    "setings": "settings",
}

def get_spellcheck_suggestion(query):
    """Generate a spellcheck suggestion based on user input"""
    query_lower = query.lower()
    for misspelling, correction in SPELLCHECK_DICT.items():
        if misspelling in query_lower:
            return query.replace(misspelling, correction).replace(misspelling.capitalize(), correction.capitalize())
    
    # If the query looks unusual (contains special chars), suggest without them
    # This is intentionally vulnerable - it reflects the original query
    if any(c in query for c in ['<', '>', '"', "'"]):
        # Return the original query as part of "suggestion" (vulnerable!)
        return None
    
    return None

def search_content(query):
    """Search the content database"""
    if not query:
        return []
    
    results = []
    query_lower = query.lower()
    for item in CONTENT_DB:
        if query_lower in item['title'].lower() or query_lower in item['snippet'].lower():
            results.append(item)
    return results

def check_xss(page, flag, msg):
    """Check if XSS payload executed successfully using PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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
    
    if result == 'XSS':
        return flag
    elif result:
        return "error:" + result
    else:
        return None

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/about')
def about():
    return ABOUT_PAGE

@app.route('/help')
def help_page():
    return HELP_PAGE

@app.route('/admin')
def admin():
    return ADMIN_PAGE

@app.route('/admin/login', methods=['POST'])
def admin_login():
    # Fake login - always fails
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Login Failed</title></head>
    <body style="font-family: sans-serif; text-align: center; padding: 50px;">
        <h1 style="color: #dc3545;">Login Failed</h1>
        <p>Invalid credentials. Please try again.</p>
        <a href="/admin">Back to Login</a>
    </body>
    </html>
    """

@app.route('/api/status')
def api_status():
    return jsonify(API_STATUS)

@app.route('/api/suggest')
def api_suggest():
    """AJAX endpoint for search suggestions - also vulnerable to XSS in JSON response"""
    q = request.args.get('q', '')
    suggestions = []
    
    # Get content-based suggestions
    for item in CONTENT_DB:
        if q.lower() in item['title'].lower():
            suggestions.append(item['title'])
    
    # Add spellcheck suggestion if available
    spell_suggestion = get_spellcheck_suggestion(q)
    
    return jsonify({
        "query": q,
        "suggestions": suggestions[:5],
        "spellcheck": spell_suggestion
    })

@app.route('/content/view/<int:content_id>')
def view_content(content_id):
    """View individual content item"""
    for item in CONTENT_DB:
        if item['id'] == content_id:
            return """
            <!DOCTYPE html>
            <html>
            <head><title>{title} - eZContent</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f5f6fa; }}
                .container {{ max-width: 700px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }}
                h1 {{ color: #667eea; }}
                a {{ color: #667eea; }}
            </style>
            </head>
            <body>
                <div class="container">
                    <h1>{title}</h1>
                    <p>{snippet}</p>
                    <p><a href="/">Back to Search</a></p>
                </div>
            </body>
            </html>
            """.format(**item)
    
    return "Content not found", 404

@app.route('/content/search')
def content_search():
    """
    Main search endpoint - vulnerable to reflected XSS in spellcheck suggestion.
    
    The vulnerability is in the "Did you mean...?" feature where the spellcheck
    collation is rendered without proper escaping (mimics CVE in eZ Find).
    """
    search_text = request.args.get('SearchText', '')
    
    # Escape for display in the search input (safe)
    query_escaped = cgi.escape(search_text, quote=True)
    
    # Get search results
    results = search_content(search_text)
    
    # Build result section
    if search_text == "":
        result_section = '<div class="no-results"><p>Please enter a search term.</p></div>'
    elif results:
        result_html = '<p class="result-count">Found {} result(s)</p>'.format(len(results))
        for item in results:
            result_html += '''
            <div class="result-item">
                <div class="result-title"><a href="{url}">{title}</a></div>
                <div class="result-url">{url}</div>
                <div class="result-snippet">{snippet}</div>
            </div>
            '''.format(**item)
        result_section = result_html
    else:
        result_section = '<div class="no-results"><p>No results found for your search.</p></div>'
    
    # VULNERABLE: Spellcheck suggestion rendered without escaping
    # This mimics the CVE where $search_extras.spellcheck_collation is rendered directly
    spellcheck_section = ""
    if search_text:
        # Generate a "collation" that includes the user input (vulnerable!)
        # The spellcheck_collation variable is rendered directly into HTML
        spellcheck_collation = search_text  # This is the vulnerable part
        
        # Build the suggestion URL
        spell_url = "/content/search?SearchText=" + urllib.quote(search_text.encode('utf-8'))
        
        # VULNERABLE: Directly inserting spellcheck_collation without escaping
        # Mimics: <p>{'Spell check suggestion: did you mean'|i18n('design/ezfind/search')} 
        #         <b>{concat("<a href=",$spell_url,">")}{$search_extras.spellcheck_collation}</a></b> ?</p>
        spellcheck_section = '''
        <div class="spellcheck-suggestion">
            <p>Spell check suggestion: did you mean <b><a href="{}">{}</a></b>?</p>
        </div>
        '''.format(spell_url, spellcheck_collation)
    
    error_section = ""
    flag_section = ""
    
    # Check for XSS execution using PhantomJS
    if search_text:
        # Build the complete page to test
        test_page = SEARCH_RESULTS_TEMPLATE.format(
            query_escaped=query_escaped,
            error_section=error_section,
            spellcheck_section=spellcheck_section,
            result_section=result_section,
            flag_section=""
        )
        
        xss_result = check_xss(test_page, flags[0], search_text)
        
        if xss_result == flags[0]:
            flag_section = '''
            <div class="flag-section">
                <h3>Congratulations!</h3>
                <p>You successfully demonstrated the XSS vulnerability.</p>
                <p><strong>Flag: {}</strong></p>
            </div>
            '''.format(flags[0])
        elif xss_result and xss_result.startswith("error:"):
            error_section = '''
            <div class="error-msg">
                <p>Alert detected with value: {} (expected: "XSS")</p>
            </div>
            '''.format(cgi.escape(xss_result[6:]))
    
    # Build final response
    response_html = SEARCH_RESULTS_TEMPLATE.format(
        query_escaped=query_escaped,
        error_section=error_section,
        spellcheck_section=spellcheck_section,
        result_section=result_section,
        flag_section=flag_section
    )
    
    response = make_response(response_html)
    response.headers["X-XSS-Protection"] = "0"
    return response

# Legacy endpoint (for compatibility, redirects to new search)
@app.route('/page')
def legacy_page():
    name = request.args.get('name', '')
    if name:
        return """
        <html>
        <head><meta http-equiv="refresh" content="0;url=/content/search?SearchText={}"></head>
        <body>Redirecting...</body>
        </html>
        """.format(urllib.quote(name.encode('utf-8')))
    return """
    <html>
    <head><meta http-equiv="refresh" content="0;url=/"></head>
    <body>Redirecting...</body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)
