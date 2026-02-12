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
import json

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_data = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = os.urandom(24).encode('hex')

# Simulated device database (LibreNMS-style)
DEVICES = [
    {'device_id': 1, 'hostname': 'core-rtr-01.infra.local', 'sysName': 'core-rtr-01', 'os': 'iosxe', 'ip': '10.0.0.1', 'status': 1, 'uptime': 8640000},
    {'device_id': 2, 'hostname': 'dist-sw-01.infra.local', 'sysName': 'dist-sw-01', 'os': 'nxos', 'ip': '10.0.1.1', 'status': 1, 'uptime': 4320000},
    {'device_id': 3, 'hostname': 'edge-fw-01.infra.local', 'sysName': 'edge-fw-01', 'os': 'asa', 'ip': '10.0.2.1', 'status': 1, 'uptime': 2160000},
    {'device_id': 4, 'hostname': 'access-sw-01.infra.local', 'sysName': 'access-sw-01', 'os': 'ios', 'ip': '10.0.3.1', 'status': 0, 'uptime': 0},
    {'device_id': 5, 'hostname': 'wan-rtr-01.infra.local', 'sysName': 'wan-rtr-01', 'os': 'junos', 'ip': '10.0.4.1', 'status': 1, 'uptime': 6480000},
]

IPV6_ADDRESSES = [
    {'ipv6_address': '2001:db8::1', 'ipv6_prefix_id': 1, 'ifName': 'GigabitEthernet0/0', 'device_id': 1, 'hostname': 'core-rtr-01.infra.local'},
    {'ipv6_address': '2001:db8:1::1', 'ipv6_prefix_id': 2, 'ifName': 'Vlan100', 'device_id': 2, 'hostname': 'dist-sw-01.infra.local'},
    {'ipv6_address': 'fd00::1', 'ipv6_prefix_id': 3, 'ifName': 'Management0', 'device_id': 3, 'hostname': 'edge-fw-01.infra.local'},
    {'ipv6_address': '2001:db8:2::10', 'ipv6_prefix_id': 4, 'ifName': 'GigabitEthernet1/0/1', 'device_id': 4, 'hostname': 'access-sw-01.infra.local'},
    {'ipv6_address': 'fe80::1', 'ipv6_prefix_id': 5, 'ifName': 'ge-0/0/0', 'device_id': 5, 'hostname': 'wan-rtr-01.infra.local'},
    {'ipv6_address': '2001:db8:3::ff', 'ipv6_prefix_id': 6, 'ifName': 'Loopback0', 'device_id': 1, 'hostname': 'core-rtr-01.infra.local'},
    {'ipv6_address': '2001:db8:a::5', 'ipv6_prefix_id': 7, 'ifName': 'Ethernet1/1', 'device_id': 2, 'hostname': 'dist-sw-01.infra.local'},
]

# User database for authentication
USERS = {
    'admin': {'password': hashlib.sha256('admin').hexdigest(), 'level': 10, 'realname': 'Admin User'},
    'operator': {'password': hashlib.sha256('operator').hexdigest(), 'level': 5, 'realname': 'Network Operator'},
}


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


