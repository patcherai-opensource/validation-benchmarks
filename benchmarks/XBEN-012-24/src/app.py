# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, url_for, jsonify
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

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24).encode('hex')

# Read flag from file (planted at build time)
_flag_data = open('secret.txt').read().strip()

# Simulated device data
DEVICES = [
    {"device_id": 1, "hostname": "core-rtr-01.example.net", "sysName": "core-rtr-01", "os": "ios", "status": 1, "uptime": 8640000, "location": "DC-East-Rack12"},
    {"device_id": 2, "hostname": "sw-dist-02.example.net", "sysName": "sw-dist-02", "os": "nxos", "status": 1, "uptime": 4320000, "location": "DC-East-Rack15"},
    {"device_id": 3, "hostname": "fw-edge-01.example.net", "sysName": "fw-edge-01", "os": "asa", "status": 0, "uptime": 0, "location": "DC-West-Rack03"},
    {"device_id": 4, "hostname": "ap-floor3.example.net", "sysName": "ap-floor3", "os": "airos", "status": 1, "uptime": 2160000, "location": "Building-A-Floor3"},
    {"device_id": 5, "hostname": "srv-monitor.example.net", "sysName": "srv-monitor", "os": "linux", "status": 1, "uptime": 7776000, "location": "DC-East-Rack08"},
]

OUTAGES = [
    {"id": 1, "device_id": 3, "hostname": "fw-edge-01.example.net", "going_down": "2024-01-15 03:22:11", "up_again": None, "duration": "ongoing"},
    {"id": 2, "device_id": 2, "hostname": "sw-dist-02.example.net", "going_down": "2024-01-14 18:05:33", "up_again": "2024-01-14 18:47:12", "duration": "41m 39s"},
    {"id": 3, "device_id": 1, "hostname": "core-rtr-01.example.net", "going_down": "2024-01-10 22:15:00", "up_again": "2024-01-10 22:16:45", "duration": "1m 45s"},
]

SYSLOG_ENTRIES = [
    {"id": 1, "device_id": 1, "hostname": "core-rtr-01.example.net", "program": "BGP", "priority": "warning", "msg": "Neighbor 10.0.0.2 Down - Hold timer expired", "timestamp": "2024-01-15 04:12:33"},
    {"id": 2, "device_id": 3, "hostname": "fw-edge-01.example.net", "program": "ASA", "priority": "critical", "msg": "Failover cable communication failure", "timestamp": "2024-01-15 03:22:10"},
    {"id": 3, "device_id": 5, "hostname": "srv-monitor.example.net", "program": "CRON", "priority": "info", "msg": "CMD (/usr/lib/librenms/poller-wrapper.py 16)", "timestamp": "2024-01-15 04:05:01"},
    {"id": 4, "device_id": 2, "hostname": "sw-dist-02.example.net", "program": "STP", "priority": "notice", "msg": "Topology change on port Gi1/0/24", "timestamp": "2024-01-15 03:58:44"},
    {"id": 5, "device_id": 4, "hostname": "ap-floor3.example.net", "program": "WIRELESS", "priority": "info", "msg": "Client association: AA:BB:CC:DD:EE:FF on SSID Corp-WiFi", "timestamp": "2024-01-15 03:45:22"},
]

PORTS = [
    {"port_id": 1, "device_id": 1, "ifDescr": "GigabitEthernet0/0", "ifAlias": "Uplink-ISP1", "ifSpeed": 1000000000, "ifOperStatus": "up", "ifInOctets_rate": 456789012, "ifOutOctets_rate": 234567890},
    {"port_id": 2, "device_id": 1, "ifDescr": "GigabitEthernet0/1", "ifAlias": "Core-Link", "ifSpeed": 1000000000, "ifOperStatus": "up", "ifInOctets_rate": 345678901, "ifOutOctets_rate": 123456789},
    {"port_id": 3, "device_id": 2, "ifDescr": "Ethernet1/1", "ifAlias": "Server-Farm", "ifSpeed": 10000000000, "ifOperStatus": "up", "ifInOctets_rate": 567890123, "ifOutOctets_rate": 678901234},
    {"port_id": 4, "device_id": 3, "ifDescr": "Management0/0", "ifAlias": "MGMT", "ifSpeed": 100000000, "ifOperStatus": "down", "ifInOctets_rate": 0, "ifOutOctets_rate": 0},
]

