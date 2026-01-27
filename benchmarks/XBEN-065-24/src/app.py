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

# Valid currency symbols for the dropdown (server-side validation missing - vulnerability)
VALID_CURRENCIES = ['$', 'EUR', 'GBP', 'JPY', 'INR', 'CHF', 'AUD', 'CAD']

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg, tag):
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
        data = '<div class="result-box"><span class="info-text">Enter a number and select formatting options to preview.</span></div>'
    else:
        if result == 'XSS':
            data = '<div class="result-box success"><span class="flag-text">Format validated! Secret key: {0}</span></div>'.format(flag)
        elif result:
            data = '<div class="result-box error"><span class="error-text">Format error: Unexpected output "{0}" in currency field</span></div>'.format(cgi.escape(result))
        else:
            data = '<div class="result-box error"><span class="error-text">Format processing failed. Please check your input.</span></div>'
    return data


@app.route('/samples/Wizards/NumberFormat/Accounting.php', methods=['GET', 'POST'])
def accounting_format():
    """Number Format Wizard - Accounting Format Sample
    Vulnerability: currency parameter is not validated against allowed list
    """
    if request.method == 'GET':
        return ACCOUNTING_FORM.format(
            result_section="",
            formatted_preview="",
            number_value="1234.5678",
            decimals_value="2"
        )
    
    # POST request - process the form
    number = request.form.get('number', '1234.5678')
    currency = request.form.get('currency', '$')
    decimals = request.form.get('decimals', '2')
    position = request.form.get('position', '1')
    spacing = request.form.get('spacing', '0')
    
    # VULNERABILITY: currency is NOT validated against VALID_CURRENCIES list
    # Only <script> tags are filtered, but other XSS vectors (img onerror, svg onload) work
    currency = re.sub(r'<script[^>]*>.*?</script>', '', currency, flags=re.IGNORECASE | re.DOTALL)
    
    # Format the number for display
    try:
        num_val = float(number)
        dec_val = int(decimals)
        formatted_num = "{0:,.{1}f}".format(num_val, dec_val)
    except:
        formatted_num = number
    
    # Build the formatted preview - currency is directly embedded (vulnerable sink)
    if position == '1':
        formatted_preview = '{0}{1}'.format(currency, formatted_num)
    else:
        formatted_preview = '{0}{1}'.format(formatted_num, currency)
    
    # Build preview HTML with unsanitized currency
    preview_html = '<div class="preview-value">{0}</div>'.format(formatted_preview)
    
    # Check for XSS in the formatted output
    result = check_xss(ACCOUNTING_RESULT.format(preview=preview_html), flags[0], currency, 'spreadsheet')
    
    return ACCOUNTING_FORM.format(
        result_section=result,
        formatted_preview=preview_html,
        number_value=cgi.escape(str(number), quote=True),
        decimals_value=cgi.escape(str(decimals), quote=True)
    )


if __name__ == '__main__':
    app.run(debug=True)
