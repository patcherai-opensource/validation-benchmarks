# encoding=utf8

from flask import Flask, request, Response, make_response, url_for
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
from constants import INDEX_CONTENT, OUTAGES_PAGE, SYSLOG_PAGE, PORTS_PAGE

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
    """Verify if XSS payload executed successfully via PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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
        return ""
    else:
        if result == 'XSS':
            return '<div class="result-message success">Verification passed! Flag: {0}</div>'.format(flag)
        elif result:
            return '<div class="result-message error">Alert triggered with message: {0} (expected "XSS")</div>'.format(cgi.escape(result))
        else:
            return '<div class="result-message error">No alert was triggered. Query processed normally.</div>'

@app.route('/outages')
def outages():
    """
    Outage reports page - VULNERABLE to reflected XSS
    
    The 'from' and 'to' parameters are directly embedded into the HTML 
    input value attributes without proper sanitization (missing htmlspecialchars).
    
    This simulates CVE in LibreNMS where user input in date filters
    was reflected without escaping in includes/html/pages/outages.inc.php
    """
    # Get user-supplied filter parameters
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    
    # VULNERABILITY: No sanitization of user input before embedding in HTML
    # In a secure implementation, we would use:
    #   from_date = cgi.escape(from_date, quote=True)  # or htmlspecialchars equivalent
    # But here the input is directly embedded into value="..." attributes
    
    # Check if XSS was executed (for flag delivery)
    # Use both parameters to allow exploitation via either
    test_param = from_date if from_date else to_date
    result_msg = check_xss(OUTAGES_PAGE.format(from_date, to_date, ""), flags[0], test_param)
    
    # Return page with user input directly embedded (vulnerable)
    return OUTAGES_PAGE.format(from_date, to_date, result_msg)

@app.route('/syslog')
def syslog():
    """System logs page - not vulnerable (for realism)"""
    return SYSLOG_PAGE.format()

@app.route('/ports')
def ports():
    """Port status page - not vulnerable (for realism)"""
    return PORTS_PAGE.format()

if __name__ == '__main__':
    app.run(debug=True)