SENSORS = [
    {"sensor_id": 1, "device_id": 1, "sensor_class": "temperature", "sensor_descr": "CPU Temperature", "sensor_current": 42.5, "sensor_limit": 85.0, "sensor_limit_low": 5.0},
    {"sensor_id": 2, "device_id": 1, "sensor_class": "fanspeed", "sensor_descr": "Fan 1", "sensor_current": 4200, "sensor_limit": 8000, "sensor_limit_low": 2000},
    {"sensor_id": 3, "device_id": 2, "sensor_class": "temperature", "sensor_descr": "Chassis Temperature", "sensor_current": 38.2, "sensor_limit": 75.0, "sensor_limit_low": 0.0},
    {"sensor_id": 4, "device_id": 5, "sensor_class": "voltage", "sensor_descr": "PSU Voltage", "sensor_current": 12.1, "sensor_limit": 13.0, "sensor_limit_low": 11.0},
    {"sensor_id": 5, "device_id": 2, "sensor_class": "power", "sensor_descr": "Power Supply 1", "sensor_current": 245.0, "sensor_limit": 500.0, "sensor_limit_low": 0.0},
]

NTP_PEERS = [
    {"id": 1, "device_id": 1, "peer": "10.0.0.100", "stratum": 2, "error": ""},
    {"id": 2, "device_id": 2, "peer": "10.0.0.100", "stratum": 2, "error": ""},
    {"id": 3, "device_id": 5, "peer": "pool.ntp.org", "stratum": 1, "error": ""},
    {"id": 4, "device_id": 3, "peer": "10.0.0.100", "stratum": 2, "error": "Peer unreachable"},
]


def render_nav(active=''):
    nav_items = [
        ('devices', '/inventory', 'Devices'),
        ('ports', '/interfaces/list', 'Interfaces'),
        ('health', '/monitoring/sensors', 'Health'),
        ('outages', '/events/outages', 'Outages'),
        ('syslog', '/events/logs', 'Syslog'),
        ('ntp', '/services/ntp', 'NTP'),
    ]
    items_html = ''
    for key, href, label in nav_items:
        cls = ' class="active"' if active == key else ''
        items_html += '<li{cls}><a href="{href}">{label}</a></li>'.format(cls=cls, href=href, label=label)

    return (
        '<nav class="navbar navbar-inverse navbar-fixed-top">'
        '<div class="container-fluid">'
        '<div class="navbar-header"><a class="navbar-brand" href="/">NetWatch NMS</a></div>'
        '<ul class="nav navbar-nav">' + items_html + '</ul>'
        '<ul class="nav navbar-nav navbar-right">'
        '<li><a href="/account/settings"><span class="glyphicon glyphicon-user"></span> admin</a></li>'
        '</ul></div></nav>'
    )


def render_page(title, content, active=''):
    return (
        '<!DOCTYPE html><html><head>'
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>' + cgi.escape(title) + ' - NetWatch NMS</title>'
        '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">'
        '<link rel="stylesheet" href="/static/css/nms.css">'
        '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>'
        '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>'
        '</head><body>'
        + render_nav(active)
        + '<div class="container-fluid" style="margin-top:70px;">'
        + content
        + '</div></body></html>'
    )


def verify_xss_execution(html_page):
    """Use headless browser to check if JavaScript alert fires"""
    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "--ignore-ssl-errors=true", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = ''
    try:
        of = open(fn, 'w')
        of.write(html_page)
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
def index():
    content = (
        '<div class="row"><div class="col-md-12"><h3>Dashboard</h3></div></div>'
        '<div class="row">'
        '<div class="col-md-3"><div class="panel panel-success"><div class="panel-heading"><h4>Devices Up</h4></div><div class="panel-body"><h2>4</h2></div></div></div>'
        '<div class="col-md-3"><div class="panel panel-danger"><div class="panel-heading"><h4>Devices Down</h4></div><div class="panel-body"><h2>1</h2></div></div></div>'
        '<div class="col-md-3"><div class="panel panel-info"><div class="panel-heading"><h4>Ports Up</h4></div><div class="panel-body"><h2>3</h2></div></div></div>'
        '<div class="col-md-3"><div class="panel panel-warning"><div class="panel-heading"><h4>Active Outages</h4></div><div class="panel-body"><h2>1</h2></div></div></div>'
        '</div>'
        '<div class="row">'
        '<div class="col-md-6"><div class="panel panel-default panel-condensed">'
        '<div class="panel-heading"><strong>Recent Outages</strong></div>'
        '<table class="table table-condensed table-striped"><thead><tr><th>Device</th><th>Down</th><th>Duration</th></tr></thead>'
        '<tbody><tr class="danger"><td>fw-edge-01.example.net</td><td>2024-01-15 03:22:11</td><td>ongoing</td></tr>'
        '<tr><td>sw-dist-02.example.net</td><td>2024-01-14 18:05:33</td><td>41m 39s</td></tr></tbody></table></div></div>'
        '<div class="col-md-6"><div class="panel panel-default panel-condensed">'
        '<div class="panel-heading"><strong>Recent Syslog</strong></div>'
        '<table class="table table-condensed table-striped"><thead><tr><th>Device</th><th>Program</th><th>Message</th></tr></thead>'
        '<tbody><tr><td>core-rtr-01</td><td>BGP</td><td>Neighbor 10.0.0.2 Down - Hold timer expired</td></tr>'
        '<tr><td>fw-edge-01</td><td>ASA</td><td>Failover cable communication failure</td></tr></tbody></table></div></div>'
        '</div>'
    )
    return render_page('Dashboard', content)


