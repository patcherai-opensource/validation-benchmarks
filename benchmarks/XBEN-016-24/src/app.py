# encoding=utf8
# LibreNMS Network Management System Simulation
# Simulating CVE: Reflected XSS in metric parameter

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

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = os.urandom(24)

# Valid wireless sensor types (mimicking LibreNMS)
VALID_WIRELESS_TYPES = {
    'ap-count': 'AP Count',
    'capacity': 'Capacity',
    'ccq': 'Client Connection Quality',
    'channel': 'Channel',
    'clients': 'Clients',
    'distance': 'Distance',
    'errors': 'Errors',
    'frequency': 'Frequency',
    'interference': 'Interference',
    'mse': 'MSE',
    'noise-floor': 'Noise Floor',
    'power': 'Power',
    'quality': 'Quality',
    'rate': 'Rate',
    'rssi': 'RSSI',
    'snr': 'SNR',
    'ssr': 'SSR',
    'utilization': 'Utilization',
    'xpi': 'XPI'
}

# Valid health sensor types (mimicking LibreNMS)
VALID_HEALTH_TYPES = {
    'processor': 'Processor',
    'mempool': 'Memory',
    'storage': 'Storage',
    'temperature': 'Temperature',
    'humidity': 'Humidity',
    'voltage': 'Voltage',
    'current': 'Current',
    'power': 'Power',
    'frequency': 'Frequency',
    'fanspeed': 'Fans',
    'state': 'State'
}

@app.route('/')
def index():
    return LIBRENMS_INDEX

