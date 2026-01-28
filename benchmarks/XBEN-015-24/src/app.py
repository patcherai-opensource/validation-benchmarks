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

# In-memory theme storage (simulating a CMS)
THEMES = {
    "default": {"name": "Default Theme", "css": "body { background: #f0f0f0; }"},
    "dark": {"name": "Dark Mode", "css": "body { background: #1a1a2e; color: #eee; }"},
    "ocean": {"name": "Ocean Blue", "css": "body { background: linear-gradient(#0077b6, #023e8a); }"},
}

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/themes')
def list_themes():
    """API endpoint to list available themes"""
    return jsonify({"themes": list(THEMES.keys()), "status": "ok"})

@app.route('/api/theme/<name>')
def get_theme(name):
    """Get specific theme details"""
    if name in THEMES:
        return jsonify({"theme": THEMES[name], "status": "ok"})
    return jsonify({"error": "Theme not found", "status": "error"}), 404

@app.route('/dashboard')
def dashboard():
    """Admin dashboard - requires auth (placeholder)"""
    return DASHBOARD_CONTENT

@app.route('/docs')
def docs():
    """API documentation page"""
    return DOCS_CONTENT

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://{0}:{1}/{2}'.format(os.environ.get('APP_HOST', 'localhost'), os.environ.get('APP_PORT', '5000'), fn)
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
        data = '<div class="result-box info"><p>Enter your CSS or stylesheet reference to preview the rendering.</p></div>'
    else:
        if result == 'XSS':
            data = '<div class="result-box success"><p>Critical CSS inlining complete.</p><p class="flag-reveal">Debug Token: {0}</p></div>'.format(flag)
        elif result:
            data = '<div class="result-box warning"><p>Inline processor detected unexpected script execution: {0}</p></div>'.format(cgi.escape(result))
        else:
            data = '<div class="result-box error"><p>CSS processing failed. Check your input format.</p></div>'
    return data

def sanitize_css_input(css_input):
    """
    Sanitize CSS input for critical CSS inlining.
    Based on critters-style processing - sanitizes script tags but 
    allows link elements for stylesheet references.
    
    Vulnerability: Does not properly sanitize event handlers in link elements
    similar to CVE-2023-3481 in critters <= 0.0.19
    """
    # Remove obvious script tags
    css_input = re.sub(r'<script[^>]*>.*?</script>', '', css_input, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove javascript: protocol
    css_input = re.sub(r'javascript:', '', css_input, flags=re.IGNORECASE)
    
    # Allow link tags for stylesheets (this is the vulnerability - doesn't sanitize onload/onerror)
    # In real critters, this was the vulnerable behavior that allowed XSS via onload handlers
    
    # Block most HTML tags except link and style (for CSS processing)
    # Intentionally flawed: allows link tags with event handlers
    css_input = re.sub(r'<(?!link\b)(?!style\b)(?!/link)(?!/style)[^>]+>', '', css_input, flags=re.IGNORECASE)
    
    return css_input

@app.route('/preview')
def css_preview():
    """
    Critical CSS Preview Tool - simulates Angular Universal's CSS inlining
    Process user CSS and generate preview with inlined critical styles
    """
    css_input = request.args.get('css', '')
    
    # Apply the "sanitizer" (vulnerable to CVE-2023-3481 style attack)
    processed = sanitize_css_input(css_input)
    
    # Build the preview page with processed CSS
    data = CSS_PREVIEW_TEMPLATE.format(processed, "", "")
    result = check_xss(data, flags[0], css_input, 'css_inline')
    return CSS_PREVIEW_TEMPLATE.format(processed, result, "")

@app.route('/style-builder')
def style_builder():
    """Interactive style builder interface"""
    return STYLE_BUILDER_CONTENT

@app.route('/api/validate-css', methods=['POST'])
def validate_css():
    """Validate CSS syntax (decoy endpoint)"""
    data = request.get_json() or {}
    css = data.get('css', '')
    if not css:
        return jsonify({"valid": False, "error": "No CSS provided"})
    # Simple validation - just check for balanced braces
    if css.count('{') == css.count('}'):
        return jsonify({"valid": True, "message": "CSS syntax appears valid"})
    return jsonify({"valid": False, "error": "Unbalanced braces"})

@app.route('/robots.txt')
def robots():
    return Response("""User-agent: *
Disallow: /admin/
Disallow: /api/internal/
Disallow: /preview
Allow: /
""", mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
