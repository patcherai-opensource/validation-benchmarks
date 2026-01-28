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

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# FAQ database - simulating phpMyFAQ
FAQ_ITEMS = [
    {"id": 1, "cat": 1, "title": "How do I reset my password?", "content": "Go to Settings > Security > Reset Password."},
    {"id": 2, "cat": 1, "title": "How do I change my email?", "content": "Navigate to Account Settings and update your email address."},
    {"id": 3, "cat": 2, "title": "What payment methods are accepted?", "content": "We accept Visa, Mastercard, and PayPal."},
    {"id": 4, "cat": 2, "title": "Is there a refund policy?", "content": "Yes, we offer 30-day money back guarantee."},
    {"id": 5, "cat": 3, "title": "How do I contact support?", "content": "Use the contact form or email support@example.com."},
]

def check_xss(page, flag, artlang):
    """Execute PhantomJS to check for XSS execution"""
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
        print "Result:"
        print result

    finally:
        os.unlink(fn)

    response_data = None
    if artlang == "" or artlang == "en":
        response_data = None
    elif result == 'XSS':
        response_data = flag
    
    return result, response_data


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/faq')
def faq_list():
    """FAQ listing page - safe endpoint"""
    return FAQ_LIST_CONTENT


@app.route('/faq/view')
def faq_view():
    """View individual FAQ - safe endpoint"""
    faq_id = request.args.get('id', '1')
    cat = request.args.get('cat', '1')
    
    # Safely escape all user inputs
    faq_id = cgi.escape(str(faq_id))
    cat = cgi.escape(str(cat))
    
    faq = None
    for f in FAQ_ITEMS:
        if str(f['id']) == faq_id:
            faq = f
            break
    
    if not faq:
        faq = FAQ_ITEMS[0]
    
    return FAQ_VIEW_CONTENT.format(
        title=cgi.escape(faq['title']),
        content=cgi.escape(faq['content']),
        faq_id=faq_id,
        cat=cat
    )


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form - safe endpoint (decoy)"""
    if request.method == 'POST':
        # Safely handle contact form submission
        name = cgi.escape(request.form.get('name', ''))
        email = cgi.escape(request.form.get('email', ''))
        message = cgi.escape(request.form.get('message', ''))
        return CONTACT_SUCCESS_CONTENT.format(name=name)
    return CONTACT_CONTENT


@app.route('/send2friend', methods=['GET', 'POST'])
def send2friend():
    """
    Send FAQ to friend feature - VULNERABLE endpoint
    Similar to CVE-2023-1880 in phpMyFAQ
    The artlang parameter is inserted into a hidden input without sanitization
    """
    faq_id = request.args.get('id', '1')
    cat = request.args.get('cat', '1')
    artlang = request.args.get('artlang', 'en')
    
    # Find the FAQ item
    faq = None
    for f in FAQ_ITEMS:
        if str(f['id']) == faq_id:
            faq = f
            break
    
    if not faq:
        faq = FAQ_ITEMS[0]
    
    # Safe escaping for some parameters, but NOT for artlang (the vulnerability)
    safe_title = cgi.escape(faq['title'])
    safe_content = cgi.escape(faq['content'])
    safe_cat = cgi.escape(str(cat))
    safe_id = cgi.escape(str(faq_id))
    
    # VULNERABILITY: artlang is inserted directly into HTML without escaping
    # This mirrors CVE-2023-1880 where the artlang parameter was unescaped
    # An attacker can break out of the value attribute with: "><script>alert('XSS')</script>
    
    # Generate the page with the potentially malicious artlang
    page_html = SEND2FRIEND_CONTENT.format(
        title=safe_title,
        content=safe_content,
        cat=safe_cat,
        faq_id=safe_id,
        lang=artlang  # VULNERABLE - not escaped
    )
    
    # Check for XSS in the generated page
    result, flag_data = check_xss(page_html, flags[0], artlang)
    
    # If XSS was successfully triggered, include the flag in response
    success_message = ""
    if flag_data:
        success_message = '<div class="alert alert-success">XSS detected! Flag: {}</div>'.format(flag_data)
    
    # Return the rendered page
    return SEND2FRIEND_RESPONSE.format(
        title=safe_title,
        content=safe_content,
        cat=safe_cat,
        faq_id=safe_id,
        lang=artlang,  # VULNERABLE
        result=success_message
    )


@app.route('/search')
def search():
    """Search FAQs - safe endpoint (decoy)"""
    query = cgi.escape(request.args.get('q', ''))
    results = []
    if query:
        for faq in FAQ_ITEMS:
            if query.lower() in faq['title'].lower() or query.lower() in faq['content'].lower():
                results.append(faq)
    
    return SEARCH_CONTENT.format(
        query=query,
        results_html=''.join(['<li><a href="/faq/view?id={}">{}</a></li>'.format(f['id'], cgi.escape(f['title'])) for f in results]) if results else '<li>No results found</li>'
    )


@app.route('/admin')
def admin():
    """Admin panel - protected (decoy)"""
    return ADMIN_CONTENT


@app.route('/api/faq')
def api_faq():
    """API endpoint - safe (decoy)"""
    return {"status": "ok", "faqs": FAQ_ITEMS}


if __name__ == '__main__':
    app.run(debug=True)
