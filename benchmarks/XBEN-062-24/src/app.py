# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, url_for
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import time

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

stored_flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# Sample data for the monitoring dashboard
SAMPLE_DEVICES = [
    {"id": 1, "hostname": "core-rtr-01.dc1.internal", "sysname": "core-rtr-01", "os": "ios", "status": 1, "uptime": 8640000},
    {"id": 2, "hostname": "dist-sw-02.dc1.internal", "sysname": "dist-sw-02", "os": "nxos", "status": 1, "uptime": 4320000},
    {"id": 3, "hostname": "edge-fw-01.dc2.internal", "sysname": "edge-fw-01", "os": "asa", "status": 0, "uptime": 0},
    {"id": 4, "hostname": "access-sw-14.dc1.internal", "sysname": "access-sw-14", "os": "ios", "status": 1, "uptime": 2160000},
    {"id": 5, "hostname": "mon-srv-01.dc1.internal", "sysname": "mon-srv-01", "os": "linux", "status": 1, "uptime": 1728000},
]

SAMPLE_INCIDENTS = [
    {"id": 1, "device_id": 3, "hostname": "edge-fw-01.dc2.internal", "started": "2024-01-15 08:23:11", "ended": "2024-01-15 09:45:33", "duration": "1h 22m"},
    {"id": 2, "device_id": 1, "hostname": "core-rtr-01.dc1.internal", "started": "2024-01-10 14:02:45", "ended": "2024-01-10 14:08:12", "duration": "5m 27s"},
    {"id": 3, "device_id": 2, "hostname": "dist-sw-02.dc1.internal", "started": "2024-01-05 22:15:00", "ended": "2024-01-05 22:17:30", "duration": "2m 30s"},
    {"id": 4, "device_id": 3, "hostname": "edge-fw-01.dc2.internal", "started": "2024-01-02 03:10:22", "ended": "2024-01-02 11:55:01", "duration": "8h 44m"},
]

SAMPLE_EVENTS = [
    {"id": 1, "device_id": 1, "hostname": "core-rtr-01.dc1.internal", "program": "bgpd", "priority": "warning", "msg": "BGP peer 10.0.0.2 state changed to Idle", "timestamp": "2024-01-15 12:30:01"},
    {"id": 2, "device_id": 5, "hostname": "mon-srv-01.dc1.internal", "program": "snmpd", "priority": "info", "msg": "Connection from UDP: [10.0.1.5]:44231", "timestamp": "2024-01-15 12:28:45"},
    {"id": 3, "device_id": 2, "hostname": "dist-sw-02.dc1.internal", "program": "stp", "priority": "notice", "msg": "Topology change on Vlan100", "timestamp": "2024-01-15 12:25:12"},
    {"id": 4, "device_id": 4, "hostname": "access-sw-14.dc1.internal", "program": "dot1x", "priority": "info", "msg": "Authentication success on Gi0/12", "timestamp": "2024-01-15 12:22:00"},
    {"id": 5, "device_id": 3, "hostname": "edge-fw-01.dc2.internal", "program": "kernel", "priority": "error", "msg": "Interface GigabitEthernet0/1 link down", "timestamp": "2024-01-15 08:23:11"},
]

SAMPLE_NTP_PEERS = [
    {"id": 1, "device_id": 1, "hostname": "core-rtr-01.dc1.internal", "peer": "0.pool.ntp.org", "stratum": 2, "offset": 0.234, "delay": 12.5, "status": "ok"},
    {"id": 2, "device_id": 2, "hostname": "dist-sw-02.dc1.internal", "peer": "1.pool.ntp.org", "stratum": 2, "offset": -0.112, "delay": 8.3, "status": "ok"},
    {"id": 3, "device_id": 4, "hostname": "access-sw-14.dc1.internal", "peer": "10.0.0.1", "stratum": 3, "offset": 1.445, "delay": 2.1, "status": "ok"},
    {"id": 4, "device_id": 3, "hostname": "edge-fw-01.dc2.internal", "peer": "ntp.internal.lan", "stratum": 0, "offset": 0.0, "delay": 0.0, "status": "error"},
]

