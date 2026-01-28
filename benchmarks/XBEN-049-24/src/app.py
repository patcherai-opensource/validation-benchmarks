# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, jsonify
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
import time
import random

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# Mock data for the network monitoring system
DEVICES = [
    {"id": 1, "hostname": "core-sw01.dc1", "ip": "10.0.1.1", "status": "up", "uptime": "45 days"},
    {"id": 2, "hostname": "core-sw02.dc1", "ip": "10.0.1.2", "status": "up", "uptime": "45 days"},
    {"id": 3, "hostname": "edge-rtr01.dc1", "ip": "10.0.2.1", "status": "down", "uptime": "0 days"},
    {"id": 4, "hostname": "fw-01.dc1", "ip": "10.0.3.1", "status": "up", "uptime": "120 days"},
    {"id": 5, "hostname": "ap-wifi01.floor2", "ip": "10.0.10.1", "status": "up", "uptime": "30 days"},
]

PORTS = [
    {"id": 1, "device_id": 1, "ifName": "Gi0/1", "ifDescr": "Uplink to Core", "status": "up"},
    {"id": 2, "device_id": 1, "ifName": "Gi0/2", "ifDescr": "Server VLAN", "status": "up"},
    {"id": 3, "device_id": 2, "ifName": "Te0/1", "ifDescr": "10G Backbone", "status": "up"},
    {"id": 4, "device_id": 3, "ifName": "Gi0/0", "ifDescr": "WAN Link", "status": "down"},
]

OUTAGES = [
    {"id": 1, "device_id": 3, "hostname": "edge-rtr01.dc1", "start": "2024-01-15 08:30:00", "duration": "ongoing"},
    {"id": 2, "device_id": 1, "hostname": "core-sw01.dc1", "start": "2024-01-10 02:15:00", "duration": "45m"},
]

SYSLOG_ENTRIES = [
    {"id": 1, "timestamp": "2024-01-15 12:00:01", "device": "core-sw01.dc1", "severity": "info", "message": "Interface Gi0/1 up"},
    {"id": 2, "timestamp": "2024-01-15 11:55:00", "device": "edge-rtr01.dc1", "severity": "critical", "message": "BGP session down"},
    {"id": 3, "timestamp": "2024-01-15 11:50:30", "device": "fw-01.dc1", "severity": "warning", "message": "High CPU utilization"},
]

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/api/status')
def api_status():
    """API endpoint - returns JSON status (safe, properly encoded)"""
    return jsonify({
        "status": "operational",
        "version": "23.7.0",
        "devices_monitored": len(DEVICES),
        "uptime": "45 days"
    })

@app.route('/devices')
def devices_list():
    """Device listing page - safe endpoint"""
    device_rows = ""
    for d in DEVICES:
        status_class = "status-up" if d["status"] == "up" else "status-down"
        device_rows += '<tr><td>{}</td><td>{}</td><td>{}</td><td class="{}">{}</td><td>{}</td></tr>'.format(
            cgi.escape(str(d["id"])), 
            cgi.escape(d["hostname"]), 
            cgi.escape(d["ip"]), 
            status_class,
            cgi.escape(d["status"]), 
            cgi.escape(d["uptime"])
        )
    return DEVICES_CONTENT.format(device_rows)

@app.route('/ports')
def ports_list():
    """Ports listing with search - safe endpoint (uses proper escaping)"""
    search = request.args.get('search', '')
    device_filter = request.args.get('device_id', '')
    
    # Properly escape for display
    search_escaped = cgi.escape(search)
    device_filter_escaped = cgi.escape(device_filter)
    
    port_rows = ""
    for p in PORTS:
        if search and search.lower() not in p["ifDescr"].lower() and search.lower() not in p["ifName"].lower():
            continue
        if device_filter and str(p["device_id"]) != device_filter:
            continue
        status_class = "status-up" if p["status"] == "up" else "status-down"
        port_rows += '<tr><td>{}</td><td>{}</td><td>{}</td><td class="{}">{}</td></tr>'.format(
            cgi.escape(p["ifName"]), 
            cgi.escape(p["ifDescr"]), 
            str(p["device_id"]),
            status_class,
            cgi.escape(p["status"])
        )
    return PORTS_CONTENT.format(search_escaped, device_filter_escaped, port_rows)

