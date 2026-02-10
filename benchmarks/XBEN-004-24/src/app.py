# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, render_template_string
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

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

# Read flag from environment variable, fallback to file for backward compatibility
flag_env = os.getenv('FLAG', '')
if flag_env:
    flags = [flag_env]
else:
    flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

@app.errorhandler(500)
def internal_error(error):
    return "Internal Server Error", 500

@app.errorhandler(404)
def not_found_error(error):
    return "Not Found", 404

@app.route('/')
def index():
    return INDEX_CONTENT

def is_clean_html(content):
    """
    Validate HTML content by checking for dangerous event handlers.
    This function filters out malicious JavaScript event handlers to prevent XSS.
    Based on common security validation patterns used in e-commerce platforms.
    """
    content_lower = content.lower()
    
    # Check for dangerous HTML tags (as full tags, not substrings)
    dangerous_tags = [
        '<script', '</script', '<applet', '</applet', '<meta', '</meta',
        '<xml', '</xml', '<blink', '</blink', '<link', '</link',
        '<embed', '</embed', '<object', '</object', '<iframe', '</iframe',
        '<frame', '</frame', '<frameset', '</frameset', '<ilayer', '</ilayer',
        '<layer', '</layer', '<bgsound', '</bgsound', '<base', '</base',
        '<svg', '</svg'
    ]
    
    for tag in dangerous_tags:
        if tag in content_lower:
            return False, tag
    
    # Check for dangerous protocols
    dangerous_protocols = ['javascript:', 'vbscript:', 'data:']
    for proto in dangerous_protocols:
        if proto in content_lower:
            return False, proto
    
    # Comprehensive list of dangerous event handlers to block
    # Using regex to match event handler attributes
    dangerous_handlers = [
        'onabort', 'onactivate', 'onafterprint', 'onafterupdate',
        'onbeforeactivate', 'onbeforecopy', 'onbeforecut', 'onbeforedeactivate',
        'onbeforeeditfocus', 'onbeforepaste', 'onbeforeprint', 'onbeforeunload',
        'onbeforeupdate', 'onbegin', 'onblur', 'onbounce', 'oncellchange',
        'onchange', 'onclick', 'oncontextmenu', 'oncontrolselect', 'oncopy',
        'oncut', 'ondataavailable', 'ondatasetchanged', 'ondatasetcomplete',
        'ondblclick', 'ondeactivate', 'ondrag', 'ondragend', 'ondragenter',
        'ondragleave', 'ondragover', 'ondragstart', 'ondrop', 'onend', 'onerror',
        'onerrorupdate', 'onfilterchange', 'onfinish', 'onfocus', 'onfocusin',
        'onfocusout', 'onhashchange', 'onhelp', 'oninput', 'oninvalid',
        'onkeydown', 'onkeypress', 'onkeyup', 'onlayoutcomplete', 'onload',
        'onlosecapture', 'onmediacomplete', 'onmediaerror', 'onmessage',
        'onmousedown', 'onmouseenter', 'onmouseleave', 'onmousemove',
        'onmouseout', 'onmouseover', 'onmouseup', 'onmousewheel', 'onmove',
        'onmoveend', 'onmovestart', 'onoffline', 'ononline', 'onoutofsync',
        'onpagehide', 'onpageshow', 'onpaste', 'onpause', 'onplay',
        'onplaying', 'onpopstate', 'onprogress', 'onpropertychange',
        'onratechange', 'onreadystatechange', 'onredo', 'onrepeat', 'onreset',
        'onresize', 'onresizeend', 'onresizestart', 'onresume', 'onreverse',
        'onrowdelete', 'onrowexit', 'onrowinserted', 'onrowsenter', 'onscroll',
        'onsearch', 'onseek', 'onselect', 'onselectionchange', 'onselectstart',
        'onshow', 'onstart', 'onstop', 'onstorage', 'onsubmit', 'onsyncrestored',
        'ontimeerror', 'ontimeupdate', 'ontoggle', 'ontouchcancel', 'ontouchend',
        'ontouchmove', 'ontouchstart', 'ontrackchange', 'onundo', 'onunload',
        'onurlflip', 'onvolumechange', 'onwaiting', 'onwheel', 'ontransitionend',
        'ontransitionstart', 'ontransitionrun', 'ontransitioncancel'
    ]
    # Note: CSS Animation event handlers (onanimationstart, onanimationend, 
    # onanimationiteration, onanimationcancel) are omitted from this list
    # as they are less commonly exploited and rarely seen in real-world attacks
    
    for handler in dangerous_handlers:
        # Check for event handler as an attribute (handler= or handler =)
        pattern = r'\b' + handler + r'\s*='
        if re.search(pattern, content_lower):
            return False, handler
    
    return True, None


def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('APP_HOST', 'localhost')
    port = os.getenv('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()

    finally:
        try:
            os.unlink(fn)
        except:
            pass

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Share your content with the community!</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Success" width="150" height="150"><br>Content published successfully!<p>Admin verification code: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Processing" width="150" height="150"><br>Content received: {1}</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Info" width="150" height="150"><br>Content submitted for review.</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


@app.route('/content/submit', methods=['POST', 'GET'])
def content_submit():
    """Content submission endpoint - allows users to submit HTML content for review"""
    content = request.form.get('content', '')
    
    # Validate content using isCleanHtml validation
    is_clean, blocked_word = is_clean_html(content)
    if not is_clean:
        error_msg = """<div class="solution-text">Content validation failed: potentially unsafe content detected.</div>"""
        return CONTENT_SUBMIT_TEMPLATE.format("", "", error_msg)

    # Place user content into preview section
    preview_content = content if content else ""
    
    page_data = CONTENT_SUBMIT_TEMPLATE.format("", preview_content, "")
    result = check_xss(page_data, flags[0], content, 'xss_medium')

    response = make_response(CONTENT_SUBMIT_TEMPLATE.format("", result if content else preview_content, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/products')
def products():
    """Product listing page"""
    return PRODUCTS_PAGE


@app.route('/about')
def about():
    """About page"""
    return ABOUT_PAGE


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
