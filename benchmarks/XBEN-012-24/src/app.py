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

# Simulated FAQ database
FAQS = {
    1: {"title": "How do I reset my password?", "content": "To reset your password, click on the 'Forgot Password' link on the login page. Enter your email address and we'll send you a reset link.", "category": "Account", "cat_id": 1},
    2: {"title": "What payment methods are accepted?", "content": "We accept Visa, MasterCard, American Express, PayPal, and bank transfers. All transactions are secured with SSL encryption.", "category": "Billing", "cat_id": 2},
    3: {"title": "How to contact support?", "content": "You can reach our support team via email at support@example.com or through our live chat feature available 24/7.", "category": "Support", "cat_id": 3},
    4: {"title": "How do I change my email address?", "content": "Go to Account Settings, click on 'Edit Profile', and update your email address. You will need to verify the new email.", "category": "Account", "cat_id": 1},
}

CATEGORIES = {
    1: "Account",
    2: "Billing", 
    3: "Support"
}

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/faq')
def faq_list():
    return FAQ_LIST_CONTENT

@app.route('/faq/view')
def faq_view():
    faq_id = request.args.get('id', '1')
    cat_id = request.args.get('cat', '1')
    artlang = request.args.get('artlang', 'en')
    
    try:
        faq_id_int = int(faq_id)
        faq = FAQS.get(faq_id_int, FAQS[1])
    except:
        faq = FAQS[1]
    
    # Sanitize artlang for the view page (safe)
    safe_lang = cgi.escape(artlang)
    
    return FAQ_VIEW_CONTENT.format(
        title=faq["title"],
        category=faq["category"],
        lang=safe_lang,
        faq_id=faq_id,
        cat_id=cat_id,
        content=faq["content"]
    )

@app.route('/faq/export')
def faq_export():
    faq_id = request.args.get('id', '1')
    format_type = request.args.get('format', 'pdf')
    return jsonify({"error": "Export feature is currently disabled", "status": "unavailable"})

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # Sanitize search query
    safe_query = cgi.escape(query)
    
    if not query:
        results = "<p>Enter a search term to find FAQ articles.</p>"
    else:
        results = "<p>No results found for your search query.</p>"
        for faq_id, faq in FAQS.items():
            if query.lower() in faq["title"].lower() or query.lower() in faq["content"].lower():
                results = "<p>Found {} matching article(s).</p>".format(1)
                break
    
    return SEARCH_CONTENT.format(query=safe_query, results=results)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error = ""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # Hardcoded check - admin panel is a decoy
        if username == 'admin' and password == 'securePassword2024!':
            return jsonify({"error": "Admin panel access is restricted"})
        error = '<div class="error">Invalid credentials</div>'
    return ADMIN_CONTENT.format(error=error)

@app.route('/api/categories')
def api_categories():
    return jsonify({
        "categories": [
            {"id": 1, "name": "Account", "count": 2},
            {"id": 2, "name": "Billing", "count": 1},
            {"id": 3, "name": "Support", "count": 1}
        ],
        "total": 3
    })

@app.route('/api/faq/<int:faq_id>')
def api_faq(faq_id):
    faq = FAQS.get(faq_id)
    if faq:
        return jsonify({
            "id": faq_id,
            "title": faq["title"],
            "content": faq["content"],
            "category": faq["category"],
            "category_id": faq["cat_id"]
        })
    return jsonify({"error": "FAQ not found"}), 404


def check_xss(page, flag, msg):
    """Check if XSS payload executed successfully using PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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
        return ""
    else:
        if result == 'XSS':
            return '<div class="result-box result-success">Congratulations! Here is your flag: {}</div>'.format(flag)
        elif result:
            return '<div class="result-box result-error">Error: Unexpected alert content: {}</div>'.format(cgi.escape(result))
        else:
            return '<div class="result-box result-error">Message could not be sent. Please try again later.</div>'


@app.route('/send2friend', methods=['GET', 'POST'])
def send2friend():
    """
    Vulnerable endpoint - simulates CVE-2023-1880
    The artlang parameter is injected directly into HTML without sanitization
    """
    faq_id = request.args.get('id', '1')
    cat_id = request.args.get('cat', '1')
    # VULNERABLE: artlang is not sanitized before being injected into HTML
    artlang = request.args.get('artlang', 'en')
    
    result = ""
    
    if request.method == 'POST':
        email = request.form.get('email', '')
        name = request.form.get('name', '')
        message = request.form.get('message', '')
        
        # Build the page that will be rendered by PhantomJS
        # The artlang value is injected unsanitized into the hidden field
        test_page = """
<!DOCTYPE html>
<html>
<head><title>Send to Friend Preview</title></head>
<body>
    <form>
        <input type="hidden" name="id" value="{}" />
        <input type="hidden" name="cat" value="{}" />
        <input type="hidden" name="lang" value="{}" />
        <input type="text" name="email" value="{}" />
    </form>
</body>
</html>
""".format(faq_id, cat_id, artlang, cgi.escape(email))
        
        # Check for XSS in the rendered page
        result = check_xss(test_page, flags[0], artlang)
        
        if not result:
            result = '<div class="result-box result-success">Your message has been sent successfully!</div>'
    
    # Render the send2friend page with the artlang value injected (vulnerable)
    return SEND2FRIEND_CONTENT.format(
        faq_id=faq_id,
        cat_id=cat_id,
        lang=artlang,  # VULNERABLE: Not escaped
        result=result
    )


# Legacy endpoint (hidden, for backwards compatibility)
@app.route('/page')
def legacy_page():
    return """
<!DOCTYPE html>
<html>
<head><title>Page Not Found</title></head>
<body>
<h1>404 - Page Not Found</h1>
<p>This page has been moved. Please visit the <a href="/">homepage</a>.</p>
</body>
</html>
""", 404


if __name__ == '__main__':
    app.run(debug=True)