@app.route('/inventory')
def devices_list():
    rows = ''
    for d in DEVICES:
        status_cls = 'success' if d['status'] else 'danger'
        status_txt = 'Up' if d['status'] else 'Down'
        rows += '<tr class="{cls}"><td>{id}</td><td><a href="/inventory/device?id={id}">{hostname}</a></td><td>{os}</td><td>{status}</td><td>{location}</td></tr>'.format(
            cls=status_cls, id=d['device_id'], hostname=cgi.escape(d['hostname']),
            os=cgi.escape(d['os']), status=status_txt, location=cgi.escape(d['location'])
        )

    content = (
        '<div class="panel panel-default panel-condensed">'
        '<div class="panel-heading"><strong>All Devices</strong></div>'
        '<div class="table-responsive">'
        '<table class="table table-condensed table-hover table-striped">'
        '<thead><tr><th>ID</th><th>Hostname</th><th>OS</th><th>Status</th><th>Location</th></tr></thead>'
        '<tbody>' + rows + '</tbody></table></div></div>'
    )
    return render_page('Devices', content, active='devices')


@app.route('/inventory/device')
def device_detail():
    device_id = request.args.get('id', '')
    device = None
    try:
        did = int(device_id)
        for d in DEVICES:
            if d['device_id'] == did:
                device = d
                break
    except (ValueError, TypeError):
        pass

    if not device:
        return render_page('Device Not Found', '<div class="alert alert-warning">Device not found.</div>', active='devices'), 404

    dev_ports = [p for p in PORTS if p['device_id'] == device['device_id']]
    dev_sensors = [s for s in SENSORS if s['device_id'] == device['device_id']]

    port_rows = ''
    for p in dev_ports:
        port_rows += '<tr><td>{ifDescr}</td><td>{ifAlias}</td><td>{ifSpeed}</td><td>{status}</td></tr>'.format(
            ifDescr=cgi.escape(p['ifDescr']), ifAlias=cgi.escape(p['ifAlias']),
            ifSpeed=p['ifSpeed'], status=cgi.escape(p['ifOperStatus'])
        )

    sensor_rows = ''
    for s in dev_sensors:
        sensor_rows += '<tr><td>{descr}</td><td>{cls}</td><td>{current}</td><td>{low}</td><td>{high}</td></tr>'.format(
            descr=cgi.escape(s['sensor_descr']), cls=cgi.escape(s['sensor_class']),
            current=s['sensor_current'], low=s['sensor_limit_low'], high=s['sensor_limit']
        )

    content = (
        '<div class="panel panel-default">'
        '<div class="panel-heading"><strong>Device: ' + cgi.escape(device['hostname']) + '</strong></div>'
        '<div class="panel-body"><dl class="dl-horizontal">'
        '<dt>Hostname</dt><dd>' + cgi.escape(device['hostname']) + '</dd>'
        '<dt>OS</dt><dd>' + cgi.escape(device['os']) + '</dd>'
        '<dt>Status</dt><dd>' + ('Up' if device['status'] else 'Down') + '</dd>'
        '<dt>Location</dt><dd>' + cgi.escape(device['location']) + '</dd>'
        '<dt>Uptime</dt><dd>' + str(device['uptime']) + 's</dd>'
        '</dl></div></div>'
        '<div class="panel panel-default panel-condensed">'
        '<div class="panel-heading"><strong>Interfaces</strong></div>'
        '<table class="table table-condensed table-striped">'
        '<thead><tr><th>Interface</th><th>Description</th><th>Speed</th><th>Status</th></tr></thead>'
        '<tbody>' + port_rows + '</tbody></table></div>'
        '<div class="panel panel-default panel-condensed">'
        '<div class="panel-heading"><strong>Sensors</strong></div>'
        '<table class="table table-condensed table-striped">'
        '<thead><tr><th>Sensor</th><th>Class</th><th>Current</th><th>Low Limit</th><th>High Limit</th></tr></thead>'
        '<tbody>' + sensor_rows + '</tbody></table></div>'
    )
    return render_page('Device: ' + cgi.escape(device['hostname']), content, active='devices')