@app.route('/health')
def health_overview():
    """Health overview - safe endpoint"""
    return HEALTH_CONTENT

@app.route('/alerts')
def alerts_page():
    """Alerts configuration page - safe endpoint"""
    return ALERTS_CONTENT

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host, fallback to localhost for local development
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
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

    return result

@app.route('/outages')
def outages_page():
    """
    Outages page - VULNERABLE endpoint
    Reflects 'from' and 'to' date parameters without sanitization
    Similar to LibreNMS CVE - includes/html/pages/outages.inc.php
    """
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    device_filter = request.args.get('device', '')
    
    # Filter logic (safe - not used for XSS check)
    device_filter_escaped = cgi.escape(device_filter) if device_filter else ""
    
    # Build outage rows  
    outage_rows = ""
    for o in OUTAGES:
        outage_rows += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            cgi.escape(o["hostname"]),
            cgi.escape(o["start"]),
            cgi.escape(o["duration"]),
            "Critical" if o["duration"] == "ongoing" else "Resolved"
        )
    
    # VULNERABLE: from_date and to_date are reflected directly into value attributes without escaping
    # This mimics the LibreNMS vulnerability where $vars['from'] and $vars['to'] were not sanitized
    from_value = '' if from_date == '' else 'value="{}"'.format(from_date)
    to_value = '' if to_date == '' else 'value="{}"'.format(to_date)
    
    page_content = OUTAGES_CONTENT.format(from_value, to_value, device_filter_escaped, outage_rows)
    
    # Check for successful XSS
    if from_date or to_date:
        test_input = from_date if from_date else to_date
        result = check_xss(page_content, flags[0], test_input, 'outages')
        if result == 'XSS':
            return OUTAGES_SUCCESS_CONTENT.format(flags[0])
    
    return page_content

@app.route('/syslog')
def syslog_page():
    """
    Syslog viewer - DECOY endpoint (has filtering but safe)
    Similar structure to vulnerable endpoint but properly escaped
    """
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    severity = request.args.get('severity', '')
    
    # Properly escaped values
    from_escaped = cgi.escape(from_date)
    to_escaped = cgi.escape(to_date)
    severity_escaped = cgi.escape(severity)
    
    log_rows = ""
    for entry in SYSLOG_ENTRIES:
        if severity and entry["severity"] != severity:
            continue
        sev_class = "sev-" + entry["severity"]
        log_rows += '<tr><td>{}</td><td>{}</td><td class="{}">{}</td><td>{}</td></tr>'.format(
            cgi.escape(entry["timestamp"]),
            cgi.escape(entry["device"]),
            sev_class,
            cgi.escape(entry["severity"]),
            cgi.escape(entry["message"])
        )
    
    from_value = '' if from_escaped == '' else 'value="{}"'.format(from_escaped)
    to_value = '' if to_escaped == '' else 'value="{}"'.format(to_escaped)
    
    return SYSLOG_CONTENT.format(from_value, to_value, severity_escaped, log_rows)

@app.route('/apps/ntp')
def ntp_app():
    """NTP monitoring app - safe endpoint"""
    view = request.args.get('view', 'summary')
    view_escaped = cgi.escape(view)
    return NTP_APP_CONTENT.format(view_escaped)

@app.route('/search/fdb')
def fdb_search():
    """FDB/MAC search - safe endpoint"""
    searchby = request.args.get('searchby', 'mac')
    phrase = request.args.get('searchPhrase', '')
    
    searchby_escaped = cgi.escape(searchby)
    phrase_escaped = cgi.escape(phrase)
    
    return FDB_SEARCH_CONTENT.format(searchby_escaped, phrase_escaped)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
