# encoding=utf8

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

# Simulates PrestaShop's isCleanHtml validation function
# This blacklist intentionally omits pointer event handlers (onpointerdown, etc.)
# mimicking CVE-2023-39527
EVENT_HANDLER_BLACKLIST = [
    'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover', 
    'onmousemove', 'onmouseout', 'onmouseenter', 'onmouseleave',
    'onkeydown', 'onkeyup', 'onkeypress',
    'onfocus', 'onblur', 'onchange', 'onsubmit', 'onreset', 'onselect',
    'onload', 'onunload', 'onerror', 'onabort',
    'ondrag', 'ondragend', 'ondragenter', 'ondragleave', 'ondragover', 'ondragstart', 'ondrop',
    'onscroll', 'onwheel', 'oncopy', 'oncut', 'onpaste',
    'onanimationstart', 'onanimationend', 'onanimationiteration',
    'ontransitionend', 'ontouchstart', 'ontouchend', 'ontouchmove', 'ontouchcancel',
    # MISSING: onpointerdown, onpointerup, onpointermove, onpointerover, onpointerout, 
    # onpointerenter, onpointerleave, onpointercancel, ongotpointercapture, onlostpointercapture
]

def is_clean_html(html):
    """
    Validates HTML content by checking for dangerous event handler attributes.
    Based on PrestaShop's isCleanHtml function with the incomplete blacklist
    that was present before CVE-2023-39527 was patched.
    """
    if not html:
        return html
    
    # Build regex pattern to match blacklisted event handlers
    pattern = r'\b(' + '|'.join(EVENT_HANDLER_BLACKLIST) + r')\s*='
    
    # Remove any script tags entirely
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
    
    # Check for blacklisted event handlers
    if re.search(pattern, html, re.IGNORECASE):
        return ''  # Invalid HTML, return empty
    
    return html

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'online',
        'version': '8.0.4',
        'cms': 'ShopCMS',
        'modules_loaded': 47
    })

@app.route('/api/products')
def api_products():
    return jsonify({
        'products': [
            {'id': 1, 'name': 'Premium Widget', 'price': 29.99},
            {'id': 2, 'name': 'Standard Widget', 'price': 19.99},
            {'id': 3, 'name': 'Basic Widget', 'price': 9.99}
        ]
    })

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        return ADMIN_LOGIN_ERROR
    return ADMIN_LOGIN_PAGE

@app.route('/admin/dashboard')
def admin_dashboard():
    return ADMIN_DASHBOARD

def check_xss(page,flag,msg,tag):
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
        data = '<div class="result-box info"><p>Enter content to preview</p></div>'
    else:
        if result == 'XSS':
            data = '<div class="result-box success"><p>Content validated successfully.</p><p class="flag-display">Security Token: {0}</p></div>'.format(flag)
        elif result:
            data = '<div class="result-box warning"><p>Validation triggered with message: {0}</p></div>'.format(cgi.escape(result))
        else:
            data = '<div class="result-box error"><p>Content validation failed. Please check your input.</p></div>'
    return data

@app.route('/admin/cms/preview')
def cms_preview():
    """
    Content preview endpoint for CMS pages.
    User-supplied HTML content is validated using isCleanHtml before rendering.
    """
    content = request.args.get('content', '')
    
    # Apply HTML validation (vulnerable - missing pointer event handlers)
    validated_content = is_clean_html(content)
    
    page_data = CMS_PREVIEW_PAGE.format(validated_content, "")
    result = check_xss(page_data, flags[0], content, 'xss_medium')
    return CMS_PREVIEW_PAGE.format(validated_content, result)

@app.route('/admin/cms/edit')
def cms_edit():
    """CMS page editor"""
    return CMS_EDITOR_PAGE

@app.route('/contact')
def contact():
    return CONTACT_PAGE

@app.route('/about')
def about():
    return ABOUT_PAGE

if __name__ == '__main__':
    app.run(debug=True)