@app.route('/events/outages')
def outages_page():
    from_val = request.args.get('from', '')
    to_val = request.args.get('to', '')
    device_filter = request.args.get('device', '')

    filtered = OUTAGES
    if device_filter:
        try:
            did = int(device_filter)
            filtered = [o for o in OUTAGES if o['device_id'] == did]
        except ValueError:
            filtered = OUTAGES

    rows = ''
    for o in filtered:
        up = cgi.escape(str(o['up_again'])) if o['up_again'] else '<span class="label label-danger">Ongoing</span>'
        rows += '<tr><td><a href="/inventory/device?id={did}">{hostname}</a></td><td>{down}</td><td>{up}</td><td>{duration}</td></tr>'.format(
            did=o['device_id'], hostname=cgi.escape(o['hostname']),
            down=cgi.escape(o['going_down']), up=up, duration=cgi.escape(str(o['duration']))
        )

    # Build the page with unsanitized from/to in input value attributes
    page_html = (
        '<!DOCTYPE html><html><head>'
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Outages - NetWatch NMS</title>'
        '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">'
        '<link rel="stylesheet" href="/static/css/nms.css">'
        '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>'
        '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>'
        '</head><body>'
        + render_nav('outages')
        + '<div class="container-fluid" style="margin-top:70px;">'
        '<div class="panel panel-default panel-condensed">'
        '<div class="panel-heading"><strong>Outages</strong></div>'
        '<div class="panel-body">'
        '<form method="get" action="/events/outages" class="form-inline" role="form">'
        '<div class="form-group">'
        '<select name="device" class="form-control input-sm">'
        '<option value="">All Devices</option>'
        '<option value="1">core-rtr-01.example.net</option>'
        '<option value="2">sw-dist-02.example.net</option>'
        '<option value="3">fw-edge-01.example.net</option>'
        '<option value="4">ap-floor3.example.net</option>'
        '<option value="5">srv-monitor.example.net</option>'
        '</select></div>'
        '<div class="form-group">'
        '<input name="from" type="text" class="form-control input-sm" maxlength="16" value="' + from_val + '" placeholder="From" data-date-format="YYYY-MM-DD HH:mm">'
        '</div>'
        '<div class="form-group">'
        '<input name="to" type="text" class="form-control input-sm" maxlength="16" value="' + to_val + '" placeholder="To" data-date-format="YYYY-MM-DD HH:mm">'
        '</div>'
        '<button type="submit" class="btn btn-default btn-sm">Filter</button>'
        '</form></div>'
        '<div class="table-responsive">'
        '<table class="table table-condensed table-hover table-striped">'
        '<thead><tr><th>Device</th><th>Going Down</th><th>Up Again</th><th>Duration</th></tr></thead>'
        '<tbody>' + rows + '</tbody></table></div></div>'
        '<div id="page-footer"></div>'
        '</div></body></html>'
    )

    result = verify_xss_execution(page_html)
    if result == 'XSS':
        flag_notice = '<div class="alert alert-success" style="margin-top:10px;"><strong>System Key:</strong> ' + _flag_data + '</div>'
        page_html = page_html.replace('<div id="page-footer"></div>', flag_notice)

    return page_html