SAMPLE_PORTS = [
    {"id": 1, "device_id": 1, "hostname": "core-rtr-01.dc1.internal", "ifDescr": "GigabitEthernet0/0", "ifAlias": "Uplink to ISP", "ifSpeed": 1000000000, "ifOperStatus": "up", "ifInOctets_rate": 45000000, "ifOutOctets_rate": 32000000},
    {"id": 2, "device_id": 1, "hostname": "core-rtr-01.dc1.internal", "ifDescr": "GigabitEthernet0/1", "ifAlias": "Link to dist-sw-02", "ifSpeed": 1000000000, "ifOperStatus": "up", "ifInOctets_rate": 12000000, "ifOutOctets_rate": 8000000},
    {"id": 3, "device_id": 2, "hostname": "dist-sw-02.dc1.internal", "ifDescr": "Ethernet1/1", "ifAlias": "Uplink to core-rtr-01", "ifSpeed": 10000000000, "ifOperStatus": "up", "ifInOctets_rate": 8000000, "ifOutOctets_rate": 12000000},
    {"id": 4, "device_id": 3, "hostname": "edge-fw-01.dc2.internal", "ifDescr": "GigabitEthernet0/1", "ifAlias": "WAN Interface", "ifSpeed": 1000000000, "ifOperStatus": "down", "ifInOctets_rate": 0, "ifOutOctets_rate": 0},
    {"id": 5, "device_id": 4, "hostname": "access-sw-14.dc1.internal", "ifDescr": "GigabitEthernet0/12", "ifAlias": "User Port - Floor 3", "ifSpeed": 100000000, "ifOperStatus": "up", "ifInOctets_rate": 500000, "ifOutOctets_rate": 200000},
]

SAMPLE_HEALTH = [
    {"id": 1, "device_id": 1, "hostname": "core-rtr-01.dc1.internal", "sensor": "CPU Usage", "current": 34, "unit": "%", "high_limit": 90, "status": "ok"},
    {"id": 2, "device_id": 1, "hostname": "core-rtr-01.dc1.internal", "sensor": "Memory Pool: Processor", "current": 67, "unit": "%", "high_limit": 95, "status": "ok"},
    {"id": 3, "device_id": 2, "hostname": "dist-sw-02.dc1.internal", "sensor": "Temperature: Chassis", "current": 42, "unit": "C", "high_limit": 65, "status": "ok"},
    {"id": 4, "device_id": 5, "hostname": "mon-srv-01.dc1.internal", "sensor": "Disk /: Usage", "current": 78, "unit": "%", "high_limit": 90, "status": "warning"},
    {"id": 5, "device_id": 3, "hostname": "edge-fw-01.dc2.internal", "sensor": "CPU Usage", "current": 0, "unit": "%", "high_limit": 90, "status": "unknown"},
]


def format_uptime(seconds):
    if seconds == 0:
        return "Down"
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    return "%dd %dh" % (days, hours)


def format_speed(bps):
    if bps >= 1000000000:
        return "%.1f Gbps" % (bps / 1000000000.0)
    elif bps >= 1000000:
        return "%.1f Mbps" % (bps / 1000000.0)
    elif bps >= 1000:
        return "%.1f Kbps" % (bps / 1000.0)
    return "%d bps" % bps


