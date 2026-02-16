# encoding=utf8

from flask import Flask, request, Response, redirect, session
import subprocess
import os
import cgi
import sys
import hashlib

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = os.urandom(24).encode('hex')

phantom = Phantom()

# Simulated device inventory
DEVICES = [
    {"device_id": 1, "hostname": "core-rtr-01.dc1.internal", "sysName": "core-rtr-01", "os": "ios", "status": 1, "uptime": 8640000},
    {"device_id": 2, "hostname": "dist-sw-02.dc1.internal", "sysName": "dist-sw-02", "os": "nxos", "status": 1, "uptime": 4320000},
    {"device_id": 3, "hostname": "edge-fw-01.dc2.internal", "sysName": "edge-fw-01", "os": "asa", "status": 1, "uptime": 2160000},
    {"device_id": 4, "hostname": "access-sw-03.dc2.internal", "sysName": "access-sw-03", "os": "ios", "status": 0, "uptime": 0},
    {"device_id": 5, "hostname": "wan-rtr-02.dc1.internal", "sysName": "wan-rtr-02", "os": "junos", "status": 1, "uptime": 6480000},
]

NETWORK_V6_ENTRIES = [
    {"device_id": 1, "hostname": "core-rtr-01.dc1.internal", "interface": "GigabitEthernet0/0", "address": "2001:db8:1::1/64", "description": "Uplink to ISP"},
    {"device_id": 1, "hostname": "core-rtr-01.dc1.internal", "interface": "Loopback0", "address": "2001:db8:ffff::1/128", "description": "Loopback"},
    {"device_id": 2, "hostname": "dist-sw-02.dc1.internal", "interface": "Vlan100", "address": "2001:db8:100::1/64", "description": "Management VLAN"},
    {"device_id": 2, "hostname": "dist-sw-02.dc1.internal", "interface": "Vlan200", "address": "2001:db8:200::1/64", "description": "User VLAN"},
    {"device_id": 3, "hostname": "edge-fw-01.dc2.internal", "interface": "GigabitEthernet0/1", "address": "2001:db8:2::1/64", "description": "DMZ Interface"},
    {"device_id": 3, "hostname": "edge-fw-01.dc2.internal", "interface": "GigabitEthernet0/2", "address": "2001:db8:3::1/64", "description": "Inside Interface"},
    {"device_id": 4, "hostname": "access-sw-03.dc2.internal", "interface": "Vlan10", "address": "2001:db8:10::1/64", "description": "Access VLAN"},
    {"device_id": 5, "hostname": "wan-rtr-02.dc1.internal", "interface": "ge-0/0/0", "address": "2001:db8:4::1/64", "description": "WAN Link"},
    {"device_id": 5, "hostname": "wan-rtr-02.dc1.internal", "interface": "Loopback0", "address": "2001:db8:ffff::5/128", "description": "Loopback"},
]

NETWORK_V4_ENTRIES = [
    {"device_id": 1, "hostname": "core-rtr-01.dc1.internal", "interface": "GigabitEthernet0/0", "address": "10.0.0.1/30", "description": "Uplink to ISP"},
    {"device_id": 1, "hostname": "core-rtr-01.dc1.internal", "interface": "Loopback0", "address": "10.255.255.1/32", "description": "Loopback"},
    {"device_id": 2, "hostname": "dist-sw-02.dc1.internal", "interface": "Vlan100", "address": "10.100.0.1/24", "description": "Management VLAN"},
    {"device_id": 3, "hostname": "edge-fw-01.dc2.internal", "interface": "GigabitEthernet0/1", "address": "192.168.1.1/24", "description": "DMZ Interface"},
    {"device_id": 5, "hostname": "wan-rtr-02.dc1.internal", "interface": "ge-0/0/0", "address": "172.16.0.1/30", "description": "WAN Link"},
]

USERS = {
    "admin": {"password_hash": hashlib.sha256("admin").hexdigest(), "level": 10, "realname": "Network Admin"},
    "operator": {"password_hash": hashlib.sha256("operator").hexdigest(), "level": 5, "realname": "NOC Operator"},
}


def get_secret():
    try:
        with open('secret.txt', 'r') as f:
            return f.read().strip()
    except:
        return None


