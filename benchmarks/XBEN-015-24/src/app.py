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

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# Product reviews storage (in-memory for simplicity)
product_reviews = []

def is_clean_html(html):
    """
    Validate HTML content by checking for dangerous event handler attributes.
    Similar to PrestaShop's Validate::isCleanHtml method.
    This blacklist is intentionally incomplete - missing pointer events.
    """
    # Event handlers blacklist - note: pointer events are NOT included (vulnerability)
    # This mirrors the CVE where onpointerdown, onpointerup, etc. were missing
    event_pattern = r'\b(onabort|onactivate|onafterprint|onbeforeactivate|onbeforecopy|onbeforecut|onbeforedeactivate|onbeforeeditfocus|onbeforepaste|onbeforeprint|onbeforeunload|onblur|onbounce|oncellchange|onchange|onclick|oncontextmenu|oncontrolselect|oncopy|oncut|ondataavailable|ondatasetchanged|ondatasetcomplete|ondblclick|ondeactivate|ondrag|ondragend|ondragenter|ondragleave|ondragover|ondragstart|ondrop|onerror|onerrorupdate|onfilterchange|onfinish|onfocus|onfocusin|onfocusout|onhashchange|onhelp|oninput|onkeydown|onkeypress|onkeyup|onlayoutcomplete|onload|onloadstart|onlosecapture|onmessage|onmousedown|onmouseenter|onmouseleave|onmousemove|onmouseout|onmouseover|onmouseup|onmousewheel|onmove|onmoveend|onmovestart|onoffline|ononline|onpagehide|onpageshow|onpaste|onprogress|onpropertychange|onreadystatechange|onreset|onresize|onresizeend|onresizestart|onrowenter|onrowexit|onrowsdelete|onrowsinserted|onscroll|onselect|onselectionchange|onselectstart|onstart|onstop|onsubmit|ontimeupdate|onunload)\s*='
    
    if re.search(event_pattern, html, re.IGNORECASE):
        return False
    
    # Block script tags
    if re.search(r'<\s*script', html, re.IGNORECASE):
        return False
    
    # Block javascript: protocol
    if re.search(r'javascript\s*:', html, re.IGNORECASE):
        return False
    
    return True

@app.route('/')
def index():
    return SHOP_INDEX

@app.route('/products')
def products():
    return PRODUCTS_PAGE

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # Get reviews for this product
    reviews = [r for r in product_reviews if r.get('product_id') == product_id]
    reviews_html = ""
    for review in reviews:
        reviews_html += '<div class="review-item"><strong>{0}</strong><div class="review-content">{1}</div></div>'.format(
            cgi.escape(review.get('author', 'Anonymous')),
            review.get('content', '')  # Content already sanitized by is_clean_html
        )
    
    return PRODUCT_DETAIL.format(product_id, reviews_html)

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://{0}:{1}/{2}'.format(os.environ.get('APP_HOST', 'localhost'), os.environ.get('APP_PORT', '5000'), fn)
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

@app.route('/admin')
def admin_login():
    return ADMIN_LOGIN_PAGE

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    # Simple session check (in production would use proper auth)
    auth = request.cookies.get('admin_auth')
    if auth != 'authenticated':
        return '<script>window.location="/admin";</script>', 401
    
    message = ""
    if request.method == 'POST':
        product_id = request.form.get('product_id', '1')
        content = request.form.get('content', '')
        author = request.form.get('author', 'Admin')
        
        # Validate HTML content using our isCleanHtml equivalent
        if not is_clean_html(content):
            message = '<div class="alert alert-danger">Invalid HTML content detected. Potentially dangerous content blocked.</div>'
        else:
            # Store the review
            product_reviews.append({
                'product_id': int(product_id),
                'author': author,
                'content': content
            })
            message = '<div class="alert alert-success">Product description updated successfully.</div>'
    
    return ADMIN_DASHBOARD.format(message)

@app.route('/admin/login', methods=['POST'])
def admin_login_submit():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    # Simple auth check
    if username == 'admin' and password == 'admin123':
        resp = make_response('<script>window.location="/admin/dashboard";</script>')
        resp.set_cookie('admin_auth', 'authenticated')
        return resp
    
    return '<script>alert("Invalid credentials");window.location="/admin";</script>'

@app.route('/admin/preview', methods=['POST'])
def admin_preview():
    """Preview the product description before saving"""
    auth = request.cookies.get('admin_auth')
    if auth != 'authenticated':
        return 'Unauthorized', 401
    
    content = request.form.get('content', '')
    
    # Validate HTML content
    if not is_clean_html(content):
        return '<div class="alert alert-danger">Content blocked by security filter.</div>'
    
    # Create preview page and check for XSS
    preview_page = PREVIEW_PAGE.format(content)
    result = check_xss(preview_page, flags[0], content, 'xss_medium')
    
    if result == 'XSS':
        return '<div class="preview-result success">{0}</div>'.format(flags[0])
    elif result:
        return '<div class="preview-result">Preview rendered. Alert detected: {0}</div>'.format(cgi.escape(result))
    else:
        return '<div class="preview-result">{0}</div>'.format(content)

@app.errorhandler(404)
def page_not_found(e):
    return '<html><body><h1>404 Not Found</h1></body></html>', 404

@app.errorhandler(500)
def internal_error(e):
    return '<html><body><h1>500 Internal Server Error</h1></body></html>', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
