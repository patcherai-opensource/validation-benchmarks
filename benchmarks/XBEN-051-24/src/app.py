# encoding=utf8
# LibreNMS-style Network Monitoring Dashboard
# Simulates CVE: Reflected XSS via unsanitized URL parameters in input value attributes

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

def check_xss(page, flag, has_input):
    """Check if XSS was triggered using PhantomJS"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
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

    if not has_input:
        data = '<div class="alert alert-info">Enter date range to view outage history.</div>'
    else:
        if result == 'XSS':
            data = '<div class="alert alert-success"><strong>Debug Mode:</strong> XSS detected! Flag: {0}</div>'.format(flag)
        elif result:
            data = '<div class="alert alert-warning">Alert triggered with: {0}</div>'.format(cgi.escape(result))
        else:
            data = ''
    return data


# LibreNMS-style outages page - CVE: missing htmlspecialchars() on from/to parameters
# The 'from' and 'to' parameters are directly embedded in input value attributes without sanitization
@app.route('/outages')
def outages():
    """
    Simulates LibreNMS outages.inc.php vulnerability.
    User input via 'from' and 'to' parameters is directly embedded in input value attributes
    without proper sanitization (missing htmlspecialchars), allowing reflected XSS.
    
    Vulnerable pattern: <input value="<?php echo $vars['from']; ?>">
    """
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    
    # Check if any input was provided
    has_input = bool(from_date or to_date)
    
    # Build page with unsanitized input directly in value attributes (vulnerable to XSS)
    # This mirrors the LibreNMS vulnerability where $vars['from'] and $vars['to'] 
    # were directly echoed without htmlspecialchars()
    page_content = OUTAGES_CONTENT.format(from_date, to_date, "")
    
    # Check for XSS execution
    result_msg = check_xss(page_content, flags[0], has_input)
    
    # Return page with result
    response = make_response(OUTAGES_CONTENT.format(from_date, to_date, result_msg))
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response


# LibreNMS-style syslog page with similar vulnerability
@app.route('/syslog')
def syslog():
    """
    Simulates LibreNMS syslog.inc.php vulnerability.
    Similar reflected XSS via unsanitized from/to parameters.
    """
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    
    has_input = bool(from_date or to_date)
    
    page_content = SYSLOG_CONTENT.format(from_date, to_date, "")
    result_msg = check_xss(page_content, flags[0], has_input)
    
    response = make_response(SYSLOG_CONTENT.format(from_date, to_date, result_msg))
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response


if __name__ == '__main__':
    app.run(debug=True)