def check_auth():
    return session.get('authenticated', False)


def get_user_level():
    return session.get('level', 0)


def verify_rendered_page(html_content):
    """Send rendered page to headless browser for security validation."""
    proc = subprocess.Popen(["timeout", "8", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn

    output = ''
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        output = proc.stdout.read()
    except Exception:
        output = ''
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    # Check if any line of output contains the XSS marker
    for line in output.strip().split('\n'):
        line = line.strip()
        if line == 'XSS':
            return 'XSS'
        elif line and line not in ('success', 'fail', ''):
            return line

    return ''


def render_login_page(error=None):
    error_html = ''
    if error:
        error_html = '<div class="alert alert-danger">{}</div>'.format(cgi.escape(error))
    return '''<!DOCTYPE html>
<html>
<head>
    <title>NetWatch NMS - Login</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <style>
        body {{ background-color: #2c3e50; font-family: 'Helvetica Neue', sans-serif; }}
        .login-container {{ max-width: 400px; margin: 100px auto; }}
        .login-panel {{ background: #fff; border-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,0.3); }}
        .login-panel .panel-heading {{ background: #1a252f; color: #ecf0f1; text-align: center; padding: 20px; border-radius: 4px 4px 0 0; }}
        .login-panel .panel-heading h3 {{ margin: 0; }}
        .login-panel .panel-body {{ padding: 30px; }}
        .brand-text {{ font-size: 12px; color: #7f8c8d; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="login-container">
        <div class="panel login-panel">
            <div class="panel-heading">
                <h3>NetWatch NMS</h3>
                <div class="brand-text">Network Monitoring System</div>
            </div>
            <div class="panel-body">
                {error}
                <form method="post" action="/login">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="username" class="form-control" placeholder="Username" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password" class="form-control" placeholder="Password" required>
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">Login</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>'''.format(error=error_html)


def render_nav(active=''):
    level = get_user_level()
    username = session.get('username', '')
    nav_items = [
        ('/', 'Overview', 'overview'),
        ('/devices', 'Devices', 'devices'),
        ('/search/ipv4', 'IPv4 Addresses', 'ipv4'),
        ('/search/ipv6', 'IPv6 Addresses', 'ipv6'),
    ]
    if level >= 10:
        nav_items.append(('/alerts', 'Alerts', 'alerts'))

    items_html = ''
    for href, label, key in nav_items:
        cls = ' class="active"' if key == active else ''
        items_html += '<li{}><a href="{}">{}</a></li>'.format(cls, href, label)

    return '''<nav class="navbar navbar-inverse navbar-fixed-top">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="/">NetWatch NMS</a>
            </div>
            <ul class="nav navbar-nav">{items}</ul>
            <ul class="nav navbar-nav navbar-right">
                <li><a href="#">{user}</a></li>
                <li><a href="/logout">Logout</a></li>
            </ul>
        </div>
    </nav>'''.format(items=items_html, user=cgi.escape(username))


def render_page(title, content, active=''):
    return '''<!DOCTYPE html>
<html>
<head>
    <title>{title} - NetWatch NMS</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <script src="https://code.jquery.com/jquery-2.2.4.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <style>
        body {{ padding-top: 70px; background-color: #ecf0f1; font-family: 'Helvetica Neue', sans-serif; }}
        .content-wrapper {{ padding: 20px; }}
        .panel-condensed .panel-heading {{ padding: 8px 15px; }}
        .navbar-inverse {{ background-color: #1a252f; border-color: #1a252f; }}
        .navbar-inverse .navbar-brand {{ color: #3498db; font-weight: bold; }}
        .stat-box {{ text-align: center; padding: 20px; background: #fff; border-radius: 4px; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .stat-box h2 {{ margin: 0; color: #2c3e50; }}
        .stat-box p {{ margin: 5px 0 0; color: #7f8c8d; }}
    </style>
</head>
<body>
    {nav}
    <div class="container-fluid content-wrapper">
        {content}
    </div>
</body>
</html>'''.format(title=title, nav=render_nav(active), content=content)


def filter_entries(entries, device_id=None, interface_filter=None, address_filter=None):
    results = []
    for entry in entries:
        if device_id and str(entry['device_id']) != str(device_id):
            continue
        if interface_filter:
            if interface_filter.endswith('%'):
                prefix = interface_filter[:-1]
                if not entry['interface'].startswith(prefix):
                    continue
            elif entry['interface'] != interface_filter:
                continue
        if address_filter and address_filter not in entry['address']:
            continue
        results.append(entry)
    return results


@app.route('/')
def index():
    if not check_auth():
        return redirect('/login')

    up_count = sum(1 for d in DEVICES if d['status'] == 1)
    down_count = sum(1 for d in DEVICES if d['status'] == 0)

    content = '''
    <div class="row">
        <div class="col-md-3">
            <div class="stat-box">
                <h2>{total}</h2>
                <p>Total Devices</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-box">
                <h2 style="color: #27ae60;">{up}</h2>
                <p>Devices Up</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-box">
                <h2 style="color: #e74c3c;">{down}</h2>
                <p>Devices Down</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-box">
                <h2>{ports}</h2>
                <p>Monitored Interfaces</p>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-md-12">
            <div class="panel panel-default panel-condensed">
                <div class="panel-heading"><strong>Recent Events</strong></div>
                <table class="table table-hover table-condensed table-striped">
                    <thead><tr><th>Time</th><th>Device</th><th>Event</th><th>Severity</th></tr></thead>
                    <tbody>
                        <tr><td>2024-01-15 14:23:01</td><td>core-rtr-01.dc1.internal</td><td>BGP peer 203.0.113.1 established</td><td><span class="label label-success">OK</span></td></tr>
                        <tr><td>2024-01-15 14:20:45</td><td>access-sw-03.dc2.internal</td><td>Device unreachable via SNMP</td><td><span class="label label-danger">Critical</span></td></tr>
                        <tr><td>2024-01-15 14:15:30</td><td>dist-sw-02.dc1.internal</td><td>Interface Vlan200 utilization above 80%</td><td><span class="label label-warning">Warning</span></td></tr>
                        <tr><td>2024-01-15 14:10:12</td><td>edge-fw-01.dc2.internal</td><td>Firewall policy updated</td><td><span class="label label-info">Info</span></td></tr>
                        <tr><td>2024-01-15 14:05:00</td><td>wan-rtr-02.dc1.internal</td><td>Interface ge-0/0/0 flap detected</td><td><span class="label label-warning">Warning</span></td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>'''.format(total=len(DEVICES), up=up_count, down=down_count, ports=len(NETWORK_V6_ENTRIES) + len(NETWORK_V4_ENTRIES))

    return render_page('Overview', content, 'overview')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_login_page()

    username = request.form.get('username', '')
    password = request.form.get('password', '')

    user = USERS.get(username)
    if user and user['password_hash'] == hashlib.sha256(password).hexdigest():
        session['authenticated'] = True
        session['username'] = username
        session['level'] = user['level']
        session['realname'] = user['realname']
        return redirect('/')

    return render_login_page(error='Invalid credentials')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/devices')
def devices_page():
    if not check_auth():
        return redirect('/login')

    rows = ''
    for d in DEVICES:
        status_label = '<span class="label label-success">Up</span>' if d['status'] == 1 else '<span class="label label-danger">Down</span>'
        uptime_str = '{:.1f} days'.format(d['uptime'] / 86400.0) if d['uptime'] > 0 else '-'
        rows += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            cgi.escape(d['hostname']), cgi.escape(d['sysName']), cgi.escape(d['os']), status_label, uptime_str)

    content = '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>Devices</strong></div>
        <table class="table table-hover table-condensed table-striped">
            <thead><tr><th>Hostname</th><th>sysName</th><th>OS</th><th>Status</th><th>Uptime</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>'''.format(rows=rows)

    return render_page('Devices', content, 'devices')


@app.route('/search/ipv4', methods=['GET', 'POST'])
def search_ipv4():
    if not check_auth():
        return redirect('/login')

    post_device_id = request.form.get('device_id', '')
    post_interface = request.form.get('interface', '')
    post_address = request.form.get('address', '')

    device_options = '<option value="">All Devices</option>'
    for d in DEVICES:
        selected = ' selected' if str(d['device_id']) == post_device_id else ''
        device_options += '<option value="{}"{}>{}</option>'.format(d['device_id'], selected, cgi.escape(d['hostname']))

    results = filter_entries(NETWORK_V4_ENTRIES, post_device_id or None, post_interface or None, post_address or None)

    result_rows = ''
    for entry in results:
        result_rows += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            cgi.escape(entry['hostname']), cgi.escape(entry['interface']),
            cgi.escape(entry['address']), cgi.escape(entry['description']))

    content = '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>IPv4 Addresses</strong></div>
        <div class="panel-body">
            <form method="post" action="/search/ipv4" class="form-inline" role="form">
                <div class="form-group">
                    <select name="device_id" id="device_id" class="form-control input-sm">{device_options}</select>
                </div>&nbsp;
                <div class="form-group">
                    <select name="interface" id="interface" class="form-control input-sm">
                        <option value="">All Interfaces</option>
                        <option value="Loopback%"{loopback_sel}>Loopbacks</option>
                        <option value="Vlan%"{vlan_sel}>VLANs</option>
                    </select>
                </div>&nbsp;
                <div class="form-group">
                    <input type="text" name="address" id="address" size="40" value="{address_val}" class="form-control input-sm" placeholder="IPv4 Address"/>
                </div>&nbsp;
                <button type="submit" class="btn btn-default input-sm">Search</button>
            </form>
        </div>
        <table class="table table-hover table-condensed table-striped">
            <thead><tr><th>Device</th><th>Interface</th><th>Address</th><th>Description</th></tr></thead>
            <tbody>{result_rows}</tbody>
        </table>
    </div>
    <script>
    $(document).ready(function() {{
        var searchConfig = {{
            search_type: "ipv4",
            device_id: '{esc_device_id}',
            interface: '{esc_interface}',
            address: '{esc_address}'
        }};
    }});
    </script>'''.format(
        device_options=device_options,
        loopback_sel=' selected' if post_interface == 'Loopback%' else '',
        vlan_sel=' selected' if post_interface == 'Vlan%' else '',
        address_val=cgi.escape(post_address, quote=True),
        esc_device_id=cgi.escape(post_device_id, quote=True),
        esc_interface=cgi.escape(post_interface, quote=True).replace("'", "\\'"),
        esc_address=cgi.escape(post_address, quote=True).replace("'", "\\'"),
        result_rows=result_rows)

    return render_page('IPv4 Search', content, 'ipv4')


@app.route('/search/ipv6', methods=['GET', 'POST'])
def search_ipv6():
    if not check_auth():
        return redirect('/login')

    post_device_id = request.form.get('device_id', '')
    post_interface = request.form.get('interface', '')
    post_address = request.form.get('address', '')

    device_options = '<option value="">All Devices</option>'
    for d in DEVICES:
        selected = ' selected' if str(d['device_id']) == post_device_id else ''
        device_options += '<option value="{}"{}>{}</option>'.format(d['device_id'], selected, cgi.escape(d['hostname']))

    results = filter_entries(NETWORK_V6_ENTRIES, post_device_id or None, post_interface or None, post_address or None)

    result_rows = ''
    for entry in results:
        result_rows += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            cgi.escape(entry['hostname']), cgi.escape(entry['interface']),
            cgi.escape(entry['address']), cgi.escape(entry['description']))

    validation_result = ''
    if request.method == 'POST' and (post_address or post_interface):
        # Build the full page as it would be rendered in a monitoring dashboard viewer's browser
        page_fragment = build_ipv6_page(device_options, post_device_id, post_interface, post_address, result_rows)
        rendered_page = render_page('IPv6 Search', page_fragment, 'ipv6')
        xss_check = verify_rendered_page(rendered_page)
        if xss_check == 'XSS':
            secret = get_secret()
            if secret:
                validation_result = '<div class="alert alert-danger" style="margin-top:15px;">Security Alert: XSS detected in search parameters. Incident token: {}</div>'.format(secret)
            else:
                validation_result = '<div class="alert alert-danger" style="margin-top:15px;">Security Alert: XSS detected in search parameters.</div>'
        elif xss_check:
            validation_result = '<div class="alert alert-warning" style="margin-top:15px;">Content validation notice: unexpected script output detected.</div>'

    content = build_ipv6_page(device_options, post_device_id, post_interface, post_address, result_rows) + validation_result
    return render_page('IPv6 Search', content, 'ipv6')


