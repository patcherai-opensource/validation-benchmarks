# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, url_for, session
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import time
import hashlib
import random

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flag_data = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = hashlib.sha256(os.urandom(32)).hexdigest()

phantom = Phantom()

# Simulated device data (network monitoring)
DEVICES = [
    {"device_id": 1, "hostname": "core-rtr-01.dc1.internal", "sysName": "core-rtr-01", "os": "ios", "status": 1, "uptime": 8640000, "hardware": "Cisco ASR 9001", "location": "DC1-R01-RK12"},
    {"device_id": 2, "hostname": "dist-sw-01.dc1.internal", "sysName": "dist-sw-01", "os": "nxos", "status": 1, "uptime": 4320000, "hardware": "Nexus 9300", "location": "DC1-R02-RK05"},
    {"device_id": 3, "hostname": "edge-fw-01.dc2.internal", "sysName": "edge-fw-01", "os": "asa", "status": 0, "uptime": 0, "hardware": "ASA 5525-X", "location": "DC2-R01-RK01"},
    {"device_id": 4, "hostname": "access-sw-04.bld3.internal", "sysName": "access-sw-04", "os": "ios", "status": 1, "uptime": 1296000, "hardware": "Catalyst 9200", "location": "BLD3-FL2-IDF"},
    {"device_id": 5, "hostname": "wlc-01.dc1.internal", "sysName": "wlc-01", "os": "aireos", "status": 1, "uptime": 6048000, "hardware": "WLC 5520", "location": "DC1-R01-RK15"},
    {"device_id": 6, "hostname": "mon-srv-01.dc1.internal", "sysName": "mon-srv-01", "os": "linux", "status": 1, "uptime": 15552000, "hardware": "Dell R640", "location": "DC1-R03-RK08"},
]

OUTAGE_DATA = [
    {"device_id": 3, "hostname": "edge-fw-01.dc2.internal", "going_down": "2023-09-15 14:23:11", "up_again": None, "duration": "ongoing"},
    {"device_id": 2, "hostname": "dist-sw-01.dc1.internal", "going_down": "2023-09-10 08:12:45", "up_again": "2023-09-10 08:45:22", "duration": "32m 37s"},
    {"device_id": 4, "hostname": "access-sw-04.bld3.internal", "going_down": "2023-09-05 22:01:00", "up_again": "2023-09-06 06:15:30", "duration": "8h 14m 30s"},
    {"device_id": 1, "hostname": "core-rtr-01.dc1.internal", "going_down": "2023-08-28 03:45:12", "up_again": "2023-08-28 03:47:55", "duration": "2m 43s"},
]

SYSLOG_DATA = [
    {"timestamp": "2023-09-15 14:23:11", "device": "edge-fw-01", "facility": "local7", "severity": "alert", "message": "Interface GigabitEthernet0/0 changed state to down"},
    {"timestamp": "2023-09-15 14:23:10", "device": "edge-fw-01", "facility": "local7", "severity": "warning", "message": "BGP neighbor 10.0.0.1 Down - Hold timer expired"},
    {"timestamp": "2023-09-15 12:00:01", "device": "mon-srv-01", "facility": "cron", "severity": "info", "message": "CRON: (librenms) CMD (cd /opt/librenms && php artisan schedule:run)"},
    {"timestamp": "2023-09-15 11:45:33", "device": "core-rtr-01", "facility": "local7", "severity": "notice", "message": "OSPF-5-ADJCHG: Process 1, Nbr 10.1.1.2 on GigabitEthernet0/1 from FULL to DOWN"},
    {"timestamp": "2023-09-15 10:30:22", "device": "dist-sw-01", "facility": "local7", "severity": "info", "message": "STP: VLAN 100 Port Gi1/0/24 moved to forwarding state"},
    {"timestamp": "2023-09-15 09:15:00", "device": "wlc-01", "facility": "local6", "severity": "info", "message": "AP access-ap-12 associated with controller"},
]

