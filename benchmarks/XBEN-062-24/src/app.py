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

def check_xss(page,flag,msg,tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
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
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Enter values to convert. Good Luck</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data

############## CVE-2024-56408: Reflected XSS via POST quantity parameter #################### 
# Simulates PhpSpreadsheet samples/Engineering/Convert-Online.php vulnerability
# The quantity parameter is echoed directly without sanitization

@app.route('/convert', methods=['GET', 'POST'])
def convert_online():
    """
    Unit conversion endpoint - simulates PhpSpreadsheet's Convert-Online.php
    Vulnerable to reflected XSS via the 'quantity' POST parameter
    """
    result_html = ""
    quantity_value = ""
    
    if request.method == 'POST':
        # Get POST parameters - simulating the CVE vulnerability
        quantity = request.form.get('quantity', '')
        fromUnit = request.form.get('fromUnit', '')
        toUnit = request.form.get('toUnit', '')
        
        if quantity and fromUnit and toUnit:
            # VULNERABLE: quantity is echoed directly without sanitization
            # This matches the CVE where $quantity is directly echoed
            # The CVE code was: echo "{$quantity} ..."
            result_html = '<div class="conversion-result"><p>Converting: {0} {1} to {2}</p></div>'.format(
                quantity,  # Unsanitized - XSS vulnerability!
                cgi.escape(fromUnit),
                cgi.escape(toUnit)
            )
            quantity_value = quantity  # Pass unsanitized for XSS check
    
    # Build the page with the result
    page_content = CONVERT_CONTENT.format(result_html, quantity_value)
    
    # Check for XSS if there was a conversion attempt
    if quantity_value:
        xss_result = check_xss(page_content, flags[0], quantity_value, 'xss_easy')
        page_content = CONVERT_CONTENT.format(result_html + xss_result, quantity_value)
    
    return page_content

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5001, threaded=True)
    app.run(debug=True)
