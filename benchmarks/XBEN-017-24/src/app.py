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

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = os.urandom(24).encode('hex')

phantom = Phantom()

# Simulated user database (LibreNMS style)
USERS = {
    'admin': {
        'password': 'admin',
        'level': 10,
        'realname': 'LibreNMS Admin',
        'email': 'admin@librenms.local'
    }
}

# Simulated device data
DEVICES = [
    {'device_id': 1, 'hostname': 'core-rtr01.librenms.local', 'sysName': 'core-rtr01', 'os': 'ios', 'status': 1, 'uptime': 8640000},
    {'device_id': 2, 'hostname': 'sw-dist01.librenms.local', 'sysName': 'sw-dist01', 'os': 'nxos', 'status': 1, 'uptime': 4320000},
    {'device_id': 3, 'hostname': 'fw-edge01.librenms.local', 'sysName': 'fw-edge01', 'os': 'asa', 'status': 0, 'uptime': 0},
    {'device_id': 4, 'hostname': 'srv-mon01.librenms.local', 'sysName': 'srv-mon01', 'os': 'linux', 'status': 1, 'uptime': 12960000},
]

# Simulated IPv6 address data
IPV6_DATA = [
    {'ipv6_address': '2001:db8::1', 'ipv6_prefixlen': 64, 'port_id': 1, 'ifName': 'GigabitEthernet0/0', 'device_id': 1, 'hostname': 'core-rtr01.librenms.local'},
    {'ipv6_address': '2001:db8::2', 'ipv6_prefixlen': 64, 'port_id': 2, 'ifName': 'Vlan100', 'device_id': 2, 'hostname': 'sw-dist01.librenms.local'},
    {'ipv6_address': 'fe80::1', 'ipv6_prefixlen': 10, 'port_id': 3, 'ifName': 'Management0/0', 'device_id': 3, 'hostname': 'fw-edge01.librenms.local'},
    {'ipv6_address': '2001:db8:1::10', 'ipv6_prefixlen': 48, 'port_id': 4, 'ifName': 'eth0', 'device_id': 4, 'hostname': 'srv-mon01.librenms.local'},
    {'ipv6_address': '2001:db8:2::ff', 'ipv6_prefixlen': 64, 'port_id': 5, 'ifName': 'GigabitEthernet0/1', 'device_id': 1, 'hostname': 'core-rtr01.librenms.local'},
    {'ipv6_address': 'fd00::1', 'ipv6_prefixlen': 128, 'port_id': 6, 'ifName': 'Loopback0', 'device_id': 1, 'hostname': 'core-rtr01.librenms.local'},
]

