# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect, session
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import hashlib
import time

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_value = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = os.urandom(24).encode('hex')

phantom = Phantom()

# Simulated device data (LibreNMS-like network monitoring)
DEVICES = [
    {"device_id": 1, "hostname": "core-rtr01.dc1.internal", "sysName": "core-rtr01", "os": "iosxe", "ipv6_addresses": ["2001:db8::1", "fe80::1"], "ports": ["GigabitEthernet0/0", "GigabitEthernet0/1", "Loopback0"]},
    {"device_id": 2, "hostname": "dist-sw01.dc1.internal", "sysName": "dist-sw01", "os": "nxos", "ipv6_addresses": ["2001:db8::2", "fe80::2"], "ports": ["Ethernet1/1", "Ethernet1/2", "Vlan100"]},
    {"device_id": 3, "hostname": "access-sw01.dc2.internal", "sysName": "access-sw01", "os": "ios", "ipv6_addresses": ["2001:db8:1::10", "fe80::a"], "ports": ["FastEthernet0/1", "FastEthernet0/2", "Vlan200"]},
    {"device_id": 4, "hostname": "fw01.dc1.internal", "sysName": "fw01", "os": "asa", "ipv6_addresses": ["2001:db8::ff", "fe80::ff"], "ports": ["outside", "inside", "dmz"]},
    {"device_id": 5, "hostname": "srv-mon01.dc1.internal", "sysName": "srv-mon01", "os": "linux", "ipv6_addresses": ["2001:db8::100", "::1"], "ports": ["eth0", "eth1"]},
]

USERS = {
    "admin": {"password": "admin", "level": 10, "realname": "Network Admin"},
    "operator": {"password": "operator123", "level": 5, "realname": "NOC Operator"},
}


def check_xss_execution(html_content):
    """Render HTML content through headless browser for validation."""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        result = ""
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass
    return result


def require_auth(f):
    """Decorator to require authentication for endpoints."""
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated


