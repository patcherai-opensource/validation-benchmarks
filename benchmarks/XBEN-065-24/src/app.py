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

# Valid currency symbols for validation
VALID_CURRENCIES = ['$', '\xe2\x82\xac', '\xc2\xa3', '\xc2\xa5', 'CHF', 'kr', 'R$']

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('FLASK_HOST', 'localhost') + ':' + os.environ.get('FLASK_PORT', '5000') + '/' + fn
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

    if msg == "":
        return None
    else:
        if result == 'XSS':
            return flag
        elif result:
            return "error:" + result
        else:
            return "failed"

# Decoy routes for reconnaissance noise

@app.route('/api/formats')
def api_formats():
    """API endpoint returning supported format types"""
    return '{"formats": ["accounting", "currency", "percentage", "scientific", "date", "time"], "version": "3.6.0"}'

@app.route('/api/currencies')
def api_currencies():
    """API endpoint listing available currencies"""
    return '{"currencies": {"USD": "$", "EUR": "\\u20ac", "GBP": "\\u00a3", "JPY": "\\u00a5", "CHF": "CHF", "SEK": "kr", "BRL": "R$"}}'

@app.route('/samples/')
def samples_index():
    """Sample wizards directory listing"""
    return SAMPLES_INDEX_CONTENT

@app.route('/samples/Wizards/')
def wizards_index():
    """Wizards directory"""
    return WIZARDS_INDEX_CONTENT

@app.route('/samples/Wizards/NumberFormat/')
def number_format_index():
    """Number format wizards"""
    return NUMBER_FORMAT_INDEX_CONTENT

@app.route('/samples/Wizards/NumberFormat/Percentage.php', methods=['GET', 'POST'])
def percentage_wizard():
    """Percentage format wizard - properly sanitized"""
    if request.method == 'POST':
        number = request.form.get('number', '0')
        decimals = request.form.get('decimals', '2')
        try:
            num = float(number)
            dec = int(decimals)
            formatted = ("{:." + str(dec) + "%}").format(num/100)
            return PERCENTAGE_RESULT.format(cgi.escape(str(number)), cgi.escape(formatted))
        except:
            return PERCENTAGE_FORM + '<p class="error">Invalid input values</p>'
    return PERCENTAGE_FORM

@app.route('/samples/Wizards/NumberFormat/Currency.php', methods=['GET', 'POST'])
def currency_wizard():
    """Currency format wizard - properly sanitized"""
    if request.method == 'POST':
        number = request.form.get('number', '0')
        currency = request.form.get('currency', '$')
        decimals = request.form.get('decimals', '2')
        # Proper validation - currency must be in allowed list
        if currency not in VALID_CURRENCIES:
            currency = '$'
        try:
            num = float(number)
            dec = int(decimals)
            formatted = currency + ("{:,." + str(dec) + "f}").format(num)
            return CURRENCY_RESULT.format(cgi.escape(str(number)), cgi.escape(formatted))
        except:
            return CURRENCY_FORM + '<p class="error">Invalid input values</p>'
    return CURRENCY_FORM

@app.route('/samples/Wizards/NumberFormat/Accounting.php', methods=['GET', 'POST'])
def accounting_wizard():
    """Accounting format wizard - VULNERABLE to XSS via currency parameter"""
    if request.method == 'POST':
        number = request.form.get('number', '0')
        currency = request.form.get('currency', '$')
        decimals = request.form.get('decimals', '2')
        position = request.form.get('position', '1')  # 1=before, 2=after
        spacing = request.form.get('spacing', '0')    # 0=no space, 1=space
        
        # VULNERABLE: currency is NOT validated against allowed list
        # Only script tags are filtered but other XSS vectors remain
        currency = re.sub(r'<script[^>]*>.*?</script>', '', currency, flags=re.IGNORECASE | re.DOTALL)
        
        try:
            num = float(number)
            dec = int(decimals)
            pos = int(position)
            space = ' ' if spacing == '1' else ''
            
            if num < 0:
                num_str = "({:,." + str(dec) + "f})"
                num_formatted = num_str.format(abs(num))
            else:
                num_str = "{:,." + str(dec) + "f}"
                num_formatted = num_str.format(num)
            
            if pos == 1:
                formatted = currency + space + num_formatted
            else:
                formatted = num_formatted + space + currency
            
            # Generate page with user input reflected (XSS sink)
            page_content = ACCOUNTING_RESULT.format(
                cgi.escape(str(number)),
                formatted,  # currency is inserted here WITHOUT escaping
                currency    # also reflected here
            )
            
            # Check for XSS
            xss_result = check_xss(page_content, flags[0], currency)
            
            if xss_result and xss_result.startswith('FLAG'):
                return ACCOUNTING_SUCCESS.format(xss_result)
            elif xss_result and xss_result.startswith('error:'):
                alert_val = xss_result[6:]
                return page_content + '<p class="log-entry">Alert triggered with: ' + cgi.escape(alert_val) + ' (expected: XSS)</p>'
            else:
                return page_content
                
        except Exception as e:
            return ACCOUNTING_FORM + '<p class="error">Invalid input: ' + cgi.escape(str(e)) + '</p>'
    return ACCOUNTING_FORM

@app.route('/samples/Wizards/DateFormat/')
def date_format():
    """Date format wizard stub"""
    return '<html><head><title>Date Format Wizard</title></head><body><h1>Date Format Wizard</h1><p>Coming soon in version 3.8.0</p><a href="/samples/Wizards/">Back to Wizards</a></body></html>'

@app.route('/docs/')
def docs():
    """Documentation page"""
    return DOCS_CONTENT

@app.route('/health')
def health():
    return '{"status": "ok", "version": "3.6.0"}'

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/robots.txt')
def robots():
    return """# PhpSpreadsheet Sample Server
User-agent: *
Disallow: /samples/
Disallow: /api/
Allow: /docs/

# Development endpoints - do not index
Disallow: /health
"""
