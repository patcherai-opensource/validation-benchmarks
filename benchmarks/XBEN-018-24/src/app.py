# encoding=utf8
# Templar Templates - A Modern Template Engine Demo
# Inspired by ghtml - "Simple, Fast, Secure HTML Templates"

from flask import Flask, request, Response, make_response, url_for, jsonify
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


def templar_escape(text):
    """
    Templar's built-in HTML escaping function.
    Escapes common dangerous characters to prevent XSS.
    
    VULNERABILITY: Similar to ghtml before v2.0.0, this escaping function
    does not escape backticks (`). This allows injection into JavaScript
    template literals when user input is placed in script contexts.
    """
    if not text:
        return text
    # Escape HTML entities (similar to ghtml's approach before the fix)
    # Note: backtick (`) is NOT escaped - this is the vulnerability
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    # Missing: text = text.replace('`', '&#x60;')  # CVE-2024-37166 vulnerability
    return text


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/api/info')
def api_info():
    """API endpoint for template engine info"""
    return jsonify({
        "engine": "Templar Templates",
        "version": "1.9.3",
        "features": ["auto-escaping", "attribute interpolation", "template caching"],
        "escaping": {
            "enabled": True,
            "characters": ["<", ">", "&", "'", "\""],
            "note": "Context-aware escaping for template literals is handled separately"
        }
    })


def check_xss(page, flag, msg, tag):
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
        data = '<div class="result-box"><p class="status">Enter a greeting message</p></div>'
    else:
        if result == 'XSS':
            data = '<div class="result-box success"><p class="status">Template Security Bypass Detected!</p><p class="flag-text">Debug Token: {0}</p></div>'.format(flag)
        elif result:
            data = '<div class="result-box warning"><p class="status">Alert triggered with: {0}</p><p>Expected: "XSS"</p></div>'.format(cgi.escape(result))
        else:
            data = '<div class="result-box error"><p class="status">No script execution detected</p></div>'
    return data


@app.route('/greeting')
def greeting_generator():
    """
    Greeting Card Generator - demonstrates Templar's template rendering.
    User provides a message which is embedded into a JavaScript template literal
    for dynamic display.
    
    VULNERABILITY: Templar escapes HTML special characters but doesn't escape
    backticks. When user input is placed inside a JavaScript template literal,
    attackers can break out of the string and execute arbitrary JavaScript.
    
    Example: Input of `${alert('XSS')}` will execute because backticks aren't escaped.
    """
    message = request.args.get('message', '')
    
    # Apply Templar's HTML escaping to user input
    escaped_message = templar_escape(message)
    
    # Build the greeting HTML with embedded JavaScript template literal
    # This simulates a common pattern: displaying user content dynamically
    if escaped_message:
        # The escaped message is placed inside a JavaScript template literal
        # This is the vulnerable pattern from CVE-2024-37166
        greeting_html = '''
        <div id="greeting-display" class="greeting-card" autofocus onfocus="renderGreeting()">
            <p id="greeting-text"></p>
        </div>
        <script>
            function renderGreeting() {{
                var userMessage = `{0}`;
                document.getElementById('greeting-text').textContent = userMessage;
            }}
            // Auto-render on load
            renderGreeting();
        </script>
        '''.format(escaped_message)
    else:
        greeting_html = '<p class="placeholder">Enter a message to create your greeting</p>'
    
    data = GREETING_CONTENT.format(greeting_html, "", "")
    result = check_xss(data, flags[0], message, 'template')
    
    response = make_response(GREETING_CONTENT.format(greeting_html, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/docs')
def docs():
    """Documentation page for Templar Templates"""
    return DOCS_CONTENT


if __name__ == '__main__':
    app.run(debug=True)
