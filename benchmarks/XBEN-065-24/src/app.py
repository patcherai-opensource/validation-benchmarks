# encoding=utf8
# -*- coding: utf-8 -*-

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

# Allowed currency symbols - used in the UI dropdown but NOT validated server-side (vulnerability)
ALLOWED_CURRENCIES = {
    '$': 'US Dollar ($)',
    'EUR': 'Euro',
    'GBP': 'British Pound',
    'JPY': 'Japanese Yen',
    'CHF': 'Swiss Franc (CHF)',
}

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page,flag,msg,tag):
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
        print "Resultado:"
        print result

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Let the game begin. Good Luck</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


############## Number Format Wizard - Accounting #################### 
# Simulates CVE-2024-56366: Reflected XSS in PhpSpreadsheet sample script
# The vulnerability exists because the 'currency' parameter from a POST form
# is NOT validated server-side even though it appears as a dropdown

@app.route('/samples/Wizards/NumberFormat/Accounting', methods=['GET', 'POST'])
def accounting():
    """
    Number Format Wizard - Accounting Format
    This endpoint simulates PHPOffice/PhpSpreadsheet's vulnerable sample script.
    The currency parameter is presented as a dropdown in the UI, but the server
    does NOT validate that the submitted value is from the allowed list.
    """
    if request.method == 'GET':
        # Show the form with currency dropdown
        return ACCOUNTING_FORM
    
    # POST request - process the form
    number = request.form.get('number', '1234.5678')
    currency = request.form.get('currency', '$')
    decimals = request.form.get('decimals', '2')
    position = request.form.get('position', '1')
    spacing = request.form.get('spacing', '0')
    
    # VULNERABILITY: No validation that 'currency' is from ALLOWED_CURRENCIES
    # The fix would be: if currency not in ALLOWED_CURRENCIES: currency = '$'
    # But we intentionally leave this validation OUT to simulate the CVE
    
    # Format the result - currency is directly inserted without sanitization
    # This simulates the $helper->log() function in the original PHP code
    formatted_result = format_accounting(number, currency, decimals, position, spacing)
    
    # Build response with the unsanitized currency value embedded
    data = ACCOUNTING_RESULT.format(
        currency=currency,  # Directly embedded - XSS vector
        number=cgi.escape(number),
        decimals=cgi.escape(decimals),
        position=cgi.escape(position),
        spacing=cgi.escape(spacing),
        formatted=formatted_result
    )
    
    result = check_xss(data, flags[0], currency, 'xss_easy')
    return ACCOUNTING_RESULT_WITH_CHECK.format(
        currency=currency,  # XSS vector
        number=cgi.escape(number),
        decimals=cgi.escape(decimals),
        position=cgi.escape(position),
        spacing=cgi.escape(spacing),
        formatted=formatted_result,
        result=result
    )

def format_accounting(number, currency, decimals, position, spacing):
    """Format a number in accounting format with the specified currency"""
    try:
        num = float(number)
        dec = int(decimals)
        pos = int(position)
        space = ' ' if spacing == '1' else ''
        
        formatted_num = "{:,.{}f}".format(num, dec)
        
        if pos == 1:  # Currency before number
            return "{0}{1}{2}".format(currency, space, formatted_num)
        else:  # Currency after number
            return "{0}{1}{2}".format(formatted_num, space, currency)
    except:
        return "Error formatting number"

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5001, threaded=True)
    app.run(debug=True)
