# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect
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

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# Simulated device data for the network monitoring system
DEVICES = [
    {"device_id": 1, "hostname": "core-rtr-01.dc1.local", "sysName": "core-rtr-01", "os": "ios", "status": 1, "uptime": 8640000},
    {"device_id": 2, "hostname": "dist-sw-01.dc1.local", "sysName": "dist-sw-01", "os": "nxos", "status": 1, "uptime": 4320000},
    {"device_id": 3, "hostname": "edge-fw-01.dc1.local", "sysName": "edge-fw-01", "os": "asa", "status": 0, "uptime": 0},
    {"device_id": 4, "hostname": "access-sw-01.dc2.local", "sysName": "access-sw-01", "os": "ios", "status": 1, "uptime": 2160000},
    {"device_id": 5, "hostname": "wan-rtr-01.dc2.local", "sysName": "wan-rtr-01", "os": "iosxr", "status": 1, "uptime": 6480000},
]

OUTAGES = [
    {"id": 1, "device_id": 3, "hostname": "edge-fw-01.dc1.local", "going_down": "2023-09-15 08:23:11", "up_again": None, "duration": "ongoing"},
    {"id": 2, "device_id": 2, "hostname": "dist-sw-01.dc1.local", "going_down": "2023-09-14 02:15:33", "up_again": "2023-09-14 02:45:12", "duration": "29m 39s"},
    {"id": 3, "device_id": 1, "hostname": "core-rtr-01.dc1.local", "going_down": "2023-09-10 14:05:22", "up_again": "2023-09-10 14:06:01", "duration": "39s"},
    {"id": 4, "device_id": 4, "hostname": "access-sw-01.dc2.local", "going_down": "2023-09-08 19:44:10", "up_again": "2023-09-08 20:12:55", "duration": "28m 45s"},
]

SYSLOG_ENTRIES = [
    {"timestamp": "2023-09-15 08:23:11", "device": "edge-fw-01.dc1.local", "program": "snmpd", "msg": "Connection lost", "priority": "err"},
    {"timestamp": "2023-09-15 08:20:05", "device": "core-rtr-01.dc1.local", "program": "bgpd", "msg": "Neighbor 10.0.0.2 state changed to Established", "priority": "notice"},
    {"timestamp": "2023-09-15 08:15:33", "device": "dist-sw-01.dc1.local", "program": "sshd", "msg": "Accepted publickey for admin from 10.1.1.100", "priority": "info"},
    {"timestamp": "2023-09-15 07:55:10", "device": "wan-rtr-01.dc2.local", "program": "ospfd", "msg": "Interface GigabitEthernet0/1 state changed to DR", "priority": "notice"},
]

PORTS = [
    {"port_id": 1, "device_id": 1, "ifName": "GigabitEthernet0/0", "ifAlias": "Uplink to ISP", "ifOperStatus": "up", "ifSpeed": 1000000000},
    {"port_id": 2, "device_id": 1, "ifName": "GigabitEthernet0/1", "ifAlias": "Core Link", "ifOperStatus": "up", "ifSpeed": 10000000000},
    {"port_id": 3, "device_id": 2, "ifName": "Ethernet1/1", "ifAlias": "Server VLAN", "ifOperStatus": "up", "ifSpeed": 10000000000},
    {"port_id": 4, "device_id": 3, "ifName": "GigabitEthernet0/0", "ifAlias": "DMZ Interface", "ifOperStatus": "down", "ifSpeed": 1000000000},
    {"port_id": 5, "device_id": 4, "ifName": "FastEthernet0/1", "ifAlias": "Access Port", "ifOperStatus": "up", "ifSpeed": 100000000},
]

def format_uptime(seconds):
    if seconds == 0:
        return "Down"
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    return "{}d {}h".format(days, hours)

