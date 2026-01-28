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

# Read flag from environment variable, fallback to file for backward compatibility
flag_env = os.getenv('FLAG', '')
if flag_env:
    flags = [flag_env]
else:
    flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/products')
def products():
    return PRODUCTS_PAGE

@app.route('/settings')
def settings():
    return SETTINGS_PAGE

@app.route('/api/status')
def api_status():
    response = make_response(API_STATUS)
    response.headers['Content-Type'] = 'application/json'
    return response

def check_xss(page, flag, msg):
    """Check if the HTML content triggers XSS via PhantomJS"""
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
        return ""
    else:
        if result == 'XSS':
            return '<div class="result success"><strong>Validation Passed!</strong> Content is safe. Admin token: {}</div>'.format(flag)
        elif result:
            return '<div class="result error"><strong>Alert Detected:</strong> Unexpected content "{}" was triggered. Content blocked.</div>'.format(cgi.escape(result))
        else:
            return '<div class="result error"><strong>Validation Failed:</strong> Content did not pass security checks.</div>'


@app.route('/content', methods=['POST', 'GET'])
def content_editor():
    """Content editor with HTML sanitization - vulnerable to animation event handlers XSS"""
    html_content = request.form.get('html_content', '')
    
    # Comprehensive blacklist of event handlers - but missing animation event handlers!
    # This mimics CVE-2023-30838 in PrestaShop's Validate::isCleanHtml() 
    blacklist = [
        'script',       # Block script tags
        'onclick',      # Mouse click
        'ondblclick',   # Double click
        'onmousedown',  # Mouse button pressed
        'onmouseup',    # Mouse button released
        'onmouseover',  # Mouse over element
        'onmouseout',   # Mouse leaves element
        'onmousemove',  # Mouse movement
        'onmouseenter', # Mouse enters element
        'onmouseleave', # Mouse leaves element
        'onkeydown',    # Key pressed
        'onkeyup',      # Key released
        'onkeypress',   # Key press
        'onload',       # Page/element loaded
        'onunload',     # Page unloaded
        'onerror',      # Error occurred
        'onabort',      # Loading aborted
        'onfocus',      # Element focused
        'onblur',       # Element lost focus
        'onchange',     # Value changed
        'oninput',      # Input received
        'onsubmit',     # Form submitted
        'onreset',      # Form reset
        'onselect',     # Text selected
        'ondrag',       # Dragging
        'ondragend',    # Drag ended
        'ondragenter',  # Drag entered
        'ondragleave',  # Drag left
        'ondragover',   # Drag over
        'ondragstart',  # Drag started
        'ondrop',       # Dropped
        'onscroll',     # Scrolling
        'oncopy',       # Copy
        'oncut',        # Cut
        'onpaste',      # Paste
        'oncontextmenu',# Right click menu
        'ontouchstart', # Touch start
        'ontouchend',   # Touch end
        'ontouchmove',  # Touch move
        'ontouchcancel',# Touch cancelled
        'onwheel',      # Mouse wheel
        'onresize',     # Resize
        'oninvalid',    # Invalid input
        'onsearch',     # Search
        'ontoggle',     # Toggle
        'onbeforeunload', # Before unload
        'onhashchange', # Hash change
        'onpopstate',   # History state change
        'onpageshow',   # Page shown
        'onpagehide',   # Page hidden
        'oncanplay',    # Media can play
        'oncanplaythrough', # Media can play through
        'ondurationchange', # Duration changed
        'onemptied',    # Media emptied
        'onended',      # Media ended
        'onloadeddata', # Media data loaded
        'onloadedmetadata', # Media metadata loaded
        'onloadstart',  # Load started
        'onpause',      # Media paused
        'onplay',       # Media playing
        'onplaying',    # Media playing
        'onprogress',   # Media progress
        'onratechange', # Playback rate change
        'onseeked',     # Seek completed
        'onseeking',    # Seeking
        'onstalled',    # Media stalled
        'onsuspend',    # Media suspended
        'ontimeupdate', # Time update
        'onvolumechange', # Volume change
        'onwaiting',    # Waiting
        'svg',          # SVG elements
        'iframe',       # Iframe elements
        'object',       # Object elements
        'embed',        # Embed elements
        'javascript:',  # JavaScript protocol
        'vbscript:',    # VBScript protocol
        'data:text/html', # Data URI HTML
        # NOTE: Animation event handlers are NOT blocked (onanimationstart, onanimationend, etc.)
        # This is intentional to mimic CVE-2023-30838 vulnerability
    ]
    
    result_html = ""
    preview_content = ""
    
    if html_content:
        # Check against blacklist
        blocked = False
        blocked_term = None
        for term in blacklist:
            if term.lower() in html_content.lower():
                blocked = True
                blocked_term = term
                break
        
        if blocked:
            result_html = '<div class="result error"><strong>Content Blocked:</strong> Dangerous content detected - "{}" is not allowed.</div>'.format(cgi.escape(blocked_term))
            preview_content = "<em>Content blocked for security reasons.</em>"
        else:
            # Content passed blacklist, render it for preview and check with PhantomJS
            preview_content = html_content
            page_to_check = CONTENT_EDITOR_PAGE.format(cgi.escape(html_content), "", html_content)
            result_html = check_xss(page_to_check, flags[0], html_content)
    
    response = make_response(CONTENT_EDITOR_PAGE.format(cgi.escape(html_content), result_html, preview_content))
    response.headers["X-XSS-Protection"] = "0"
    return response


# Legacy endpoint - redirect to new content editor
@app.route('/xss25', methods=['POST', 'GET'])
def xss25_redirect():
    return Response(
        '{"error": "Endpoint deprecated", "redirect": "/content"}',
        status=301,
        headers={'Location': '/content', 'Content-Type': 'application/json'}
    )


if __name__ == '__main__':
    app.run(debug=True)