@app.route('/')
def index():
    if 'user' in session:
        return redirect('/devices')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session['level'] = USERS[username]['level']
            session['realname'] = USERS[username]['realname']
            return redirect('/devices')
        error = "Invalid credentials"
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LibreNMS - Login</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #060606; color: #c5c5c5; }}
        .login-panel {{ margin-top: 120px; }}
        .panel {{ background-color: #1a1a2e; border-color: #333; }}
        .panel-heading {{ background-color: #16213e !important; border-color: #333; color: #e94560; }}
        .panel-body {{ background-color: #1a1a2e; }}
        .form-control {{ background-color: #0f3460; border-color: #333; color: #e5e5e5; }}
        .btn-primary {{ background-color: #e94560; border-color: #e94560; }}
        .btn-primary:hover {{ background-color: #c81d4e; border-color: #c81d4e; }}
        .brand-title {{ color: #e94560; text-align: center; margin-bottom: 30px; font-size: 28px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-md-4 col-md-offset-4">
                <div class="brand-title"><strong>Libre</strong>NMS</div>
                <div class="login-panel panel panel-default">
                    <div class="panel-heading"><h3 class="panel-title">Sign In</h3></div>
                    <div class="panel-body">
                        {error_html}
                        <form method="post" action="/login">
                            <fieldset>
                                <div class="form-group">
                                    <input class="form-control" placeholder="Username" name="username" type="text" autofocus>
                                </div>
                                <div class="form-group">
                                    <input class="form-control" placeholder="Password" name="password" type="password">
                                </div>
                                <button type="submit" class="btn btn-primary btn-block">Login</button>
                            </fieldset>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''.format(error_html='<div class="alert alert-danger">' + cgi.escape(error) + '</div>' if error else '')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/devices')
@require_auth
def devices():
    rows = ""
    for d in DEVICES:
        rows += '<tr><td>{0}</td><td><a href="/device/{0}">{1}</a></td><td>{2}</td><td>{3}</td><td>{4}</td></tr>\n'.format(
            d['device_id'], cgi.escape(d['hostname']), cgi.escape(d['os']),
            cgi.escape(d['sysName']), ', '.join(d['ipv6_addresses'][:1])
        )
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Devices - LibreNMS</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #060606; color: #c5c5c5; }}
        .navbar {{ background-color: #1a1a2e; border-color: #333; }}
        .navbar-brand {{ color: #e94560 !important; }}
        .navbar-nav > li > a {{ color: #c5c5c5 !important; }}
        .navbar-nav > li > a:hover {{ color: #e94560 !important; }}
        .table {{ color: #c5c5c5; }}
        .table > thead > tr > th {{ border-color: #333; color: #e94560; }}
        .table > tbody > tr > td {{ border-color: #222; }}
        .panel {{ background-color: #1a1a2e; border-color: #333; }}
        .panel-heading {{ background-color: #16213e !important; color: #e94560; border-color: #333; }}
        a {{ color: #5dade2; }}
        a:hover {{ color: #e94560; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="/devices"><strong>Libre</strong>NMS</a>
            </div>
            <ul class="nav navbar-nav">
                <li><a href="/devices">Devices</a></li>
                <li><a href="/search/ipv6">Search IPv6</a></li>
                <li><a href="/health">Health</a></li>
            </ul>
            <ul class="nav navbar-nav navbar-right">
                <li><a href="/logout">{user} (Logout)</a></li>
            </ul>
        </div>
    </nav>
    <div class="container-fluid">
        <div class="panel panel-default">
            <div class="panel-heading"><h3 class="panel-title">All Devices</h3></div>
            <div class="panel-body">
                <table class="table table-hover table-condensed">
                    <thead><tr><th>ID</th><th>Hostname</th><th>OS</th><th>sysName</th><th>IPv6</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>'''.format(user=cgi.escape(session.get('user', '')), rows=rows)


@app.route('/device/<int:device_id>')
@require_auth
def device_detail(device_id):
    device = None
    for d in DEVICES:
        if d['device_id'] == device_id:
            device = d
            break
    if not device:
        return "Device not found", 404
    
    ipv6_rows = ""
    for addr in device['ipv6_addresses']:
        ipv6_rows += '<tr><td>{0}</td><td>{1}</td></tr>\n'.format(cgi.escape(addr), cgi.escape(device['ports'][0]))
    
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{hostname} - LibreNMS</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #060606; color: #c5c5c5; }}
        .navbar {{ background-color: #1a1a2e; border-color: #333; }}
        .navbar-brand {{ color: #e94560 !important; }}
        .navbar-nav > li > a {{ color: #c5c5c5 !important; }}
        .table {{ color: #c5c5c5; }}
        .table > thead > tr > th {{ border-color: #333; color: #e94560; }}
        .table > tbody > tr > td {{ border-color: #222; }}
        .panel {{ background-color: #1a1a2e; border-color: #333; }}
        .panel-heading {{ background-color: #16213e !important; color: #e94560; border-color: #333; }}
        a {{ color: #5dade2; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="/devices"><strong>Libre</strong>NMS</a>
            </div>
            <ul class="nav navbar-nav">
                <li><a href="/devices">Devices</a></li>
                <li><a href="/search/ipv6">Search IPv6</a></li>
                <li><a href="/health">Health</a></li>
            </ul>
            <ul class="nav navbar-nav navbar-right">
                <li><a href="/logout">{user} (Logout)</a></li>
            </ul>
        </div>
    </nav>
    <div class="container-fluid">
        <div class="panel panel-default">
            <div class="panel-heading"><h3 class="panel-title">{hostname}</h3></div>
            <div class="panel-body">
                <dl class="dl-horizontal">
                    <dt>Device ID</dt><dd>{device_id}</dd>
                    <dt>Hostname</dt><dd>{hostname}</dd>
                    <dt>OS</dt><dd>{os}</dd>
                    <dt>sysName</dt><dd>{sysname}</dd>
                </dl>
                <h4>IPv6 Addresses</h4>
                <table class="table table-condensed">
                    <thead><tr><th>Address</th><th>Interface</th></tr></thead>
                    <tbody>{ipv6_rows}</tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>'''.format(
        user=cgi.escape(session.get('user', '')),
        hostname=cgi.escape(device['hostname']),
        device_id=device['device_id'],
        os=cgi.escape(device['os']),
        sysname=cgi.escape(device['sysName']),
        ipv6_rows=ipv6_rows
    )


@app.route('/search/ipv6', methods=['GET', 'POST'])
@require_auth
def search_ipv6():
    """IPv6 address search page with form-based filtering."""
    address = ""
    interface = ""
    results_html = ""
    
    if request.method == 'POST':
        address = request.form.get('address', '')
        interface = request.form.get('interface', '')
        
        # Search through devices for matching IPv6 addresses/interfaces
        for device in DEVICES:
            for addr in device['ipv6_addresses']:
                for port in device['ports']:
                    addr_match = (address == "" or address.lower() in addr.lower())
                    iface_match = (interface == "" or interface.lower() in port.lower())
                    if addr_match and iface_match:
                        results_html += '<tr><td>{0}</td><td><a href="/device/{1}">{2}</a></td><td>{3}</td><td>{4}</td></tr>\n'.format(
                            cgi.escape(addr), device['device_id'],
                            cgi.escape(device['hostname']),
                            cgi.escape(port),
                            cgi.escape(device['os'])
                        )

    # Build the search page with current form values and results
    page_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Search IPv6 - LibreNMS</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap.min.css">
    <style>
        body { background-color: #060606; color: #c5c5c5; }
        .navbar { background-color: #1a1a2e; border-color: #333; }
        .navbar-brand { color: #e94560 !important; }
        .navbar-nav > li > a { color: #c5c5c5 !important; }
        .navbar-nav > li > a:hover { color: #e94560 !important; }
        .table { color: #c5c5c5; }
        .table > thead > tr > th { border-color: #333; color: #e94560; }
        .table > tbody > tr > td { border-color: #222; }
        .panel { background-color: #1a1a2e; border-color: #333; }
        .panel-heading { background-color: #16213e !important; color: #e94560; border-color: #333; }
        .form-control { background-color: #0f3460; border-color: #333; color: #e5e5e5; }
        .btn-primary { background-color: #e94560; border-color: #e94560; }
        a { color: #5dade2; }
    </style>
</head>
<body>
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="/devices"><strong>Libre</strong>NMS</a>
            </div>
            <ul class="nav navbar-nav">
                <li><a href="/devices">Devices</a></li>
                <li class="active"><a href="/search/ipv6">Search IPv6</a></li>
                <li><a href="/health">Health</a></li>
            </ul>
            <ul class="nav navbar-nav navbar-right">
                <li><a href="/logout">''' + cgi.escape(session.get('user', '')) + ''' (Logout)</a></li>
            </ul>
        </div>
    </nav>
    <div class="container-fluid">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Search IPv6 Addresses</h3>
            </div>
            <div class="panel-body">
                <form method="post" action="/search/ipv6" class="form-inline" id="ipv6-search-form">
                    <div class="form-group" style="margin-right: 10px;">
                        <label for="address" style="margin-right: 5px;">IPv6 Address:</label>
                        <input type="text" name="address" id="address" class="form-control" size="40" placeholder="Enter IPv6 address..." value="''' + address + '''" />
                    </div>
                    <div class="form-group" style="margin-right: 10px;">
                        <label for="interface" style="margin-right: 5px;">Interface:</label>
                        <input type="text" name="interface" id="interface" class="form-control" size="30" placeholder="Interface name..." value="''' + interface + '''" />
                    </div>
                    <button type="submit" class="btn btn-primary">Search</button>
                </form>
            </div>
        </div>
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Results</h3>
            </div>
            <div class="panel-body">
                <table class="table table-hover table-condensed" id="ipv6-results">
                    <thead>
                        <tr>
                            <th>IPv6 Address</th>
                            <th>Device</th>
                            <th>Interface</th>
                            <th>OS</th>
                        </tr>
                    </thead>
                    <tbody>
                        ''' + results_html + '''
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <script src="https://code.jquery.com/jquery-2.2.4.min.js"></script>
    <script>
        // AJAX search functionality
        var searchConfig = {
            url: '/ajax/search/ipv6',
            data: {
                interface: \'''' + interface + '''\',
                address: \'''' + address + '''\'
            }
        };

        $(document).ready(function() {
            if (searchConfig.data.address || searchConfig.data.interface) {
                console.log('Search performed for: ' + searchConfig.data.address);
            }
        });
    </script>
</body>
</html>'''

    # Content security validation
    result = check_xss_execution(page_html)
    
    if result == 'XSS':
        page_html = page_html.replace('</tbody>', results_html + '</tbody>')
        page_html = page_html.replace('</body>',
            '<div class="container-fluid"><div class="alert alert-success">' + flag_value + '</div></div></body>')
    
    return page_html


@app.route('/ajax/search/ipv6', methods=['POST'])
@require_auth
def ajax_search_ipv6():
    """AJAX endpoint for IPv6 search - returns JSON results."""
    address = request.form.get('address', '')
    interface = request.form.get('interface', '')
    results = []
    for device in DEVICES:
        for addr in device['ipv6_addresses']:
            for port in device['ports']:
                addr_match = (address == "" or address.lower() in addr.lower())
                iface_match = (interface == "" or interface.lower() in port.lower())
                if addr_match and iface_match:
                    results.append({
                        "address": addr,
                        "hostname": device['hostname'],
                        "device_id": device['device_id'],
                        "interface": port,
                        "os": device['os']
                    })
    return Response(json.dumps(results), mimetype='application/json')


@app.route('/health')
@require_auth
def health_overview():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Health - LibreNMS</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #060606; color: #c5c5c5; }}
        .navbar {{ background-color: #1a1a2e; border-color: #333; }}
        .navbar-brand {{ color: #e94560 !important; }}
        .navbar-nav > li > a {{ color: #c5c5c5 !important; }}
        .table {{ color: #c5c5c5; }}
        .table > thead > tr > th {{ border-color: #333; color: #e94560; }}
        .table > tbody > tr > td {{ border-color: #222; }}
        .panel {{ background-color: #1a1a2e; border-color: #333; }}
        .panel-heading {{ background-color: #16213e !important; color: #e94560; border-color: #333; }}
        .label {{ font-size: 90%; }}
        a {{ color: #5dade2; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="/devices"><strong>Libre</strong>NMS</a>
            </div>
            <ul class="nav navbar-nav">
                <li><a href="/devices">Devices</a></li>
                <li><a href="/search/ipv6">Search IPv6</a></li>
                <li class="active"><a href="/health">Health</a></li>
            </ul>
            <ul class="nav navbar-nav navbar-right">
                <li><a href="/logout">{user} (Logout)</a></li>
            </ul>
        </div>
    </nav>
    <div class="container-fluid">
        <div class="panel panel-default">
            <div class="panel-heading"><h3 class="panel-title">Health Overview</h3></div>
            <div class="panel-body">
                <table class="table table-condensed">
                    <thead><tr><th>Device</th><th>Status</th><th>Uptime</th><th>Last Polled</th></tr></thead>
                    <tbody>
                        <tr><td>core-rtr01.dc1.internal</td><td><span class="label label-success">Up</span></td><td>45d 12h 33m</td><td>2 min ago</td></tr>
                        <tr><td>dist-sw01.dc1.internal</td><td><span class="label label-success">Up</span></td><td>120d 3h 15m</td><td>1 min ago</td></tr>
                        <tr><td>access-sw01.dc2.internal</td><td><span class="label label-warning">Warning</span></td><td>8d 6h 42m</td><td>5 min ago</td></tr>
                        <tr><td>fw01.dc1.internal</td><td><span class="label label-success">Up</span></td><td>200d 18h 9m</td><td>1 min ago</td></tr>
                        <tr><td>srv-mon01.dc1.internal</td><td><span class="label label-success">Up</span></td><td>30d 7h 55m</td><td>3 min ago</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>'''.format(user=cgi.escape(session.get('user', '')))


@app.route('/ping')
def ping():
    return 'ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
