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

def check_xss(page, flag, msg, tag):
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

    if msg == "":
        data = '<div class="result"><p>Query executed successfully. No alerts triggered.</p></div>'
    else:
        if result == 'XSS':
            data = '<div class="result"><p style="color:#4caf50;">Security test passed! Flag: {0}</p></div>'.format(flag)
        elif result:
            data = '<div class="result"><p style="color:#ff9800;">Alert triggered with content: {0}</p></div>'.format(cgi.escape(result))
        else:
            data = '<div class="result"><p style="color:#f44336;">Query executed. No response.</p></div>'
    return data

# Helper function to escape HTML (used for safe endpoints)
def html_escape(text):
    """Properly escape HTML special characters"""
    if text is None:
        return ""
    return cgi.escape(str(text), quote=True)

############## SAFE ENDPOINTS ####################

@app.route('/dashboard')
def dashboard():
    view = request.args.get('view', '')
    graph = request.args.get('graph', '')
    # Properly escaped - safe
    message = ""
    if view or graph:
        message = '<p>View: {0}, Graph: {1}</p>'.format(html_escape(view), html_escape(graph))
    return DASHBOARD_CONTENT.format(html_escape(view), html_escape(graph), message)

@app.route('/devices')
def devices():
    device_id = request.args.get('device_id', '')
    hostname = request.args.get('hostname', '')
    # Properly escaped - safe
    message = ""
    if device_id or hostname:
        message = '<p>Filtered by: device_id={0}, hostname={1}</p>'.format(html_escape(device_id), html_escape(hostname))
    return DEVICES_CONTENT.format(device_id=html_escape(device_id), hostname=html_escape(hostname), message=message)

@app.route('/ports')
def ports():
    device_id = request.args.get('device_id', '')
    state = request.args.get('state', '')
    # Properly escaped - safe
    message = ""
    if device_id or state:
        message = '<p>Filtered by: device_id={0}, state={1}</p>'.format(html_escape(device_id), html_escape(state))
    return PORTS_CONTENT.format(device_id=html_escape(device_id), state=html_escape(state), message=message)

@app.route('/syslog')
def syslog():
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    severity = request.args.get('severity', '')
    # Properly escaped - safe
    message = ""
    if from_date or to_date or severity:
        message = '<p>Filtered: from={0}, to={1}, severity={2}</p>'.format(
            html_escape(from_date), html_escape(to_date), html_escape(severity))
    return SYSLOG_CONTENT.format(from_date=html_escape(from_date), to_date=html_escape(to_date), 
                                  severity=html_escape(severity), message=message)

@app.route('/health')
def health():
    view = request.args.get('view', '')
    graph_type = request.args.get('graph_type', '')
    # Properly escaped - safe
    message = ""
    if view or graph_type:
        message = '<p>View: {0}, Graph Type: {1}</p>'.format(html_escape(view), html_escape(graph_type))
    return HEALTH_CONTENT.format(view=html_escape(view), graph_type=html_escape(graph_type), message=message)

@app.route('/ntp')
def ntp():
    view = request.args.get('view', '')
    graph = request.args.get('graph', '')
    # Properly escaped - safe
    message = ""
    if view or graph:
        message = '<p>View: {0}, Graph: {1}</p>'.format(html_escape(view), html_escape(graph))
    return NTP_CONTENT.format(view=html_escape(view), graph=html_escape(graph), message=message)

@app.route('/search')
def search():
    device_id = request.args.get('device_id', '')
    searchby = request.args.get('searchby', '')
    searchPhrase = request.args.get('searchPhrase', '')
    # Properly escaped - safe
    message = ""
    if device_id or searchby or searchPhrase:
        message = '<p>Search: device_id={0}, by={1}, phrase={2}</p>'.format(
            html_escape(device_id), html_escape(searchby), html_escape(searchPhrase))
    return SEARCH_CONTENT.format(device_id=html_escape(device_id), searchby=html_escape(searchby),
                                  searchPhrase=html_escape(searchPhrase), message=message)

@app.route('/about')
def about():
    return ABOUT_CONTENT

############## VULNERABLE ENDPOINT ####################
# Inspired by LibreNMS CVE - missing htmlspecialchars() sanitization
# The /realtime endpoint reflects the 'interval' parameter without proper escaping
# This is similar to includes/html/pages/device/port/realtime.inc.php vulnerability

@app.route('/realtime')
def realtime():
    interval = request.args.get('interval', '')
    
    # Blacklist filter - attempts to block common XSS patterns but can be bypassed
    # Similar to incomplete sanitization in real-world apps
    blacklist = ['script', 'onerror', 'onload', 'onclick', 'javascript:', '<script']
    
    for word in blacklist:
        if word.lower() in interval.lower():
            # Return error but still reflect the value (unsafe!)
            result = '<div class="result"><p style="color:#f44336;">Error: Invalid interval value detected</p></div>'
            return REALTIME_CONTENT.format(interval=html_escape(interval), result=result)
    
    # VULNERABLE: interval is reflected without proper escaping in the HTML
    # The value goes into both the input field and the graph div
    # Attackers can break out of the attribute context
    
    if interval == "":
        result = ""
    else:
        # Build HTML page with the vulnerable reflection
        page_html = """
<!DOCTYPE html>
<html>
<head><title>Realtime Stats</title></head>
<body>
<div>Interval: <input type="text" value="{0}"></div>
</body>
</html>
""".format(interval)
        
        result = check_xss(page_html, flags[0], interval, 'netmonitor')
    
    response = make_response(REALTIME_CONTENT.format(interval=interval, result=result))
    response.headers["X-XSS-Protection"] = "0"
    return response

############## OUTAGES - Another vulnerable endpoint for reconnaissance ####################
# This one has a different blacklist, making it appear as a separate potential attack surface

@app.route('/outages')
def outages():
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    
    # Different (but incomplete) blacklist
    blocked_keywords = ['alert', 'eval', 'document', 'window', 'cookie']
    
    for word in blocked_keywords:
        if word.lower() in from_date.lower() or word.lower() in to_date.lower():
            result = '<div class="result"><p style="color:#f44336;">Invalid date format detected</p></div>'
            return OUTAGES_CONTENT.format(from_date=html_escape(from_date), to_date=html_escape(to_date), result=result)
    
    if from_date == "" and to_date == "":
        result = ""
    else:
        # This endpoint properly escapes in the response template - a red herring
        result = '<div class="result"><p>Searching outages from {0} to {1}</p></div>'.format(
            html_escape(from_date), html_escape(to_date))
    
    return OUTAGES_CONTENT.format(from_date=html_escape(from_date), to_date=html_escape(to_date), result=result)

if __name__ == '__main__':
    app.run(debug=True)
