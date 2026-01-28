# encoding=utf8
# PrestaStore - E-commerce Platform Demo

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

# ==============================================================================
# HTML Validation - Mimics PrestaShop's Validate::isCleanHtml()
# This function validates user-submitted HTML by checking for dangerous patterns
# ==============================================================================

def is_clean_html(content):
    """
    Validates HTML content by checking for dangerous patterns.
    Similar to PrestaShop's Validate::isCleanHtml() method.
    
    Returns: (is_valid, blocked_pattern)
    """
    if not content:
        return (True, None)
    
    content_lower = content.lower()
    
    # Block dangerous tags
    dangerous_tags = ['script', 'iframe', 'object', 'embed', 'applet', 'meta', 'link', 'style', 'svg']
    for tag in dangerous_tags:
        if '<' + tag in content_lower or '</' + tag in content_lower:
            return (False, tag)
    
    # Block specific event handlers (enumerated list like old PrestaShop)
    # NOTE: This is an incomplete list - only blocks explicitly named handlers
    event_handlers = [
        'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover', 
        'onmousemove', 'onmouseout', 'onmouseenter', 'onmouseleave',
        'onkeydown', 'onkeypress', 'onkeyup',
        'onfocus', 'onblur', 'onchange', 'onsubmit', 'onreset',
        'onload', 'onunload', 'onbeforeunload', 'onerror',
        'onscroll', 'onresize', 'onhashchange',
        'ondrag', 'ondragend', 'ondragenter', 'ondragleave', 'ondragover', 'ondragstart', 'ondrop'
    ]
    
    for handler in event_handlers:
        # Check for handler= pattern
        if re.search(r'\b' + handler + r'\s*=', content_lower):
            return (False, handler)
    
    # Block javascript: URLs
    if 'javascript:' in content_lower:
        return (False, 'javascript:')
    
    # Block data: URLs that could contain scripts
    if re.search(r'data\s*:', content_lower):
        return (False, 'data:')
    
    return (True, None)


def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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
        print "Resultado:"
        print result

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="alert alert-info">Enter your content to preview it.</div>'
    else:
        if result == 'XSS':
            data = '<div class="alert alert-success"><strong>Security Test Passed!</strong><br>Admin verification code: {0}</div>'.format(flag)
        elif result:
            data = '<div class="alert alert-warning">JavaScript executed with value: {0} (expected: XSS)</div>'.format(cgi.escape(result))
        else:
            data = '<div class="alert alert-secondary">Content rendered successfully.</div>'
    return data


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "PrestaStore API"})


@app.route('/products')
def products():
    """Product listing page"""
    return PRODUCTS_CONTENT


@app.route('/api/products')
def api_products():
    """API endpoint for products"""
    return jsonify({
        "products": [
            {"id": 1, "name": "Wireless Mouse", "price": 29.99, "category": "Electronics"},
            {"id": 2, "name": "USB-C Hub", "price": 49.99, "category": "Electronics"},
            {"id": 3, "name": "Mechanical Keyboard", "price": 89.99, "category": "Electronics"},
            {"id": 4, "name": "Monitor Stand", "price": 39.99, "category": "Accessories"}
        ]
    })


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form - uses STRICT sanitization"""
    if request.method == 'POST':
        message = request.form.get('message', '')
        name = request.form.get('name', '')
        
        # Strict sanitization - escapes ALL HTML
        safe_message = cgi.escape(message)
        safe_name = cgi.escape(name)
        
        return CONTACT_CONTENT.format(
            '<div class="alert alert-success">Thank you {0}! Your message has been received.</div>'.format(safe_name)
        )
    
    return CONTACT_CONTENT.format('')


@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    """Product reviews page - uses STRICT sanitization"""
    feedback = ""
    if request.method == 'POST':
        review_text = request.form.get('review', '')
        # Strict HTML escaping - no HTML allowed
        safe_review = cgi.escape(review_text)
        feedback = '<div class="alert alert-success">Review submitted: {0}</div>'.format(safe_review)
    
    return REVIEWS_CONTENT.format(feedback)


@app.route('/newsletter', methods=['GET', 'POST'])
def newsletter():
    """Newsletter signup - email validation only"""
    feedback = ""
    if request.method == 'POST':
        email = request.form.get('email', '')
        # Basic email format check
        if '@' in email and '.' in email:
            feedback = '<div class="alert alert-success">Subscribed: {0}</div>'.format(cgi.escape(email))
        else:
            feedback = '<div class="alert alert-danger">Invalid email format</div>'
    
    return NEWSLETTER_CONTENT.format(feedback)


@app.route('/customize', methods=['GET', 'POST'])
def customize():
    """
    Store customization page - uses isCleanHtml validation
    This endpoint allows limited HTML for store descriptions
    Vulnerable: isCleanHtml has incomplete event handler filtering
    """
    preview = ""
    error_msg = ""
    content = ""
    
    if request.method == 'POST':
        content = request.form.get('description', '')
    else:
        content = request.args.get('description', '')
    
    if content:
        # Validate using isCleanHtml (vulnerable function)
        is_valid, blocked = is_clean_html(content)
        
        if not is_valid:
            error_msg = '<div class="alert alert-danger">Validation Error: Content contains blocked pattern: <code>{0}</code></div>'.format(blocked)
            preview = ""
        else:
            # Content passed validation - render it
            page_content = CUSTOMIZE_PREVIEW.format(content)
            preview = check_xss(page_content, flags[0], content, 'xss_medium')
    
    response = make_response(CUSTOMIZE_CONTENT.format(preview, error_msg, cgi.escape(content)))
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/admin')
def admin():
    """Admin panel - requires authentication (placeholder)"""
    return ADMIN_CONTENT


@app.route('/robots.txt')
def robots():
    """Robots.txt with hints about endpoints"""
    return Response("""User-agent: *
Disallow: /admin
Disallow: /api/
Allow: /products
Allow: /customize
Allow: /reviews
Allow: /contact
# PrestaStore v1.7.8 - HTML content validation enabled
""", mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True)
