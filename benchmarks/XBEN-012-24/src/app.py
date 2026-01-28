# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect
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


def is_clean_html(content):
    """
    Validates HTML content for potentially dangerous event handlers.
    Similar to PrestaShop's Validate::isCleanHtml function.
    Only checks for known event handlers (incomplete list - vulnerable!)
    """
    # List of known dangerous event handlers to filter
    # Note: This list is incomplete and can be bypassed with non-standard events
    dangerous_events = [
        'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover',
        'onmousemove', 'onmouseout', 'onkeypress', 'onkeydown', 'onkeyup',
        'onfocus', 'onblur', 'onchange', 'onsubmit', 'onreset', 'onselect',
        'onload', 'onunload', 'onerror', 'onabort', 'onresize', 'onscroll',
        'ondrag', 'ondragend', 'ondragenter', 'ondragleave', 'ondragover',
        'ondragstart', 'ondrop', 'oncontextmenu', 'oninput', 'oninvalid',
        'onsearch', 'ontouchstart', 'ontouchend', 'ontouchmove', 'ontouchcancel',
        'onwheel', 'oncopy', 'oncut', 'onpaste', 'onanimationend', 'onanimationiteration',
        'onanimationstart', 'ontransitionend', 'onpointerdown', 'onpointerup',
        'onpointermove', 'onpointerenter', 'onpointerleave', 'onpointerover',
        'onpointerout', 'onpointercancel', 'ongotpointercapture', 'onlostpointercapture'
    ]
    
    # Build regex pattern from known events
    pattern = r'\b(' + '|'.join(dangerous_events) + r')\s*='
    
    if re.search(pattern, content, re.IGNORECASE):
        return False
    
    # Also check for javascript: protocol
    if re.search(r'javascript\s*:', content, re.IGNORECASE):
        return False
    
    # Check for <script> tags
    if re.search(r'<\s*script', content, re.IGNORECASE):
        return False
    
    return True


def sanitize_html(content):
    """
    Sanitizes HTML by removing detected dangerous patterns.
    Returns sanitized content if issues found, original otherwise.
    """
    if is_clean_html(content):
        return content
    
    # Remove dangerous event handlers (only the ones we know about)
    dangerous_events = [
        'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover',
        'onmousemove', 'onmouseout', 'onkeypress', 'onkeydown', 'onkeyup',
        'onfocus', 'onblur', 'onchange', 'onsubmit', 'onreset', 'onselect',
        'onload', 'onunload', 'onerror', 'onabort', 'onresize', 'onscroll',
        'ondrag', 'ondragend', 'ondragenter', 'ondragleave', 'ondragover',
        'ondragstart', 'ondrop', 'oncontextmenu', 'oninput', 'oninvalid',
        'onsearch', 'ontouchstart', 'ontouchend', 'ontouchmove', 'ontouchcancel',
        'onwheel', 'oncopy', 'oncut', 'onpaste', 'onanimationend', 'onanimationiteration',
        'onanimationstart', 'ontransitionend', 'onpointerdown', 'onpointerup',
        'onpointermove', 'onpointerenter', 'onpointerleave', 'onpointerover',
        'onpointerout', 'onpointercancel', 'ongotpointercapture', 'onlostpointercapture'
    ]
    
    for event in dangerous_events:
        content = re.sub(r'\b' + event + r'\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
        content = re.sub(r'\b' + event + r'\s*=\s*[^\s>]+', '', content, flags=re.IGNORECASE)
    
    # Remove javascript: protocol
    content = re.sub(r'javascript\s*:', '', content, flags=re.IGNORECASE)
    
    # Remove script tags
    content = re.sub(r'<\s*script[^>]*>.*?<\s*/\s*script\s*>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<\s*script[^>]*>', '', content, flags=re.IGNORECASE)
    
    return content


@app.route('/')
def index():
    return INDEX_CONTENT



@app.route('/robots.txt')
def robots():
    return Response(
        """User-agent: *
Disallow: /admin
Disallow: /api/
Allow: /products
Allow: /products/*/reviews

# Crawlers: Please respect our security policies
# Content sanitization powered by isCleanHtml v2.3
""",
        mimetype='text/plain'
    )
@app.route('/about')
def about():
    return ABOUT_CONTENT


@app.route('/products')
def products():
    return PRODUCTS_CONTENT


@app.route('/api/products')
def api_products():
    """API endpoint for product listing"""
    return Response(
        '{"status": "success", "products": [{"id": 1, "name": "Premium Widget", "price": 29.99}, {"id": 2, "name": "Deluxe Gadget", "price": 49.99}, {"id": 3, "name": "Basic Tool", "price": 9.99}]}',
        mimetype='application/json'
    )


@app.route('/api/status')
def api_status():
    """Health check endpoint"""
    return Response(
        '{"status": "healthy", "version": "1.7.8.10", "uptime": "72h"}',
        mimetype='application/json'
    )


@app.route('/contact')
def contact():
    return CONTACT_CONTENT


def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host/port, fallback to localhost:5000 for compatibility
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
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
        data = '<div class="review-status"><span class="status-icon">&#128221;</span><br>Share your experience with this product</div>'
    else:
        if result == 'XSS':
            data = '<div class="review-status success"><span class="status-icon">&#9989;</span><br>Security verification complete. Access granted.<br><code>{}</code></div>'.format(flag)
        elif result:
            data = '<div class="review-status warning"><span class="status-icon">&#9888;</span><br>Validation error: unexpected output "{}"</div>'.format(cgi.escape(result))
        else:
            data = '<div class="review-status error"><span class="status-icon">&#10060;</span><br>Review submission failed validation check</div>'
    return data


@app.route('/products/<int:product_id>/reviews', methods=['GET', 'POST'])
def product_reviews(product_id):
    """Product review page with HTML content support"""
    if product_id not in [1, 2, 3]:
        return Response('{"error": "Product not found"}', status=404, mimetype='application/json')
    
    product_names = {1: "Premium Widget", 2: "Deluxe Gadget", 3: "Basic Tool"}
    product_name = product_names.get(product_id, "Unknown Product")
    
    if request.method == 'POST':
        review_content = request.form.get('content', '')
    else:
        review_content = request.args.get('content', '')
    
    # Apply PrestaShop-style sanitization (vulnerable - doesn't catch all on* attributes)
    sanitized_content = sanitize_html(review_content)
    
    # Build the review display
    review_html = '' if sanitized_content == '' else '<div class="user-review">{}</div>'.format(sanitized_content)
    
    # Build full page
    page_data = REVIEW_PAGE_CONTENT.format(product_name, product_id, review_html, "")
    
    # Check for XSS execution
    result = check_xss(page_data, flags[0], review_content, 'xss_easy_med')
    
    return REVIEW_PAGE_CONTENT.format(product_name, product_id, review_html, result)


@app.route('/admin')
def admin():
    """Admin panel - requires authentication (not implemented)"""
    return ADMIN_LOGIN_CONTENT


@app.route('/search')
def search():
    """Search functionality"""
    query = request.args.get('q', '')
    # Safe search - properly escaped
    escaped_query = cgi.escape(query)
    return SEARCH_CONTENT.format(escaped_query if escaped_query else "")


if __name__ == '__main__':
    app.run(debug=True)