def check_xss_on_page(page_html):
    """Server-side rendering check for content security policy validation"""
    proc = subprocess.Popen(["timeout", "8", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        result = ''
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result


# ---------- NAV / LAYOUT ----------

NAV_HTML = """
<nav class="navbar navbar-default">
  <div class="container-fluid">
    <div class="navbar-header">
      <a class="navbar-brand" href="/">LibreNMS</a>
    </div>
    <ul class="nav navbar-nav">
      <li><a href="/devices">Devices</a></li>
      <li><a href="/ports/list">Ports</a></li>
      <li><a href="/outages">Outages</a></li>
      <li><a href="/health/processor">Health</a></li>
      <li><a href="/syslog">Syslog</a></li>
      <li><a href="/apps/ntp">Apps</a></li>
    </ul>
  </div>
</nav>
"""

PAGE_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} - LibreNMS</title>
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
  <style>
    body {{ background-color: #f5f5f5; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }}
    .navbar-default {{ background-color: #333; border-color: #333; }}
    .navbar-default .navbar-brand {{ color: #e74c3c; font-weight: bold; font-size: 20px; }}
    .navbar-default .navbar-brand:hover {{ color: #c0392b; }}
    .navbar-default .navbar-nav > li > a {{ color: #ccc; }}
    .navbar-default .navbar-nav > li > a:hover {{ color: #fff; }}
    .content-wrapper {{ margin: 20px; }}
    .panel-title {{ font-size: 14px; }}
    .table > thead > tr > th {{ background-color: #333; color: #fff; font-size: 12px; }}
    .status-up {{ color: #27ae60; }}
    .status-down {{ color: #e74c3c; }}
    .filter-bar {{ background-color: #fff; padding: 15px; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 4px; }}
    .filter-bar label {{ font-weight: normal; margin-right: 10px; }}
  </style>
</head>
<body>
"""

PAGE_FOOT = """
</body>
</html>
"""


# ---------- ROUTES ----------

@app.route('/')
def index():
    device_count = len(DEVICES)
    up_count = sum(1 for d in DEVICES if d['status'] == 1)
    down_count = device_count - up_count
    port_count = len(PORTS)
    outage_count = sum(1 for o in OUTAGES if o['up_again'] is None)

    html = PAGE_HEAD.format(title="Dashboard")
    html += NAV_HTML
    html += """
    <div class="content-wrapper">
      <div class="row">
        <div class="col-md-3">
          <div class="panel panel-default">
            <div class="panel-heading"><h3 class="panel-title">Devices</h3></div>
            <div class="panel-body text-center">
              <h2>{}</h2>
              <p><span class="status-up">{} up</span> / <span class="status-down">{} down</span></p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="panel panel-default">
            <div class="panel-heading"><h3 class="panel-title">Ports</h3></div>
            <div class="panel-body text-center"><h2>{}</h2></div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="panel panel-default">
            <div class="panel-heading"><h3 class="panel-title">Active Outages</h3></div>
            <div class="panel-body text-center"><h2 class="status-down">{}</h2></div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="panel panel-default">
            <div class="panel-heading"><h3 class="panel-title">Syslog Entries</h3></div>
            <div class="panel-body text-center"><h2>{}</h2></div>
          </div>
        </div>
      </div>

      <div class="panel panel-default">
        <div class="panel-heading"><h3 class="panel-title">Recent Outages</h3></div>
        <table class="table table-condensed table-striped">
          <thead><tr><th>Device</th><th>Going Down</th><th>Up Again</th><th>Duration</th></tr></thead>
          <tbody>
    """.format(device_count, up_count, down_count, port_count, outage_count, len(SYSLOG_ENTRIES))

    for o in OUTAGES[:5]:
        status = '<span class="status-down">Ongoing</span>' if o['up_again'] is None else o['up_again']
        html += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            cgi.escape(o['hostname']), o['going_down'], status, o['duration'])

    html += """
          </tbody>
        </table>
      </div>
    </div>
    """
    html += PAGE_FOOT
    return html


@app.route('/devices')
def devices():
    html = PAGE_HEAD.format(title="Devices")
    html += NAV_HTML
    html += """
    <div class="content-wrapper">
      <div class="panel panel-default">
        <div class="panel-heading"><h3 class="panel-title">All Devices</h3></div>
        <table class="table table-condensed table-striped">
          <thead><tr><th>Device</th><th>sysName</th><th>OS</th><th>Status</th><th>Uptime</th></tr></thead>
          <tbody>
    """
    for d in DEVICES:
        status_class = "status-up" if d['status'] == 1 else "status-down"
        status_text = "Up" if d['status'] == 1 else "Down"
        html += '<tr><td><a href="/devices/{}">{}</a></td><td>{}</td><td>{}</td><td><span class="{}">{}</span></td><td>{}</td></tr>'.format(
            d['device_id'], cgi.escape(d['hostname']), cgi.escape(d['sysName']),
            cgi.escape(d['os']), status_class, status_text, format_uptime(d['uptime']))

    html += """
          </tbody>
        </table>
      </div>
    </div>
    """
    html += PAGE_FOOT
    return html


@app.route('/devices/<int:device_id>')
def device_detail(device_id):
    device = None
    for d in DEVICES:
        if d['device_id'] == device_id:
            device = d
            break
    if not device:
        return "Device not found", 404

    html = PAGE_HEAD.format(title=device['hostname'])
    html += NAV_HTML
    html += """
    <div class="content-wrapper">
      <div class="panel panel-default">
        <div class="panel-heading"><h3 class="panel-title">{hostname}</h3></div>
        <div class="panel-body">
          <dl class="dl-horizontal">
            <dt>Hostname</dt><dd>{hostname}</dd>
            <dt>sysName</dt><dd>{sysName}</dd>
            <dt>OS</dt><dd>{os}</dd>
            <dt>Status</dt><dd>{status}</dd>
            <dt>Uptime</dt><dd>{uptime}</dd>
          </dl>
        </div>
      </div>
    </div>
    """.format(
        hostname=cgi.escape(device['hostname']),
        sysName=cgi.escape(device['sysName']),
        os=cgi.escape(device['os']),
        status="Up" if device['status'] == 1 else "Down",
        uptime=format_uptime(device['uptime']))
    html += PAGE_FOOT
    return html


@app.route('/outages')
def outages():
    from_val = request.args.get('from', '')
    to_val = request.args.get('to', '')

    html = PAGE_HEAD.format(title="Outages")
    html += NAV_HTML
    html += '<div class="content-wrapper">'
    html += '<div class="panel panel-default">'
    html += '<div class="panel-heading"><h3 class="panel-title">Network Outages</h3></div>'
    html += '<div class="panel-body">'
    html += '<div class="filter-bar">'
    html += '<form method="get" action="/outages" class="form-inline">'
    html += '<label for="from">From:</label>'
    html += '<input type="text" class="form-control input-sm" id="from" name="from" value="' + from_val + '">'
    html += '&nbsp;&nbsp;'
    html += '<label for="to">To:</label>'
    html += '<input type="text" class="form-control input-sm" id="to" name="to" value="' + to_val + '">'
    html += '&nbsp;&nbsp;'
    html += '<button type="submit" class="btn btn-default btn-sm">Filter</button>'
    html += '</form>'
    html += '</div>'

    if from_val or to_val:
        page_for_check = html + '</div></div></div>' + PAGE_FOOT
        xss_result = check_xss_on_page(page_for_check)
        if xss_result:
            html += '<div class="alert alert-info" role="alert">' + flag + '</div>'

    html += '<table class="table table-condensed table-striped">'
    html += '<thead><tr><th>Device</th><th>Going Down</th><th>Up Again</th><th>Duration</th></tr></thead>'
    html += '<tbody>'

    for o in OUTAGES:
        show = True
        if from_val and not any(c in from_val for c in '<>"\''):
            try:
                if o['going_down'] < from_val:
                    show = False
            except:
                pass
        if to_val and not any(c in to_val for c in '<>"\''):
            try:
                if o['going_down'] > to_val:
                    show = False
            except:
                pass

        if show:
            up = '<span class="status-down">Ongoing</span>' if o['up_again'] is None else o['up_again']
            html += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                cgi.escape(o['hostname']), o['going_down'], up, o['duration'])

    html += '</tbody></table>'
    html += '</div></div></div>'
    html += PAGE_FOOT
    return html


@app.route('/syslog')
def syslog():
    from_val = request.args.get('from', '')
    to_val = request.args.get('to', '')

    html = PAGE_HEAD.format(title="Syslog")
    html += NAV_HTML
    html += '<div class="content-wrapper">'
    html += '<div class="panel panel-default">'
    html += '<div class="panel-heading"><h3 class="panel-title">Syslog</h3></div>'
    html += '<div class="panel-body">'
    html += '<div class="filter-bar">'
    html += '<form method="get" action="/syslog" class="form-inline">'
    html += '<label for="from">From:</label>'
    html += '<input type="text" class="form-control input-sm" id="from" name="from" value="' + from_val + '">'
    html += '&nbsp;&nbsp;'
    html += '<label for="to">To:</label>'
    html += '<input type="text" class="form-control input-sm" id="to" name="to" value="' + to_val + '">'
    html += '&nbsp;&nbsp;'
    html += '<button type="submit" class="btn btn-default btn-sm">Filter</button>'
    html += '</form>'
    html += '</div>'

    html += '<table class="table table-condensed table-striped">'
    html += '<thead><tr><th>Timestamp</th><th>Device</th><th>Program</th><th>Message</th><th>Priority</th></tr></thead>'
    html += '<tbody>'

    for entry in SYSLOG_ENTRIES:
        html += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            entry['timestamp'], cgi.escape(entry['device']), cgi.escape(entry['program']),
            cgi.escape(entry['msg']), cgi.escape(entry['priority']))

    html += '</tbody></table>'
    html += '</div></div></div>'
    html += PAGE_FOOT
    return html


@app.route('/ports/list')
def ports_list():
    device_id = request.args.get('device_id', '')
    hostname = request.args.get('hostname', '')
    state = request.args.get('state', '')

    html = PAGE_HEAD.format(title="Ports")
    html += NAV_HTML
    html += '<div class="content-wrapper">'
    html += '<div class="panel panel-default">'
    html += '<div class="panel-heading"><h3 class="panel-title">Port Listing</h3></div>'
    html += '<div class="panel-body">'
    html += '<div class="filter-bar">'
    html += '<form method="get" action="/ports/list" class="form-inline">'
    html += '<label>Device ID:</label>'
    html += '<input type="text" class="form-control input-sm" name="device_id" value="' + cgi.escape(device_id, quote=True) + '">'
    html += '&nbsp;&nbsp;'
    html += '<label>Hostname:</label>'
    html += '<input type="text" class="form-control input-sm" name="hostname" value="' + cgi.escape(hostname, quote=True) + '">'
    html += '&nbsp;&nbsp;'
    html += '<label>State:</label>'
    html += '<select name="state" class="form-control input-sm">'
    states = [('', 'All'), ('up', 'Up'), ('down', 'Down')]
    for val, label in states:
        selected = ' selected' if state == val else ''
        html += '<option value="{}"{}>{}</option>'.format(cgi.escape(val, quote=True), selected, label)
    html += '</select>'
    html += '&nbsp;&nbsp;'
    html += '<button type="submit" class="btn btn-default btn-sm">Filter</button>'
    html += '</form>'
    html += '</div>'

    html += '<table class="table table-condensed table-striped">'
    html += '<thead><tr><th>Port</th><th>Device</th><th>Interface</th><th>Description</th><th>Status</th><th>Speed</th></tr></thead>'
    html += '<tbody>'

    for p in PORTS:
        dev = None
        for d in DEVICES:
            if d['device_id'] == p['device_id']:
                dev = d
                break
        if not dev:
            continue
        if device_id and str(dev['device_id']) != device_id:
            continue
        if state and p['ifOperStatus'] != state:
            continue

        status_class = "status-up" if p['ifOperStatus'] == 'up' else "status-down"
        speed = "{}G".format(p['ifSpeed'] // 1000000000) if p['ifSpeed'] >= 1000000000 else "{}M".format(p['ifSpeed'] // 1000000)
        html += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td><span class="{}">{}</span></td><td>{}</td></tr>'.format(
            p['port_id'], cgi.escape(dev['hostname']), cgi.escape(p['ifName']),
            cgi.escape(p['ifAlias']), status_class, p['ifOperStatus'], speed)

    html += '</tbody></table>'
    html += '</div></div></div>'
    html += PAGE_FOOT
    return html


@app.route('/health/processor')
def health_processor():
    view = request.args.get('view', 'graphs')

    html = PAGE_HEAD.format(title="Health :: Processor")
    html += NAV_HTML
    html += '<div class="content-wrapper">'
    html += '<div class="panel panel-default">'
    html += '<div class="panel-heading"><h3 class="panel-title">Processor Health</h3></div>'
    html += '<div class="panel-body">'

    html += '<ul class="nav nav-tabs">'
    for v in ['graphs', 'details']:
        active = ' class="active"' if view == v else ''
        html += '<li{}><a href="/health/processor?view={}">{}</a></li>'.format(active, cgi.escape(v, quote=True), v.capitalize())
    html += '</ul>'
    html += '<br>'

    # Simulated processor health data
    processors = [
        {"device": "core-rtr-01.dc1.local", "processor": "CPU0", "usage": 23},
        {"device": "dist-sw-01.dc1.local", "processor": "CPU0", "usage": 45},
        {"device": "edge-fw-01.dc1.local", "processor": "CPU0", "usage": 0},
        {"device": "access-sw-01.dc2.local", "processor": "CPU0", "usage": 12},
        {"device": "wan-rtr-01.dc2.local", "processor": "CPU0", "usage": 67},
    ]

    if cgi.escape(view, quote=True) == 'details':
        html += '<table class="table table-condensed table-striped">'
        html += '<thead><tr><th>Device</th><th>Processor</th><th>Usage %</th></tr></thead><tbody>'
        for p in processors:
            html += '<tr><td>{}</td><td>{}</td><td>{}%</td></tr>'.format(
                cgi.escape(p['device']), p['processor'], p['usage'])
        html += '</tbody></table>'
    else:
        for p in processors:
            bar_class = "progress-bar-success" if p['usage'] < 50 else ("progress-bar-warning" if p['usage'] < 80 else "progress-bar-danger")
            html += '<div style="margin-bottom:10px"><strong>{} - {}</strong>'.format(cgi.escape(p['device']), p['processor'])
            html += '<div class="progress"><div class="progress-bar {}" style="width:{}%">{}%</div></div></div>'.format(
                bar_class, max(p['usage'], 5), p['usage'])

    html += '</div></div></div>'
    html += PAGE_FOOT
    return html


@app.route('/apps/ntp')
def apps_ntp():
    view = request.args.get('view', 'overview')

    html = PAGE_HEAD.format(title="Apps :: NTP")
    html += NAV_HTML
    html += '<div class="content-wrapper">'
    html += '<div class="panel panel-default">'
    html += '<div class="panel-heading"><h3 class="panel-title">NTP Monitoring</h3></div>'
    html += '<div class="panel-body">'

    html += '<ul class="nav nav-tabs">'
    for v in ['overview', 'peers', 'graphs']:
        active = ' class="active"' if view == v else ''
        html += '<li{}><a href="/apps/ntp?view={}">{}</a></li>'.format(active, cgi.escape(v, quote=True), v.capitalize())
    html += '</ul>'
    html += '<br>'

    ntp_peers = [
        {"peer": "0.pool.ntp.org", "stratum": 2, "offset": "+0.023ms", "jitter": "1.234ms", "reach": "377"},
        {"peer": "1.pool.ntp.org", "stratum": 2, "offset": "-0.012ms", "jitter": "0.567ms", "reach": "377"},
        {"peer": "2.pool.ntp.org", "stratum": 3, "offset": "+0.045ms", "jitter": "2.345ms", "reach": "376"},
    ]

    html += '<table class="table table-condensed table-striped">'
    html += '<thead><tr><th>Peer</th><th>Stratum</th><th>Offset</th><th>Jitter</th><th>Reach</th></tr></thead>'
    html += '<tbody>'
    for p in ntp_peers:
        html += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            cgi.escape(p['peer']), p['stratum'], p['offset'], p['jitter'], p['reach'])
    html += '</tbody></table>'

    html += '</div></div></div>'
    html += PAGE_FOOT
    return html


@app.route('/search/fdb')
def search_fdb():
    searchby = request.args.get('searchby', 'mac')
    searchPhrase = request.args.get('searchPhrase', '')

    html = PAGE_HEAD.format(title="Search :: FDB")
    html += NAV_HTML
    html += '<div class="content-wrapper">'
    html += '<div class="panel panel-default">'
    html += '<div class="panel-heading"><h3 class="panel-title">FDB Table Search</h3></div>'
    html += '<div class="panel-body">'
    html += '<form method="get" action="/search/fdb" class="form-inline">'
    html += '<label>Search by:</label>&nbsp;'
    html += '<select name="searchby" class="form-control input-sm">'
    for val in ['mac', 'port', 'vlan']:
        selected = ' selected' if searchby == val else ''
        html += '<option value="{}"{}>{}</option>'.format(cgi.escape(val, quote=True), selected, val.upper())
    html += '</select>&nbsp;&nbsp;'
    html += '<input type="text" name="searchPhrase" class="form-control input-sm" placeholder="Search..." value="' + cgi.escape(searchPhrase, quote=True) + '">'
    html += '&nbsp;&nbsp;<button type="submit" class="btn btn-default btn-sm">Search</button>'
    html += '</form>'
    html += '<br>'

    fdb_entries = [
        {"mac": "00:1A:2B:3C:4D:5E", "device": "dist-sw-01.dc1.local", "port": "Ethernet1/1", "vlan": 100},
        {"mac": "00:2B:3C:4D:5E:6F", "device": "access-sw-01.dc2.local", "port": "FastEthernet0/1", "vlan": 200},
        {"mac": "00:3C:4D:5E:6F:7A", "device": "dist-sw-01.dc1.local", "port": "Ethernet1/2", "vlan": 100},
    ]

    html += '<table class="table table-condensed table-striped">'
    html += '<thead><tr><th>MAC Address</th><th>Device</th><th>Port</th><th>VLAN</th></tr></thead>'
    html += '<tbody>'
    for f in fdb_entries:
        if searchPhrase and searchPhrase.lower() not in str(f).lower():
            continue
        html += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            f['mac'], cgi.escape(f['device']), cgi.escape(f['port']), f['vlan'])
    html += '</tbody></table>'

    html += '</div></div></div>'
    html += PAGE_FOOT
    return html


@app.errorhandler(404)
def not_found(e):
    return '<html><body><h1>404 Not Found</h1><p>The requested URL was not found on this server.</p></body></html>', 404

@app.errorhandler(500)
def server_error(e):
    return '<html><body><h1>500 Internal Server Error</h1><p>An internal error occurred.</p></body></html>', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
