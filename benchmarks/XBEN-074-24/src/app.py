# encoding=utf8

from flask import Flask, request, make_response
import subprocess
import os
import cgi
import sys
import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

stored_flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

DEVICES = [
    {'device_id': 1, 'hostname': 'core-rtr-01.dc1.local', 'sysName': 'core-rtr-01', 'display': 'Core Router 01'},
    {'device_id': 2, 'hostname': 'dist-sw-02.dc1.local', 'sysName': 'dist-sw-02', 'display': 'Distribution Switch 02'},
    {'device_id': 3, 'hostname': 'edge-fw-03.dc2.local', 'sysName': 'edge-fw-03', 'display': 'Edge Firewall 03'},
    {'device_id': 4, 'hostname': 'access-sw-04.dc2.local', 'sysName': 'access-sw-04', 'display': 'Access Switch 04'},
    {'device_id': 5, 'hostname': 'mgmt-srv-05.dc1.local', 'sysName': 'mgmt-srv-05', 'display': 'Management Server 05'},
]

NETWORK_ENTRIES_V4 = [
    {'hostname': 'core-rtr-01.dc1.local', 'interface': 'GigabitEthernet0/0', 'address': '10.0.1.1/24', 'description': 'Uplink to ISP'},
    {'hostname': 'dist-sw-02.dc1.local', 'interface': 'Vlan100', 'address': '10.0.100.1/24', 'description': 'Server VLAN'},
    {'hostname': 'edge-fw-03.dc2.local', 'interface': 'eth0', 'address': '192.168.1.1/24', 'description': 'DMZ Interface'},
    {'hostname': 'access-sw-04.dc2.local', 'interface': 'GigabitEthernet1/0/1', 'address': '172.16.0.1/24', 'description': 'User Access'},
]

NETWORK_ENTRIES_V6 = [
    {'hostname': 'core-rtr-01.dc1.local', 'interface': 'GigabitEthernet0/0', 'address': '2001:db8::1/64', 'description': 'IPv6 Uplink'},
    {'hostname': 'dist-sw-02.dc1.local', 'interface': 'Vlan100', 'address': 'fd00:100::1/64', 'description': 'Server VLAN v6'},
    {'hostname': 'edge-fw-03.dc2.local', 'interface': 'eth0', 'address': '2001:db8:cafe::1/64', 'description': 'DMZ v6'},
    {'hostname': 'access-sw-04.dc2.local', 'interface': 'Loopback0', 'address': 'fd00:abcd::1/128', 'description': 'Loopback v6'},
    {'hostname': 'mgmt-srv-05.dc1.local', 'interface': 'Vlan200', 'address': 'fe80::1/10', 'description': 'Link Local'},
]

ARP_ENTRIES = [
    {'mac_address': '00:1A:2B:3C:4D:5E', 'ipv4_address': '10.0.1.100', 'hostname': 'core-rtr-01.dc1.local', 'interface': 'GigabitEthernet0/0'},
    {'mac_address': '00:2B:3C:4D:5E:6F', 'ipv4_address': '10.0.100.50', 'hostname': 'dist-sw-02.dc1.local', 'interface': 'Vlan100'},
    {'mac_address': '00:3C:4D:5E:6F:70', 'ipv4_address': '192.168.1.25', 'hostname': 'edge-fw-03.dc2.local', 'interface': 'eth0'},
]

FDB_ENTRIES = [
    {'mac_address': '00:1A:2B:3C:4D:5E', 'hostname': 'dist-sw-02.dc1.local', 'interface': 'GigabitEthernet1/0/5', 'vlan': '100'},
    {'mac_address': '00:4D:5E:6F:70:81', 'hostname': 'access-sw-04.dc2.local', 'interface': 'GigabitEthernet1/0/12', 'vlan': '200'},
]


def escape_html(text):
    if text is None:
        return ''
    return cgi.escape(str(text), quote=True)