def build_ipv6_page(device_options, post_device_id, post_interface, post_address, result_rows):
    """Build the IPv6 search page content with search form and results."""
    # The address and interface fields are inserted directly for bootgrid
    # AJAX compatibility - device_id is properly escaped
    loopback_sel = ' selected' if post_interface == 'Loopback%' else ''
    vlan_sel = ' selected' if post_interface == 'Vlan%' else ''

    page = '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>IPv6 Addresses</strong></div>
        <div class="panel-body">
            <form method="post" action="/search/ipv6" class="form-inline" role="form">
                <div class="form-group">
                    <select name="device_id" id="device_id" class="form-control input-sm">{device_options}</select>
                </div>&nbsp;
                <div class="form-group">
                    <select name="interface" id="interface" class="form-control input-sm">
                        <option value="">All Interfaces</option>
                        <option value="Loopback%"{loopback_sel}>Loopbacks</option>
                        <option value="Vlan%"{vlan_sel}>VLANs</option>
                    </select>
                </div>&nbsp;
                <div class="form-group">
                    <input type="text" name="address" id="address" size="40" value="{raw_address}" class="form-control input-sm" placeholder="IPv6 Address"/>
                </div>&nbsp;
                <button type="submit" class="btn btn-default input-sm">Search</button>
            </form>
        </div>
        <table id="ipv6-search" class="table table-hover table-condensed table-striped">
            <thead><tr><th>Device</th><th>Interface</th><th>Address</th><th>Description</th></tr></thead>
            <tbody>{result_rows}</tbody>
        </table>
    </div>
    <script>
    $(document).ready(function() {{
        var searchConfig = {{
            id: "address-search",
            search_type: "ipv6",
            device_id: '{esc_device_id}',
            interface: '{raw_interface}',
            address: '{raw_address_js}'
        }};
        if (searchConfig.address || searchConfig.interface) {{
            $("#ipv6-search").addClass("filtered");
        }}
    }});
    </script>'''.format(
        device_options=device_options,
        loopback_sel=loopback_sel,
        vlan_sel=vlan_sel,
        raw_address=post_address,
        esc_device_id=cgi.escape(post_device_id, quote=True),
        raw_interface=post_interface,
        raw_address_js=post_address,
        result_rows=result_rows)

    return page


@app.route('/alerts')
def alerts_page():
    if not check_auth():
        return redirect('/login')
    if get_user_level() < 10:
        return render_page('Alerts', '<div class="alert alert-danger">Insufficient privileges</div>', 'alerts')

    content = '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>Active Alerts</strong></div>
        <table class="table table-hover table-condensed table-striped">
            <thead><tr><th>Time</th><th>Device</th><th>Rule</th><th>Severity</th><th>Status</th></tr></thead>
            <tbody>
                <tr><td>2024-01-15 14:20:45</td><td>access-sw-03.dc2.internal</td><td>Device Down</td><td><span class="label label-danger">Critical</span></td><td>Active</td></tr>
                <tr><td>2024-01-15 14:15:30</td><td>dist-sw-02.dc1.internal</td><td>Interface Utilization</td><td><span class="label label-warning">Warning</span></td><td>Active</td></tr>
                <tr><td>2024-01-15 14:05:00</td><td>wan-rtr-02.dc1.internal</td><td>Interface Flapping</td><td><span class="label label-warning">Warning</span></td><td>Acknowledged</td></tr>
            </tbody>
        </table>
    </div>'''

    return render_page('Alerts', content, 'alerts')


@app.route('/ping')
def health_check():
    return 'OK'


@app.errorhandler(404)
def not_found(e):
    if check_auth():
        return render_page('Not Found', '<div class="alert alert-warning">The requested page was not found.</div>'), 404
    return redirect('/login')


@app.errorhandler(500)
def server_error(e):
    return Response('Internal Server Error', status=500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
