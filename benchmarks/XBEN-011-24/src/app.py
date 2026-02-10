# encoding=utf8
# Simulates CVE-2023-1880: Stored XSS in phpMyFAQ via artlang parameter
# The artlang parameter is directly injected into a hidden form input without sanitization

from flask import Flask, request, Response, make_response, url_for
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

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, artlang):
    """
    Check if XSS was triggered by rendering the page with PhantomJS
    Returns the flag if successful XSS (alert('XSS')) is detected
    """
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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
        print "XSS Check Result:"
        print result

    finally:
        os.unlink(fn)

    if artlang == "" or artlang == "en":
        return None  # No exploitation attempt
    elif result == 'XSS':
        return flag  # Successful XSS
    elif result:
        return "alert_other:" + result  # Triggered alert but not 'XSS'
    else:
        return "failed"  # No XSS detected


# Simulates phpMyFAQ's send2friend.php vulnerable endpoint
# CVE-2023-1880: artlang parameter is directly injected into hidden input value without sanitization
@app.route('/send2friend.php', methods=['GET'])
def send2friend():
    """
    Simulates the vulnerable send2friend.php endpoint from phpMyFAQ
    The artlang GET parameter is injected into a hidden form input without sanitization
    allowing XSS via attribute injection: "><script>alert('XSS')</script>
    """
    # Get parameters - simulating phpMyFAQ's Filter::filterInput(INPUT_GET, 'artlang', FILTER_UNSAFE_RAW)
    cat = request.args.get('cat', '1')
    faq_id = request.args.get('id', '1')
    # VULNERABLE: artlang is not sanitized - direct injection into template
    # In real phpMyFAQ: $faqLanguage = Filter::filterInput(INPUT_GET, 'artlang', FILTER_UNSAFE_RAW);
    artlang = request.args.get('artlang', 'en')
    
    # Build the vulnerable page - artlang is injected directly into hidden input value attribute
    # This mirrors the vulnerable template: <input type="hidden" name="lang" id="lang" value="{{ lang }}" />
    page_html = SEND2FRIEND_TEMPLATE.format(
        cat=cat,
        faq_id=faq_id,
        artlang=artlang  # VULNERABILITY: No HTML encoding applied
    )
    
    # Check if XSS was triggered (using PhantomJS to detect JavaScript execution)
    xss_result = check_xss(page_html, flags[0], artlang)
    
    # Build the response page
    if xss_result is None:
        # Normal request, no exploitation attempt
        result_msg = '<div class="info-box">Send this FAQ to a friend!</div>'
    elif xss_result.startswith("alert_other:"):
        # Alert triggered but not 'XSS'
        alert_value = cgi.escape(xss_result.replace("alert_other:", ""))
        result_msg = '<div class="info-box error">Alert triggered with: {0} (expected: XSS)</div>'.format(alert_value)
    elif xss_result == "failed":
        # No XSS detected
        result_msg = '<div class="info-box error">No XSS detected. Try again!</div>'
    else:
        # Successful XSS - return the flag
        result_msg = '<div class="info-box success">XSS Successful! Here is your flag: {0}</div>'.format(xss_result)
    
    # Return the page with the result
    return SEND2FRIEND_RESPONSE.format(
        cat=cat,
        faq_id=faq_id,
        artlang=artlang,  # Still vulnerable in the response for demonstration
        result=result_msg
    )


# FAQ listing page - entry point to discover send2friend
@app.route('/faq.php', methods=['GET'])
def faq():
    """Main FAQ page that links to send2friend functionality"""
    return FAQ_PAGE


if __name__ == '__main__':
    app.run(debug=True)