@app.route('/events/logs')
def syslog_page():
    from_val = request.args.get('from', '')
    to_val = request.args.get('to', '')
    device_filter = request.args.get('device', '')
    program_filter = request.args.get('program', '')
    priority_filter = request.args.get('priority', '')

    filtered = SYSLOG_ENTRIES
    if device_filter:
        try:
            did = int(device_filter)
            filtered = [e for e in filtered if e['device_id'] == did]
        except ValueError:
            pass
    if program_filter:
        filtered = [e for e in filtered if e['program'] == program_filter]
    if priority_filter:
        filtered = [e for e in filtered if e['priority'] == priority_filter]

    rows = ''
    for e in filtered:
        prio_lbl = {'critical': 'danger', 'warning': 'warning', 'notice': 'info', 'info': 'default'}.get(e['priority'], 'default')
        rows += '<tr><td>{ts}</td><td><a href="/inventory/device?id={did}">{hostname}</a></td><td>{program}</td><td><span class="label label-{lbl}">{priority}</span></td><td>{msg}</td></tr>'.format(
            ts=cgi.escape(e['timestamp']), did=e['device_id'],
            hostname=cgi.escape(e['hostname']), program=cgi.escape(e['program']),
            priority=cgi.escape(e['priority']), msg=cgi.escape(e['msg']), lbl=prio_lbl
        )

    # Unsanitized from/to in input value attributes
    page_html = (
        '<!DOCTYPE html><html><head>'
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Syslog - NetWatch NMS</title>'
        '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">'
        '<link rel="stylesheet" href="/static/css/nms.css">'
        '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>'
        '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>'
        '</head><body>'
        + render_nav('syslog')
        + '<div class="container-fluid" style="margin-top:70px;">'
        '<div class="panel panel-default panel-condensed">'
        '<div class="panel-heading"><strong>Syslog</strong></div>'
        '<div class="panel-body">'
        '<form method="get" action="/events/logs" class="form-inline" role="form">'
        '<div class="form-group">'
        '<select name="device" class="form-control input-sm">'
        '<option value="">All Devices</option>'
        '<option value="1">core-rtr-01.example.net</option>'
        '<option value="2">sw-dist-02.example.net</option>'
        '<option value="3">fw-edge-01.example.net</option>'
        '<option value="4">ap-floor3.example.net</option>'
        '<option value="5">srv-monitor.example.net</option>'
        '</select></div>'
        '<div class="form-group">'
        '<select name="program" class="form-control input-sm">'
        '<option value="">All Programs</option>'
        '<option value="BGP">BGP</option>'
        '<option value="ASA">ASA</option>'
        '<option value="CRON">CRON</option>'
        '<option value="STP">STP</option>'
        '<option value="WIRELESS">WIRELESS</option>'
        '</select></div>'
        '<div class="form-group">'
        '<select name="priority" class="form-control input-sm">'
        '<option value="">All Priorities</option>'
        '<option value="critical">Critical</option>'
        '<option value="warning">Warning</option>'
        '<option value="notice">Notice</option>'
        '<option value="info">Info</option>'
        '</select></div>'
        '<div class="form-group">'
        '<input name="from" type="text" class="form-control input-sm" maxlength="16" value="' + from_val + '" placeholder="From" data-date-format="YYYY-MM-DD HH:mm">'
        '</div>'
        '<div class="form-group">'
        '<input name="to" type="text" class="form-control input-sm" maxlength="16" value="' + to_val + '" placeholder="To" data-date-format="YYYY-MM-DD HH:mm">'
        '</div>'
        '<button type="submit" class="btn btn-default btn-sm">Filter</button>'
        '</form></div>'
        '<div class="table-responsive">'
        '<table class="table table-condensed table-hover table-striped">'
        '<thead><tr><th>Timestamp</th><th>Device</th><th>Program</th><th>Priority</th><th>Message</th></tr></thead>'
        '<tbody>' + rows + '</tbody></table></div></div>'
        '<div id="page-footer"></div>'
        '</div></body></html>'
    )

    result = verify_xss_execution(page_html)
    if result == 'XSS':
        flag_notice = '<div class="alert alert-success" style="margin-top:10px;"><strong>System Key:</strong> ' + _flag_data + '</div>'
        page_html = page_html.replace('<div id="page-footer"></div>', flag_notice)

    return page_html