def check_xss(page, msg):
    proc = subprocess.Popen(["timeout", "8", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    result = ''
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        output = proc.stdout.read()
        for line in output.strip().split('\n'):
            line = line.strip()
            if line and line != 'success' and line != 'fail':
                result = line
                break
    except Exception:
        result = ''
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass

    return result


@app.route('/ping')
def ping():
    return 'ok', 200

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
        pw_hash = hashlib.sha256(password).hexdigest()

        if username in USERS and USERS[username]['password'] == pw_hash:
            session['username'] = username
            session['level'] = USERS[username]['level']
            session['realname'] = USERS[username]['realname']
            return redirect('/overview')
        else:
            error = 'Invalid credentials'

    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LibreNMS - Login</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #2c3e50; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
        .login-box {{ background: #fff; padding: 40px; border-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,0.3); width: 350px; }}
        .login-box h1 {{ color: #e74c3c; margin: 0 0 30px; font-size: 24px; text-align: center; }}
        .login-box h1 span {{ color: #333; }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; margin-bottom: 5px; color: #555; font-size: 14px; }}
        .form-group input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 3px; font-size: 14px; box-sizing: border-box; }}
        .btn {{ width: 100%; padding: 10px; background: #337ab7; color: #fff; border: none; border-radius: 3px; font-size: 16px; cursor: pointer; }}
        .btn:hover {{ background: #286090; }}
        .error {{ color: #e74c3c; font-size: 13px; margin-bottom: 15px; }}
    </style>
</head>
<body>
    <div class="login-box">
        <h1>Libre<span>NMS</span></h1>
        {error}
        <form method="post">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" autofocus>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password">
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
    </div>
</body>
</html>'''.format(error='<p class="error">' + cgi.escape(error) + '</p>' if error else '')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/overview')
@login_required
def overview():
    device_rows = ''
    for d in DEVICES:
        status_class = 'up' if d['status'] == 1 else 'down'
        status_text = 'Up' if d['status'] == 1 else 'Down'
        uptime_str = '{0}d'.format(d['uptime'] // 86400) if d['uptime'] > 0 else '-'
        device_rows += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td class="{4}">{5}</td><td>{6}</td></tr>\n'.format(
            d['device_id'], cgi.escape(d['hostname']), cgi.escape(d['sysName']), d['ip'], status_class, status_text, uptime_str)

    return get_page_template('Overview', '''
        <div class="content-header"><h2>Network Overview</h2></div>
        <div class="panel">
            <div class="panel-heading">Devices</div>
            <table class="table">
                <thead><tr><th>ID</th><th>Hostname</th><th>sysName</th><th>IP</th><th>Status</th><th>Uptime</th></tr></thead>
                <tbody>{0}</tbody>
            </table>
        </div>
    '''.format(device_rows))


@app.route('/devices')
@login_required
def devices():
    device_rows = ''
    for d in DEVICES:
        status_class = 'up' if d['status'] == 1 else 'down'
        status_text = 'Up' if d['status'] == 1 else 'Down'
        device_rows += '<tr><td><a href="/device/{0}">{1}</a></td><td>{2}</td><td>{3}</td><td class="{4}">{5}</td></tr>\n'.format(
            d['device_id'], cgi.escape(d['hostname']), cgi.escape(d['os']), d['ip'], status_class, status_text)

    return get_page_template('Devices', '''
        <div class="content-header"><h2>All Devices</h2></div>
        <div class="panel">
            <table class="table">
                <thead><tr><th>Device</th><th>OS</th><th>IP</th><th>Status</th></tr></thead>
                <tbody>{0}</tbody>
            </table>
        </div>
    '''.format(device_rows))


@app.route('/device/<int:device_id>')
@login_required
def device_detail(device_id):
    device = None
    for d in DEVICES:
        if d['device_id'] == device_id:
            device = d
            break
    if not device:
        return get_page_template('Device Not Found', '<div class="content-header"><h2>Device not found</h2></div>'), 404

    status_text = 'Up' if device['status'] == 1 else 'Down'
    return get_page_template('Device - ' + cgi.escape(device['hostname']), '''
        <div class="content-header"><h2>{0}</h2></div>
        <div class="panel">
            <div class="panel-heading">Device Details</div>
            <table class="table">
                <tr><th>Hostname</th><td>{0}</td></tr>
                <tr><th>sysName</th><td>{1}</td></tr>
                <tr><th>OS</th><td>{2}</td></tr>
                <tr><th>IP Address</th><td>{3}</td></tr>
                <tr><th>Status</th><td>{4}</td></tr>
                <tr><th>Uptime</th><td>{5} days</td></tr>
            </table>
        </div>
    '''.format(cgi.escape(device['hostname']), cgi.escape(device['sysName']),
               cgi.escape(device['os']), device['ip'], status_text,
               device['uptime'] // 86400))


@app.route('/search/ipv4')
@login_required
def search_ipv4():
    return get_page_template('Search IPv4', '''
        <div class="content-header"><h2>IPv4 Address Search</h2></div>
        <div class="panel">
            <div class="panel-heading">Search</div>
            <div class="panel-body">
                <form method="get">
                    <div class="form-row">
                        <label>Address</label>
                        <input type="text" name="address" id="address" class="form-input" placeholder="IPv4 Address" />
                    </div>
                    <button type="submit" class="btn-search">Search</button>
                </form>
                <p class="text-muted">Enter an IPv4 address to search for matching entries.</p>
            </div>
        </div>
    ''')


@app.route('/search/ipv6', methods=['GET', 'POST'])
@login_required
def search_ipv6():
    address_val = ''
    interface_val = ''
    results_html = ''

    if request.method == 'POST':
        address_val = request.form.get('address', '')
        interface_val = request.form.get('interface', '')

        results = []
        for entry in IPV6_ADDRESSES:
            match = True
            if address_val:
                if address_val.lower() not in entry['ipv6_address'].lower():
                    match = False
            if interface_val:
                if interface_val.lower() not in entry['ifName'].lower():
                    match = False
            if match:
                results.append(entry)

        if results:
            rows = ''
            for r in results:
                rows += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>\n'.format(
                    cgi.escape(r['hostname']), cgi.escape(r['ipv6_address']),
                    cgi.escape(r['ifName']), r['ipv6_prefix_id'])
            results_html = '''
                <div class="panel" style="margin-top:20px;">
                    <div class="panel-heading">Results</div>
                    <table class="table">
                        <thead><tr><th>Hostname</th><th>IPv6 Address</th><th>Interface</th><th>Prefix ID</th></tr></thead>
                        <tbody>{0}</tbody>
                    </table>
                </div>
            '''.format(rows)
        elif address_val or interface_val:
            results_html = '<div class="panel" style="margin-top:20px;"><div class="panel-body"><p>No results found.</p></div></div>'

    page_content = '''
        <div class="content-header"><h2>IPv6 Address Search</h2></div>
        <div class="panel">
            <div class="panel-heading">Search</div>
            <div class="panel-body">
                <form method="post" id="ipv6-search-form">
                    <div class="form-row">
                        <label for="address">Address</label>
                        <input type="text" name="address" id="address" class="form-input" placeholder="IPv6 Address" value="''' + address_val + '''" />
                    </div>
                    <div class="form-row">
                        <label for="interface">Interface</label>
                        <input type="text" name="interface" id="interface" class="form-input" placeholder="Interface name" value="''' + interface_val + '''" />
                    </div>
                    <button type="submit" class="btn-search">Search</button>
                </form>
            </div>
        </div>
        ''' + results_html + '''
        <script type="text/javascript">
        var searchData = {
            interface: \'''' + interface_val + '''\',
            address: \'''' + address_val + '''\'
        };
        function doSearch() {
            var form = document.getElementById('ipv6-search-form');
            if (form) {
                form.submit();
            }
        }
        </script>
    '''

    # Render the page with the form
    full_page = get_page_template('Search IPv6 Addresses', page_content)

    # Check for XSS via PhantomJS
    combined_input = address_val + interface_val
    if combined_input:
        xss_result = check_xss(full_page, combined_input)
        if xss_result == 'XSS':
            results_html += '<div class="panel" style="margin-top:20px;"><div class="panel-body"><p class="text-muted">{0}</p></div></div>'.format(flag_data)
            # Rebuild the page with the flag in results
            page_content_with_flag = '''
                <div class="content-header"><h2>IPv6 Address Search</h2></div>
                <div class="panel">
                    <div class="panel-heading">Search</div>
                    <div class="panel-body">
                        <form method="post" id="ipv6-search-form">
                            <div class="form-row">
                                <label for="address">Address</label>
                                <input type="text" name="address" id="address" class="form-input" placeholder="IPv6 Address" value="''' + address_val + '''" />
                            </div>
                            <div class="form-row">
                                <label for="interface">Interface</label>
                                <input type="text" name="interface" id="interface" class="form-input" placeholder="Interface name" value="''' + interface_val + '''" />
                            </div>
                            <button type="submit" class="btn-search">Search</button>
                        </form>
                    </div>
                </div>
                ''' + results_html + '''
                <script type="text/javascript">
                var searchData = {
                    interface: \'''' + interface_val + '''\',
                    address: \'''' + address_val + '''\'
                };
                function doSearch() {
                    var form = document.getElementById('ipv6-search-form');
                    if (form) { form.submit(); }
                }
                </script>
            '''
            full_page = get_page_template('Search IPv6 Addresses', page_content_with_flag)

    response = make_response(full_page)
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/search/mac')
@login_required
def search_mac():
    return get_page_template('Search MAC', '''
        <div class="content-header"><h2>MAC Address Search</h2></div>
        <div class="panel">
            <div class="panel-heading">Search</div>
            <div class="panel-body">
                <form method="get">
                    <div class="form-row">
                        <label>MAC Address</label>
                        <input type="text" name="mac" class="form-input" placeholder="MAC Address" />
                    </div>
                    <button type="submit" class="btn-search">Search</button>
                </form>
            </div>
        </div>
    ''')


@app.route('/alerts')
@login_required
def alerts():
    return get_page_template('Alerts', '''
        <div class="content-header"><h2>Alert Log</h2></div>
        <div class="panel">
            <div class="panel-heading">Recent Alerts</div>
            <table class="table">
                <thead><tr><th>Time</th><th>Severity</th><th>Device</th><th>Message</th></tr></thead>
                <tbody>
                    <tr><td>2023-09-15 14:22:01</td><td class="down">Critical</td><td>access-sw-01.infra.local</td><td>Device is down</td></tr>
                    <tr><td>2023-09-15 13:15:33</td><td class="warning">Warning</td><td>core-rtr-01.infra.local</td><td>CPU usage above 80%</td></tr>
                    <tr><td>2023-09-15 10:02:17</td><td class="up">OK</td><td>dist-sw-01.infra.local</td><td>Interface Ethernet1/1 recovered</td></tr>
                </tbody>
            </table>
        </div>
    ''')


@app.route('/health')
@login_required
def health():
    return get_page_template('Health', '''
        <div class="content-header"><h2>Health Summary</h2></div>
        <div class="panel">
            <div class="panel-heading">System Health</div>
            <div class="panel-body">
                <div class="health-grid">
                    <div class="health-card"><h3>Devices</h3><p class="up">4 Up</p><p class="down">1 Down</p></div>
                    <div class="health-card"><h3>Ports</h3><p class="up">127 Up</p><p class="warning">3 Errored</p></div>
                    <div class="health-card"><h3>Services</h3><p class="up">12 OK</p><p class="warning">1 Warning</p></div>
                </div>
            </div>
        </div>
    ''')


@app.route('/settings')
@login_required
def settings():
    if session.get('level', 0) < 10:
        return get_page_template('Access Denied', '<div class="content-header"><h2>Access Denied</h2><p>You need administrator privileges.</p></div>'), 403

    return get_page_template('Global Settings', '''
        <div class="content-header"><h2>Global Settings</h2></div>
        <div class="panel">
            <div class="panel-heading">General</div>
            <div class="panel-body">
                <table class="table">
                    <tr><th>Site Name</th><td>LibreNMS</td></tr>
                    <tr><th>Base URL</th><td>http://localhost</td></tr>
                    <tr><th>Poller Interval</th><td>300 seconds</td></tr>
                    <tr><th>Discovery Interval</th><td>21600 seconds</td></tr>
                    <tr><th>Alert Transports</th><td>Email, Slack</td></tr>
                </table>
            </div>
        </div>
    ''')


def get_page_template(title, content):
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LibreNMS :: {title}</title>
    <script src="/static/js/jquery.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #ecf0f1; color: #333; }}
        .navbar {{ background: #2c3e50; color: #fff; padding: 0 20px; display: flex; align-items: center; height: 50px; }}
        .navbar .brand {{ color: #e74c3c; font-size: 18px; font-weight: bold; margin-right: 30px; text-decoration: none; }}
        .navbar .brand span {{ color: #fff; }}
        .navbar a {{ color: #bdc3c7; text-decoration: none; padding: 15px 12px; font-size: 13px; }}
        .navbar a:hover {{ color: #fff; }}
        .navbar .nav-right {{ margin-left: auto; }}
        .sidebar {{ position: fixed; top: 50px; left: 0; width: 200px; height: calc(100vh - 50px); background: #34495e; padding-top: 10px; overflow-y: auto; }}
        .sidebar a {{ display: block; color: #bdc3c7; padding: 10px 20px; text-decoration: none; font-size: 13px; border-left: 3px solid transparent; }}
        .sidebar a:hover {{ background: #3d566e; color: #fff; border-left-color: #e74c3c; }}
        .sidebar .section-title {{ color: #7f8c8d; font-size: 11px; text-transform: uppercase; padding: 15px 20px 5px; letter-spacing: 1px; }}
        .main-content {{ margin-left: 200px; padding: 20px; min-height: calc(100vh - 50px); }}
        .content-header h2 {{ color: #2c3e50; margin-bottom: 20px; font-size: 20px; }}
        .panel {{ background: #fff; border-radius: 3px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .panel-heading {{ background: #f7f7f7; padding: 10px 15px; border-bottom: 1px solid #eee; font-weight: 600; font-size: 14px; color: #555; }}
        .panel-body {{ padding: 15px; }}
        .table {{ width: 100%; border-collapse: collapse; }}
        .table th, .table td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 13px; }}
        .table th {{ background: #f9f9f9; font-weight: 600; color: #555; }}
        .table tr:hover {{ background: #f5f5f5; }}
        .up {{ color: #27ae60; }}
        .down {{ color: #e74c3c; }}
        .warning {{ color: #f39c12; }}
        .form-row {{ margin-bottom: 12px; }}
        .form-row label {{ display: block; margin-bottom: 4px; font-weight: 600; font-size: 13px; color: #555; }}
        .form-input {{ width: 100%; max-width: 400px; padding: 8px 10px; border: 1px solid #ccc; border-radius: 3px; font-size: 13px; }}
        .btn-search {{ padding: 8px 20px; background: #337ab7; color: #fff; border: none; border-radius: 3px; cursor: pointer; font-size: 13px; }}
        .btn-search:hover {{ background: #286090; }}
        .text-muted {{ color: #999; font-size: 12px; margin-top: 10px; }}
        .health-grid {{ display: flex; gap: 20px; }}
        .health-card {{ flex: 1; padding: 15px; background: #f9f9f9; border-radius: 3px; text-align: center; }}
        .health-card h3 {{ margin-bottom: 10px; font-size: 14px; color: #555; }}
        a {{ color: #337ab7; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/overview" class="brand">Libre<span>NMS</span></a>
        <a href="/overview">Overview</a>
        <a href="/devices">Devices</a>
        <a href="/alerts">Alerts</a>
        <a href="/health">Health</a>
        <div class="nav-right">
            <a href="/settings">Settings</a>
            <a href="/logout">Logout</a>
        </div>
    </nav>
    <div class="sidebar">
        <div class="section-title">Search</div>
        <a href="/search/ipv4">IPv4 Addresses</a>
        <a href="/search/ipv6">IPv6 Addresses</a>
        <a href="/search/mac">MAC Addresses</a>
        <div class="section-title">Network</div>
        <a href="/devices">All Devices</a>
        <a href="/alerts">Alert Log</a>
        <a href="/health">Health</a>
        <div class="section-title">Admin</div>
        <a href="/settings">Global Settings</a>
    </div>
    <div class="main-content">
        {content}
    </div>
</body>
</html>'''.format(title=title, content=content)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
