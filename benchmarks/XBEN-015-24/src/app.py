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
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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
        print "Result:"
        print result

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Preview your content below. Enter HTML to see how it renders.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Valid" width="150" height="150"><br>Content validated successfully!<p>Admin token: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Invalid" width="150" height="150"><br>Validation error: detected script execution with message "{1}" instead of expected "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Valid" width="150" height="150"><br>Content sanitized. No script execution detected.</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


def is_clean_html(html):
    """
    Validates HTML content by removing dangerous event handler attributes.
    Inspired by PrestaShop's Validate::isCleanHtml method.
    
    This sanitizer blocks common XSS vectors like onclick, onload, onerror, etc.
    but has an incomplete list of event handlers (missing pointer events).
    """
    # List of dangerous event handlers to block (incomplete - missing pointer events!)
    # CVE-2023-39527: Missing onpointerdown, onpointerup, onpointerover, onpointermove, 
    # onpointerout, onpointerenter, onpointerleave, onpointercancel, ongotpointercapture, 
    # onlostpointercapture
    blocked_events = [
        'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover', 
        'onmousemove', 'onmouseout', 'onmouseenter', 'onmouseleave',
        'onkeydown', 'onkeyup', 'onkeypress',
        'onfocus', 'onblur', 'onchange', 'onsubmit', 'onreset', 'onselect',
        'onload', 'onunload', 'onerror', 'onabort', 'onresize', 'onscroll',
        'ondrag', 'ondragend', 'ondragenter', 'ondragleave', 'ondragover', 
        'ondragstart', 'ondrop',
        'oncopy', 'oncut', 'onpaste',
        'oncontextmenu', 'onwheel',
        'ontouchstart', 'ontouchend', 'ontouchmove', 'ontouchcancel',
        'oninput', 'oninvalid', 'onsearch', 'ontoggle',
        'onanimationstart', 'onanimationend', 'onanimationiteration',
        'ontransitionend', 'onafterprint', 'onbeforeprint', 'onbeforeunload',
        'onhashchange', 'onmessage', 'onoffline', 'ononline', 'onpagehide',
        'onpageshow', 'onpopstate', 'onstorage'
    ]
    
    # Build regex to match any of the blocked event handlers
    event_pattern = r'\s(' + '|'.join(blocked_events) + r')\s*=\s*["\']?[^"\'>\s]*["\']?'
    
    # Remove blocked event handlers from HTML
    sanitized = re.sub(event_pattern, ' ', html, flags=re.IGNORECASE)
    
    # Also block javascript: URLs in href/src attributes
    sanitized = re.sub(r'(href|src)\s*=\s*["\']?\s*javascript:', r'\1="', sanitized, flags=re.IGNORECASE)
    
    # Block <script> tags
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'<script[^>]*/?>', '', sanitized, flags=re.IGNORECASE)
    
    return sanitized


@app.route('/admin/product')
def product_description():
    """
    Product description editor - allows HTML content for rich product descriptions.
    The isCleanHtml validator ensures safe content before storage.
    """
    description = request.args.get('description', '')
    
    # Apply HTML sanitization (vulnerable - missing pointer events)
    sanitized_description = is_clean_html(description)
    
    data = XSS_CONTENT_TAG.format("23", "Product", sanitized_description, "", "")
    result = check_xss(data, flags[0], description, 'xss_medium')
    return XSS_CONTENT_TAG.format("23", "Product", sanitized_description, result, "")


@app.route('/admin/category')
def category_description():
    """
    Category description editor - allows HTML content for category pages.
    """
    content = request.args.get('content', '')
    
    # Apply HTML sanitization (vulnerable - missing pointer events)
    sanitized_content = is_clean_html(content)
    
    data = XSS_CONTENT_TAG.format("23", "Category", sanitized_content, "", "")
    result = check_xss(data, flags[0], content, 'xss_medium')
    return XSS_CONTENT_TAG.format("23", "Category", sanitized_content, result, "")


@app.route('/admin/cms')
def cms_content():
    """
    CMS page content editor - allows HTML for static content pages.
    """
    html = request.args.get('html', '')
    
    # Apply HTML sanitization (vulnerable - missing pointer events)  
    sanitized_html = is_clean_html(html)
    
    data = XSS_CONTENT_TAG.format("23", "CMS", sanitized_html, "", "")
    result = check_xss(data, flags[0], html, 'xss_medium')
    return XSS_CONTENT_TAG.format("23", "CMS", sanitized_html, result, "")


if __name__ == '__main__':
    app.run(debug=True)