def login_required(f):
    """Decorator to require authentication for routes"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


def check_xss(page):
    """Render page in PhantomJS and check for XSS alert execution"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
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
    if 'username' not in session:
        return redirect('/login')
    return redirect('/overview')


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
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LibreNMS - Login</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #060606; color: #ccc; }}
        .login-box {{ max-width: 400px; margin: 100px auto; padding: 30px; background: #1a1a2e; border-radius: 4px; }}
        .login-box h2 {{ color: #e74c3c; text-align: center; margin-bottom: 20px; }}
        .btn-primary {{ background-color: #e74c3c; border-color: #c0392b; }}
    </style>
</head>
<body>
    <div class="login-box">
        <h2><i class="glyphicon glyphicon-signal"></i> LibreNMS</h2>
        {error}
        <form method="post">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" class="form-control" name="username" id="username" placeholder="Username">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" class="form-control" name="password" id="password" placeholder="Password">
            </div>
            <button type="submit" class="btn btn-primary btn-block">Login</button>
        </form>
    </div>
</body>
</html>'''.format(error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


NAV_BAR = '''
<nav class="navbar navbar-inverse navbar-fixed-top">
    <div class="container-fluid">
        <div class="navbar-header">
            <a class="navbar-brand" href="/overview" style="color:#e74c3c;">
                <i class="glyphicon glyphicon-signal"></i> LibreNMS
            </a>
        </div>
        <ul class="nav navbar-nav">
            <li><a href="/overview">Overview</a></li>
            <li><a href="/devices">Devices</a></li>
            <li class="dropdown">
                <a href="#" class="dropdown-toggle" data-toggle="dropdown">Search <span class="caret"></span></a>
                <ul class="dropdown-menu">
                    <li><a href="/search/ipv4">IPv4 Search</a></li>
                    <li><a href="/search/ipv6">IPv6 Search</a></li>
                    <li><a href="/search/mac">MAC Search</a></li>
                </ul>
            </li>
        </ul>
        <ul class="nav navbar-nav navbar-right">
            <li><a href="/logout"><i class="glyphicon glyphicon-log-out"></i> Logout</a></li>
        </ul>
    </div>
</nav>
'''


@app.route('/overview')
@login_required
def overview():
    up = sum(1 for d in DEVICES if d['status'] == 1)
    down = sum(1 for d in DEVICES if d['status'] == 0)
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>LibreNMS - Overview</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #060606; color: #ccc; padding-top: 60px; }}
        .panel {{ background-color: #1a1a2e; border-color: #333; }}
        .panel-heading {{ background-color: #16213e !important; color: #e74c3c !important; }}
        .table {{ color: #ccc; }}
    </style>
</head>
<body>
    {nav}
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-3">
                <div class="panel panel-default">
                    <div class="panel-heading">Device Summary</div>
                    <div class="panel-body">
                        <p><span class="label label-success">Up: {up}</span></p>
                        <p><span class="label label-danger">Down: {down}</span></p>
                        <p><strong>Total: {total}</strong></p>
                    </div>
                </div>
            </div>
            <div class="col-md-9">
                <div class="panel panel-default">
                    <div class="panel-heading">Recent Alerts</div>
                    <div class="panel-body">
                        <table class="table table-condensed">
                            <tr><th>Time</th><th>Device</th><th>Alert</th></tr>
                            <tr><td>2024-01-15 08:23:11</td><td>fw-edge01</td><td><span class="label label-danger">Device Down</span></td></tr>
                            <tr><td>2024-01-15 07:45:00</td><td>core-rtr01</td><td><span class="label label-warning">High CPU Usage</span></td></tr>
                            <tr><td>2024-01-14 22:10:33</td><td>sw-dist01</td><td><span class="label label-info">Port Flap on Gi0/24</span></td></tr>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''.format(nav=NAV_BAR, up=up, down=down, total=len(DEVICES))


@app.route('/devices')
@login_required
def devices():
    rows = ''
    for d in DEVICES:
        status = '<span class="label label-success">Up</span>' if d['status'] == 1 else '<span class="label label-danger">Down</span>'
        days = d['uptime'] // 86400
        rows += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{} days</td></tr>'.format(
            d['device_id'], d['hostname'], d['os'], status, days)
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>LibreNMS - Devices</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #060606; color: #ccc; padding-top: 60px; }}
        .panel {{ background-color: #1a1a2e; border-color: #333; }}
        .panel-heading {{ background-color: #16213e !important; color: #e74c3c !important; }}
        .table {{ color: #ccc; }}
        .table-striped > tbody > tr:nth-child(odd) {{ background-color: #0f3460; }}
    </style>
</head>
<body>
    {nav}
    <div class="container-fluid">
        <div class="panel panel-default">
            <div class="panel-heading">All Devices</div>
            <div class="panel-body">
                <table class="table table-striped table-condensed">
                    <thead><tr><th>ID</th><th>Hostname</th><th>OS</th><th>Status</th><th>Uptime</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>'''.format(nav=NAV_BAR, rows=rows)


@app.route('/search/ipv4', methods=['GET', 'POST'])
@login_required
def search_ipv4():
    address = ''
    results_html = ''
    if request.method == 'POST':
        address = request.form.get('address', '')
        results_html = '<tr><td colspan="4">No IPv4 results found for: {}</td></tr>'.format(cgi.escape(address))
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>LibreNMS - IPv4 Search</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #060606; color: #ccc; padding-top: 60px; }}
        .panel {{ background-color: #1a1a2e; border-color: #333; }}
        .panel-heading {{ background-color: #16213e !important; color: #e74c3c !important; }}
        .table {{ color: #ccc; }}
    </style>
</head>
<body>
    {nav}
    <div class="container-fluid">
        <div class="panel panel-default">
            <div class="panel-heading">IPv4 Address Search</div>
            <div class="panel-body">
                <form method="post" class="form-inline" style="margin-bottom:15px;">
                    <div class="form-group">
                        <input type="text" name="address" id="address" class="form-control" placeholder="IPv4 Address" value="{address}">
                    </div>
                    <button type="submit" class="btn btn-primary">Search</button>
                </form>
                <table class="table table-condensed">
                    <thead><tr><th>Address</th><th>Device</th><th>Interface</th><th>Prefix</th></tr></thead>
                    <tbody>{results}</tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>'''.format(nav=NAV_BAR, address=cgi.escape(address, quote=True), results=results_html)


@app.route('/search/mac', methods=['GET', 'POST'])
@login_required
def search_mac():
    address = ''
    results_html = ''
    if request.method == 'POST':
        address = request.form.get('address', '')
        results_html = '<tr><td colspan="4">No MAC address results found for: {}</td></tr>'.format(cgi.escape(address))
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>LibreNMS - MAC Search</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #060606; color: #ccc; padding-top: 60px; }}
        .panel {{ background-color: #1a1a2e; border-color: #333; }}
        .panel-heading {{ background-color: #16213e !important; color: #e74c3c !important; }}
        .table {{ color: #ccc; }}
    </style>
</head>
<body>
    {nav}
    <div class="container-fluid">
        <div class="panel panel-default">
            <div class="panel-heading">MAC Address Search</div>
            <div class="panel-body">
                <form method="post" class="form-inline" style="margin-bottom:15px;">
                    <div class="form-group">
                        <input type="text" name="address" id="address" class="form-control" placeholder="MAC Address" value="{address}">
                    </div>
                    <button type="submit" class="btn btn-primary">Search</button>
                </form>
                <table class="table table-condensed">
                    <thead><tr><th>MAC</th><th>Device</th><th>Interface</th><th>VLAN</th></tr></thead>
                    <tbody>{results}</tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>'''.format(nav=NAV_BAR, address=cgi.escape(address, quote=True), results=results_html)


@app.route('/search/ipv6', methods=['GET', 'POST'])
@login_required
def search_ipv6():
    address = ''
    interface = ''
    results_html = ''

    if request.method == 'POST':
        # Get user-supplied values from POST data
        address = request.form.get('address', '')
        interface = request.form.get('interface', '')

        # Search the IPv6 data
        matches = []
        for entry in IPV6_DATA:
            if address and address.lower() not in entry['ipv6_address'].lower():
                continue
            if interface and interface.lower() not in entry['ifName'].lower():
                continue
            matches.append(entry)

        if matches:
            for m in matches:
                results_html += '<tr><td>{}</td><td>{}</td><td>{}</td><td>/{}</td></tr>'.format(
                    cgi.escape(m['ipv6_address']),
                    cgi.escape(m['hostname']),
                    cgi.escape(m['ifName']),
                    m['ipv6_prefixlen']
                )
        else:
            results_html = '<tr><td colspan="4">No results found</td></tr>'

    # Build the search results page with the form values populated
    page = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>LibreNMS - IPv6 Address Search</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #060606; color: #ccc; padding-top: 60px; }}
        .panel {{ background-color: #1a1a2e; border-color: #333; }}
        .panel-heading {{ background-color: #16213e !important; color: #e74c3c !important; }}
        .table {{ color: #ccc; }}
        .table-striped > tbody > tr:nth-child(odd) {{ background-color: #0f3460; }}
    </style>
</head>
<body>
    <div class="container-fluid" style="padding-top:20px;">
        <div class="panel panel-default">
            <div class="panel-heading">IPv6 Address Search</div>
            <div class="panel-body">
                <form method="post" id="searchform" class="form-inline" style="margin-bottom:15px;">
                    <div class="form-group">
                        <label for="address">Address</label>
                        <input type="text" name="address" id="address" class="form-control" placeholder="IPv6 Address" value="''' + address + '''" />
                    </div>
                    <div class="form-group" style="margin-left:10px;">
                        <label for="interface">Interface</label>
                        <input type="text" name="interface" id="interface" class="form-control" placeholder="Interface" value="''' + interface + '''" />
                    </div>
                    <button type="submit" class="btn btn-primary" style="margin-left:10px;">Search</button>
                </form>
                <table class="table table-striped table-condensed">
                    <thead><tr><th>IPv6 Address</th><th>Device</th><th>Interface</th><th>Prefix Length</th></tr></thead>
                    <tbody>''' + results_html + '''</tbody>
                </table>
            </div>
        </div>
    </div>
    <script>
        var searchData = {
            interface: \'''' + interface + '''\',
            address: \'''' + address + '''\'
        };
    </script>
</body>
</html>'''

    # Server-side XSS check: render the page in PhantomJS to detect if JS executed
    result = check_xss(page)
    if result == 'XSS':
        # XSS confirmed - return a page that includes the flag
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>LibreNMS - IPv6 Address Search</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #060606; color: #ccc; padding-top: 60px; }}
        .alert-success {{ background-color: #1a4731; border-color: #27ae60; color: #2ecc71; }}
    </style>
</head>
<body>
    <div class="container-fluid" style="padding-top:80px;">
        <div class="alert alert-success" style="max-width:600px;margin:0 auto;text-align:center;">
            <h4>{f}</h4>
        </div>
    </div>
</body>
</html>'''.format(f=flag)

    return page


@app.route('/ping')
def health_check():
    return 'ok'


if __name__ == '__main__':
    app.run(debug=False)
