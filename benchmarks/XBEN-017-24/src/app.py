# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, url_for, session
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import hashlib
import time

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flag_data = open('secret.txt').read().strip()

app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')

USERS = {
    'admin': {
        'password': 'QGhNm8$kL2vx',
        'level': 10,
        'realname': 'Admin User',
        'email': 'admin@netmonitor.local'
    },
    'operator': {
        'password': 'operator',
        'level': 5,
        'realname': 'Network Operator',
        'email': 'operator@netmonitor.local'
    }
}

SAMPLE_DEVICES = [
    {'device_id': 1, 'hostname': 'core-sw01.net.local', 'sysName': 'core-sw01', 'os': 'ios', 'status': 1},
    {'device_id': 2, 'hostname': 'edge-rtr01.net.local', 'sysName': 'edge-rtr01', 'os': 'iosxe', 'status': 1},
    {'device_id': 3, 'hostname': 'dist-sw02.net.local', 'sysName': 'dist-sw02', 'os': 'nxos', 'status': 0},
    {'device_id': 4, 'hostname': 'fw-ext01.net.local', 'sysName': 'fw-ext01', 'os': 'asa', 'status': 1},
    {'device_id': 5, 'hostname': 'ap-floor3.net.local', 'sysName': 'ap-floor3', 'os': 'airos', 'status': 1},
]

SAMPLE_RESULTS_V4 = [
    {'hostname': 'core-sw01.net.local', 'interface': 'Vlan100', 'address': '10.0.100.1', 'description': 'Management VLAN'},
    {'hostname': 'edge-rtr01.net.local', 'interface': 'GigabitEthernet0/0', 'address': '192.168.1.1', 'description': 'WAN uplink'},
    {'hostname': 'dist-sw02.net.local', 'interface': 'Loopback0', 'address': '10.255.0.2', 'description': 'Router ID'},
    {'hostname': 'fw-ext01.net.local', 'interface': 'GigabitEthernet0/1', 'address': '172.16.0.1', 'description': 'DMZ gateway'},
]

SAMPLE_RESULTS_V6 = [
    {'hostname': 'core-sw01.net.local', 'interface': 'Vlan100', 'address': '2001:db8:100::1', 'description': 'Management VLAN v6'},
    {'hostname': 'edge-rtr01.net.local', 'interface': 'GigabitEthernet0/0', 'address': '2001:db8:1::1', 'description': 'WAN uplink v6'},
    {'hostname': 'dist-sw02.net.local', 'interface': 'Loopback0', 'address': '2001:db8:ffff::2', 'description': 'Router ID v6'},
    {'hostname': 'fw-ext01.net.local', 'interface': 'outside', 'address': 'fe80::1', 'description': 'External interface link-local'},
]

SAMPLE_ARP = [
    {'mac_address': '00:1A:2B:3C:4D:5E', 'ipv4_address': '10.0.100.10', 'hostname': 'core-sw01.net.local', 'interface': 'Vlan100'},
    {'mac_address': '00:2B:3C:4D:5E:6F', 'ipv4_address': '192.168.1.100', 'hostname': 'edge-rtr01.net.local', 'interface': 'GigabitEthernet0/1'},
    {'mac_address': '00:3C:4D:5E:6F:70', 'ipv4_address': '172.16.0.50', 'hostname': 'fw-ext01.net.local', 'interface': 'GigabitEthernet0/1'},
]


def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


def render_nav(active=''):
    user = session.get('username', '')
    level = USERS.get(user, {}).get('level', 0)
    return '''
    <nav class="navbar navbar-inverse navbar-fixed-top">
      <div class="container-fluid">
        <div class="navbar-header">
          <a class="navbar-brand" href="/overview">NetMonitor</a>
        </div>
        <ul class="nav navbar-nav">
          <li {ov}><a href="/overview">Overview</a></li>
          <li {dv}><a href="/devices">Devices</a></li>
          <li class="dropdown {sv}">
            <a href="#" class="dropdown-toggle" data-toggle="dropdown">Search <span class="caret"></span></a>
            <ul class="dropdown-menu">
              <li><a href="/search/ipv4">IPv4 Addresses</a></li>
              <li><a href="/search/ipv6">IPv6 Addresses</a></li>
              <li><a href="/search/arp">ARP Tables</a></li>
              <li><a href="/search/mac">MAC Addresses</a></li>
            </ul>
          </li>
          <li {av}><a href="/alerts">Alerts</a></li>
        </ul>
        <ul class="nav navbar-nav navbar-right">
          <li><a href="#">{user} (Level {level})</a></li>
          <li><a href="/logout">Logout</a></li>
        </ul>
      </div>
    </nav>
    '''.format(
        ov='class="active"' if active == 'overview' else '',
        dv='class="active"' if active == 'devices' else '',
        sv='class="active"' if active == 'search' else '',
        av='class="active"' if active == 'alerts' else '',
        user=cgi.escape(user),
        level=level
    )