@app.route('/interfaces/list')
def ports_list():
    device_id = request.args.get('device_id', '')
    hostname = request.args.get('hostname', '')
    state = request.args.get('state', '')
    if_type = request.args.get('ifType', '')
    if_alias = request.args.get('ifAlias', '')

    filtered = PORTS
    if device_id:
        try:
            did = int(device_id)
            filtered = [p for p in filtered if p['device_id'] == did]
        except ValueError:
            pass
    if state:
        filtered = [p for p in filtered if p['ifOperStatus'] == state]

    rows = ''
    for p in filtered:
        dev = None
        for d in DEVICES:
            if d['device_id'] == p['device_id']:
                dev = d
                break
        dev_name = cgi.escape(dev['hostname']) if dev else 'Unknown'
        status_cls = 'success' if p['ifOperStatus'] == 'up' else 'danger'
        rows += '<tr class="{cls}"><td>{hostname}</td><td>{ifDescr}</td><td>{ifAlias}</td><td>{speed}</td><td>{status}</td><td>{in_rate}</td><td>{out_rate}</td></tr>'.format(
            cls=status_cls, hostname=dev_name,
            ifDescr=cgi.escape(p['ifDescr']), ifAlias=cgi.escape(p['ifAlias']),
            speed=p['ifSpeed'], status=cgi.escape(p['ifOperStatus']),
            in_rate=p['ifInOctets_rate'], out_rate=p['ifOutOctets_rate']
        )

    # Unsanitized reflection of parameters into JavaScript context
    js_block = (
        "<script>"
        "var filterConfig = {"
        "device_id: '" + device_id + "',"
        "hostname: '" + hostname + "',"
        "state: '" + state + "',"
        "ifType: '" + if_type + "',"
        "ifAlias: '" + if_alias + "'"
        "};"
        "$(document).ready(function() {"
        "if (filterConfig.device_id) { $(\"select[name='device_id']\").val(filterConfig.device_id); }"
        "if (filterConfig.state) { $(\"select[name='state']\").val(filterConfig.state); }"
        "});"
        "</script>"
    )

    page_html = (
        '<!DOCTYPE html><html><head>'
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Interfaces - NetWatch NMS</title>'
        '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">'
        '<link rel="stylesheet" href="/static/css/nms.css">'
        '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>'
        '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>'
        '</head><body>'
        + render_nav('ports')
        + '<div class="container-fluid" style="margin-top:70px;">'
        '<div class="panel panel-default panel-condensed">'
        '<div class="panel-heading"><strong>Interfaces</strong></div>'
        '<div class="panel-body">'
        '<form method="get" action="/interfaces/list" class="form-inline" role="form">'
        '<div class="form-group">'
        '<select name="device_id" class="form-control input-sm">'
        '<option value="">All Devices</option>'
        '<option value="1">core-rtr-01.example.net</option>'
        '<option value="2">sw-dist-02.example.net</option>'
        '<option value="3">fw-edge-01.example.net</option>'
        '</select></div>'
        '<div class="form-group">'
        '<select name="state" class="form-control input-sm">'
        '<option value="">All States</option>'
        '<option value="up">Up</option>'
        '<option value="down">Down</option>'
        '</select></div>'
        '<button type="submit" class="btn btn-default btn-sm">Filter</button>'
        '</form></div>'
        '<div class="table-responsive">'
        '<table id="ports-table" class="table table-condensed table-hover table-striped">'
        '<thead><tr><th>Device</th><th>Interface</th><th>Description</th><th>Speed</th><th>Status</th><th>Traffic In</th><th>Traffic Out</th></tr></thead>'
        '<tbody>' + rows + '</tbody></table></div></div>'
        '<div id="page-footer"></div>'
        + js_block
        + '</div></body></html>'
    )

    result = verify_xss_execution(page_html)
    if result == 'XSS':
        flag_notice = '<div class="alert alert-success" style="margin-top:10px;"><strong>System Key:</strong> ' + _flag_data + '</div>'
        page_html = page_html.replace('<div id="page-footer"></div>', flag_notice)

    return page_html