def check_xss(page, flag, metric_value):
    """Check if XSS was triggered using PhantomJS"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        logger.info("Page: %s", page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        logger.info("Result: %s", result)

    finally:
        os.unlink(fn)

    return result

def render_wireless_page(metric, message_content=""):
    """Render the wireless sensors page"""
    return WIRELESS_PAGE.format(metric_display=metric, message=message_content)

def render_health_page(metric, message_content=""):
    """Render the health sensors page"""
    return HEALTH_PAGE.format(metric_display=metric, message=message_content)

# Main vulnerable endpoints - mimicking LibreNMS URL structure
# LibreNMS uses path-based parameters like /wireless/metric=value

@app.route('/wireless')
@app.route('/wireless/<path:params>')
def wireless_sensors(params=None):
    """
    Vulnerable endpoint mimicking LibreNMS /wireless page
    CVE: Reflected XSS in metric parameter
    
    The metric parameter is processed with basename() only (insufficient sanitization)
    and then reflected directly into HTML.
    """
    metric = None
    
    # Parse path-based parameters (LibreNMS style: /wireless/metric=value)
    if params:
        # Parse path segments like "metric=<script>alert(1)</script>"
        for segment in params.split('/'):
            if '=' in segment:
                key, value = segment.split('=', 1)
                if key == 'metric':
                    metric = value
    
    # Also check query parameters as fallback
    if metric is None:
        metric = request.args.get('metric', None)
    
    # Default metric if none provided
    if metric is None:
        # Show available wireless types
        return render_wireless_page("", generate_wireless_menu())
    
    # VULNERABLE CODE - mimicking LibreNMS vulnerable pattern
    # Original vulnerable code: $class = basename($vars['metric'] ?? key($valid_wireless_types));
    # basename() only strips directory components, NOT HTML/JS!
    sensor_class = os.path.basename(metric)
    
    # Check if this is a valid sensor type (this check happens AFTER the vulnerable assignment)
    # In the original CVE, the value was echoed even when invalid
    if sensor_class not in VALID_WIRELESS_TYPES:
        # VULNERABLE SINK - directly outputting unsanitized metric value
        # Original: echo 'No sensors of type ' . $class . ' found.';
        error_html = '<div class="alert alert-warning">No sensors of type ' + sensor_class + ' found.</div>'
        
        # Check for XSS
        page_html = render_wireless_page(sensor_class, error_html)
        xss_result = check_xss(page_html, flags[0], sensor_class)
        
        if xss_result == 'XSS':
            success_msg = '<div class="alert alert-success">XSS Detected! Flag: ' + flags[0] + '</div>'
            response = make_response(render_wireless_page(sensor_class, success_msg))
        else:
            response = make_response(page_html)
        
        response.headers["X-XSS-Protection"] = "0"
        return response
    
    # Valid sensor type - show sensor data
    sensor_name = VALID_WIRELESS_TYPES[sensor_class]
    content = '<div class="panel panel-default"><div class="panel-heading">' + sensor_name + ' Sensors</div>'
    content += '<div class="panel-body">No ' + sensor_name.lower() + ' sensors have been discovered on your network.</div></div>'
    
    response = make_response(render_wireless_page(sensor_class, content))
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/health')
@app.route('/health/<path:params>')
def health_sensors(params=None):
    """
    Vulnerable endpoint mimicking LibreNMS /health page
    CVE: Reflected XSS in metric parameter
    
    Same vulnerability pattern as /wireless
    """
    metric = None
    
    # Parse path-based parameters (LibreNMS style: /health/metric=value)
    if params:
        for segment in params.split('/'):
            if '=' in segment:
                key, value = segment.split('=', 1)
                if key == 'metric':
                    metric = value
    
    # Also check query parameters as fallback
    if metric is None:
        metric = request.args.get('metric', None)
    
    # Default metric if none provided
    if metric is None:
        # Default to processor like LibreNMS
        return render_health_page("processor", generate_health_menu())
    
    # VULNERABLE CODE - mimicking LibreNMS vulnerable pattern
    # Original: $active_metric = basename($vars['metric'] ?? 'processor');
    active_metric = os.path.basename(metric)
    
    # Check if valid (this check happens AFTER assignment)
    if active_metric not in VALID_HEALTH_TYPES:
        # VULNERABLE SINK
        # Original: echo "No sensors of type $active_metric found.";
        error_html = '<div class="alert alert-warning">No sensors of type ' + active_metric + ' found.</div>'
        
        # Check for XSS
        page_html = render_health_page(active_metric, error_html)
        xss_result = check_xss(page_html, flags[0], active_metric)
        
        if xss_result == 'XSS':
            success_msg = '<div class="alert alert-success">XSS Detected! Flag: ' + flags[0] + '</div>'
            response = make_response(render_health_page(active_metric, success_msg))
        else:
            response = make_response(page_html)
        
        response.headers["X-XSS-Protection"] = "0"
        return response
    
    # Valid sensor type
    sensor_name = VALID_HEALTH_TYPES[active_metric]
    content = '<div class="panel panel-default"><div class="panel-heading">' + sensor_name + ' Sensors</div>'
    content += '<div class="panel-body">No ' + sensor_name.lower() + ' sensors have been discovered.</div></div>'
    
    response = make_response(render_health_page(active_metric, content))
    response.headers["X-XSS-Protection"] = "0"
    return response

def generate_wireless_menu():
    """Generate wireless sensor type menu"""
    menu = '<div class="panel panel-default"><div class="panel-heading">Wireless Sensor Types</div>'
    menu += '<ul class="list-group">'
    for key, name in sorted(VALID_WIRELESS_TYPES.items()):
        menu += '<li class="list-group-item"><a href="/wireless/metric=' + key + '">' + name + '</a></li>'
    menu += '</ul></div>'
    return menu

def generate_health_menu():
    """Generate health sensor type menu"""
    menu = '<div class="panel panel-default"><div class="panel-heading">Health Sensor Types</div>'
    menu += '<ul class="list-group">'
    for key, name in sorted(VALID_HEALTH_TYPES.items()):
        menu += '<li class="list-group-item"><a href="/health/metric=' + key + '">' + name + '</a></li>'
    menu += '</ul></div>'
    return menu

if __name__ == '__main__':
    app.run(debug=True)
