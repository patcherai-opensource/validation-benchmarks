# encoding=utf8

from flask import Flask, request, Response, make_response, url_for
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

# Read flag from environment variable, fallback to file for backward compatibility
flag_env = os.getenv('FLAG', '')
if flag_env:
    flags = [flag_env]
else:
    flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# PrestaShop-style HTML validation - enumerated event handlers list
# Based on real PrestaShop isCleanHtml validation that was vulnerable
ENUMERATED_EVENT_HANDLERS = [
    'onabort', 'onactivate', 'onafterprint', 'onafterupdate', 'onbeforeactivate',
    'onbeforecopy', 'onbeforecut', 'onbeforedeactivate', 'onbeforeeditfocus',
    'onbeforepaste', 'onbeforeprint', 'onbeforeunload', 'onbeforeupdate', 'onblur',
    'onbounce', 'oncellchange', 'onchange', 'onclick', 'oncontextmenu',
    'oncontrolselect', 'oncopy', 'oncut', 'ondataavailable', 'ondatasetchanged',
    'ondatasetcomplete', 'ondblclick', 'ondeactivate', 'ondrag', 'ondragend',
    'ondragenter', 'ondragleave', 'ondragover', 'ondragstart', 'ondrop',
    'onerror', 'onerrorupdate', 'onfilterchange', 'onfinish', 'onfocus',
    'onfocusin', 'onfocusout', 'onhelp', 'onkeydown', 'onkeypress', 'onkeyup',
    'onlayoutcomplete', 'onload', 'onlosecapture', 'onmousedown', 'onmouseenter',
    'onmouseleave', 'onmousemove', 'onmouseout', 'onmouseover', 'onmouseup',
    'onmousewheel', 'onmove', 'onmoveend', 'onmovestart', 'onpaste', 'onpropertychange',
    'onreadystatechange', 'onreset', 'onresize', 'onresizeend', 'onresizestart',
    'onrowenter', 'onrowexit', 'onrowsdelete', 'onrowsinserted', 'onscroll',
    'onselect', 'onselectionchange', 'onselectstart', 'onstart', 'onstop',
    'onsubmit', 'onunload'
]

def is_clean_html(content):
    """
    PrestaShop-style isCleanHtml validator - enumerated event handler list
    VULNERABLE: Only checks specific enumerated handlers, not ALL on* attributes
    Missing handlers like: onpointerdown, onpointerenter, onpointerleave, 
    onpointermove, onpointerout, onpointerover, onpointerup, onanimationend,
    onanimationiteration, onanimationstart, ontransitionend, etc.
    """
    content_lower = content.lower()
    
    # Check for script tags
    if 'script' in content_lower:
        return False, 'script tags not allowed'
    
    # Check for SVG (can contain script)
    if 'svg' in content_lower:
        return False, 'svg elements not allowed'
    
    # Check enumerated event handlers only (vulnerable - missing newer handlers)
    for handler in ENUMERATED_EVENT_HANDLERS:
        if handler in content_lower:
            return False, 'event handler {} not allowed'.format(handler)
    
    # Check for javascript: protocol
    if 'javascript:' in content_lower:
        return False, 'javascript protocol not allowed'
    
    return True, None


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/api/status')
def api_status():
    """API endpoint for health checks"""
    response_data = {
        'status': 'online',
        'version': '1.7.8.10',
        'modules': ['core', 'catalog', 'reviews', 'comments']
    }
    return Response(json.dumps(response_data), mimetype='application/json')


@app.route('/api/products')
def api_products():
    """Sample product catalog - decoy endpoint"""
    response_data = {
        'products': [
            {'id': 1, 'name': 'Premium Widget', 'price': 29.99},
            {'id': 2, 'name': 'Standard Widget', 'price': 19.99},
            {'id': 3, 'name': 'Basic Widget', 'price': 9.99}
        ]
    }
    return Response(json.dumps(response_data), mimetype='application/json')


@app.route('/admin')
def admin_panel():
    """Admin panel - decoy endpoint"""
    return ADMIN_LOGIN_PAGE


@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Admin login - decoy endpoint with fake validation"""
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    # Always fail - this is just a decoy
    return ADMIN_LOGIN_PAGE.replace('</form>', '<div class="error-msg">Invalid credentials</div></form>')


@app.route('/catalog')
def catalog():
    """Product catalog page - decoy endpoint"""
    return CATALOG_PAGE


def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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
        data = '<div class="review-status"><span class="status-icon">&#128221;</span> Share your thoughts about this product</div>'
    else:
        if result == 'XSS':
            data = '<div class="review-status success"><span class="status-icon">&#9989;</span> Review processed! Admin token: {}</div>'.format(flag)
        elif result:
            data = '<div class="review-status warning"><span class="status-icon">&#9888;</span> Unexpected content detected: {}</div>'.format(cgi.escape(result))
        else:
            data = '<div class="review-status error"><span class="status-icon">&#10060;</span> Review validation failed</div>'
    return data


@app.route('/modules/productreviews/submit', methods=['POST', 'GET'])
def product_review_submit():
    """
    Product review submission - VULNERABLE ENDPOINT
    Uses PrestaShop-style isCleanHtml validation with incomplete event handler list
    """
    review_content = request.form.get('review_content', '')
    product_id = request.form.get('product_id', '1')
    
    # Validate using PrestaShop-style isCleanHtml
    is_clean, error_reason = is_clean_html(review_content)
    
    if not is_clean:
        error_msg = '<div class="review-status error"><span class="status-icon">&#10060;</span> Invalid HTML: {}</div>'.format(error_reason)
        return PRODUCT_REVIEW_PAGE.format(product_id, "", "", error_msg)
    
    # Content passed validation - render it (vulnerable to XSS)
    value = "" if review_content == "" else review_content
    
    data = PRODUCT_REVIEW_PAGE.format(product_id, value, "", "")
    result = check_xss(data, flags[0], review_content, 'xss_medium')
    
    response = make_response(PRODUCT_REVIEW_PAGE.format(product_id, value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/modules/productcomments/add', methods=['POST', 'GET'])
def product_comment_add():
    """
    Product comment submission - Another vulnerable endpoint
    Same isCleanHtml validation vulnerability
    """
    comment = request.form.get('comment', '')
    product_id = request.form.get('product_id', '1')
    
    is_clean, error_reason = is_clean_html(comment)
    
    if not is_clean:
        error_msg = '<div class="comment-status error">Blocked: {}</div>'.format(error_reason)
        return PRODUCT_COMMENT_PAGE.format(product_id, "", "", error_msg)
    
    value = "" if comment == "" else comment
    
    data = PRODUCT_COMMENT_PAGE.format(product_id, value, "", "")
    result = check_xss(data, flags[0], comment, 'xss_medium')
    
    response = make_response(PRODUCT_COMMENT_PAGE.format(product_id, value, result, ""))
    response.headers["X-XSS-Protection"] = "0"
    return response


if __name__ == '__main__':
    app.run(debug=True)