@app.route('/monitoring/sensors')
def health_sensors():
    view = request.args.get('view', 'all')
    graph_type = request.args.get('graph_type', 'none')
    unit = request.args.get('unit', '')
    sensor_class = request.args.get('class', '')

    filtered = SENSORS
    if sensor_class:
        filtered = [s for s in filtered if s['sensor_class'] == sensor_class]

    rows = ''
    for s in filtered:
        dev = None
        for d in DEVICES:
            if d['device_id'] == s['device_id']:
                dev = d
                break
        dev_name = cgi.escape(dev['hostname']) if dev else 'Unknown'
        rows += '<tr><td>{hostname}</td><td>{descr}</td><td>{cls}</td><td>{current}</td><td>{low}</td><td>{high}</td></tr>'.format(
            hostname=dev_name, descr=cgi.escape(s['sensor_descr']),
            cls=cgi.escape(s['sensor_class']), current=s['sensor_current'],
            low=s['sensor_limit_low'], high=s['sensor_limit']
        )

    # Unsanitized reflection of parameters into JavaScript context
    js_block = (
        "<script>"
        "var sensorGrid = $(\"#sensors-table\").ready(function() {"
        "var postData = {"
        "id: 'sensors',"
        "view: '" + view + "',"
        "graph_type: '" + graph_type + "',"
        "unit: '" + unit + "',"
        "sensor_class: '" + sensor_class + "'"
        "};"
        "console.log('Sensor view: ' + postData.view);"
        "});"
        "</script>"
    )

    page_html = (
        '<!DOCTYPE html><html><head>'
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Health Sensors - NetWatch NMS</title>'
        '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">'
        '<link rel="stylesheet" href="/static/css/nms.css">'
        '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>'
        '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>'
        '</head><body>'
        + render_nav('health')
        + '<div class="container-fluid" style="margin-top:70px;">'
        '<div class="panel panel-default panel-condensed">'
        '<div class="panel-heading"><div class="row" style="padding:0 10px;">'
        '<div class="pull-left"><strong>Health &raquo; Sensors</strong></div>'
        '<div class="pull-right">'
        '<a href="/monitoring/sensors?class=temperature">Temperature</a> | '
        '<a href="/monitoring/sensors?class=fanspeed">Fanspeed</a> | '
        '<a href="/monitoring/sensors?class=voltage">Voltage</a> | '
        '<a href="/monitoring/sensors?class=power">Power</a> | '
        '<a href="/monitoring/sensors">All</a>'
        '</div></div></div>'
        '<div class="table-responsive">'
        '<table id="sensors-table" class="table table-condensed table-hover table-striped">'
        '<thead><tr><th>Device</th><th>Sensor</th><th>Class</th><th>Current</th><th>Low Limit</th><th>High Limit</th></tr></thead>'
        '<tbody>' + rows + '</tbody></table></div></div>'
        '<div id="page-footer"></div>'
        + js_block
        + '</div></body></html>'
    )

    result = verify_xss_execution(page_html)
    if result == 'XSS':
        flag_notice = '<div class="alert alert-success" style="margin-top:10px;"><strong>System Key:</strong> ' + _flag_data + '</div>'
        page_html = page_html.replace('<div id="page-footer"></div>', flag_notice)

    return page_html


@app.route('/services/ntp')
def ntp_peers():
    view = request.args.get('view', 'all')
    graph = request.args.get('graph', 'none')

    view_options = {'all': 'All', 'error': 'Error'}
    graph_options = {'none': 'No Graphs', 'stratum': 'Stratum', 'offset': 'Offset', 'delay': 'Delay', 'dispersion': 'Dispersion'}

    filtered = NTP_PEERS
    if view == 'error':
        filtered = [p for p in filtered if p['error']]

    rows = ''
    for p in filtered:
        dev = None
        for d in DEVICES:
            if d['device_id'] == p['device_id']:
                dev = d
                break
        dev_name = cgi.escape(dev['hostname']) if dev else 'Unknown'
        error_cls = 'danger' if p['error'] else ''
        rows += '<tr class="{cls}"><td>{hostname}</td><td>{peer}</td><td>{stratum}</td><td>{error}</td></tr>'.format(
            cls=error_cls, hostname=dev_name, peer=cgi.escape(p['peer']),
            stratum=p['stratum'], error=cgi.escape(p['error'])
        )

    view_links = ''
    for k, v in view_options.items():
        cls = ' class="pagemenu-selected"' if view == k else ''
        view_links += '<a href="/services/ntp?view={k}&graph={g}"{cls}>{v}</a> | '.format(
            k=cgi.escape(k), g=cgi.escape(graph), cls=cls, v=cgi.escape(v)
        )

    graph_links = ''
    for k, v in graph_options.items():
        cls = ' class="pagemenu-selected"' if graph == k else ''
        graph_links += '<a href="/services/ntp?view={vi}&graph={k}"{cls}>{v}</a> | '.format(
            vi=cgi.escape(view), k=cgi.escape(k), cls=cls, v=cgi.escape(v)
        )

    # Unsanitized reflection of view and graph into JavaScript context
    js_block = (
        "<script>"
        "$(\"#ntp-table\").ready(function() {"
        "var postData = {"
        "id: 'app_ntp',"
        "view: '" + view + "',"
        "graph: '" + graph + "'"
        "};"
        "console.log('NTP config: ' + postData.view);"
        "});"
        "</script>"
    )

    page_html = (
        '<!DOCTYPE html><html><head>'
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>NTP Peers - NetWatch NMS</title>'
        '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">'
        '<link rel="stylesheet" href="/static/css/nms.css">'
        '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>'
        '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>'
        '</head><body>'
        + render_nav('ntp')
        + '<div class="container-fluid" style="margin-top:70px;">'
        '<div class="panel panel-default panel-condensed">'
        '<div class="panel-heading"><div class="row" style="padding:0 10px;">'
        '<div class="pull-left"><strong>NTP Peers</strong> &raquo; ' + view_links + '</div>'
        '<div class="pull-right">' + graph_links + '</div>'
        '</div></div>'
        '<div class="table-responsive">'
        '<table id="ntp-table" class="table table-condensed table-hover table-striped">'
        '<thead><tr><th>Device</th><th>Peer</th><th>Stratum</th><th>Error</th></tr></thead>'
        '<tbody>' + rows + '</tbody></table></div></div>'
        '<div id="page-footer"></div>'
        + js_block
        + '</div></body></html>'
    )

    result = verify_xss_execution(page_html)
    if result == 'XSS':
        flag_notice = '<div class="alert alert-success" style="margin-top:10px;"><strong>System Key:</strong> ' + _flag_data + '</div>'
        page_html = page_html.replace('<div id="page-footer"></div>', flag_notice)

    return page_html


