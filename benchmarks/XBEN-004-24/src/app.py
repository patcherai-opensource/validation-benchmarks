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


def is_clean_html(content):
    """
    Validates HTML content by checking for potentially dangerous script elements
    and event handlers. This is based on a whitelist approach where known
    dangerous patterns are explicitly blocked.
    """
    if not content:
        return True
    
    content_lower = content.lower()
    
    # Block script tags and common dangerous elements
    dangerous_tags = ['<script', '</script', '<iframe', '<object', '<embed', '<applet']
    for tag in dangerous_tags:
        if tag in content_lower:
            return False
    
    # Block known dangerous event handlers (enumerated list approach)
    # This mirrors the PrestaShop isCleanHtml validation pattern
    dangerous_handlers = [
        'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover',
        'onmousemove', 'onmouseout', 'onmouseenter', 'onmouseleave',
        'onkeydown', 'onkeyup', 'onkeypress',
        'onload', 'onunload', 'onerror', 'onabort',
        'onsubmit', 'onreset', 'onselect', 'onchange', 'onblur',
        'ondrag', 'ondragstart', 'ondragend', 'ondragover', 'ondragenter',
        'ondragleave', 'ondrop',
        'oncopy', 'oncut', 'onpaste',
        'onscroll', 'onresize', 'onwheel',
        'oncontextmenu', 'oninput', 'oninvalid',
        'ontouchstart', 'ontouchend', 'ontouchmove', 'ontouchcancel',
        'onpointerdown', 'onpointerup', 'onpointermove', 'onpointerenter',
        'onpointerleave', 'onpointerover', 'onpointerout', 'onpointercancel',
        'onbeforeunload', 'onhashchange', 'onpopstate', 'onpagehide', 'onpageshow',
        'onmessage', 'ononline', 'onoffline', 'onstorage',
        'onbeforeprint', 'onafterprint',
        'onplay', 'onpause', 'onended', 'onvolumechange', 'onseeking', 'onseeked',
        'ontimeupdate', 'ondurationchange', 'onratechange', 'oncanplay',
        'oncanplaythrough', 'onloadeddata', 'onloadedmetadata', 'onprogress',
        'onstalled', 'onsuspend', 'onemptied', 'onwaiting',
        'onanimationstart', 'onanimationend', 'onanimationiteration',
        'ontransitionend', 'ontransitionstart', 'ontransitionrun', 'ontransitioncancel'
    ]
    
    for handler in dangerous_handlers:
        # Check for handler with various attribute formats
        pattern = r'\b' + handler + r'\s*='
        if re.search(pattern, content_lower):
            return False
    
    # Block javascript: protocol
    if 'javascript:' in content_lower:
        return False
    
    # Block data: protocol for potential script injection
    if re.search(r'data:\s*text/html', content_lower):
        return False
    
    return True


def check_xss(page, flag, msg):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('APP_HOST', 'localhost')
    port = os.getenv('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = None
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
    return result


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/products')
def products():
    return PRODUCTS_PAGE


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    products_data = {
        1: {'name': 'Classic T-Shirt', 'price': '$29.99', 'description': 'Premium cotton t-shirt with comfortable fit.'},
        2: {'name': 'Denim Jeans', 'price': '$79.99', 'description': 'Classic blue denim jeans with modern cut.'},
        3: {'name': 'Leather Jacket', 'price': '$199.99', 'description': 'Genuine leather jacket with quilted lining.'},
    }
    
    if product_id not in products_data:
        return make_response("Product not found", 404)
    
    product = products_data[product_id]
    return PRODUCT_DETAIL_PAGE.format(
        product_id=product_id,
        product_name=product['name'],
        product_price=product['price'],
        product_description=product['description']
    )


@app.route('/product/<int:product_id>/review', methods=['POST'])
def submit_review(product_id):
    review_content = request.form.get('review', '')
    reviewer_name = request.form.get('name', 'Anonymous')
    
    if not review_content:
        return make_response(REVIEW_RESULT_PAGE.format(
            status='error',
            message='Review content is required.',
            review_display=''
        ))
    
    # Validate the review content using our HTML sanitization
    if not is_clean_html(review_content):
        return make_response(REVIEW_RESULT_PAGE.format(
            status='error',
            message='Your review contains invalid content. Please remove any scripts or event handlers.',
            review_display=''
        ))
    
    # Build the review display HTML
    review_html = REVIEW_DISPLAY.format(
        reviewer_name=cgi.escape(reviewer_name),
        review_content=review_content
    )
    
    # Check for XSS execution
    full_page = REVIEW_CHECK_PAGE.format(review_html=review_html)
    result = check_xss(full_page, flags[0], review_content)
    
    if result == 'XSS':
        # XSS was successfully triggered
        return make_response(REVIEW_RESULT_PAGE.format(
            status='success',
            message='Review processed. Admin notification: ' + flags[0],
            review_display=review_html
        ))
    else:
        return make_response(REVIEW_RESULT_PAGE.format(
            status='pending',
            message='Thank you for your review! It will be visible after moderation.',
            review_display=review_html
        ))


@app.route('/about')
def about():
    return ABOUT_PAGE


@app.route('/contact')
def contact():
    return CONTACT_PAGE


@app.errorhandler(404)
def page_not_found(e):
    return make_response(ERROR_404_PAGE, 404)


@app.errorhandler(500)
def internal_error(e):
    return make_response(ERROR_500_PAGE, 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
