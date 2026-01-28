# encoding=utf8
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for, redirect
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

# LibreNMS-style Network Monitoring System
APP_NAME = "NetMonitor"
VERSION = "2.3.7"

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/login')
def login():
    error = request.args.get('error', '')
    # Properly escaped - not vulnerable
    error_safe = cgi.escape(error) if error else ''
    return LOGIN_PAGE.format(error=error_safe)

@app.route('/dashboard')
def dashboard():
    return DASHBOARD_CONTENT

@app.route('/devices')
def devices():
    return DEVICES_PAGE

@app.route('/api/devices')
def api_devices():
    """API endpoint - returns JSON, properly escaped"""
    device_id = request.args.get('device_id', '1')
    import json
    return Response(json.dumps({
        'status': 'ok',
        'device_id': device_id,
        'data': {'hostname': 'router-01', 'status': 'up'}
    }), mimetype='application/json')

@app.route('/ports')
def ports():
    """Ports listing - similar to LibreNMS ports page"""
    device_id = request.args.get('device_id', '')
    hostname = request.args.get('hostname', '')
    state = request.args.get('state', 'up')
    
    # Properly sanitized - not vulnerable
    device_id_safe = cgi.escape(device_id)
    hostname_safe = cgi.escape(hostname)
    state_safe = cgi.escape(state)
    
    return PORTS_PAGE.format(
        device_id=device_id_safe,
        hostname=hostname_safe,
        state=state_safe
    )

@app.route('/health')
def health():
    """Health monitoring page - similar to LibreNMS health pages"""
    view = request.args.get('view', 'overview')
    graph_type = request.args.get('graph_type', 'line')
    unit = request.args.get('unit', 'percent')
    
    # These are sanitized properly
    view_safe = cgi.escape(view)
    graph_type_safe = cgi.escape(graph_type)
    unit_safe = cgi.escape(unit)
    
    return HEALTH_PAGE.format(
        view=view_safe,
        graph_type=graph_type_safe,
        unit=unit_safe
    )

@app.route('/syslog')
def syslog():
    """Syslog page - similar to LibreNMS syslog.inc.php"""
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    device = request.args.get('device', '')
    
    # Properly escaped
    from_safe = cgi.escape(from_date)
    to_safe = cgi.escape(to_date)
    device_safe = cgi.escape(device)
    
    return SYSLOG_PAGE.format(
        from_date=from_safe,
        to_date=to_safe,
        device=device_safe
    )

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('FLASK_HOST', 'localhost') + ':' + os.environ.get('FLASK_PORT', '5000') + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Resultado:")
        print(result)

    finally:
        os.unlink(fn)

    if msg == "":
        return ""
    else:
        if result == 'XSS':
            return '<div class="alert alert-success">Verified! Token: {0}</div>'.format(flag)
        elif result:
            return '<div class="alert alert-warning">Validation returned: {0}</div>'.format(cgi.escape(result))
        else:
            return '<div class="alert alert-danger">Validation failed</div>'


@app.route('/outages')
def outages():
    """
    VULNERABLE ENDPOINT - Similar to LibreNMS outages.inc.php
    The 'from' and 'to' parameters are directly embedded into HTML input value attributes
    without proper sanitization (missing htmlspecialchars equivalent)
    """
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    
    # VULNERABLE: No sanitization before embedding in HTML attribute context
    # This mirrors CVE where $vars['from'] was echoed directly into value=""
    
    # Build the page with user input directly in HTML attributes
    page_content = OUTAGES_PAGE_TEMPLATE.format(
        from_date=from_date,  # VULNERABLE - unsanitized
        to_date=to_date       # VULNERABLE - unsanitized
    )
    
    # Check if XSS was triggered
    combined_input = from_date + to_date
    result = check_xss(page_content, flags[0], combined_input, 'monitoring')
    
    return OUTAGES_PAGE_WITH_RESULT.format(
        from_date=from_date,
        to_date=to_date,
        result=result
    )


@app.route('/search/fdb')
def search_fdb():
    """FDB Search page - similar to LibreNMS search/fdb.inc.php"""
    device_id = request.args.get('device_id', '')
    searchby = request.args.get('searchby', 'mac')
    searchPhrase = request.args.get('searchPhrase', '')
    
    # Properly escaped
    device_id_safe = cgi.escape(device_id)
    searchby_safe = cgi.escape(searchby)
    searchPhrase_safe = cgi.escape(searchPhrase)
    
    return FDB_SEARCH_PAGE.format(
        device_id=device_id_safe,
        searchby=searchby_safe,
        searchPhrase=searchPhrase_safe
    )


@app.route('/apps/ntp')
def apps_ntp():
    """NTP App page - similar to LibreNMS apps/ntp.inc.php"""
    view = request.args.get('view', 'graphs')
    graph = request.args.get('graph', 'offset')
    
    # Properly sanitized
    view_safe = cgi.escape(view)
    graph_safe = cgi.escape(graph)
    
    return NTP_APP_PAGE.format(
        view=view_safe,
        graph=graph_safe
    )


@app.route('/alerts')
def alerts():
    """Alerts page"""
    return ALERTS_PAGE


@app.route('/about')
def about():
    return ABOUT_PAGE


@app.route('/robots.txt')
def robots():
    return Response("""User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /config/
Allow: /

# NetMonitor v2.3.7
# Please report security issues to security@netmonitor.local
""", mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True)