def render_page(title, content, active=''):
    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} - NetMonitor</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
    <style>
        body {{ padding-top: 70px; background: #f5f5f5; }}
        .panel {{ margin-bottom: 20px; }}
        .navbar-brand {{ font-weight: bold; }}
        .table-status-up {{ color: #5cb85c; }}
        .table-status-down {{ color: #d9534f; }}
        .search-form {{ margin-bottom: 15px; }}
        .footer {{ margin-top: 40px; padding: 20px 0; text-align: center; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    {nav}
    <div class="container-fluid">
        {content}
        <div class="footer">
            <p>NetMonitor &copy; 2023 - Network Monitoring System</p>
        </div>
    </div>
    <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
</body>
</html>'''.format(title=cgi.escape(title), nav=render_nav(active), content=content)


@app.route('/')
def index():
    if 'username' in session:
        return redirect('/overview')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username in USERS and USERS[username]['password'] == password:
            session['username'] = username
            session['level'] = USERS[username]['level']
            return redirect('/overview')
        error = '<div class="alert alert-danger">Invalid credentials</div>'

    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>NetMonitor - Login</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
    <style>
        body {{ background: #2c3e50; display: flex; align-items: center; justify-content: center; height: 100vh; }}
        .login-panel {{ max-width: 400px; width: 100%; }}
        .panel-heading {{ background: #34495e !important; color: white !important; text-align: center; }}
        .panel-heading h3 {{ margin: 0; }}
    </style>
</head>
<body>
    <div class="login-panel">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3>NetMonitor</h3>
                <small>Network Monitoring System</small>
            </div>
            <div class="panel-body">
                {error}
                <form method="post" action="/login">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="username" class="form-control" placeholder="Username" autofocus>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password" class="form-control" placeholder="Password">
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">Login</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>'''.format(error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/overview')
@require_auth
def overview():
    up_count = sum(1 for d in SAMPLE_DEVICES if d['status'] == 1)
    down_count = sum(1 for d in SAMPLE_DEVICES if d['status'] == 0)
    content = '''
    <div class="row">
        <div class="col-md-3">
            <div class="panel panel-success">
                <div class="panel-heading"><h4>Devices Up</h4></div>
                <div class="panel-body"><h2>{up}</h2></div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="panel panel-danger">
                <div class="panel-heading"><h4>Devices Down</h4></div>
                <div class="panel-body"><h2>{down}</h2></div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="panel panel-info">
                <div class="panel-heading"><h4>Total Devices</h4></div>
                <div class="panel-body"><h2>{total}</h2></div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="panel panel-warning">
                <div class="panel-heading"><h4>Active Alerts</h4></div>
                <div class="panel-body"><h2>2</h2></div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-md-12">
            <div class="panel panel-default">
                <div class="panel-heading"><strong>Recent Devices</strong></div>
                <table class="table table-hover table-condensed table-striped">
                    <thead><tr>
                        <th>Hostname</th><th>sysName</th><th>OS</th><th>Status</th>
                    </tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
        </div>
    </div>
    '''.format(
        up=up_count, down=down_count, total=len(SAMPLE_DEVICES),
        rows=''.join(
            '<tr><td>{}</td><td>{}</td><td>{}</td><td class="{}">{}</td></tr>'.format(
                d['hostname'], d['sysName'], d['os'],
                'table-status-up' if d['status'] else 'table-status-down',
                'Up' if d['status'] else 'Down'
            ) for d in SAMPLE_DEVICES
        )
    )
    return render_page('Overview', content, 'overview')


@app.route('/devices')
@require_auth
def devices():
    content = '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>All Devices</strong></div>
        <table class="table table-hover table-condensed table-striped">
            <thead><tr>
                <th>ID</th><th>Hostname</th><th>sysName</th><th>OS</th><th>Status</th>
            </tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    '''.format(
        rows=''.join(
            '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td class="{}">{}</td></tr>'.format(
                d['device_id'], d['hostname'], d['sysName'], d['os'],
                'table-status-up' if d['status'] else 'table-status-down',
                'Up' if d['status'] else 'Down'
            ) for d in SAMPLE_DEVICES
        )
    )
    return render_page('Devices', content, 'devices')


@app.route('/alerts')
@require_auth
def alerts():
    content = '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>Active Alerts</strong></div>
        <table class="table table-hover table-condensed table-striped">
            <thead><tr>
                <th>ID</th><th>Device</th><th>Rule</th><th>Severity</th><th>Timestamp</th>
            </tr></thead>
            <tbody>
                <tr><td>1</td><td>dist-sw02.net.local</td><td>Device Down</td>
                    <td><span class="label label-danger">Critical</span></td>
                    <td>2023-09-15 14:23:01</td></tr>
                <tr><td>2</td><td>edge-rtr01.net.local</td><td>High CPU Usage</td>
                    <td><span class="label label-warning">Warning</span></td>
                    <td>2023-09-15 13:45:22</td></tr>
            </tbody>
        </table>
    </div>
    '''
    return render_page('Alerts', content, 'alerts')


@app.route('/search/ipv4', methods=['GET', 'POST'])
@require_auth
def search_ipv4():
    device_id = ''
    interface_val = ''
    address_val = ''

    if request.method == 'POST':
        device_id = request.form.get('device_id', '')
        interface_val = request.form.get('interface', '')
        address_val = request.form.get('address', '')

    device_options = ''.join(
        '<option value="{did}" {sel}>{host}</option>'.format(
            did=d['device_id'],
            sel='selected' if str(d['device_id']) == device_id else '',
            host=cgi.escape(d['hostname'])
        ) for d in SAMPLE_DEVICES
    )

    results_html = ''
    if request.method == 'POST':
        filtered = SAMPLE_RESULTS_V4
        if address_val:
            filtered = [r for r in filtered if address_val.lower() in r['address'].lower()]
        if interface_val:
            filtered = [r for r in filtered if interface_val.replace('%', '').lower() in r['interface'].lower()]
        results_html = ''.join(
            '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                cgi.escape(r['hostname']), cgi.escape(r['interface']),
                cgi.escape(r['address']), cgi.escape(r['description'])
            ) for r in filtered
        )
        if not filtered:
            results_html = '<tr><td colspan="4" class="text-center text-muted">No results found</td></tr>'

    content = '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>IPv4 Addresses</strong></div>
        <div class="panel-body">
            <form method="post" action="/search/ipv4" class="form-inline search-form">
                <div class="form-group">
                    <select name="device_id" class="form-control input-sm">
                        <option value="">All Devices</option>
                        {device_options}
                    </select>
                </div>&nbsp;
                <div class="form-group">
                    <select name="interface" class="form-control input-sm">
                        <option value="">All Interfaces</option>
                        <option value="Loopback%" {lo_sel}>Loopbacks</option>
                        <option value="Vlan%" {vl_sel}>VLANs</option>
                    </select>
                </div>&nbsp;
                <div class="form-group">
                    <input type="text" name="address" class="form-control input-sm"
                           value="{addr_safe}" placeholder="IPv4 Address" size="40">
                </div>&nbsp;
                <button type="submit" class="btn btn-default input-sm">Search</button>
            </form>
        </div>
        <table class="table table-hover table-condensed table-striped">
            <thead><tr>
                <th>Device</th><th>Interface</th><th>Address</th><th>Description</th>
            </tr></thead>
            <tbody>{results}</tbody>
        </table>
    </div>
    '''.format(
        device_options=device_options,
        lo_sel='selected' if interface_val == 'Loopback%' else '',
        vl_sel='selected' if interface_val == 'Vlan%' else '',
        addr_safe=cgi.escape(address_val, quote=True),
        results=results_html
    )
    return render_page('Search - IPv4', content, 'search')


def build_ipv6_page(device_id, interface_val, address_val, results_html, include_nav=True):
    device_options = ''.join(
        '<option value="{did}" {sel}>{host}</option>'.format(
            did=d['device_id'],
            sel='selected' if str(d['device_id']) == device_id else '',
            host=cgi.escape(d['hostname'])
        ) for d in SAMPLE_DEVICES
    )

    escaped_device_id = cgi.escape(device_id, quote=True)

    content = '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>IPv6 Addresses</strong></div>
        <div class="panel-body">
            <form method="post" action="/search/ipv6" class="form-inline search-form">
                <div class="form-group">
                    <select name="device_id" id="device_id" class="form-control input-sm">
                        <option value="">All Devices</option>
                        {device_options}
                    </select>
                </div>&nbsp;
                <div class="form-group">
                    <select name="interface" id="interface" class="form-control input-sm">
                        <option value="">All Interfaces</option>
                        <option value="Loopback%" {lo_sel}>Loopbacks</option>
                        <option value="Vlan%" {vl_sel}>VLANs</option>
                    </select>
                </div>&nbsp;
                <div class="form-group">
                    <input type="text" name="address" id="address" size="40" value="{addr_raw}" class="form-control input-sm" placeholder="IPv6 Address"/>
                </div>&nbsp;
                <button type="submit" class="btn btn-default input-sm">Search</button>
            </form>
        </div>
        <table id="ipv6-search" class="table table-hover table-condensed table-striped">
            <thead><tr>
                <th>Device</th><th>Interface</th><th>Address</th><th>Description</th>
            </tr></thead>
            <tbody>{results}</tbody>
        </table>
    </div>
    <script>
    $(document).ready(function() {{
        var searchConfig = {{
            id: "address-search",
            search_type: "ipv6",
            device_id: '{device_id_safe}',
            interface: '{iface_raw}',
            address: '{addr_raw}'
        }};
    }});
    </script>
    '''.format(
        device_options=device_options,
        lo_sel='selected' if interface_val == 'Loopback%' else '',
        vl_sel='selected' if interface_val == 'Vlan%' else '',
        device_id_safe=escaped_device_id,
        iface_raw=interface_val,
        addr_raw=address_val,
        results=results_html
    )

    if include_nav:
        return render_page('Search - IPv6', content, 'search')
    else:
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Search - IPv6 - NetMonitor</title>
    <script>window.$ = window.jQuery = function(s) {{ return {{ ready: function(fn) {{ if (document.readyState !== 'loading') fn(); else document.addEventListener('DOMContentLoaded', fn); }}, bootgrid: function() {{ return this; }} }}; }};</script>
</head>
<body>
    <div class="container-fluid">
        {content}
    </div>
</body>
</html>'''.format(content=content)


@app.route('/search/ipv6', methods=['GET', 'POST'])
@require_auth
def search_ipv6():
    device_id = ''
    interface_val = ''
    address_val = ''

    if request.method == 'POST':
        device_id = request.form.get('device_id', '')
        interface_val = request.form.get('interface', '')
        address_val = request.form.get('address', '')

    results_html = ''
    if request.method == 'POST':
        filtered = SAMPLE_RESULTS_V6
        if address_val:
            filtered = [r for r in filtered if address_val.lower() in r['address'].lower()]
        if interface_val:
            filtered = [r for r in filtered if interface_val.replace('%', '').lower() in r['interface'].lower()]
        results_html = ''.join(
            '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                cgi.escape(r['hostname']), cgi.escape(r['interface']),
                cgi.escape(r['address']), cgi.escape(r['description'])
            ) for r in filtered
        )
        if not filtered:
            results_html = '<tr><td colspan="4" class="text-center text-muted">No results found</td></tr>'

    page_html = build_ipv6_page(device_id, interface_val, address_val, results_html)

    if request.method == 'POST' and (address_val or interface_val):
        check_page = build_ipv6_page(device_id, interface_val, address_val, results_html, include_nav=False)
        xss_result = run_xss_check(check_page)
        if xss_result and xss_result not in ('success', 'fail', 'Failed to load the page.'):
            alert_insert = '<div class="alert alert-danger"><strong>Security Alert:</strong> Suspicious activity detected in search parameters.<br>Incident reference: <code>{}</code></div>'.format(flag_data)
            page_html = page_html.replace('<table id="ipv6-search"', alert_insert + '<table id="ipv6-search"', 1)

    return page_html


@app.route('/search/arp', methods=['GET', 'POST'])
@require_auth
def search_arp():
    search_phrase = ''
    search_by = 'mac'
    device_id = ''

    if request.method == 'POST':
        search_phrase = request.form.get('searchPhrase', '')
        search_by = request.form.get('searchby', 'mac')
        device_id = request.form.get('device_id', '')

    device_options = ''.join(
        '<option value="{did}" {sel}>{host}</option>'.format(
            did=d['device_id'],
            sel='selected' if str(d['device_id']) == device_id else '',
            host=cgi.escape(d['hostname'])
        ) for d in SAMPLE_DEVICES
    )

    results_html = ''
    if request.method == 'POST':
        filtered = SAMPLE_ARP
        if search_phrase:
            if search_by == 'mac':
                filtered = [r for r in filtered if search_phrase.lower() in r['mac_address'].lower()]
            else:
                filtered = [r for r in filtered if search_phrase.lower() in r['ipv4_address'].lower()]
        results_html = ''.join(
            '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                cgi.escape(r['mac_address']), cgi.escape(r['ipv4_address']),
                cgi.escape(r['hostname']), cgi.escape(r['interface'])
            ) for r in filtered
        )
        if not filtered:
            results_html = '<tr><td colspan="4" class="text-center text-muted">No results found</td></tr>'

    content = '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>ARP Entries</strong></div>
        <div class="panel-body">
            <form method="post" action="/search/arp" class="form-inline search-form">
                <div class="form-group">
                    <select name="device_id" class="form-control input-sm">
                        <option value="">All Devices</option>
                        {device_options}
                    </select>
                </div>&nbsp;
                <div class="form-group">
                    <select name="searchby" class="form-control input-sm">
                        <option value="mac" {mac_sel}>MAC Address</option>
                        <option value="ip" {ip_sel}>IP Address</option>
                    </select>
                </div>&nbsp;
                <div class="form-group">
                    <input type="text" name="searchPhrase" class="form-control input-sm"
                           value="{phrase_safe}" placeholder="Address" size="40">
                </div>&nbsp;
                <button type="submit" class="btn btn-default input-sm">Search</button>
            </form>
        </div>
        <table class="table table-hover table-condensed table-striped">
            <thead><tr>
                <th>MAC Address</th><th>IP Address</th><th>Device</th><th>Interface</th>
            </tr></thead>
            <tbody>{results}</tbody>
        </table>
    </div>
    '''.format(
        device_options=device_options,
        mac_sel='selected' if search_by == 'mac' else '',
        ip_sel='selected' if search_by == 'ip' else '',
        phrase_safe=cgi.escape(search_phrase, quote=True),
        results=results_html
    )
    return render_page('Search - ARP', content, 'search')


@app.route('/search/mac', methods=['GET', 'POST'])
@require_auth
def search_mac():
    content = '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>MAC Addresses</strong></div>
        <div class="panel-body">
            <form method="post" action="/search/mac" class="form-inline search-form">
                <div class="form-group">
                    <select name="device_id" class="form-control input-sm">
                        <option value="">All Devices</option>
                    </select>
                </div>&nbsp;
                <div class="form-group">
                    <input type="text" name="address" class="form-control input-sm"
                           placeholder="MAC Address" size="40">
                </div>&nbsp;
                <button type="submit" class="btn btn-default input-sm">Search</button>
            </form>
        </div>
        <table class="table table-hover table-condensed table-striped">
            <thead><tr>
                <th>Device</th><th>Interface</th><th>MAC Address</th><th>Description</th>
            </tr></thead>
            <tbody>
                <tr><td colspan="4" class="text-center text-muted">No results</td></tr>
            </tbody>
        </table>
    </div>
    '''
    return render_page('Search - MAC', content, 'search')


def run_xss_check(page_html):
    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "check.js"],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    output_lines = []
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        stdout_data = proc.communicate()[0]
        output_lines = [l.strip() for l in stdout_data.strip().split('\n') if l.strip()]
    except Exception:
        try:
            proc.kill()
        except OSError:
            pass
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass

    for line in output_lines:
        if line not in ('success', 'fail', 'Failed to load the page.', ''):
            return line
    return ''


@app.errorhandler(404)
def not_found(e):
    return Response('<html><body><h1>404 Not Found</h1></body></html>', status=404)


@app.errorhandler(500)
def server_error(e):
    return Response('<html><body><h1>500 Internal Server Error</h1></body></html>', status=500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