def verify_xss_execution(html_content):
    """Validate page content rendering."""
    proc = subprocess.Popen(["timeout", "8", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
    result = ""
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        pass
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass
    return result


@app.route('/')
def dashboard():
    device_count = len(SAMPLE_DEVICES)
    up_count = len([d for d in SAMPLE_DEVICES if d['status'] == 1])
    down_count = device_count - up_count
    alert_count = len([e for e in SAMPLE_EVENTS if e['priority'] in ('error', 'warning')])

    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>NetWatch NMS</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/css/bootstrap.min.css">
    <style>
        body {{ background: #f5f5f5; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }}
        .navbar {{ background: #2c3e50; border: none; margin-bottom: 0; }}
        .navbar-brand {{ color: #ecf0f1 !important; font-weight: bold; }}
        .navbar-nav > li > a {{ color: #bdc3c7 !important; }}
        .navbar-nav > li > a:hover {{ color: #ecf0f1 !important; background: #34495e !important; }}
        .stat-box {{ background: #fff; border-radius: 4px; padding: 20px; margin: 10px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.12); text-align: center; }}
        .stat-box h2 {{ margin: 0; font-size: 36px; }}
        .stat-box p {{ margin: 5px 0 0; color: #7f8c8d; }}
        .stat-up h2 {{ color: #27ae60; }}
        .stat-down h2 {{ color: #e74c3c; }}
        .stat-alert h2 {{ color: #f39c12; }}
        .stat-total h2 {{ color: #2980b9; }}
        .panel-condensed {{ margin-top: 15px; }}
        .panel-heading strong {{ font-size: 14px; }}
        .content-wrapper {{ padding: 20px; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="/">NetWatch NMS</a>
            </div>
            <ul class="nav navbar-nav">
                <li><a href="/">Overview</a></li>
                <li><a href="/inventory">Devices</a></li>
                <li><a href="/interfaces">Interfaces</a></li>
                <li><a href="/incidents">Incidents</a></li>
                <li><a href="/eventlog">Event Log</a></li>
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown">Health <span class="caret"></span></a>
                    <ul class="dropdown-menu">
                        <li><a href="/health/sensors">Sensors</a></li>
                        <li><a href="/health/mempool">Memory</a></li>
                    </ul>
                </li>
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown">Apps <span class="caret"></span></a>
                    <ul class="dropdown-menu">
                        <li><a href="/apps/ntp">NTP</a></li>
                    </ul>
                </li>
            </ul>
        </div>
    </nav>
    <div class="content-wrapper">
        <div class="row">
            <div class="col-md-3"><div class="stat-box stat-total"><h2>{total}</h2><p>Total Devices</p></div></div>
            <div class="col-md-3"><div class="stat-box stat-up"><h2>{up}</h2><p>Devices Up</p></div></div>
            <div class="col-md-3"><div class="stat-box stat-down"><h2>{down}</h2><p>Devices Down</p></div></div>
            <div class="col-md-3"><div class="stat-box stat-alert"><h2>{alerts}</h2><p>Active Alerts</p></div></div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <div class="panel panel-default panel-condensed">
                    <div class="panel-heading"><strong>Recent Incidents</strong></div>
                    <table class="table table-condensed table-striped table-hover">
                        <thead><tr><th>Device</th><th>Started</th><th>Duration</th></tr></thead>
                        <tbody>''' + ''.join(['<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (i['hostname'], i['started'], i['duration']) for i in SAMPLE_INCIDENTS[:3]]) + '''</tbody>
                    </table>
                </div>
            </div>
            <div class="col-md-6">
                <div class="panel panel-default panel-condensed">
                    <div class="panel-heading"><strong>Recent Events</strong></div>
                    <table class="table table-condensed table-striped table-hover">
                        <thead><tr><th>Device</th><th>Message</th><th>Time</th></tr></thead>
                        <tbody>''' + ''.join(['<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (cgi.escape(e['hostname']), cgi.escape(e['msg']), e['timestamp']) for e in SAMPLE_EVENTS[:3]]) + '''</tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/js/bootstrap.min.js"></script>
</body>
</html>'''.format(total=device_count, up=up_count, down=down_count, alerts=alert_count)


@app.route('/inventory')
def device_list():
    rows = ""
    for d in SAMPLE_DEVICES:
        status_label = '<span class="label label-success">Up</span>' if d['status'] == 1 else '<span class="label label-danger">Down</span>'
        rows += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            cgi.escape(d['hostname']), cgi.escape(d['os']), status_label,
            format_uptime(d['uptime']), cgi.escape(d['sysname'])
        )

    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>NetWatch NMS - Devices</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/css/bootstrap.min.css">
    <style>
        body { background: #f5f5f5; }
        .navbar { background: #2c3e50; border: none; margin-bottom: 0; }
        .navbar-brand { color: #ecf0f1 !important; font-weight: bold; }
        .navbar-nav > li > a { color: #bdc3c7 !important; }
        .navbar-nav > li > a:hover { color: #ecf0f1 !important; background: #34495e !important; }
        .content-wrapper { padding: 20px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header"><a class="navbar-brand" href="/">NetWatch NMS</a></div>
            <ul class="nav navbar-nav">
                <li><a href="/">Overview</a></li>
                <li class="active"><a href="/inventory">Devices</a></li>
                <li><a href="/interfaces">Interfaces</a></li>
                <li><a href="/incidents">Incidents</a></li>
                <li><a href="/eventlog">Event Log</a></li>
                <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Health <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/health/sensors">Sensors</a></li><li><a href="/health/mempool">Memory</a></li></ul></li>
                <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Apps <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/apps/ntp">NTP</a></li></ul></li>
            </ul>
        </div>
    </nav>
    <div class="content-wrapper">
        <div class="panel panel-default panel-condensed">
            <div class="panel-heading"><strong>Devices</strong></div>
            <table class="table table-condensed table-striped table-hover">
                <thead><tr><th>Hostname</th><th>OS</th><th>Status</th><th>Uptime</th><th>SysName</th></tr></thead>
                <tbody>''' + rows + '''</tbody>
            </table>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/js/bootstrap.min.js"></script>
</body>
</html>'''


@app.route('/incidents')
def incidents_page():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    device_filter = request.args.get('device', '')

    filtered = SAMPLE_INCIDENTS
    if device_filter:
        try:
            did = int(device_filter)
            filtered = [i for i in filtered if i['device_id'] == did]
        except ValueError:
            filtered = SAMPLE_INCIDENTS

    rows = ""
    for inc in filtered:
        rows += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            cgi.escape(str(inc['id'])), cgi.escape(inc['hostname']),
            cgi.escape(inc['started']), cgi.escape(inc['duration'])
        )

    device_options = '<option value="">All Devices</option>'
    for d in SAMPLE_DEVICES:
        selected = ' selected' if device_filter == str(d['id']) else ''
        device_options += '<option value="%s"%s>%s</option>' % (
            cgi.escape(str(d['id'])), selected, cgi.escape(d['hostname']))

    page_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>NetWatch NMS - Incidents</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/css/bootstrap.min.css">
    <style>
        body { background: #f5f5f5; }
        .navbar { background: #2c3e50; border: none; margin-bottom: 0; }
        .navbar-brand { color: #ecf0f1 !important; font-weight: bold; }
        .navbar-nav > li > a { color: #bdc3c7 !important; }
        .navbar-nav > li > a:hover { color: #ecf0f1 !important; background: #34495e !important; }
        .content-wrapper { padding: 20px; }
        .filter-bar { background: #fff; padding: 10px 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }
        .filter-bar .form-group { margin-right: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header"><a class="navbar-brand" href="/">NetWatch NMS</a></div>
            <ul class="nav navbar-nav">
                <li><a href="/">Overview</a></li>
                <li><a href="/inventory">Devices</a></li>
                <li><a href="/interfaces">Interfaces</a></li>
                <li class="active"><a href="/incidents">Incidents</a></li>
                <li><a href="/eventlog">Event Log</a></li>
                <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Health <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/health/sensors">Sensors</a></li><li><a href="/health/mempool">Memory</a></li></ul></li>
                <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Apps <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/apps/ntp">NTP</a></li></ul></li>
            </ul>
        </div>
    </nav>
    <div class="content-wrapper">
        <div class="panel panel-default panel-condensed">
            <div class="panel-heading"><strong>Incidents</strong></div>
            <div class="filter-bar">
                <form method="get" action="/incidents" class="form-inline" role="form">
                    <div class="form-group">
                        <select name="device" class="form-control input-sm">''' + device_options + '''</select>
                    </div>
                    <div class="form-group">
                        <input name="start" type="text" class="form-control input-sm" id="dtpickerfrom" maxlength="16" value="''' + start_date + '''" placeholder="From" data-date-format="YYYY-MM-DD HH:mm">
                    </div>
                    <div class="form-group">
                        <input name="end" type="text" class="form-control input-sm" id="dtpickerto" maxlength="16" value="''' + end_date + '''" placeholder="To" data-date-format="YYYY-MM-DD HH:mm">
                    </div>
                    <button type="submit" class="btn btn-default btn-sm">Filter</button>
                </form>
            </div>
            <table class="table table-condensed table-striped table-hover">
                <thead><tr><th>#</th><th>Device</th><th>Started</th><th>Duration</th></tr></thead>
                <tbody>''' + rows + '''</tbody>
            </table>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/js/bootstrap.min.js"></script>
</body>
</html>'''

    xss_result = verify_xss_execution(page_html)
    if xss_result == 'XSS':
        page_html = page_html.replace('</tbody>', '</tbody></table><div class="alert alert-info" style="margin:15px;">' + stored_flag + '</div><table style="display:none"><tbody>')

    return page_html


@app.route('/eventlog')
def eventlog_page():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    device_filter = request.args.get('device', '')
    program_filter = request.args.get('program', '')

    filtered = SAMPLE_EVENTS
    if device_filter:
        try:
            did = int(device_filter)
            filtered = [e for e in filtered if e['device_id'] == did]
        except ValueError:
            pass
    if program_filter:
        filtered = [e for e in filtered if e['program'] == program_filter]

    rows = ""
    for ev in filtered:
        prio_class = 'danger' if ev['priority'] == 'error' else ('warning' if ev['priority'] == 'warning' else 'default')
        rows += '<tr><td>%s</td><td>%s</td><td><span class="label label-%s">%s</span></td><td>%s</td><td>%s</td></tr>' % (
            cgi.escape(ev['hostname']), cgi.escape(ev['program']),
            prio_class, cgi.escape(ev['priority']),
            cgi.escape(ev['msg']), ev['timestamp']
        )

    device_options = '<option value="">All Devices</option>'
    for d in SAMPLE_DEVICES:
        selected = ' selected' if device_filter == str(d['id']) else ''
        device_options += '<option value="%s"%s>%s</option>' % (
            cgi.escape(str(d['id'])), selected, cgi.escape(d['hostname']))

    page_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>NetWatch NMS - Event Log</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/css/bootstrap.min.css">
    <style>
        body { background: #f5f5f5; }
        .navbar { background: #2c3e50; border: none; margin-bottom: 0; }
        .navbar-brand { color: #ecf0f1 !important; font-weight: bold; }
        .navbar-nav > li > a { color: #bdc3c7 !important; }
        .navbar-nav > li > a:hover { color: #ecf0f1 !important; background: #34495e !important; }
        .content-wrapper { padding: 20px; }
        .filter-bar { background: #fff; padding: 10px 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }
    </style>
</head>
<body>
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header"><a class="navbar-brand" href="/">NetWatch NMS</a></div>
            <ul class="nav navbar-nav">
                <li><a href="/">Overview</a></li>
                <li><a href="/inventory">Devices</a></li>
                <li><a href="/interfaces">Interfaces</a></li>
                <li><a href="/incidents">Incidents</a></li>
                <li class="active"><a href="/eventlog">Event Log</a></li>
                <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Health <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/health/sensors">Sensors</a></li><li><a href="/health/mempool">Memory</a></li></ul></li>
                <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Apps <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/apps/ntp">NTP</a></li></ul></li>
            </ul>
        </div>
    </nav>
    <div class="content-wrapper">
        <div class="panel panel-default panel-condensed">
            <div class="panel-heading"><strong>Event Log</strong></div>
            <div class="filter-bar">
                <form method="get" action="/eventlog" class="form-inline" role="form">
                    <div class="form-group">
                        <select name="device" class="form-control input-sm">''' + device_options + '''</select>
                    </div>
                    <div class="form-group">
                        <input name="start" type="text" class="form-control input-sm" maxlength="16" value="''' + start_date + '''" placeholder="From" data-date-format="YYYY-MM-DD HH:mm">
                    </div>
                    <div class="form-group">
                        <input name="end" type="text" class="form-control input-sm" maxlength="16" value="''' + end_date + '''" placeholder="To" data-date-format="YYYY-MM-DD HH:mm">
                    </div>
                    <button type="submit" class="btn btn-default btn-sm">Filter</button>
                </form>
            </div>
            <table class="table table-condensed table-striped table-hover">
                <thead><tr><th>Device</th><th>Program</th><th>Priority</th><th>Message</th><th>Timestamp</th></tr></thead>
                <tbody>''' + rows + '''</tbody>
            </table>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/js/bootstrap.min.js"></script>
</body>
</html>'''

    xss_result = verify_xss_execution(page_html)
    if xss_result == 'XSS':
        page_html = page_html.replace('</tbody>', '</tbody></table><div class="alert alert-info" style="margin:15px;">' + stored_flag + '</div><table style="display:none"><tbody>')

    return page_html


@app.route('/interfaces')
def ports_list():
    device_filter = request.args.get('device_id', '')
    hostname_filter = request.args.get('hostname', '')
    state_filter = request.args.get('state', '')

    filtered = SAMPLE_PORTS
    if device_filter:
        try:
            did = int(device_filter)
            filtered = [p for p in filtered if p['device_id'] == did]
        except ValueError:
            pass
    if state_filter:
        filtered = [p for p in filtered if p['ifOperStatus'] == state_filter]

    rows = ""
    for p in filtered:
        status_label = '<span class="label label-success">up</span>' if p['ifOperStatus'] == 'up' else '<span class="label label-danger">down</span>'
        rows += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            cgi.escape(p['hostname']), cgi.escape(p['ifDescr']), cgi.escape(p['ifAlias']),
            status_label, format_speed(p['ifSpeed']),
            format_speed(p['ifInOctets_rate']), format_speed(p['ifOutOctets_rate'])
        )

    state_options = '<option value="">All States</option>'
    for s in ['up', 'down']:
        selected = ' selected' if state_filter == s else ''
        state_options += '<option value="%s"%s>%s</option>' % (s, selected, s)

    page_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>NetWatch NMS - Interfaces</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/css/bootstrap.min.css">
    <style>
        body { background: #f5f5f5; }
        .navbar { background: #2c3e50; border: none; margin-bottom: 0; }
        .navbar-brand { color: #ecf0f1 !important; font-weight: bold; }
        .navbar-nav > li > a { color: #bdc3c7 !important; }
        .navbar-nav > li > a:hover { color: #ecf0f1 !important; background: #34495e !important; }
        .content-wrapper { padding: 20px; }
        .filter-bar { background: #fff; padding: 10px 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }
    </style>
</head>
<body>
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header"><a class="navbar-brand" href="/">NetWatch NMS</a></div>
            <ul class="nav navbar-nav">
                <li><a href="/">Overview</a></li>
                <li><a href="/inventory">Devices</a></li>
                <li class="active"><a href="/interfaces">Interfaces</a></li>
                <li><a href="/incidents">Incidents</a></li>
                <li><a href="/eventlog">Event Log</a></li>
                <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Health <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/health/sensors">Sensors</a></li><li><a href="/health/mempool">Memory</a></li></ul></li>
                <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Apps <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/apps/ntp">NTP</a></li></ul></li>
            </ul>
        </div>
    </nav>
    <div class="content-wrapper">
        <div class="panel panel-default panel-condensed">
            <div class="panel-heading"><strong>Interfaces</strong></div>
            <div class="filter-bar">
                <form method="get" action="/interfaces" class="form-inline" role="form">
                    <div class="form-group">
                        <select name="state" class="form-control input-sm">''' + state_options + '''</select>
                    </div>
                    <button type="submit" class="btn btn-default btn-sm">Filter</button>
                </form>
            </div>
            <table class="table table-condensed table-striped table-hover">
                <thead><tr><th>Device</th><th>Port</th><th>Description</th><th>Status</th><th>Speed</th><th>Traffic In</th><th>Traffic Out</th></tr></thead>
                <tbody>''' + rows + '''</tbody>
            </table>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/js/bootstrap.min.js"></script>
    <script>
        var filters = {
            device_id: \'''' + device_filter + '''\',
            hostname: \'''' + hostname_filter + '''\',
            state: \'''' + state_filter + '''\'
        };
        $(document).ready(function() {
            if (filters.device_id) {
                $('tr').each(function() { /* client filter */ });
            }
        });
    </script>
</body>
</html>'''

    xss_result = verify_xss_execution(page_html)
    if xss_result == 'XSS':
        page_html = page_html.replace('</tbody>', '</tbody></table><div class="alert alert-info" style="margin:15px;">' + stored_flag + '</div><table style="display:none"><tbody>')

    return page_html


@app.route('/health/sensors')
def health_sensors():
    display_mode = request.args.get('view', 'list')
    graph_type = request.args.get('graph_type', 'none')
    metric_unit = request.args.get('unit', '')
    sensor_class = request.args.get('class', '')

    filtered = SAMPLE_HEALTH
    if metric_unit:
        filtered = [h for h in filtered if h['unit'] == metric_unit]

    rows = ""
    for h in filtered:
        status_label = '<span class="label label-success">ok</span>' if h['status'] == 'ok' else (
            '<span class="label label-warning">warning</span>' if h['status'] == 'warning' else '<span class="label label-default">unknown</span>')
        rows += '<tr><td>%s</td><td>%s</td><td>%s %s</td><td>%s %s</td><td>%s</td></tr>' % (
            cgi.escape(h['hostname']), cgi.escape(h['sensor']),
            str(h['current']), cgi.escape(h['unit']),
            str(h['high_limit']), cgi.escape(h['unit']),
            status_label
        )

    page_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>NetWatch NMS - Health Sensors</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/css/bootstrap.min.css">
    <style>
        body { background: #f5f5f5; }
        .navbar { background: #2c3e50; border: none; margin-bottom: 0; }
        .navbar-brand { color: #ecf0f1 !important; font-weight: bold; }
        .navbar-nav > li > a { color: #bdc3c7 !important; }
        .navbar-nav > li > a:hover { color: #ecf0f1 !important; background: #34495e !important; }
        .content-wrapper { padding: 20px; }
        .option-bar { background: #fff; padding: 8px 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }
        .option-bar a { margin: 0 5px; }
        .pagemenu-selected { font-weight: bold; text-decoration: underline; }
    </style>
</head>
<body>
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header"><a class="navbar-brand" href="/">NetWatch NMS</a></div>
            <ul class="nav navbar-nav">
                <li><a href="/">Overview</a></li>
                <li><a href="/inventory">Devices</a></li>
                <li><a href="/interfaces">Interfaces</a></li>
                <li><a href="/incidents">Incidents</a></li>
                <li><a href="/eventlog">Event Log</a></li>
                <li class="dropdown active"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Health <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/health/sensors">Sensors</a></li><li><a href="/health/mempool">Memory</a></li></ul></li>
                <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Apps <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/apps/ntp">NTP</a></li></ul></li>
            </ul>
        </div>
    </nav>
    <div class="content-wrapper">
        <div class="option-bar">
            <strong>Sensors</strong> &raquo;
            <a href="/health/sensors?view=list">List</a> |
            <a href="/health/sensors?view=graphs">Graphs</a>
            <span class="pull-right">
                Graph: <a href="/health/sensors?view=''' + cgi.escape(display_mode) + '''&graph_type=none">None</a> |
                <a href="/health/sensors?view=''' + cgi.escape(display_mode) + '''&graph_type=line">Line</a> |
                <a href="/health/sensors?view=''' + cgi.escape(display_mode) + '''&graph_type=bar">Bar</a>
            </span>
        </div>
        <div class="panel panel-default panel-condensed">
            <div class="panel-heading"><strong>Health - Sensors</strong></div>
            <table id="sensor-table" class="table table-condensed table-striped table-hover">
                <thead><tr><th>Device</th><th>Sensor</th><th>Current</th><th>Limit</th><th>Status</th></tr></thead>
                <tbody>''' + rows + '''</tbody>
            </table>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/js/bootstrap.min.js"></script>
    <script>
        $("#sensor-table").bootgrid({
            ajax: false,
            post: function() {
                return {
                    view: \'''' + display_mode + '''\',
                    graph_type: \'''' + graph_type + '''\',
                    unit: \'''' + metric_unit + '''\',
                    class: \'''' + sensor_class + '''\'
                };
            }
        });
    </script>
</body>
</html>'''

    xss_result = verify_xss_execution(page_html)
    if xss_result == 'XSS':
        page_html = page_html.replace('</tbody>', '</tbody></table><div class="alert alert-info" style="margin:15px;">' + stored_flag + '</div><table style="display:none"><tbody>')

    return page_html


@app.route('/health/mempool')
def health_mempool():
    display_mode = request.args.get('view', 'list')

    mem_data = [
        {"hostname": "core-rtr-01.dc1.internal", "descr": "Processor", "used": 268435456, "total": 536870912, "perc": 50},
        {"hostname": "dist-sw-02.dc1.internal", "descr": "System Memory", "used": 1073741824, "total": 2147483648, "perc": 50},
        {"hostname": "mon-srv-01.dc1.internal", "descr": "Physical Memory", "used": 6442450944, "total": 8589934592, "perc": 75},
    ]

    rows = ""
    for m in mem_data:
        bar_class = 'success' if m['perc'] < 70 else ('warning' if m['perc'] < 90 else 'danger')
        rows += '<tr><td>%s</td><td>%s</td><td>%s MB</td><td><div class="progress" style="margin:0"><div class="progress-bar progress-bar-%s" style="width:%d%%">%d%%</div></div></td></tr>' % (
            cgi.escape(m['hostname']), cgi.escape(m['descr']),
            str(m['used'] // 1048576), bar_class, m['perc'], m['perc']
        )

    page_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>NetWatch NMS - Memory Pools</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/css/bootstrap.min.css">
    <style>
        body { background: #f5f5f5; }
        .navbar { background: #2c3e50; border: none; margin-bottom: 0; }
        .navbar-brand { color: #ecf0f1 !important; font-weight: bold; }
        .navbar-nav > li > a { color: #bdc3c7 !important; }
        .navbar-nav > li > a:hover { color: #ecf0f1 !important; background: #34495e !important; }
        .content-wrapper { padding: 20px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header"><a class="navbar-brand" href="/">NetWatch NMS</a></div>
            <ul class="nav navbar-nav">
                <li><a href="/">Overview</a></li>
                <li><a href="/inventory">Devices</a></li>
                <li><a href="/interfaces">Interfaces</a></li>
                <li><a href="/incidents">Incidents</a></li>
                <li><a href="/eventlog">Event Log</a></li>
                <li class="dropdown active"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Health <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/health/sensors">Sensors</a></li><li><a href="/health/mempool">Memory</a></li></ul></li>
                <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Apps <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/apps/ntp">NTP</a></li></ul></li>
            </ul>
        </div>
    </nav>
    <div class="content-wrapper">
        <div class="panel panel-default panel-condensed">
            <div class="panel-heading"><strong>Health :: Memory</strong></div>
            <table id="mempool" class="table table-condensed table-striped table-hover">
                <thead><tr><th>Device</th><th>Memory</th><th>Used</th><th>Usage</th></tr></thead>
                <tbody>''' + rows + '''</tbody>
            </table>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/js/bootstrap.min.js"></script>
    <script>
        var grid = $("#mempool").bootgrid({
            ajax: false,
            post: function() {
                return {
                    view: \'''' + display_mode + '''\'
                };
            }
        });
    </script>
</body>
</html>'''

    xss_result = verify_xss_execution(page_html)
    if xss_result == 'XSS':
        page_html = page_html.replace('</tbody>', '</tbody></table><div class="alert alert-info" style="margin:15px;">' + stored_flag + '</div><table style="display:none"><tbody>')

    return page_html


@app.route('/apps/ntp')
def ntp_peers():
    display_mode = request.args.get('view', 'all')
    graph_mode = request.args.get('graph', 'none')

    filtered = SAMPLE_NTP_PEERS
    if display_mode == 'error':
        filtered = [n for n in filtered if n['status'] == 'error']

    rows = ""
    for n in filtered:
        status_label = '<span class="label label-success">ok</span>' if n['status'] == 'ok' else '<span class="label label-danger">error</span>'
        rows += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%.3f</td><td>%.1f</td><td>%s</td></tr>' % (
            cgi.escape(n['hostname']), cgi.escape(n['peer']),
            str(n['stratum']), n['offset'], n['delay'], status_label
        )

    page_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>NetWatch NMS - NTP Peers</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/css/bootstrap.min.css">
    <style>
        body { background: #f5f5f5; }
        .navbar { background: #2c3e50; border: none; margin-bottom: 0; }
        .navbar-brand { color: #ecf0f1 !important; font-weight: bold; }
        .navbar-nav > li > a { color: #bdc3c7 !important; }
        .navbar-nav > li > a:hover { color: #ecf0f1 !important; background: #34495e !important; }
        .content-wrapper { padding: 20px; }
        .option-bar { background: #fff; padding: 8px 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }
        .pagemenu-selected { font-weight: bold; text-decoration: underline; }
    </style>
</head>
<body>
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header"><a class="navbar-brand" href="/">NetWatch NMS</a></div>
            <ul class="nav navbar-nav">
                <li><a href="/">Overview</a></li>
                <li><a href="/inventory">Devices</a></li>
                <li><a href="/interfaces">Interfaces</a></li>
                <li><a href="/incidents">Incidents</a></li>
                <li><a href="/eventlog">Event Log</a></li>
                <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Health <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/health/sensors">Sensors</a></li><li><a href="/health/mempool">Memory</a></li></ul></li>
                <li class="dropdown active"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Apps <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/apps/ntp">NTP</a></li></ul></li>
            </ul>
        </div>
    </nav>
    <div class="content-wrapper">
        <div class="option-bar">
            <strong>NTP Peers</strong> &raquo;
            <a href="/apps/ntp?view=all"''' + (' class="pagemenu-selected"' if display_mode == 'all' else '') + '''>All</a> |
            <a href="/apps/ntp?view=error"''' + (' class="pagemenu-selected"' if display_mode == 'error' else '') + '''>Error</a>
            <span class="pull-right">
                <a href="/apps/ntp?view=''' + cgi.escape(display_mode) + '''&graph=none">No Graphs</a> |
                <a href="/apps/ntp?view=''' + cgi.escape(display_mode) + '''&graph=stratum">Stratum</a> |
                <a href="/apps/ntp?view=''' + cgi.escape(display_mode) + '''&graph=offset">Offset</a> |
                <a href="/apps/ntp?view=''' + cgi.escape(display_mode) + '''&graph=delay">Delay</a>
            </span>
        </div>
        <div class="panel panel-default panel-condensed">
            <div class="panel-heading"><strong>NTP Peers</strong></div>
            <table id="ntp-table" class="table table-condensed table-striped table-hover">
                <thead><tr><th>Device</th><th>Peer</th><th>Stratum</th><th>Offset</th><th>Delay</th><th>Status</th></tr></thead>
                <tbody>''' + rows + '''</tbody>
            </table>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/js/bootstrap.min.js"></script>
    <script>
        $("#ntp-table").bootgrid({
            ajax: false,
            post: function() {
                return {
                    id: "app_ntp",
                    view: \'''' + display_mode + '''\',
                    graph: \'''' + graph_mode + '''\'
                };
            },
        });
    </script>
</body>
</html>'''

    xss_result = verify_xss_execution(page_html)
    if xss_result == 'XSS':
        page_html = page_html.replace('</tbody>', '</tbody></table><div class="alert alert-info" style="margin:15px;">' + stored_flag + '</div><table style="display:none"><tbody>')

    return page_html


@app.errorhandler(404)
def not_found(e):
    return '''<!DOCTYPE html>
<html><head><title>404 - Not Found</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/3.4.1/css/bootstrap.min.css">
<style>body{background:#f5f5f5;text-align:center;padding-top:80px;}.navbar{background:#2c3e50;border:none;}.navbar-brand{color:#ecf0f1!important;font-weight:bold;}</style>
</head><body>
<nav class="navbar navbar-default"><div class="container-fluid"><div class="navbar-header"><a class="navbar-brand" href="/">NetWatch NMS</a></div></div></nav>
<h1>404</h1><p>The requested page was not found.</p><a href="/">Return to Dashboard</a>
</body></html>''', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