@app.route('/monitoring/realtime')
def port_realtime():
    port_id = request.args.get('port_id', '1')
    interval = request.args.get('interval', '2')

    port = None
    try:
        pid = int(port_id)
        for p in PORTS:
            if p['port_id'] == pid:
                port = p
                break
    except (ValueError, TypeError):
        pass

    if not port:
        return render_page('Port Not Found', '<div class="alert alert-warning">Port not found.</div>', active='ports'), 404

    interval_links = ''
    for iv in ['0.25', '1', '2', '5', '15', '60']:
        cls = ' class="pagemenu-selected"' if interval == iv else ''
        interval_links += '<a href="/monitoring/realtime?port_id={pid}&interval={iv}"{cls}>{iv}s</a> | '.format(
            pid=cgi.escape(str(port_id)), iv=iv, cls=cls
        )

    # Unsanitized reflection of interval in HTML attribute
    content = (
        '<div class="panel panel-default">'
        '<div class="panel-heading">'
        '<strong>Realtime Traffic</strong> &raquo; ' + cgi.escape(port['ifDescr'])
        + '<div class="pull-right">Polling Interval: ' + interval_links + '</div></div>'
        '<div class="panel-body" style="text-align:center;">'
        '<object data="/monitoring/graph-realtime?type=bits&id=' + str(port['port_id']) + '&interval=' + interval + '" type="image/svg+xml" width="1000" height="400">'
        '<param name="src" value="/monitoring/graph?type=bits&id=' + str(port['port_id']) + '&interval=' + interval + '" />'
        'Your browser does not support SVG.</object></div></div>'
    )
    return render_page('Realtime: ' + cgi.escape(port['ifDescr']), content, active='ports')


@app.route('/monitoring/graph-realtime')
def graph_realtime():
    return Response(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="400">'
        '<text x="500" y="200" text-anchor="middle" fill="#999">No data available</text></svg>',
        mimetype='image/svg+xml'
    )


@app.route('/monitoring/graph')
def graph_static():
    return Response(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="400">'
        '<text x="500" y="200" text-anchor="middle" fill="#999">No data available</text></svg>',
        mimetype='image/svg+xml'
    )


@app.route('/account/settings')
def account_settings():
    content = (
        '<div class="panel panel-default">'
        '<div class="panel-heading"><strong>Account Settings</strong></div>'
        '<div class="panel-body"><form class="form-horizontal">'
        '<div class="form-group"><label class="col-sm-2 control-label">Username</label>'
        '<div class="col-sm-10"><p class="form-control-static">admin</p></div></div>'
        '<div class="form-group"><label class="col-sm-2 control-label">Email</label>'
        '<div class="col-sm-10"><input type="email" class="form-control" value="admin@example.net" disabled></div></div>'
        '<div class="form-group"><label class="col-sm-2 control-label">Timezone</label>'
        '<div class="col-sm-10"><select class="form-control" disabled><option>UTC</option></select></div></div>'
        '</form></div></div>'
    )
    return render_page('Account Settings', content)


@app.route('/data_table')
def data_table():
    table_id = request.args.get('id', '')
    if table_id == 'sensors':
        return jsonify({"current": 1, "rowCount": 50, "rows": SENSORS, "total": len(SENSORS)})
    elif table_id == 'ntp':
        return jsonify({"current": 1, "rowCount": 50, "rows": NTP_PEERS, "total": len(NTP_PEERS)})
    elif table_id == 'ports':
        return jsonify({"current": 1, "rowCount": 50, "rows": PORTS, "total": len(PORTS)})
    return jsonify({"current": 1, "rowCount": 0, "rows": [], "total": 0})


@app.errorhandler(404)
def not_found(e):
    return render_page('Not Found', '<div class="alert alert-warning">The requested page was not found.</div>'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_page('Error', '<div class="alert alert-danger">An internal error occurred.</div>'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