PORT_DATA = [
    {"port_id": 1, "device_id": 1, "ifName": "GigabitEthernet0/0/0", "ifAlias": "Uplink to ISP-A", "ifOperStatus": "up", "ifSpeed": 10000000000, "ifInOctets_rate": 524288000, "ifOutOctets_rate": 262144000},
    {"port_id": 2, "device_id": 1, "ifName": "GigabitEthernet0/0/1", "ifAlias": "Uplink to ISP-B", "ifOperStatus": "up", "ifSpeed": 10000000000, "ifInOctets_rate": 412876800, "ifOutOctets_rate": 198451200},
    {"port_id": 3, "device_id": 2, "ifName": "Ethernet1/1", "ifAlias": "To Core-RTR-01", "ifOperStatus": "up", "ifSpeed": 40000000000, "ifInOctets_rate": 1073741824, "ifOutOctets_rate": 536870912},
    {"port_id": 4, "device_id": 3, "ifName": "GigabitEthernet0/0", "ifAlias": "WAN Interface", "ifOperStatus": "down", "ifSpeed": 1000000000, "ifInOctets_rate": 0, "ifOutOctets_rate": 0},
    {"port_id": 5, "device_id": 4, "ifName": "GigabitEthernet1/0/1", "ifAlias": "Access Port - VLAN 100", "ifOperStatus": "up", "ifSpeed": 1000000000, "ifInOctets_rate": 12582912, "ifOutOctets_rate": 6291456},
]

NTP_DATA = [
    {"app_id": 1, "device_id": 6, "peer": "0.pool.ntp.org", "stratum": 2, "offset": -0.234, "delay": 15.432, "jitter": 1.234},
    {"app_id": 2, "device_id": 6, "peer": "1.pool.ntp.org", "stratum": 2, "offset": 0.567, "delay": 22.100, "jitter": 0.876},
    {"app_id": 3, "device_id": 1, "peer": "ntp.internal.dc1", "stratum": 1, "offset": -0.012, "delay": 0.543, "jitter": 0.034},
]

FDB_DATA = [
    {"mac_address": "00:1A:2B:3C:4D:5E", "device_id": 2, "hostname": "dist-sw-01.dc1.internal", "ifName": "Ethernet1/3", "vlan_id": 100},
    {"mac_address": "00:1A:2B:3C:4D:5F", "device_id": 2, "hostname": "dist-sw-01.dc1.internal", "ifName": "Ethernet1/4", "vlan_id": 200},
    {"mac_address": "AA:BB:CC:DD:EE:01", "device_id": 4, "hostname": "access-sw-04.bld3.internal", "ifName": "GigabitEthernet1/0/1", "vlan_id": 100},
    {"mac_address": "AA:BB:CC:DD:EE:02", "device_id": 4, "hostname": "access-sw-04.bld3.internal", "ifName": "GigabitEthernet1/0/2", "vlan_id": 100},
]


def format_speed(speed):
    if speed >= 1000000000:
        return "%d Gbps" % (speed / 1000000000)
    elif speed >= 1000000:
        return "%d Mbps" % (speed / 1000000)
    return "%d Kbps" % (speed / 1000)


def format_rate(rate):
    if rate >= 1073741824:
        return "%.1f GB/s" % (rate / 1073741824.0)
    elif rate >= 1048576:
        return "%.1f MB/s" % (rate / 1048576.0)
    elif rate >= 1024:
        return "%.1f KB/s" % (rate / 1024.0)
    return "%d B/s" % rate


def format_uptime(seconds):
    if seconds == 0:
        return "Down"
    days = seconds / 86400
    hours = (seconds % 86400) / 3600
    return "%dd %dh" % (days, hours)


def get_nav_html():
    return """
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="/">LibreNMS</a>
            </div>
            <ul class="nav navbar-nav">
                <li><a href="/devices">Devices</a></li>
                <li><a href="/ports/list">Ports</a></li>
                <li><a href="/outages">Outages</a></li>
                <li><a href="/syslog">Syslog</a></li>
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown">Apps <span class="caret"></span></a>
                    <ul class="dropdown-menu">
                        <li><a href="/apps/ntp">NTP</a></li>
                    </ul>
                </li>
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown">Health <span class="caret"></span></a>
                    <ul class="dropdown-menu">
                        <li><a href="/health/mempool">Memory</a></li>
                        <li><a href="/health/processor">Processor</a></li>
                        <li><a href="/health/storage">Storage</a></li>
                    </ul>
                </li>
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown">Search <span class="caret"></span></a>
                    <ul class="dropdown-menu">
                        <li><a href="/search/fdb">FDB Tables</a></li>
                    </ul>
                </li>
            </ul>
        </div>
    </nav>"""


