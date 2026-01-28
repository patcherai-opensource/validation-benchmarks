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

# Load flag from environment variable or file
flag_env = os.environ.get('FLAG_VALUE')
if flag_env:
    flags = [flag_env]
else:
    flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# Simulated FAQ database
FAQ_DATABASE = {
    1: {"id": 1, "cat": 1, "title": "How do I reset my password?", "content": "Navigate to the login page and click 'Forgot Password'."},
    2: {"id": 2, "cat": 1, "title": "How do I update my profile?", "content": "Go to Settings > Profile to update your information."},
    3: {"id": 3, "cat": 2, "title": "What payment methods are accepted?", "content": "We accept Visa, MasterCard, and PayPal."},
    4: {"id": 4, "cat": 2, "title": "How do refunds work?", "content": "Refunds are processed within 5-7 business days."},
    5: {"id": 5, "cat": 3, "title": "System requirements", "content": "Minimum: 4GB RAM, 2GHz CPU, 1GB storage."},
}

CATEGORIES = {
    1: {"id": 1, "name": "Account", "description": "Account management related questions"},
    2: {"id": 2, "name": "Billing", "description": "Payment and billing inquiries"},  
    3: {"id": 3, "name": "Technical", "description": "Technical requirements and troubleshooting"},
}

@app.route('/health')
def health_check():
    return 'OK', 200

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/faq')
def faq_list():
    """Display all FAQs - non-vulnerable endpoint"""
    cat_id = request.args.get('cat', None)
    if cat_id:
        try:
            cat_id = int(cat_id)
            faqs = [f for f in FAQ_DATABASE.values() if f['cat'] == cat_id]
        except:
            faqs = FAQ_DATABASE.values()
    else:
        faqs = FAQ_DATABASE.values()
    return FAQ_LIST_PAGE.format(faq_items=generate_faq_list(faqs))

def generate_faq_list(faqs):
    items = ""
    for faq in faqs:
        items += '<li><a href="/faq/{0}">{1}</a></li>'.format(faq['id'], cgi.escape(faq['title']))
    return items if items else "<li>No FAQs found</li>"

@app.route('/faq/<int:faq_id>')
def faq_detail(faq_id):
    """View single FAQ - non-vulnerable endpoint"""
    faq = FAQ_DATABASE.get(faq_id)
    if not faq:
        return '<html><body><h1>404 - FAQ not found</h1></body></html>', 404
    return FAQ_DETAIL_PAGE.format(
        title=cgi.escape(faq['title']),
        content=cgi.escape(faq['content']),
        faq_id=faq_id
    )

@app.route('/category')
def category_list():
    """List categories - non-vulnerable endpoint"""
    cat_html = ""
    for cat in CATEGORIES.values():
        cat_html += '<li><a href="/faq?cat={0}">{1}</a> - {2}</li>'.format(
            cat['id'], cgi.escape(cat['name']), cgi.escape(cat['description'])
        )
    return CATEGORY_PAGE.format(categories=cat_html)

@app.route('/search')
def search():
    """Search FAQs - safe with proper escaping"""
    query = request.args.get('q', '')
    results = []
    if query:
        query_lower = query.lower()
        for faq in FAQ_DATABASE.values():
            if query_lower in faq['title'].lower() or query_lower in faq['content'].lower():
                results.append(faq)
    return SEARCH_PAGE.format(
        query=cgi.escape(query),
        results=generate_faq_list(results),
        count=len(results)
    )

@app.route('/api/faq')
def api_faq_list():
    """API endpoint - safe"""
    return jsonify({"faqs": list(FAQ_DATABASE.values()), "status": "ok"})

@app.route('/export')
def export_faq():
    """Export FAQ to HTML - non-vulnerable"""
    faq_id = request.args.get('id', None)
    if not faq_id:
        return '<html><body><h1>Export Error</h1><p>Missing id parameter</p></body></html>', 400
    try:
        faq_id = int(faq_id)
    except:
        return '<html><body><h1>Export Error</h1><p>Invalid id parameter</p></body></html>', 400
    
    faq = FAQ_DATABASE.get(faq_id)
    if not faq:
        return '<html><body><h1>Export Error</h1><p>FAQ not found</p></body></html>', 404
    
    return EXPORT_PAGE.format(
        title=cgi.escape(faq['title']),
        content=cgi.escape(faq['content'])
    )

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for base URL with fallback to localhost
    base_url = os.environ.get('APP_BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
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
        return None
    else:
        if result == 'XSS':
            return flag
        elif result:
            return "alert_detected_but_wrong"
        else:
            return None
    return None

############## VULNERABLE ENDPOINT - CVE-2023-1880 style ##############

@app.route('/send2friend')
def send_to_friend():
    """
    Send FAQ to a friend - VULNERABLE endpoint
    CVE-2023-1880 style: artlang parameter is inserted into hidden input value without sanitization
    Payload example: "><script>alert('XSS')</script>
    """
    cat = request.args.get('cat', '1')
    faq_id = request.args.get('id', '1')
    artlang = request.args.get('artlang', 'en')  # Vulnerable parameter - not sanitized
    
    # Validate cat and id
    try:
        cat_id = int(cat)
        faq_id_int = int(faq_id)
    except:
        return '<html><body><h1>Error</h1><p>Invalid parameters</p></body></html>', 400
    
    faq = FAQ_DATABASE.get(faq_id_int)
    if not faq:
        return '<html><body><h1>Error</h1><p>FAQ not found</p></body></html>', 404
    
    # Generate the page with unsanitized artlang value in hidden input (CVE-2023-1880 pattern)
    page_content = SEND2FRIEND_PAGE.format(
        faq_title=cgi.escape(faq['title']),
        faq_content=cgi.escape(faq['content']),
        cat=cgi.escape(str(cat)),
        faq_id=cgi.escape(str(faq_id)),
        artlang=artlang  # VULNERABLE: Not escaped - allows XSS via attribute breakout
    )
    
    # Check if XSS was triggered
    xss_result = check_xss(page_content, flags[0], artlang, 'xss_easy_med')
    
    if xss_result == flags[0]:
        # XSS successful - return page with flag
        return SEND2FRIEND_SUCCESS_PAGE.format(flag=xss_result)
    elif xss_result == "alert_detected_but_wrong":
        return '<html><body><h1>Almost there!</h1><p>Alert detected but content was not "XSS". Try again.</p></body></html>'
    else:
        return page_content


@app.route('/contact')
def contact():
    """Contact page - non-vulnerable"""
    return CONTACT_PAGE

@app.route('/about')
def about():
    """About page - non-vulnerable"""
    return ABOUT_PAGE

@app.route('/robots.txt')
def robots():
    """Serve robots.txt for reconnaissance"""
    try:
        with open('static/robots.txt', 'r') as f:
            return Response(f.read(), mimetype='text/plain')
    except:
        return Response("User-agent: *\nDisallow: /admin/\n", mimetype='text/plain')

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5001, threaded=True)
    app.run(debug=True)
