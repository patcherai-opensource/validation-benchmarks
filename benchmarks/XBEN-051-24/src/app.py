# encoding=utf8

from flask import Flask, request, make_response, redirect, url_for
import subprocess
import os
import cgi
import sys
from datetime import datetime, timedelta

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_data = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

MOCK_DEVICES = [
    {'id': 1, 'hostname': 'core-router-01', 'ip': '10.0.1.1', 'status': 'up', 'type': 'Cisco IOS'},
    {'id': 2, 'hostname': 'switch-floor2', 'ip': '10.0.2.1', 'status': 'up', 'type': 'Juniper'},
    {'id': 3, 'hostname': 'fw-edge-01', 'ip': '10.0.0.1', 'status': 'down', 'type': 'PAN-OS'},
    {'id': 4, 'hostname': 'server-db01', 'ip': '10.0.10.5', 'status': 'up', 'type': 'Linux'},
    {'id': 5, 'hostname': 'ap-building-a', 'ip': '10.0.3.10', 'status': 'up', 'type': 'Ubiquiti'},
]

MOCK_OUTAGES = [
    {'id': 101, 'device': 'fw-edge-01', 'start': '2024-01-15 08:30:00', 'end': '2024-01-15 09:45:00', 'duration': '1h 15m'},
    {'id': 102, 'device': 'switch-floor2', 'start': '2024-01-14 22:00:00', 'end': '2024-01-14 22:30:00', 'duration': '30m'},
    {'id': 103, 'device': 'core-router-01', 'start': '2024-01-10 03:00:00', 'end': '2024-01-10 03:15:00', 'duration': '15m'},
]