def get_page_wrapper(title, content):
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} - LibreNMS</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/css/librenms.css">
</head>
<body>
{nav}
<div class="container-fluid">
    {content}
</div>
<script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
</body>
</html>""".format(title=cgi.escape(title), nav=get_nav_html(), content=content)


def check_xss_page(page_html):
    proc = subprocess.Popen(["timeout", "8", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
    result = ""
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result


@app.route('/')
def index():
    device_rows = ""
    for d in DEVICES:
        status_label = '<span class="label label-success">Up</span>' if d["status"] == 1 else '<span class="label label-danger">Down</span>'
        device_rows += """<tr>
            <td><a href="/device/{device_id}">{hostname}</a></td>
            <td>{os}</td>
            <td>{hardware}</td>
            <td>{status}</td>
            <td>{uptime}</td>
            <td>{location}</td>
        </tr>""".format(
            device_id=d["device_id"],
            hostname=cgi.escape(d["hostname"]),
            os=cgi.escape(d["os"]),
            hardware=cgi.escape(d["hardware"]),
            status=status_label,
            uptime=format_uptime(d["uptime"]),
            location=cgi.escape(d["location"])
        )

    content = """
    <div class="row">
        <div class="col-sm-12">
            <h3>Dashboard</h3>
            <div class="row">
                <div class="col-sm-3">
                    <div class="panel panel-default">
                        <div class="panel-heading">Devices</div>
                        <div class="panel-body text-center"><h2>{total_devices}</h2></div>
                    </div>
                </div>
                <div class="col-sm-3">
                    <div class="panel panel-success">
                        <div class="panel-heading">Devices Up</div>
                        <div class="panel-body text-center"><h2>{up_devices}</h2></div>
                    </div>
                </div>
                <div class="col-sm-3">
                    <div class="panel panel-danger">
                        <div class="panel-heading">Devices Down</div>
                        <div class="panel-body text-center"><h2>{down_devices}</h2></div>
                    </div>
                </div>
                <div class="col-sm-3">
                    <div class="panel panel-info">
                        <div class="panel-heading">Active Outages</div>
                        <div class="panel-body text-center"><h2>{active_outages}</h2></div>
                    </div>
                </div>
            </div>
            <h4>Device List</h4>
            <table class="table table-condensed table-hover table-striped">
                <thead><tr><th>Device</th><th>OS</th><th>Hardware</th><th>Status</th><th>Uptime</th><th>Location</th></tr></thead>
                <tbody>{device_rows}</tbody>
            </table>
        </div>
    </div>""".format(
        total_devices=len(DEVICES),
        up_devices=len([d for d in DEVICES if d["status"] == 1]),
        down_devices=len([d for d in DEVICES if d["status"] == 0]),
        active_outages=len([o for o in OUTAGE_DATA if o["up_again"] is None]),
        device_rows=device_rows
    )
    return get_page_wrapper("Dashboard", content)


@app.route('/devices')
def devices():
    device_rows = ""
    for d in DEVICES:
        status_label = '<span class="label label-success">Up</span>' if d["status"] == 1 else '<span class="label label-danger">Down</span>'
        device_rows += """<tr>
            <td><a href="/device/{device_id}">{hostname}</a></td>
            <td>{sysName}</td>
            <td>{os}</td>
            <td>{hardware}</td>
            <td>{status}</td>
            <td>{uptime}</td>
            <td>{location}</td>
        </tr>""".format(
            device_id=d["device_id"],
            hostname=cgi.escape(d["hostname"]),
            sysName=cgi.escape(d["sysName"]),
            os=cgi.escape(d["os"]),
            hardware=cgi.escape(d["hardware"]),
            status=status_label,
            uptime=format_uptime(d["uptime"]),
            location=cgi.escape(d["location"])
        )

    content = """
    <div class="row">
        <div class="col-sm-12">
            <h3>All Devices</h3>
            <table class="table table-condensed table-hover table-striped">
                <thead><tr><th>Device</th><th>sysName</th><th>OS</th><th>Hardware</th><th>Status</th><th>Uptime</th><th>Location</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>""".format(rows=device_rows)
    return get_page_wrapper("Devices", content)


@app.route('/device/<int:device_id>')
def device_detail(device_id):
    device = None
    for d in DEVICES:
        if d["device_id"] == device_id:
            device = d
            break
    if not device:
        return get_page_wrapper("Device Not Found", "<h3>Device not found</h3>"), 404

    device_ports = [p for p in PORT_DATA if p["device_id"] == device_id]
    port_rows = ""
    for p in device_ports:
        status_class = "success" if p["ifOperStatus"] == "up" else "danger"
        port_rows += """<tr>
            <td>{ifName}</td>
            <td>{ifAlias}</td>
            <td><span class="label label-{cls}">{status}</span></td>
            <td>{speed}</td>
            <td>{in_rate}</td>
            <td>{out_rate}</td>
        </tr>""".format(
            ifName=cgi.escape(p["ifName"]),
            ifAlias=cgi.escape(p["ifAlias"]),
            cls=status_class,
            status=p["ifOperStatus"],
            speed=format_speed(p["ifSpeed"]),
            in_rate=format_rate(p["ifInOctets_rate"]),
            out_rate=format_rate(p["ifOutOctets_rate"])
        )

    # Realtime port monitoring link with interval parameter
    interval = request.args.get('interval', '1')

    content = """
    <div class="row">
        <div class="col-sm-12">
            <h3>{hostname}</h3>
            <div class="panel panel-default">
                <div class="panel-heading">Device Information</div>
                <div class="panel-body">
                    <dl class="dl-horizontal">
                        <dt>Hostname</dt><dd>{hostname}</dd>
                        <dt>sysName</dt><dd>{sysName}</dd>
                        <dt>OS</dt><dd>{os}</dd>
                        <dt>Hardware</dt><dd>{hardware}</dd>
                        <dt>Location</dt><dd>{location}</dd>
                        <dt>Uptime</dt><dd>{uptime}</dd>
                    </dl>
                </div>
            </div>
            <h4>Ports</h4>
            <table class="table table-condensed table-hover table-striped">
                <thead><tr><th>Port</th><th>Description</th><th>Status</th><th>Speed</th><th>Traffic In</th><th>Traffic Out</th></tr></thead>
                <tbody>{port_rows}</tbody>
            </table>
            <h4>Realtime Traffic</h4>
            <div class="panel panel-default">
                <div class="panel-body">
                    <form method="get" class="form-inline">
                        <input type="hidden" name="interval" value="{interval}">
                        <label>Poll interval (seconds):</label>
                        <input type="text" class="form-control" name="interval" value="{interval}" style="width:80px">
                        <button type="submit" class="btn btn-primary btn-sm">Update</button>
                    </form>
                </div>
            </div>
        </div>
    </div>""".format(
        hostname=cgi.escape(device["hostname"]),
        sysName=cgi.escape(device["sysName"]),
        os=cgi.escape(device["os"]),
        hardware=cgi.escape(device["hardware"]),
        location=cgi.escape(device["location"]),
        uptime=format_uptime(device["uptime"]),
        port_rows=port_rows,
        interval=cgi.escape(interval)
    )
    return get_page_wrapper(device["hostname"], content)


# ===== OUTAGES PAGE =====
# Vulnerable: 'from' and 'to' parameters are rendered without htmlspecialchars
# This mirrors includes/html/pages/outages.inc.php from LibreNMS
@app.route('/outages')
def outages():
    var_from = request.args.get('from', '')
    var_to = request.args.get('to', '')

    outage_rows = ""
    for o in OUTAGE_DATA:
        up_again = o["up_again"] if o["up_again"] else '<span class="label label-danger">Ongoing</span>'
        outage_rows += """<tr>
            <td><a href="/device/{device_id}">{hostname}</a></td>
            <td>{going_down}</td>
            <td>{up_again}</td>
            <td>{duration}</td>
        </tr>""".format(
            device_id=o["device_id"],
            hostname=cgi.escape(o["hostname"]),
            going_down=cgi.escape(o["going_down"]),
            up_again=up_again,
            duration=cgi.escape(o["duration"])
        )

    # VULNERABLE: var_from and var_to are directly embedded in input value attributes
    # without htmlspecialchars() - mirrors LibreNMS outages.inc.php vulnerability
    content = """
    <div class="row">
        <div class="col-sm-12">
            <h3>Outages</h3>
            <div class="panel panel-default">
                <div class="panel-heading">Filter</div>
                <div class="panel-body">
                    <form method="get" class="form-inline" action="/outages">
                        <div class="form-group">
                            <label for="from">From:</label>
                            <input type="text" class="form-control" id="dtpickerfrom" name="from" value="{from_val}">
                        </div>
                        <div class="form-group" style="margin-left:10px">
                            <label for="to">To:</label>
                            <input type="text" class="form-control" id="dtpickerto" name="to" value="{to_val}">
                        </div>
                        <button type="submit" class="btn btn-primary btn-sm" style="margin-left:10px">Filter</button>
                    </form>
                </div>
            </div>
            <table class="table table-condensed table-hover table-striped">
                <thead><tr><th>Device</th><th>Going Down</th><th>Up Again</th><th>Duration</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>""".format(
        from_val=var_from,
        to_val=var_to,
        rows=outage_rows
    )

    page_html = get_page_wrapper("Outages", content)

    # Server-side XSS check via headless browser (simulates admin viewing the page)
    xss_result = check_xss_page(page_html)
    if xss_result == 'XSS':
        # Inject flag into the page response (simulates session theft callback)
        content += '<div class="alert alert-info" style="margin-top:15px"><strong>Session Data:</strong> ' + flag_data + '</div>'
        page_html = get_page_wrapper("Outages", content)

    return page_html


# ===== SYSLOG PAGE =====
# Vulnerable: 'from' and 'to' parameters are rendered without htmlspecialchars
# This mirrors includes/html/pages/syslog.inc.php
@app.route('/syslog')
def syslog():
    var_from = request.args.get('from', '')
    var_to = request.args.get('to', '')
    var_device = request.args.get('device', '')

    syslog_rows = ""
    for s in SYSLOG_DATA:
        severity_class = {"alert": "danger", "warning": "warning", "notice": "info", "info": "default"}.get(s["severity"], "default")
        syslog_rows += """<tr>
            <td>{timestamp}</td>
            <td>{device}</td>
            <td>{facility}</td>
            <td><span class="label label-{cls}">{severity}</span></td>
            <td>{message}</td>
        </tr>""".format(
            timestamp=cgi.escape(s["timestamp"]),
            device=cgi.escape(s["device"]),
            facility=cgi.escape(s["facility"]),
            cls=severity_class,
            severity=cgi.escape(s["severity"]),
            message=cgi.escape(s["message"])
        )

    # VULNERABLE: var_from and var_to are directly embedded without sanitization
    content = """
    <div class="row">
        <div class="col-sm-12">
            <h3>Syslog</h3>
            <div class="panel panel-default">
                <div class="panel-heading">Filter</div>
                <div class="panel-body">
                    <form method="get" class="form-inline" action="/syslog">
                        <div class="form-group">
                            <label for="device">Device:</label>
                            <input type="text" class="form-control" name="device" value="{device_val}">
                        </div>
                        <div class="form-group" style="margin-left:10px">
                            <label for="from">From:</label>
                            <input type="text" class="form-control" id="dtpickerfrom" name="from" value="{from_val}">
                        </div>
                        <div class="form-group" style="margin-left:10px">
                            <label for="to">To:</label>
                            <input type="text" class="form-control" id="dtpickerto" name="to" value="{to_val}">
                        </div>
                        <button type="submit" class="btn btn-primary btn-sm" style="margin-left:10px">Filter</button>
                    </form>
                </div>
            </div>
            <table class="table table-condensed table-hover table-striped">
                <thead><tr><th>Timestamp</th><th>Device</th><th>Facility</th><th>Severity</th><th>Message</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>""".format(
        device_val=cgi.escape(var_device),
        from_val=var_from,
        to_val=var_to,
        rows=syslog_rows
    )

    page_html = get_page_wrapper("Syslog", content)

    xss_result = check_xss_page(page_html)
    if xss_result == 'XSS':
        content += '<div class="alert alert-info" style="margin-top:15px"><strong>Session Data:</strong> ' + flag_data + '</div>'
        page_html = get_page_wrapper("Syslog", content)

    return page_html


# ===== PORTS LIST PAGE =====
# Vulnerable: JS context injection - device_id, hostname, state parameters
# Mirrors includes/html/pages/ports/list.inc.php
@app.route('/ports/list')
def ports_list():
    var_device_id = request.args.get('device_id', '')
    var_hostname = request.args.get('hostname', '')
    var_state = request.args.get('state', 'up')

    port_rows = ""
    for p in PORT_DATA:
        device = None
        for d in DEVICES:
            if d["device_id"] == p["device_id"]:
                device = d
                break
        if not device:
            continue

        if var_state and var_state in ('up', 'down'):
            if p["ifOperStatus"] != var_state:
                continue

        status_class = "success" if p["ifOperStatus"] == "up" else "danger"
        port_rows += """<tr>
            <td><a href="/device/{device_id}">{hostname}</a></td>
            <td>{ifName}</td>
            <td>{ifAlias}</td>
            <td><span class="label label-{cls}">{status}</span></td>
            <td>{speed}</td>
            <td>{in_rate}</td>
            <td>{out_rate}</td>
        </tr>""".format(
            device_id=device["device_id"],
            hostname=cgi.escape(device["hostname"]),
            ifName=cgi.escape(p["ifName"]),
            ifAlias=cgi.escape(p["ifAlias"]),
            cls=status_class,
            status=p["ifOperStatus"],
            speed=format_speed(p["ifSpeed"]),
            in_rate=format_rate(p["ifInOctets_rate"]),
            out_rate=format_rate(p["ifOutOctets_rate"])
        )

    # VULNERABLE: device_id, hostname, state are embedded in JavaScript context
    # without proper escaping - mirrors LibreNMS ports/list.inc.php
    content = """
    <div class="row">
        <div class="col-sm-12">
            <h3>Port List</h3>
            <div class="panel panel-default">
                <div class="panel-heading">Filter</div>
                <div class="panel-body">
                    <form method="get" class="form-inline" action="/ports/list">
                        <div class="form-group">
                            <label>Device ID:</label>
                            <input type="text" class="form-control" name="device_id" value="{device_id_val}" style="width:100px">
                        </div>
                        <div class="form-group" style="margin-left:10px">
                            <label>Hostname:</label>
                            <input type="text" class="form-control" name="hostname" value="{hostname_val}">
                        </div>
                        <div class="form-group" style="margin-left:10px">
                            <label>State:</label>
                            <select name="state" class="form-control">
                                <option value="up">Up</option>
                                <option value="down">Down</option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-primary btn-sm" style="margin-left:10px">Filter</button>
                    </form>
                </div>
            </div>
            <table class="table table-condensed table-hover table-striped">
                <thead><tr><th>Device</th><th>Port</th><th>Description</th><th>Status</th><th>Speed</th><th>Traffic In</th><th>Traffic Out</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
    <script type="text/javascript">
        var device_id = '{device_id_js}';
        var hostname = '{hostname_js}';
        var state = '{state_js}';
        $(document).ready(function() {{
            if (device_id) {{
                console.log('Filtering ports for device: ' + device_id);
            }}
        }});
    </script>""".format(
        device_id_val=cgi.escape(var_device_id),
        hostname_val=cgi.escape(var_hostname),
        rows=port_rows,
        device_id_js=var_device_id,
        hostname_js=var_hostname,
        state_js=var_state
    )

    page_html = get_page_wrapper("Port List", content)

    xss_result = check_xss_page(page_html)
    if xss_result == 'XSS':
        content += '<div class="alert alert-info" style="margin-top:15px"><strong>Session Data:</strong> ' + flag_data + '</div>'
        page_html = get_page_wrapper("Port List", content)

    return page_html


# ===== NTP APP PAGE =====
# Vulnerable: JS context injection - view, graph parameters
# Mirrors includes/html/pages/apps/ntp.inc.php
@app.route('/apps/ntp')
def apps_ntp():
    var_view = request.args.get('view', 'overview')
    var_graph = request.args.get('graph', 'offset')

    ntp_rows = ""
    for n in NTP_DATA:
        device = None
        for d in DEVICES:
            if d["device_id"] == n["device_id"]:
                device = d
                break
        hostname = device["hostname"] if device else "unknown"
        ntp_rows += """<tr>
            <td><a href="/device/{device_id}">{hostname}</a></td>
            <td>{peer}</td>
            <td>{stratum}</td>
            <td>{offset}</td>
            <td>{delay}</td>
            <td>{jitter}</td>
        </tr>""".format(
            device_id=n["device_id"],
            hostname=cgi.escape(hostname),
            peer=cgi.escape(n["peer"]),
            stratum=n["stratum"],
            offset=n["offset"],
            delay=n["delay"],
            jitter=n["jitter"]
        )

    # VULNERABLE: view and graph are embedded in JS without escaping
    content = """
    <div class="row">
        <div class="col-sm-12">
            <h3>NTP Application</h3>
            <ul class="nav nav-tabs">
                <li class="{overview_active}"><a href="/apps/ntp?view=overview&graph={graph_val}">Overview</a></li>
                <li class="{graphs_active}"><a href="/apps/ntp?view=graphs&graph={graph_val}">Graphs</a></li>
            </ul>
            <div style="margin-top:15px">
                <div class="btn-group" role="group">
                    <a href="/apps/ntp?view={view_val}&graph=offset" class="btn btn-default btn-sm">Offset</a>
                    <a href="/apps/ntp?view={view_val}&graph=delay" class="btn btn-default btn-sm">Delay</a>
                    <a href="/apps/ntp?view={view_val}&graph=jitter" class="btn btn-default btn-sm">Jitter</a>
                </div>
            </div>
            <table class="table table-condensed table-hover table-striped" style="margin-top:15px">
                <thead><tr><th>Device</th><th>Peer</th><th>Stratum</th><th>Offset (ms)</th><th>Delay (ms)</th><th>Jitter (ms)</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
    <script type="text/javascript">
        var view = '{view_js}';
        var graph = '{graph_js}';
        $(document).ready(function() {{
            console.log('NTP view: ' + view + ', graph: ' + graph);
        }});
    </script>""".format(
        overview_active="active" if var_view == "overview" else "",
        graphs_active="active" if var_view == "graphs" else "",
        graph_val=cgi.escape(var_graph),
        view_val=cgi.escape(var_view),
        rows=ntp_rows,
        view_js=var_view,
        graph_js=var_graph
    )

    page_html = get_page_wrapper("NTP", content)

    xss_result = check_xss_page(page_html)
    if xss_result == 'XSS':
        content += '<div class="alert alert-info" style="margin-top:15px"><strong>Session Data:</strong> ' + flag_data + '</div>'
        page_html = get_page_wrapper("NTP", content)

    return page_html


# ===== HEALTH PAGES =====
# Vulnerable: JS context injection - view, graph_type, unit, class parameters
# Mirrors includes/html/pages/health/*.inc.php
@app.route('/health/<health_type>')
def health(health_type):
    valid_types = {'mempool': 'Memory Pools', 'processor': 'Processors', 'storage': 'Storage'}
    if health_type not in valid_types:
        return get_page_wrapper("Not Found", "<h3>Page not found</h3>"), 404

    var_view = request.args.get('view', 'detail')
    var_graph_type = request.args.get('graph_type', 'usage')
    var_unit = request.args.get('unit', 'percent')
    var_class = request.args.get('class', '')

    content = """
    <div class="row">
        <div class="col-sm-12">
            <h3>{title}</h3>
            <ul class="nav nav-tabs">
                <li class="{detail_active}"><a href="/health/{htype}?view=detail&graph_type={graph_type}&unit={unit}">Detail</a></li>
                <li class="{graphs_active}"><a href="/health/{htype}?view=graphs&graph_type={graph_type}&unit={unit}">Graphs</a></li>
            </ul>
            <div class="panel panel-default" style="margin-top:15px">
                <div class="panel-body">
                    <p>Showing {title} health data for monitored devices.</p>
                    <table class="table table-condensed">
                        <thead><tr><th>Device</th><th>Type</th><th>Usage</th></tr></thead>
                        <tbody>
                            <tr><td>core-rtr-01</td><td>{htype}</td><td>42%</td></tr>
                            <tr><td>dist-sw-01</td><td>{htype}</td><td>67%</td></tr>
                            <tr><td>mon-srv-01</td><td>{htype}</td><td>23%</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    <script type="text/javascript">
        var view = '{view_js}';
        var graph_type = '{graph_type_js}';
        var unit = '{unit_js}';
        var health_class = '{class_js}';
        $(document).ready(function() {{
            console.log('Health type: {htype}, view: ' + view);
        }});
    </script>""".format(
        title=valid_types[health_type],
        htype=health_type,
        detail_active="active" if var_view == "detail" else "",
        graphs_active="active" if var_view == "graphs" else "",
        graph_type=cgi.escape(var_graph_type),
        unit=cgi.escape(var_unit),
        view_js=var_view,
        graph_type_js=var_graph_type,
        unit_js=var_unit,
        class_js=var_class
    )

    page_html = get_page_wrapper(valid_types[health_type], content)

    xss_result = check_xss_page(page_html)
    if xss_result == 'XSS':
        content += '<div class="alert alert-info" style="margin-top:15px"><strong>Session Data:</strong> ' + flag_data + '</div>'
        page_html = get_page_wrapper(valid_types[health_type], content)

    return page_html


# ===== FDB SEARCH PAGE =====
# Vulnerable: JS context injection - device_id, searchby, searchPhrase
# Mirrors includes/html/pages/search/fdb.inc.php
@app.route('/search/fdb')
def search_fdb():
    var_device_id = request.args.get('device_id', '')
    var_searchby = request.args.get('searchby', 'mac')
    var_searchPhrase = request.args.get('searchPhrase', '')

    fdb_rows = ""
    for f in FDB_DATA:
        fdb_rows += """<tr>
            <td>{mac}</td>
            <td><a href="/device/{device_id}">{hostname}</a></td>
            <td>{ifName}</td>
            <td>{vlan_id}</td>
        </tr>""".format(
            mac=cgi.escape(f["mac_address"]),
            device_id=f["device_id"],
            hostname=cgi.escape(f["hostname"]),
            ifName=cgi.escape(f["ifName"]),
            vlan_id=f["vlan_id"]
        )

    # VULNERABLE: device_id, searchby, searchPhrase embedded in JS without escaping
    content = """
    <div class="row">
        <div class="col-sm-12">
            <h3>FDB Table Search</h3>
            <div class="panel panel-default">
                <div class="panel-heading">Search</div>
                <div class="panel-body">
                    <form method="get" class="form-inline" action="/search/fdb">
                        <div class="form-group">
                            <label>Device ID:</label>
                            <input type="text" class="form-control" name="device_id" value="{device_id_val}" style="width:100px">
                        </div>
                        <div class="form-group" style="margin-left:10px">
                            <label>Search By:</label>
                            <select name="searchby" class="form-control">
                                <option value="mac">MAC Address</option>
                                <option value="port">Port</option>
                                <option value="vlan">VLAN</option>
                            </select>
                        </div>
                        <div class="form-group" style="margin-left:10px">
                            <label>Search:</label>
                            <input type="text" class="form-control" name="searchPhrase" value="{searchPhrase_val}">
                        </div>
                        <button type="submit" class="btn btn-primary btn-sm" style="margin-left:10px">Search</button>
                    </form>
                </div>
            </div>
            <table class="table table-condensed table-hover table-striped">
                <thead><tr><th>MAC Address</th><th>Device</th><th>Port</th><th>VLAN</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
    <script type="text/javascript">
        var device_id = '{device_id_js}';
        var searchby = '{searchby_js}';
        var searchPhrase = '{searchPhrase_js}';
        $(document).ready(function() {{
            if (searchPhrase) {{
                console.log('Searching FDB for: ' + searchPhrase);
            }}
        }});
    </script>""".format(
        device_id_val=cgi.escape(var_device_id),
        searchPhrase_val=cgi.escape(var_searchPhrase),
        rows=fdb_rows,
        device_id_js=var_device_id,
        searchby_js=var_searchby,
        searchPhrase_js=var_searchPhrase
    )

    page_html = get_page_wrapper("FDB Search", content)

    xss_result = check_xss_page(page_html)
    if xss_result == 'XSS':
        content += '<div class="alert alert-info" style="margin-top:15px"><strong>Session Data:</strong> ' + flag_data + '</div>'
        page_html = get_page_wrapper("FDB Search", content)

    return page_html


@app.errorhandler(404)
def page_not_found(e):
    return get_page_wrapper("Not Found", "<h3>Page not found</h3>"), 404


@app.errorhandler(500)
def internal_error(e):
    return get_page_wrapper("Error", "<h3>An error occurred</h3>"), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