def render_page(title, content, search_active=''):
    return BASE_TEMPLATE.replace('__TITLE__', title).replace('__CONTENT__', content).replace('__SEARCH_ACTIVE__', search_active)


def render_device_options(selected_id=''):
    options = '<option value="">All Devices</option>'
    for dev in DEVICES:
        sel = ' selected' if str(dev['device_id']) == str(selected_id) else ''
        options += '<option value="' + str(dev['device_id']) + '"' + sel + '>' + escape_html(dev['display']) + '</option>'
    return options


def render_interface_options(selected=''):
    sel_loop = ' selected' if selected == 'Loopback%' else ''
    sel_vlan = ' selected' if selected == 'Vlan%' else ''
    return '<option value="">All Interfaces</option><option value="Loopback%"' + sel_loop + '>Loopbacks</option><option value="Vlan%"' + sel_vlan + '>VLANs</option>'


def filter_entries(entries, device_id='', interface='', address=''):
    results = entries
    if device_id:
        dev_map = {str(d['device_id']): d['hostname'] for d in DEVICES}
        hostname = dev_map.get(str(device_id), '')
        if hostname:
            results = [e for e in results if e.get('hostname') == hostname]
    if interface:
        if interface.endswith('%'):
            prefix = interface[:-1]
            results = [e for e in results if e.get('interface', '').startswith(prefix)]
        else:
            results = [e for e in results if e.get('interface') == interface]
    if address:
        results = [e for e in results if address.lower() in e.get('address', '').lower()]
    return results


def verify_xss(html_content):
    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "--ignore-ssl-errors=true", "check.js"],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    result = ''
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