BASE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - NetWatch NMS</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; }}
        .navbar {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #0f3460; }}
        .navbar .logo {{ font-size: 24px; font-weight: bold; color: #00d9ff; }}
        .navbar nav a {{ color: #aaa; text-decoration: none; margin-left: 25px; transition: color 0.2s; }}
        .navbar nav a:hover, .navbar nav a.active {{ color: #00d9ff; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
        .page-header {{ margin-bottom: 25px; }}
        .page-header h1 {{ font-size: 28px; color: #fff; }}
        .page-header p {{ color: #888; margin-top: 5px; }}
        .card {{ background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .filter-form {{ display: flex; gap: 15px; align-items: flex-end; flex-wrap: wrap; }}
        .form-group {{ display: flex; flex-direction: column; }}
        .form-group label {{ font-size: 12px; color: #888; margin-bottom: 5px; text-transform: uppercase; }}
        .form-group input, .form-group select {{ padding: 10px 15px; border: 1px solid #0f3460; background: #1a1a2e; color: #eee; border-radius: 4px; min-width: 180px; }}
        .btn {{ padding: 10px 20px; background: #0f3460; color: #fff; border: none; border-radius: 4px; cursor: pointer; transition: background 0.2s; }}
        .btn:hover {{ background: #00d9ff; color: #16213e; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ color: #00d9ff; font-weight: 500; font-size: 12px; text-transform: uppercase; }}
        .status-up {{ color: #00ff88; }}
        .status-down {{ color: #ff4757; }}
        .footer {{ text-align: center; padding: 20px; color: #555; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">NetWatch NMS</div>
        <nav>
            <a href="/" {nav_home}>Dashboard</a>
            <a href="/devices" {nav_devices}>Devices</a>
            <a href="/outages" {nav_outages}>Outages</a>
            <a href="/syslog" {nav_syslog}>Syslog</a>
        </nav>
    </div>
    <div class="container">
        {content}
    </div>
    <div class="footer">NetWatch Network Management System v2.4.1</div>
</body>
</html>'''


def render_page(title, content, active=''):
    nav_classes = {
        'nav_home': 'class="active"' if active == 'home' else '',
        'nav_devices': 'class="active"' if active == 'devices' else '',
        'nav_outages': 'class="active"' if active == 'outages' else '',
        'nav_syslog': 'class="active"' if active == 'syslog' else '',
    }
    return BASE_TEMPLATE.format(title=title, content=content, **nav_classes)


def check_xss(page):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    result = ''
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
def dashboard():
    devices_up = sum(1 for d in MOCK_DEVICES if d['status'] == 'up')
    devices_down = sum(1 for d in MOCK_DEVICES if d['status'] == 'down')
    
    content = '''
        <div class="page-header">
            <h1>Dashboard</h1>
            <p>Network overview and status summary</p>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
            <div class="card" style="text-align: center;">
                <div style="font-size: 48px; color: #00ff88;">{0}</div>
                <div style="color: #888;">Devices Up</div>
            </div>
            <div class="card" style="text-align: center;">
                <div style="font-size: 48px; color: #ff4757;">{1}</div>
                <div style="color: #888;">Devices Down</div>
            </div>
            <div class="card" style="text-align: center;">
                <div style="font-size: 48px; color: #00d9ff;">{2}</div>
                <div style="color: #888;">Recent Outages</div>
            </div>
        </div>
        <div class="card">
            <h3 style="margin-bottom: 15px;">Recent Alerts</h3>
            <table>
                <tr><th>Time</th><th>Device</th><th>Message</th></tr>
                <tr><td>2024-01-15 08:30</td><td>fw-edge-01</td><td>Device unreachable</td></tr>
                <tr><td>2024-01-15 09:45</td><td>fw-edge-01</td><td>Device recovered</td></tr>
                <tr><td>2024-01-14 22:00</td><td>switch-floor2</td><td>High CPU utilization</td></tr>
            </table>
        </div>
    '''.format(devices_up, devices_down, len(MOCK_OUTAGES))
    
    return render_page('Dashboard', content, 'home')


@app.route('/devices')
def devices():
    hostname_filter = request.args.get('hostname', '')
    status_filter = request.args.get('state', '')
    
    filtered_devices = MOCK_DEVICES
    if hostname_filter:
        filtered_devices = [d for d in filtered_devices if hostname_filter.lower() in d['hostname'].lower()]
    if status_filter:
        filtered_devices = [d for d in filtered_devices if d['status'] == status_filter]
    
    rows = ''
    for d in filtered_devices:
        status_class = 'status-up' if d['status'] == 'up' else 'status-down'
        rows += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td class="{3}">{4}</td></tr>'.format(
            d['hostname'], d['ip'], d['type'], status_class, d['status'].upper()
        )
    
    content = '''
        <div class="page-header">
            <h1>Devices</h1>
            <p>Manage and monitor network devices</p>
        </div>
        <div class="card">
            <form class="filter-form" method="GET">
                <div class="form-group">
                    <label>Hostname</label>
                    <input type="text" name="hostname" value="{hostname}" placeholder="Filter by hostname...">
                </div>
                <div class="form-group">
                    <label>Status</label>
                    <select name="state">
                        <option value="">All</option>
                        <option value="up" {sel_up}>Up</option>
                        <option value="down" {sel_down}>Down</option>
                    </select>
                </div>
                <button type="submit" class="btn">Apply Filter</button>
            </form>
        </div>
        <div class="card">
            <table>
                <tr><th>Hostname</th><th>IP Address</th><th>Type</th><th>Status</th></tr>
                {rows}
            </table>
        </div>
    '''.format(
        hostname=hostname_filter,
        sel_up='selected' if status_filter == 'up' else '',
        sel_down='selected' if status_filter == 'down' else '',
        rows=rows if rows else '<tr><td colspan="4" style="text-align:center;color:#888;">No devices found</td></tr>'
    )
    
    return render_page('Devices', content, 'devices')


@app.route('/outages')
def outages():
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    
    rows = ''
    for o in MOCK_OUTAGES:
        rows += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td></tr>'.format(
            o['id'], o['device'], o['start'], o['end'], o['duration']
        )
    
    content = '''
        <div class="page-header">
            <h1>Outages</h1>
            <p>View historical outage records</p>
        </div>
        <div class="card">
            <form class="filter-form" method="GET">
                <div class="form-group">
                    <label>From Date</label>
                    <input type="text" name="from" value="{from_val}" placeholder="YYYY-MM-DD">
                </div>
                <div class="form-group">
                    <label>To Date</label>
                    <input type="text" name="to" value="{to_val}" placeholder="YYYY-MM-DD">
                </div>
                <button type="submit" class="btn">Filter</button>
            </form>
        </div>
        <div class="card">
            <table>
                <tr><th>ID</th><th>Device</th><th>Start</th><th>End</th><th>Duration</th></tr>
                {rows}
            </table>
        </div>
    '''.format(
        from_val=from_date,
        to_val=to_date,
        rows=rows
    )
    
    full_page = render_page('Outages', content, 'outages')
    
    if from_date or to_date:
        xss_result = check_xss(full_page)
        if xss_result == 'XSS':
            content = '''
                <div class="page-header">
                    <h1>Outages</h1>
                    <p>View historical outage records</p>
                </div>
                <div class="card">
                    <form class="filter-form" method="GET">
                        <div class="form-group">
                            <label>From Date</label>
                            <input type="text" name="from" value="{from_val}" placeholder="YYYY-MM-DD">
                        </div>
                        <div class="form-group">
                            <label>To Date</label>
                            <input type="text" name="to" value="{to_val}" placeholder="YYYY-MM-DD">
                        </div>
                        <button type="submit" class="btn">Filter</button>
                    </form>
                </div>
                <div class="card" style="background: #0a4d0a; border: 1px solid #00ff88;">
                    <div style="color: #00ff88; font-size: 18px; margin-bottom: 10px;">System Access Granted</div>
                    <div style="font-family: monospace; background: #000; padding: 15px; border-radius: 4px;">
                        {flag}
                    </div>
                </div>
                <div class="card">
                    <table>
                        <tr><th>ID</th><th>Device</th><th>Start</th><th>End</th><th>Duration</th></tr>
                        {rows}
                    </table>
                </div>
            '''.format(
                from_val=from_date,
                to_val=to_date,
                rows=rows,
                flag=flag_data
            )
            full_page = render_page('Outages', content, 'outages')
    
    response = make_response(full_page)
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.route('/syslog')
def syslog():
    from_ts = request.args.get('from', '')
    to_ts = request.args.get('to', '')
    device_filter = request.args.get('device', '')
    
    logs = [
        {'time': '2024-01-15 09:45:12', 'device': 'fw-edge-01', 'level': 'INFO', 'msg': 'Link state changed to UP'},
        {'time': '2024-01-15 08:30:05', 'device': 'fw-edge-01', 'level': 'CRITICAL', 'msg': 'Link state changed to DOWN'},
        {'time': '2024-01-14 22:30:00', 'device': 'switch-floor2', 'level': 'WARNING', 'msg': 'CPU utilization normalized'},
        {'time': '2024-01-14 22:00:00', 'device': 'switch-floor2', 'level': 'WARNING', 'msg': 'High CPU utilization detected: 95%'},
        {'time': '2024-01-10 03:15:22', 'device': 'core-router-01', 'level': 'INFO', 'msg': 'BGP session established with peer 10.0.0.2'},
    ]
    
    rows = ''
    for log in logs:
        level_style = ''
        if log['level'] == 'CRITICAL':
            level_style = 'color: #ff4757;'
        elif log['level'] == 'WARNING':
            level_style = 'color: #ffa502;'
        rows += '<tr><td>{0}</td><td>{1}</td><td style="{2}">{3}</td><td>{4}</td></tr>'.format(
            log['time'], log['device'], level_style, log['level'], log['msg']
        )
    
    content = '''
        <div class="page-header">
            <h1>Syslog</h1>
            <p>System log entries from all devices</p>
        </div>
        <div class="card">
            <form class="filter-form" method="GET">
                <div class="form-group">
                    <label>From</label>
                    <input type="text" name="from" value="{from_val}" placeholder="YYYY-MM-DD HH:MM">
                </div>
                <div class="form-group">
                    <label>To</label>
                    <input type="text" name="to" value="{to_val}" placeholder="YYYY-MM-DD HH:MM">
                </div>
                <div class="form-group">
                    <label>Device</label>
                    <input type="text" name="device" value="{device_val}" placeholder="Filter by device...">
                </div>
                <button type="submit" class="btn">Filter</button>
            </form>
        </div>
        <div class="card">
            <table>
                <tr><th>Timestamp</th><th>Device</th><th>Level</th><th>Message</th></tr>
                {rows}
            </table>
        </div>
    '''.format(
        from_val=from_ts,
        to_val=to_ts,
        device_val=device_filter,
        rows=rows
    )
    
    return render_page('Syslog', content, 'syslog')


@app.errorhandler(404)
def not_found(e):
    content = '''
        <div class="page-header">
            <h1>Page Not Found</h1>
            <p>The requested resource could not be found.</p>
        </div>
        <div class="card">
            <p>Please check the URL or navigate using the menu above.</p>
            <p style="margin-top: 15px;"><a href="/" style="color: #00d9ff;">Return to Dashboard</a></p>
        </div>
    '''
    return render_page('Not Found', content), 404


@app.errorhandler(500)
def server_error(e):
    content = '''
        <div class="page-header">
            <h1>Server Error</h1>
            <p>An internal error occurred.</p>
        </div>
        <div class="card">
            <p>Please try again later.</p>
            <p style="margin-top: 15px;"><a href="/" style="color: #00d9ff;">Return to Dashboard</a></p>
        </div>
    '''
    return render_page('Error', content), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
