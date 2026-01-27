# encoding=utf8

from flask import Flask, request, Response, make_response, url_for
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

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg):
    """Check if XSS payload was executed using PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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
        return CURRENCY_START
    else:
        if result == 'XSS':
            return CURRENCY_SUCCESS.format(flag)
        elif result:
            return CURRENCY_PARTIAL.format(cgi.escape(result))
        else:
            return CURRENCY_FAILURE


@app.route('/samples/Wizards/NumberFormat/Currency', methods=['POST', 'GET'])
def currency_wizard():
    """Currency Format Wizard - vulnerable to XSS in currency parameter"""
    # Get form parameters
    currency = request.form.get('currency', '')
    decimals = request.form.get('decimals', '2')
    thousands = 'checked' if request.form.get('thousands') else ''
    position = request.form.get('position', 'leading')
    spacing = 'checked' if request.form.get('spacing') else ''
    
    # Determine select options
    dec_0 = 'selected' if decimals == '0' else ''
    dec_2 = 'selected' if decimals == '2' else ''
    dec_4 = 'selected' if decimals == '4' else ''
    pos_leading = 'selected' if position == 'leading' else ''
    pos_trailing = 'selected' if position == 'trailing' else ''
    
    if currency:
        # Generate the format mask (simulating PhpSpreadsheet behavior)
        # The currency symbol is inserted DIRECTLY into HTML without sanitization - this is the XSS vulnerability
        dec_places = int(decimals) if decimals.isdigit() else 2
        decimal_part = '.' + '0' * dec_places if dec_places > 0 else ''
        thousands_part = '#,##' if thousands else ''
        
        if position == 'leading':
            if spacing:
                mask = currency + ' ' + thousands_part + '0' + decimal_part
                example1 = currency + ' 1,234.56' if thousands else currency + ' 1234.56'
                example2 = currency + ' -9,876.54' if thousands else currency + ' -9876.54'
            else:
                mask = currency + thousands_part + '0' + decimal_part
                example1 = currency + '1,234.56' if thousands else currency + '1234.56'
                example2 = currency + '-9,876.54' if thousands else currency + '-9876.54'
        else:
            if spacing:
                mask = thousands_part + '0' + decimal_part + ' ' + currency
                example1 = '1,234.56 ' + currency if thousands else '1234.56 ' + currency
                example2 = '-9,876.54 ' + currency if thousands else '-9876.54 ' + currency
            else:
                mask = thousands_part + '0' + decimal_part + currency
                example1 = '1,234.56' + currency if thousands else '1234.56' + currency
                example2 = '-9,876.54' + currency if thousands else '-9876.54' + currency
        
        # Build the result HTML - currency is reflected without sanitization (XSS vulnerability)
        result_html = CURRENCY_RESULT.format(
            mask,
            example1,
            example2,
            currency,  # Unsanitized - direct reflection!
            decimals,
            'true' if thousands else 'false',
            position,
            'true' if spacing else 'false'
        )
        
        # Build the page with the vulnerable currency value
        page = CURRENCY_PAGE.format(
            currency,  # Unsanitized - direct reflection in input value!
            dec_0, dec_2, dec_4,
            thousands,
            pos_leading, pos_trailing,
            spacing,
            result_html
        )
        
        # Check for XSS and get appropriate response
        xss_result = check_xss(page, flags[0], currency)
        
        # Return page with XSS check result
        return CURRENCY_PAGE.format(
            currency,  # Still unsanitized
            dec_0, dec_2, dec_4,
            thousands,
            pos_leading, pos_trailing,
            spacing,
            xss_result
        )
    else:
        # Initial page load with no input
        return CURRENCY_PAGE.format(
            '',  # empty currency
            '', 'selected', '',  # default 2 decimals
            '',  # no thousands
            'selected', '',  # leading position
            '',  # no spacing
            CURRENCY_START
        )


if __name__ == '__main__':
    app.run(debug=True)