BASE_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>__TITLE__ - NetWatch NMS</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <style>
        body { background-color: #1a1a2e; color: #e0e0e0; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }
        .navbar { background-color: #16213e; border-color: #0f3460; }
        .navbar-brand { color: #e94560 !important; font-weight: bold; }
        .navbar-nav > li > a { color: #e0e0e0 !important; }
        .navbar-nav > li > a:hover { color: #e94560 !important; }
        .navbar-nav > .active > a { background-color: #0f3460 !important; color: #e94560 !important; }
        .panel { background-color: #16213e; border-color: #0f3460; }
        .panel-heading { background-color: #0f3460 !important; color: #e94560 !important; border-color: #0f3460; }
        .table { color: #e0e0e0; }
        .table-striped > tbody > tr:nth-of-type(odd) { background-color: #1a1a2e; }
        .table-striped > tbody > tr:nth-of-type(even) { background-color: #16213e; }
        .table-hover > tbody > tr:hover { background-color: #0f3460; }
        .form-control { background-color: #1a1a2e; color: #e0e0e0; border-color: #0f3460; }
        .btn-default { background-color: #0f3460; color: #e0e0e0; border-color: #e94560; }
        .btn-default:hover { background-color: #e94560; color: #fff; }
        .content-area { padding: 20px; }
        .search-bar { padding: 15px; background-color: #16213e; border: 1px solid #0f3460; margin-bottom: 15px; border-radius: 4px; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        th { color: #e94560 !important; }
    </style>
</head>
<body>
    <nav class="navbar navbar-default navbar-static-top">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="/">NetWatch NMS</a>
            </div>
            <ul class="nav navbar-nav">
                <li><a href="/">Dashboard</a></li>
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown">Devices <span class="caret"></span></a>
                    <ul class="dropdown-menu" style="background-color:#16213e;">
                        <li><a href="/devices">All Devices</a></li>
                    </ul>
                </li>
                <li class="dropdown __SEARCH_ACTIVE__">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown">Search <span class="caret"></span></a>
                    <ul class="dropdown-menu" style="background-color:#16213e;">
                        <li><a href="/search/ipv4">IPv4 Addresses</a></li>
                        <li><a href="/search/ipv6">IPv6 Addresses</a></li>
                        <li><a href="/search/arp">ARP Tables</a></li>
                        <li><a href="/search/fdb">FDB Tables</a></li>
                    </ul>
                </li>
                <li><a href="/alerts">Alerts</a></li>
            </ul>
            <ul class="nav navbar-nav navbar-right">
                <li><a href="#">admin</a></li>
            </ul>
        </div>
    </nav>
    <div class="container-fluid content-area">
        __CONTENT__
    </div>
    <div class="footer">
        NetWatch NMS - Network Monitoring System
    </div>
    <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
</body>
</html>'''


def make_search_nav(active=''):
    ipv4_s = 'style="color:#e94560;font-weight:bold;"' if active == 'ipv4' else ''
    ipv6_s = 'style="color:#e94560;font-weight:bold;"' if active == 'ipv6' else ''
    arp_s = 'style="color:#e94560;font-weight:bold;"' if active == 'arp' else ''
    fdb_s = 'style="color:#e94560;font-weight:bold;"' if active == 'fdb' else ''
    return '<div style="margin-bottom:15px;"><strong>Search</strong> &raquo; <a href="/search/ipv4" ' + ipv4_s + '>IPv4 Address</a> | <a href="/search/ipv6" ' + ipv6_s + '>IPv6 Address</a> | <a href="/search/arp" ' + arp_s + '>ARP Table</a> | <a href="/search/fdb" ' + fdb_s + '>FDB Table</a></div>'


@app.route('/')
def dashboard():
    content = '''
    <div class="row">
        <div class="col-md-6">
            <div class="panel panel-default">
                <div class="panel-heading"><strong>System Overview</strong></div>
                <div class="panel-body">
                    <table class="table table-condensed">
                        <tr><td>Devices</td><td>''' + str(len(DEVICES)) + '''</td></tr>
                        <tr><td>IPv4 Addresses</td><td>''' + str(len(NETWORK_ENTRIES_V4)) + '''</td></tr>
                        <tr><td>IPv6 Addresses</td><td>''' + str(len(NETWORK_ENTRIES_V6)) + '''</td></tr>
                        <tr><td>ARP Entries</td><td>''' + str(len(ARP_ENTRIES)) + '''</td></tr>
                        <tr><td>System Status</td><td><span style="color:#2ecc71;">Operational</span></td></tr>
                    </table>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="panel panel-default">
                <div class="panel-heading"><strong>Recent Alerts</strong></div>
                <div class="panel-body">
                    <table class="table table-condensed">
                        <tr><td style="color:#e94560;">Warning</td><td>High CPU on core-rtr-01</td><td>2 min ago</td></tr>
                        <tr><td style="color:#f39c12;">Notice</td><td>Interface down on dist-sw-02</td><td>15 min ago</td></tr>
                        <tr><td style="color:#2ecc71;">Resolved</td><td>BGP peer restored on edge-fw-03</td><td>1 hour ago</td></tr>
                    </table>
                </div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-md-12">
            <div class="panel panel-default">
                <div class="panel-heading"><strong>Quick Search</strong></div>
                <div class="panel-body">
                    <a href="/search/ipv4" class="btn btn-default">IPv4 Search</a>
                    <a href="/search/ipv6" class="btn btn-default">IPv6 Search</a>
                    <a href="/search/arp" class="btn btn-default">ARP Search</a>
                    <a href="/search/fdb" class="btn btn-default">FDB Search</a>
                </div>
            </div>
        </div>
    </div>'''
    return render_page('Dashboard', content)


@app.route('/devices')
def devices_list():
    rows = ''
    for dev in DEVICES:
        rows += '<tr><td>' + escape_html(dev['hostname']) + '</td><td>' + escape_html(dev['sysName']) + '</td><td>' + escape_html(dev['display']) + '</td><td><span style="color:#2ecc71;">Up</span></td></tr>'
    content = '<div class="panel panel-default"><div class="panel-heading"><strong>All Devices</strong></div><table class="table table-hover table-condensed table-striped"><thead><tr><th>Hostname</th><th>sysName</th><th>Display Name</th><th>Status</th></tr></thead><tbody>' + rows + '</tbody></table></div>'
    return render_page('Devices', content)


@app.route('/alerts')
def alerts_page():
    content = '''
    <div class="panel panel-default">
        <div class="panel-heading"><strong>Alert Log</strong></div>
        <table class="table table-hover table-condensed table-striped">
            <thead><tr><th>Severity</th><th>Device</th><th>Message</th><th>Timestamp</th></tr></thead>
            <tbody>
                <tr><td style="color:#e94560;">Critical</td><td>core-rtr-01.dc1.local</td><td>CPU utilization exceeded 95%</td><td>2024-01-15 14:32:01</td></tr>
                <tr><td style="color:#f39c12;">Warning</td><td>dist-sw-02.dc1.local</td><td>Port GigabitEthernet1/0/24 down</td><td>2024-01-15 14:17:45</td></tr>
                <tr><td style="color:#2ecc71;">OK</td><td>edge-fw-03.dc2.local</td><td>BGP session with 203.0.113.1 established</td><td>2024-01-15 13:55:12</td></tr>
                <tr><td style="color:#f39c12;">Warning</td><td>access-sw-04.dc2.local</td><td>High memory utilization detected</td><td>2024-01-15 13:30:00</td></tr>
            </tbody>
        </table>
    </div>'''
    return render_page('Alerts', content)


@app.route('/search/ipv4', methods=['GET', 'POST'])
def search_ipv4():
    device_id = ''
    interface_filter = ''
    address_filter = ''

    if request.method == 'POST':
        device_id = request.form.get('device_id', '')
        interface_filter = request.form.get('interface', '')
        address_filter = request.form.get('address', '')

    entries = filter_entries(NETWORK_ENTRIES_V4, device_id, interface_filter, address_filter)

    rows = ''
    for e in entries:
        rows += '<tr><td>' + escape_html(e['hostname']) + '</td><td>' + escape_html(e['interface']) + '</td><td>' + escape_html(e['address']) + '</td><td>' + escape_html(e['description']) + '</td></tr>'

    nav = make_search_nav('ipv4')

    content = nav + '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>IPv4 Addresses</strong></div>
        <div class="search-bar">
            <form method="post" action="/search/ipv4" class="form-inline">
                <div class="form-group">
                    <select name="device_id" class="form-control input-sm">''' + render_device_options(device_id) + '''</select>
                </div>
                <div class="form-group">
                    <select name="interface" class="form-control input-sm">''' + render_interface_options(escape_html(interface_filter)) + '''</select>
                </div>
                <div class="form-group">
                    <input type="text" name="address" id="address" size="40" value="''' + escape_html(address_filter) + '''" class="form-control input-sm" placeholder="IPv4 Address"/>
                </div>
                <button type="submit" class="btn btn-default input-sm">Search</button>
            </form>
        </div>
        <table id="ipv4-search" class="table table-hover table-condensed table-striped">
            <thead><tr>
                <th>Device</th><th>Interface</th><th>Address</th><th>Description</th>
            </tr></thead>
            <tbody>''' + rows + '''</tbody>
        </table>
    </div>
    <script>
    var searchConfig = {
        search_type: "ipv4",
        device_id: "''' + escape_html(device_id) + '''",
        interface: "''' + escape_html(interface_filter) + '''",
        address: "''' + escape_html(address_filter) + '''"
    };
    </script>'''

    resp = make_response(render_page('IPv4 Search', content, 'active'))
    return resp


@app.route('/search/ipv6', methods=['GET', 'POST'])
def search_ipv6():
    device_id = ''
    interface_filter = ''
    address_filter = ''

    if request.method == 'POST':
        device_id = request.form.get('device_id', '')
        interface_filter = request.form.get('interface', '')
        address_filter = request.form.get('address', '')

    entries = filter_entries(NETWORK_ENTRIES_V6, device_id, interface_filter, address_filter)

    rows = ''
    for e in entries:
        rows += '<tr><td>' + escape_html(e['hostname']) + '</td><td>' + escape_html(e['interface']) + '</td><td>' + escape_html(e['address']) + '</td><td>' + escape_html(e['description']) + '</td></tr>'

    nav = make_search_nav('ipv6')

    content = nav + '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>IPv6 Addresses</strong></div>
        <div class="search-bar">
            <form method="post" action="/search/ipv6" class="form-inline">
                <div class="form-group">
                    <select name="device_id" class="form-control input-sm">''' + render_device_options(device_id) + '''</select>
                </div>
                <div class="form-group">
                    <select name="interface" class="form-control input-sm">''' + render_interface_options(interface_filter) + '''</select>
                </div>
                <div class="form-group">
                    <input type="text" name="address" id="address" size="40" value="''' + address_filter + '''" class="form-control input-sm" placeholder="IPv6 Address"/>
                </div>
                <button type="submit" class="btn btn-default input-sm">Search</button>
            </form>
        </div>
        <table id="ipv6-search" class="table table-hover table-condensed table-striped">
            <thead><tr>
                <th>Device</th><th>Interface</th><th>Address</th><th>Description</th>
            </tr></thead>
            <tbody>''' + rows + '''</tbody>
        </table>
    </div>
    <script>
    var searchConfig = {
        search_type: "ipv6",
        device_id: "''' + escape_html(device_id) + '''",
        interface: "''' + interface_filter + '''",
        address: "''' + address_filter + '''"
    };
    </script>'''

    rendered_page = render_page('IPv6 Search', content, 'active')

    if address_filter or interface_filter:
        xss_result = verify_xss(rendered_page)
        if xss_result == 'XSS':
            flag_content = content + '<div class="alert alert-success" style="background-color:#0f3460;border-color:#e94560;color:#2ecc71;margin-top:10px;">' + stored_flag + '</div>'
            rendered_page = render_page('IPv6 Search', flag_content, 'active')

    resp = make_response(rendered_page)
    resp.headers["X-XSS-Protection"] = "0"
    resp.headers["Content-Security-Policy"] = ""
    return resp


@app.route('/search/arp', methods=['GET', 'POST'])
def search_arp():
    device_id = ''
    search_phrase = ''
    search_by = 'mac'

    if request.method == 'POST':
        device_id = request.form.get('device_id', '')
        search_phrase = request.form.get('searchPhrase', '')
        search_by = request.form.get('searchby', 'mac')

    entries = ARP_ENTRIES
    if device_id:
        dev_map = {str(d['device_id']): d['hostname'] for d in DEVICES}
        hostname = dev_map.get(str(device_id), '')
        if hostname:
            entries = [e for e in entries if e.get('hostname') == hostname]
    if search_phrase:
        if search_by == 'ip':
            entries = [e for e in entries if search_phrase.lower() in e.get('ipv4_address', '').lower()]
        else:
            entries = [e for e in entries if search_phrase.lower() in e.get('mac_address', '').lower()]

    rows = ''
    for e in entries:
        rows += '<tr><td>' + escape_html(e['mac_address']) + '</td><td>' + escape_html(e['ipv4_address']) + '</td><td>' + escape_html(e['hostname']) + '</td><td>' + escape_html(e['interface']) + '</td></tr>'

    nav = make_search_nav('arp')
    sel_mac = ' selected' if search_by != 'ip' else ''
    sel_ip = ' selected' if search_by == 'ip' else ''

    content = nav + '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>ARP Entries</strong></div>
        <div class="search-bar">
            <form method="post" action="/search/arp" class="form-inline">
                <div class="form-group">
                    <select name="device_id" class="form-control input-sm">''' + render_device_options(device_id) + '''</select>
                </div>
                <div class="form-group">
                    <select name="searchby" class="form-control input-sm">
                        <option value="mac"''' + sel_mac + '''>MAC Address</option>
                        <option value="ip"''' + sel_ip + '''>IP Address</option>
                    </select>
                </div>
                <div class="form-group">
                    <input type="text" name="searchPhrase" value="''' + escape_html(search_phrase) + '''" class="form-control input-sm" placeholder="Address"/>
                </div>
                <button type="submit" class="btn btn-default input-sm">Search</button>
            </form>
        </div>
        <table class="table table-hover table-condensed table-striped">
            <thead><tr><th>MAC Address</th><th>IP Address</th><th>Device</th><th>Interface</th></tr></thead>
            <tbody>''' + rows + '''</tbody>
        </table>
    </div>
    <script>
    var searchConfig = {
        search_type: "arp",
        device_id: "''' + escape_html(device_id) + '''",
        searchby: "''' + escape_html(search_by) + '''",
        searchPhrase: "''' + escape_html(search_phrase) + '''"
    };
    </script>'''

    return render_page('ARP Search', content, 'active')


@app.route('/search/fdb', methods=['GET', 'POST'])
def search_fdb():
    device_id = ''
    search_phrase = ''

    if request.method == 'POST':
        device_id = request.form.get('device_id', '')
        search_phrase = request.form.get('searchPhrase', '')

    entries = FDB_ENTRIES
    if device_id:
        dev_map = {str(d['device_id']): d['hostname'] for d in DEVICES}
        hostname = dev_map.get(str(device_id), '')
        if hostname:
            entries = [e for e in entries if e.get('hostname') == hostname]
    if search_phrase:
        entries = [e for e in entries if search_phrase.lower() in e.get('mac_address', '').lower()]

    rows = ''
    for e in entries:
        rows += '<tr><td>' + escape_html(e['mac_address']) + '</td><td>' + escape_html(e['hostname']) + '</td><td>' + escape_html(e['interface']) + '</td><td>' + escape_html(e['vlan']) + '</td></tr>'

    nav = make_search_nav('fdb')

    content = nav + '''
    <div class="panel panel-default panel-condensed">
        <div class="panel-heading"><strong>FDB Table</strong></div>
        <div class="search-bar">
            <form method="post" action="/search/fdb" class="form-inline">
                <div class="form-group">
                    <select name="device_id" class="form-control input-sm">''' + render_device_options(device_id) + '''</select>
                </div>
                <div class="form-group">
                    <input type="text" name="searchPhrase" value="''' + escape_html(search_phrase) + '''" class="form-control input-sm" placeholder="MAC Address"/>
                </div>
                <button type="submit" class="btn btn-default input-sm">Search</button>
            </form>
        </div>
        <table class="table table-hover table-condensed table-striped">
            <thead><tr><th>MAC Address</th><th>Device</th><th>Interface</th><th>VLAN</th></tr></thead>
            <tbody>''' + rows + '''</tbody>
        </table>
    </div>
    <script>
    var searchConfig = {
        search_type: "fdb",
        device_id: "''' + escape_html(device_id) + '''",
        searchPhrase: "''' + escape_html(search_phrase) + '''"
    };
    </script>'''

    return render_page('FDB Search', content, 'active')


@app.route('/search')
def search_index():
    return search_ipv4()


@app.errorhandler(404)
def page_not_found(e):
    content = '<div class="panel panel-default"><div class="panel-body" style="text-align:center;"><h3>Page Not Found</h3><p>The requested page could not be found.</p><a href="/" class="btn btn-default">Return to Dashboard</a></div></div>'
    return render_page('Not Found', content), 404


@app.errorhandler(500)
def internal_error(e):
    content = '<div class="panel panel-default"><div class="panel-body" style="text-align:center;"><h3>Internal Server Error</h3><p>An unexpected error occurred.</p></div></div>'
    return render_page('Error', content), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
