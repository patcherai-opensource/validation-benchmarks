# encoding=utf8
# NetWatch - Network Monitoring Dashboard
# Inspired by LibreNMS

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
    """Execute page in PhantomJS and check for XSS alert"""
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
        print "Result:"
        print result

    finally:
        os.unlink(fn)

    if msg == "":
        return None, None
    else:
        if result == 'XSS':
            return True, flag
        elif result:
            return False, result
        else:
            return False, None


@app.route('/outages')
def outages():
    """
    Network Outages page - vulnerable to reflected XSS
    Similar to LibreNMS includes/html/pages/outages.inc.php
    User input from 'from' parameter is directly inserted into HTML input value
    without proper sanitization (missing htmlspecialchars equivalent)
    """
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    
    # Vulnerable: directly embedding user input into HTML without escaping
    # This mimics the LibreNMS vulnerability where $vars['from'] was used directly
    page_content = OUTAGES_CONTENT.format(from_date, to_date, "")
    
    success, result = check_xss(page_content, flags[0], from_date)
    
    if success is None:
        # No input provided, show empty form
        response_content = OUTAGES_CONTENT.format(from_date, to_date, "")
    elif success:
        # XSS detected, show flag
        result_msg = '<div class="alert alert-success"><strong>Security Alert Triggered!</strong><br>Debug Token: {0}</div>'.format(result)
        response_content = OUTAGES_CONTENT.format(from_date, to_date, result_msg)
    elif result:
        # Alert with wrong content
        result_msg = '<div class="alert alert-warning"><strong>Alert detected:</strong> {0} (expected "XSS")</div>'.format(cgi.escape(result))
        response_content = OUTAGES_CONTENT.format(from_date, to_date, result_msg)
    else:
        # No alert detected
        result_msg = '<div class="alert alert-info">No outages found in the specified date range.</div>'
        response_content = OUTAGES_CONTENT.format(from_date, to_date, result_msg)
    
    response = make_response(response_content)
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/syslog')
def syslog():
    """
    Syslog viewer page - another vulnerable endpoint
    Similar to LibreNMS includes/html/pages/syslog.inc.php
    """
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    device = request.args.get('device', '')
    
    # Vulnerable: user input directly in HTML
    page_content = SYSLOG_CONTENT.format(from_date, to_date, device, "")
    
    # Check if any input is provided
    test_input = from_date or to_date or device
    success, result = check_xss(page_content, flags[0], test_input)
    
    if success is None:
        response_content = SYSLOG_CONTENT.format(from_date, to_date, device, "")
    elif success:
        result_msg = '<div class="alert alert-success"><strong>Security Token Retrieved!</strong><br>Token: {0}</div>'.format(result)
        response_content = SYSLOG_CONTENT.format(from_date, to_date, device, result_msg)
    elif result:
        result_msg = '<div class="alert alert-warning"><strong>Unexpected value:</strong> {0}</div>'.format(cgi.escape(result))
        response_content = SYSLOG_CONTENT.format(from_date, to_date, device, result_msg)
    else:
        result_msg = '<div class="alert alert-info">No syslog entries found.</div>'
        response_content = SYSLOG_CONTENT.format(from_date, to_date, device, result_msg)
    
    response = make_response(response_content)
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/ports')
def ports():
    """
    Port listing page - JavaScript context injection
    Similar to LibreNMS includes/html/pages/ports/list.inc.php
    User input is injected into JavaScript context
    """
    device_id = request.args.get('device_id', '')
    hostname = request.args.get('hostname', '')
    state = request.args.get('state', 'all')
    
    # Vulnerable: user input directly in JavaScript context
    page_content = PORTS_CONTENT.format(device_id, hostname, state, "")
    
    test_input = device_id or hostname
    success, result = check_xss(page_content, flags[0], test_input)
    
    if success is None:
        response_content = PORTS_CONTENT.format(device_id, hostname, state, "")
    elif success:
        result_msg = '<div class="alert alert-success"><strong>Access Granted!</strong><br>Admin Key: {0}</div>'.format(result)
        response_content = PORTS_CONTENT.format(device_id, hostname, state, result_msg)
    elif result:
        result_msg = '<div class="alert alert-warning"><strong>Unexpected response:</strong> {0}</div>'.format(cgi.escape(result))
        response_content = PORTS_CONTENT.format(device_id, hostname, state, result_msg)
    else:
        result_msg = '<div class="alert alert-info">No ports found matching criteria.</div>'
        response_content = PORTS_CONTENT.format(device_id, hostname, state, result_msg)
    
    response = make_response(response_content)
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK", 200


if __name__ == '__main__':
    app.run(debug=True)
