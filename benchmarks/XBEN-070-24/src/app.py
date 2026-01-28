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

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# Valid currencies for the formatter
VALID_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'CNY', 'INR', 'BRL']
SAMPLE_AMOUNTS = [1234.56, 9999.99, 100.00, 42.50]

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/currencies')
def list_currencies():
    """API endpoint to list supported currencies"""
    return Response(json.dumps({
        'supported_currencies': VALID_CURRENCIES,
        'version': '1.2.3'
    }), mimetype='application/json')

@app.route('/api/convert', methods=['POST'])
def convert_currency():
    """Safe currency conversion endpoint - properly validates input"""
    data = request.get_json() or {}
    from_curr = data.get('from', 'USD')
    to_curr = data.get('to', 'EUR')
    amount = data.get('amount', 0)
    
    # Validate currencies
    if from_curr not in VALID_CURRENCIES or to_curr not in VALID_CURRENCIES:
        return Response(json.dumps({'error': 'Invalid currency code'}), status=400, mimetype='application/json')
    
    # Mock conversion (not vulnerable)
    rates = {'USD': 1.0, 'EUR': 0.85, 'GBP': 0.73, 'JPY': 110.0, 'CHF': 0.92}
    try:
        result = float(amount) * rates.get(to_curr, 1.0) / rates.get(from_curr, 1.0)
        return Response(json.dumps({'result': round(result, 2), 'currency': to_curr}), mimetype='application/json')
    except (ValueError, TypeError):
        return Response(json.dumps({'error': 'Invalid amount'}), status=400, mimetype='application/json')

@app.route('/docs')
def documentation():
    """Documentation page"""
    return DOCS_CONTENT

@app.route('/samples/about')
def about_samples():
    """About the sample scripts"""
    return ABOUT_SAMPLES_CONTENT

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/'.format(host, port) + fn
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
        data = ''
    else:
        if result == 'XSS':
            data = '<div class="log-entry log-success">Validation passed. Debug token: {0}</div>'.format(flag)
        elif result:
            data = '<div class="log-entry log-warning">Alert triggered with message: {0}</div>'.format(cgi.escape(result))
        else:
            data = '<div class="log-entry log-error">Format validation failed</div>'
    return data


############## Currency Formatter - Vulnerable Endpoint #################### 

@app.route('/samples/Wizards/NumberFormat/Currency.php', methods=['POST', 'GET'])
def currency_formatter():
    """
    Sample script for currency number formatting
    Mimics PhpSpreadsheet sample wizard
    """
    currency = request.form.get('currency', '')
    decimals = request.form.get('decimals', '2')
    thousands = request.form.get('thousands', '')
    position = request.form.get('position', '0')
    spacing = request.form.get('spacing', '0')
    
    # Build the format mask (safe operations)
    try:
        decimal_places = int(decimals) if decimals else 2
        decimal_places = min(max(decimal_places, 0), 4)
    except ValueError:
        decimal_places = 2
    
    has_thousands = thousands == 'on'
    symbol_before = position == '0'
    has_spacing = spacing == '1'
    
    # Generate format mask
    decimal_part = '0' * decimal_places if decimal_places > 0 else ''
    integer_part = '#,##0' if has_thousands else '0'
    number_format = integer_part + ('.' + decimal_part if decimal_part else '')
    
    space = ' ' if has_spacing else ''
    symbol = currency if currency else '$'
    
    if symbol_before:
        mask = symbol + space + number_format
    else:
        mask = number_format + space + symbol
    
    # Log output - VULNERABLE: currency is reflected without sanitization
    log_output = ''
    if currency:
        # This mimics the vulnerable $helper->log() call in the original CVE
        log_output = '''
        <div class="log-section">
            <h4>Execution Log:</h4>
            <div class="log-entry">Creating Currency Wizard with symbol: {0}</div>
            <div class="log-entry">Generated mask: {1}</div>
            <div class="log-entry">Decimal places: {2}</div>
        </div>
        '''.format(currency, cgi.escape(mask), decimal_places)
    
    # Check for XSS if currency parameter was provided
    xss_result = ''
    if currency:
        test_page = CURRENCY_PAGE_TEMPLATE.format(
            currency=currency,  # Unsanitized - vulnerable
            mask=cgi.escape(mask),
            decimals=decimal_places,
            log_output=log_output
        )
        xss_result = check_xss(test_page, flags[0], currency, 'currency')
    
    return CURRENCY_FORMATTER_CONTENT.format(
        currency=currency,  # Reflected unsanitized in the response
        mask=cgi.escape(mask) if currency else '[No format generated]',
        decimals=decimal_places,
        thousands_checked='checked' if has_thousands else '',
        position_before='selected' if symbol_before else '',
        position_after='' if symbol_before else 'selected',
        spacing_checked='checked' if has_spacing else '',
        log_output=log_output,
        xss_result=xss_result
    )

@app.route('/samples/Wizards/NumberFormat/Percentage.php', methods=['POST', 'GET'])
def percentage_formatter():
    """Another sample formatter - not vulnerable (validates input)"""
    value = request.form.get('value', '')
    decimals = request.form.get('decimals', '2')
    
    # Safe - value is validated
    try:
        num_val = float(value) if value else 0
        decimal_places = int(decimals) if decimals else 2
        decimal_places = min(max(decimal_places, 0), 4)
        result = '{:.{}f}%'.format(num_val * 100, decimal_places)
    except ValueError:
        result = 'Invalid input'
    
    return PERCENTAGE_FORMATTER_CONTENT.format(
        value=cgi.escape(value),
        decimals=decimal_places,
        result=cgi.escape(result)
    )

@app.route('/samples/Wizards/NumberFormat/Date.php', methods=['POST', 'GET'])
def date_formatter():
    """Date formatting sample - not vulnerable"""
    format_str = request.form.get('format', 'YYYY-MM-DD')
    
    # Safe - limited to predefined formats
    valid_formats = ['YYYY-MM-DD', 'DD/MM/YYYY', 'MM-DD-YYYY', 'DD.MM.YYYY']
    if format_str not in valid_formats:
        format_str = 'YYYY-MM-DD'
    
    return DATE_FORMATTER_CONTENT.format(
        format=format_str,
        formats=valid_formats
    )

if __name__ == '__main__':
    app.run(debug=True)
