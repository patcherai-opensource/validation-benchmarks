# encoding=utf8

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

# Valid sensor types for the network monitoring system
VALID_WIRELESS_TYPES = {
    'ap-count': 'Access Point Count',
    'clients': 'Connected Clients',
    'quality': 'Signal Quality',
    'power': 'TX Power',
    'noise-floor': 'Noise Floor',
    'rate': 'Data Rate',
    'frequency': 'Frequency',
    'channel': 'Channel',
    'snr': 'Signal to Noise Ratio',
    'errors': 'Error Rate'
}

VALID_HEALTH_TYPES = {
    'processor': 'CPU Usage',
    'mempool': 'Memory Pool',
    'storage': 'Storage Usage',
    'temperature': 'Temperature',
    'fans': 'Fan Speed',
    'voltage': 'Voltage',
    'current': 'Current Draw',
    'power': 'Power Consumption',
    'load': 'System Load',
    'state': 'System State'
}

# Sample device data for the monitoring dashboard
DEVICES_DATA = [
    {'id': 1, 'hostname': 'router-core-01', 'ip': '192.168.1.1', 'status': 'up', 'type': 'router'},
    {'id': 2, 'hostname': 'switch-access-01', 'ip': '192.168.1.10', 'status': 'up', 'type': 'switch'},
    {'id': 3, 'hostname': 'ap-floor1-01', 'ip': '192.168.1.100', 'status': 'up', 'type': 'wireless'},
    {'id': 4, 'hostname': 'ap-floor2-01', 'ip': '192.168.1.101', 'status': 'down', 'type': 'wireless'},
    {'id': 5, 'hostname': 'server-web-01', 'ip': '192.168.2.10', 'status': 'up', 'type': 'server'},
]

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/dashboard')
def dashboard():
    return DASHBOARD_CONTENT

@app.route('/devices')
def devices():
    return DEVICES_CONTENT.format(devices=DEVICES_DATA)

@app.route('/api/devices')
def api_devices():
    response = make_response('{"devices": ' + str(DEVICES_DATA).replace("'", '"') + ', "total": ' + str(len(DEVICES_DATA)) + '}')
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/api/status')
def api_status():
    response = make_response('{"status": "operational", "version": "24.1.0", "uptime": "45d 12h 33m"}')
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/alerts')
def alerts():
    return ALERTS_CONTENT

@app.route('/settings')
def settings():
    return SETTINGS_CONTENT

def check_xss(page, flag, msg):
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
        print "Resultado:"
        print result

    finally:
        os.unlink(fn)

    if msg == "":
        return None, False
    else:
        if result == 'XSS':
            return flag, True
        elif result:
            return result, False
        else:
            return None, False

############## VULNERABLE ENDPOINTS - CVE-inspired XSS #################### 

@app.route('/wireless')
def wireless():
    # Get metric from query parameter (similar to LibreNMS path parsing)
    metric = request.args.get('metric', '')
    
    if metric == '':
        # Show default wireless overview
        return WIRELESS_CONTENT.format(metric_display='', sensor_content=WIRELESS_OVERVIEW)
    
    # Check if it's a valid metric type - if not, reflect it in error message
    # This is the vulnerable code path - basename() equivalent not sufficient
    metric_class = os.path.basename(metric)  # Only strips directory components, not markup
    
    if metric_class not in VALID_WIRELESS_TYPES:
        # Vulnerable: directly echoing user input into HTML
        error_html = '<div class="alert alert-warning">No sensors of type ' + metric_class + ' found.</div>'
        page_content = WIRELESS_CONTENT.format(metric_display=metric_class, sensor_content=error_html)
        
        # Check for XSS
        result, success = check_xss(page_content, flags[0], metric)
        
        if success:
            flag_html = '<div class="alert alert-success"><strong>Debug Output:</strong> ' + result + '</div>'
            return WIRELESS_CONTENT.format(metric_display=metric_class, sensor_content=error_html + flag_html)
        
        response = make_response(page_content)
        response.headers["X-XSS-Protection"] = "0"
        return response
    
    # Valid metric - show sensor data
    sensor_html = '<div class="sensor-data"><h4>' + VALID_WIRELESS_TYPES[metric_class] + '</h4><p>Current: 75%</p><p>Average: 68%</p></div>'
    return WIRELESS_CONTENT.format(metric_display=metric_class, sensor_content=sensor_html)

@app.route('/health')
def health():
    # Get metric from query parameter
    metric = request.args.get('metric', '')
    
    if metric == '':
        # Show default health overview
        return HEALTH_CONTENT.format(metric_display='', sensor_content=HEALTH_OVERVIEW)
    
    # Check if it's a valid metric type
    active_metric = os.path.basename(metric)  # basename only, same vulnerability as /wireless
    
    if active_metric not in VALID_HEALTH_TYPES:
        # Vulnerable: directly echoing user input into HTML
        error_html = '<div class="alert alert-warning">No sensors of type ' + active_metric + ' found.</div>'
        page_content = HEALTH_CONTENT.format(metric_display=active_metric, sensor_content=error_html)
        
        # Check for XSS
        result, success = check_xss(page_content, flags[0], metric)
        
        if success:
            flag_html = '<div class="alert alert-success"><strong>Debug Output:</strong> ' + result + '</div>'
            return HEALTH_CONTENT.format(metric_display=active_metric, sensor_content=error_html + flag_html)
        
        response = make_response(page_content)
        response.headers["X-XSS-Protection"] = "0"
        return response
    
    # Valid metric - show sensor data
    sensor_html = '<div class="sensor-data"><h4>' + VALID_HEALTH_TYPES[active_metric] + '</h4><p>Current: 42%</p><p>Average: 38%</p></div>'
    return HEALTH_CONTENT.format(metric_display=active_metric, sensor_content=sensor_html)

@app.route('/graphs')
def graphs():
    device_id = request.args.get('id', '1')
    graph_type = request.args.get('type', 'traffic')
    # Safe endpoint - properly escaped
    return GRAPHS_CONTENT.format(device_id=cgi.escape(device_id), graph_type=cgi.escape(graph_type))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # Safe endpoint - properly escaped
    return SEARCH_CONTENT.format(query=cgi.escape(query))

@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

if __name__ == '__main__':
    app.run(debug=True)
