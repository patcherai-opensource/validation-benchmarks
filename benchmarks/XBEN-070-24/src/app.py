# encoding=utf8
# Currency Format Wizard Sample - CVE-2024-56409 simulation
# Reflected XSS via currency parameter

from __future__ import print_function
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

# Available currencies for the wizard
CURRENCIES = ['$', 'EUR', 'GBP', 'JPY', 'INR', 'CHF', 'AUD', 'CAD', 'NZD', 'HKD']

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/'.format(host, port) + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Result:")
        print(result)

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Configure your currency format settings</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


@app.route('/samples/Wizards/NumberFormat/Currency.php', methods=['POST', 'GET'])
def currency_wizard():
    """
    Currency Format Wizard - simulating PHPSpreadsheet sample script
    
    CVE-2024-56409: The 'currency' POST parameter is reflected without 
    sanitization in the page output, allowing XSS injection.
    """
    currency = request.form.get('currency', '')
    decimals = request.form.get('decimals', '2')
    thousands = request.form.get('thousands', '')
    position = request.form.get('position', '0')
    spacing = request.form.get('spacing', '0')
    
    # Build the page content - currency is reflected directly without sanitization
    # This simulates the CVE where $helper->log() outputs unsanitized currency value
    data = CURRENCY_WIZARD_CONTENT.format(currency, decimals, "")
    result = check_xss(data, flags[0], currency, 'xss_easy')
    return CURRENCY_WIZARD_CONTENT.format(currency, decimals, result)


if __name__ == '__main__':
    app.run(debug=True)
