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

# Valid sensor types (whitelist) - but we don't use it properly (vulnerable!)
VALID_WIRELESS_TYPES = {
    'signal': 'Signal Strength',
    'noise': 'Noise Level',
    'snr': 'Signal to Noise Ratio',
    'rate': 'Data Rate',
    'clients': 'Connected Clients',
    'frequency': 'Operating Frequency'
}

VALID_HEALTH_TYPES = {
    'processor': 'CPU Usage',
    'memory': 'Memory Usage',
    'disk': 'Disk Space',
    'temperature': 'Temperature',
    'fanspeed': 'Fan Speed',
    'voltage': 'Voltage'
}

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, metric):
    """Check if XSS is triggered using PhantomJS"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
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

    if metric == "":
        return None
    elif result == 'XSS':
        return flag
    else:
        return None

@app.route('/wireless')
@app.route('/wireless/')
@app.route('/wireless/<path:metric>')
def wireless_sensors(metric=None):
    """
    Display wireless sensor data.
    Vulnerable: The metric parameter from URL path is reflected without sanitization.
    Mimics LibreNMS wireless.inc.php vulnerability.
    """
    if metric is None:
        metric = request.args.get('metric', '')
    
    # Parse metric from path (e.g., /wireless/metric=value becomes metric=value)
    # Simulating LibreNMS's URL::parseLegacyPathVars behavior
    if '=' in metric:
        parts = metric.split('=', 1)
        if parts[0] == 'metric':
            metric = parts[1]
    
    # VULNERABLE: Using os.path.basename() like LibreNMS - doesn't prevent XSS!
    # This mimics the vulnerable code: $class = basename($vars['metric'] ?? key($valid_wireless_types));
    sensor_class = os.path.basename(metric) if metric else 'signal'
    
    # Build the page - metric is reflected directly (vulnerable!)
    page = WIRELESS_PAGE.format(sensor_class=sensor_class)
    
    # Check for XSS
    flag_result = check_xss(page, flags[0], metric)
    
    if flag_result:
        result_html = '<div class="alert alert-success">Monitoring check passed! Flag: {}</div>'.format(flag_result)
    elif metric and metric not in VALID_WIRELESS_TYPES:
        # VULNERABLE: Reflects user input directly
        result_html = '<div class="alert alert-warning">No sensors of type {} found.</div>'.format(sensor_class)
    else:
        result_html = ''
    
    response = make_response(WIRELESS_PAGE_FULL.format(sensor_class=sensor_class, result=result_html))
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/health')
@app.route('/health/')
@app.route('/health/<path:metric>')
def health_sensors(metric=None):
    """
    Display device health data.
    Vulnerable: The metric parameter from URL path is reflected without sanitization.
    Mimics LibreNMS health.inc.php vulnerability.
    """
    if metric is None:
        metric = request.args.get('metric', '')
    
    # Parse metric from path (e.g., /health/metric=value becomes metric=value)
    if '=' in metric:
        parts = metric.split('=', 1)
        if parts[0] == 'metric':
            metric = parts[1]
    
    # VULNERABLE: Using basename() - doesn't sanitize HTML/JS
    active_metric = os.path.basename(metric) if metric else 'processor'
    
    # Build the page - metric is reflected directly
    page = HEALTH_PAGE.format(active_metric=active_metric)
    
    # Check for XSS
    flag_result = check_xss(page, flags[0], metric)
    
    if flag_result:
        result_html = '<div class="alert alert-success">Health check passed! Flag: {}</div>'.format(flag_result)
    elif metric and metric not in VALID_HEALTH_TYPES:
        # VULNERABLE: Reflects user input directly  
        result_html = '<div class="alert alert-warning">No sensors of type {} found.</div>'.format(active_metric)
    else:
        result_html = ''
    
    response = make_response(HEALTH_PAGE_FULL.format(active_metric=active_metric, result=result_html))
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/devices')
def devices():
    """List monitored devices"""
    return DEVICES_PAGE

@app.route('/api/v0/devices')
def api_devices():
    """API endpoint for devices"""
    return Response('{"status":"ok","devices":[{"device_id":1,"hostname":"switch01.local","status":1},{"device_id":2,"hostname":"ap01.local","status":1}]}', mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
