# encoding=utf8

from flask import Flask, request
import subprocess
import os
import sys
import datetime
import random

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)

DEVICES = [
    {'id': 1, 'hostname': 'core-router-01.dc1', 'ip': '10.0.1.1', 'status': 'up', 'type': 'router'},
    {'id': 2, 'hostname': 'core-switch-01.dc1', 'ip': '10.0.1.2', 'status': 'up', 'type': 'switch'},
    {'id': 3, 'hostname': 'web-server-01.dc1', 'ip': '10.0.2.10', 'status': 'up', 'type': 'server'},
    {'id': 4, 'hostname': 'db-server-01.dc1', 'ip': '10.0.2.20', 'status': 'down', 'type': 'server'},
    {'id': 5, 'hostname': 'fw-edge-01.dc1', 'ip': '10.0.0.1', 'status': 'up', 'type': 'firewall'},
]

OUTAGES = [
    {'id': 1, 'device': 'db-server-01.dc1', 'start': '2024-01-15 14:30:00', 'end': '2024-01-15 15:45:00', 'duration': '1h 15m'},
    {'id': 2, 'device': 'web-server-01.dc1', 'start': '2024-01-10 08:00:00', 'end': '2024-01-10 08:15:00', 'duration': '15m'},
    {'id': 3, 'device': 'core-router-01.dc1', 'start': '2024-01-05 22:00:00', 'end': '2024-01-05 22:30:00', 'duration': '30m'},
]

SYSLOG_ENTRIES = [
    {'timestamp': '2024-01-15 14:30:05', 'device': 'db-server-01.dc1', 'severity': 'critical', 'message': 'Service postgresql stopped unexpectedly'},
    {'timestamp': '2024-01-15 14:30:10', 'device': 'core-switch-01.dc1', 'severity': 'warning', 'message': 'High CPU utilization detected: 85%'},
    {'timestamp': '2024-01-15 14:31:00', 'device': 'web-server-01.dc1', 'severity': 'info', 'message': 'Nginx service restarted'},
    {'timestamp': '2024-01-15 14:32:00', 'device': 'fw-edge-01.dc1', 'severity': 'warning', 'message': 'Suspicious traffic pattern detected from 203.0.113.50'},
]

BASE_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>NetMonitor - Network Monitoring System</title>
    <link rel="stylesheet" href="/static/css/monitor.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <span class="brand-icon">&#9737;</span> NetMonitor
        </div>
        <ul class="nav-menu">
            <li><a href="/">Dashboard</a></li>
            <li><a href="/devices">Devices</a></li>
            <li><a href="/outages">Outages</a></li>
            <li><a href="/syslog">Syslog</a></li>
            <li><a href="/health">Health</a></li>
        </ul>
        <div class="nav-user">
            <span>admin</span>
        </div>
    </nav>
    <div class="container">
        %s
    </div>
    <footer class="footer">
        <p>NetMonitor v2.3.7 &copy; 2024</p>
    </footer>
</body>
</html>'''


def check_xss(page, input_val):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = None
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
    return result == 'XSS'


@app.route('/')
def index():
    content = '''
        <div class="dashboard">
            <h1>Network Overview</h1>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">5</div>
                    <div class="stat-label">Total Devices</div>
                </div>
                <div class="stat-card status-up">
                    <div class="stat-value">4</div>
                    <div class="stat-label">Devices Up</div>
                </div>
                <div class="stat-card status-down">
                    <div class="stat-value">1</div>
                    <div class="stat-label">Devices Down</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">3</div>
                    <div class="stat-label">Recent Outages</div>
                </div>
            </div>
            <div class="quick-links">
                <h2>Quick Access</h2>
                <ul>
                    <li><a href="/devices">View All Devices</a></li>
                    <li><a href="/outages">Recent Outages</a></li>
                    <li><a href="/syslog">System Logs</a></li>
                    <li><a href="/health">Health Metrics</a></li>
                </ul>
            </div>
        </div>
    '''
    return BASE_TEMPLATE % content


@app.route('/devices')
def devices():
    device_id = request.args.get('device_id', '')
    hostname = request.args.get('hostname', '')
    state = request.args.get('state', '')
    
    filtered_devices = DEVICES
    if device_id:
        filtered_devices = [d for d in filtered_devices if str(d['id']) == device_id]
    if hostname:
        filtered_devices = [d for d in filtered_devices if hostname.lower() in d['hostname'].lower()]
    if state:
        filtered_devices = [d for d in filtered_devices if d['status'] == state]
    
    rows = ''
    for d in filtered_devices:
        status_class = 'status-up' if d['status'] == 'up' else 'status-down'
        rows += '''
            <tr>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td><span class="{}">{}</span></td>
                <td>{}</td>
            </tr>
        '''.format(d['id'], d['hostname'], d['ip'], status_class, d['status'], d['type'])
    
    content = '''
        <div class="page-header">
            <h1>Device List</h1>
        </div>
        <div class="filter-panel">
            <form method="GET" action="/devices">
                <div class="filter-row">
                    <label>Device ID:</label>
                    <input type="text" name="device_id" value="{}" placeholder="Filter by ID">
                    <label>Hostname:</label>
                    <input type="text" name="hostname" value="{}" placeholder="Filter by hostname">
                    <label>State:</label>
                    <select name="state">
                        <option value="">All</option>
                        <option value="up" {}>Up</option>
                        <option value="down" {}>Down</option>
                    </select>
                    <button type="submit">Filter</button>
                </div>
            </form>
        </div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Hostname</th>
                    <th>IP Address</th>
                    <th>Status</th>
                    <th>Type</th>
                </tr>
            </thead>
            <tbody>
                {}
            </tbody>
        </table>
    '''.format(device_id, hostname, 
               'selected' if state == 'up' else '', 
               'selected' if state == 'down' else '', 
               rows)
    
    page_html = BASE_TEMPLATE % content
    
    if device_id or hostname:
        test_input = device_id if device_id else hostname
        if check_xss(page_html, test_input):
            success_content = '''
                <div class="page-header">
                    <h1>Access Granted</h1>
                </div>
                <div class="alert alert-success">
                    <p>Security verification completed successfully.</p>
                    <p class="flag-display">{}</p>
                </div>
            '''.format(flag)
            return BASE_TEMPLATE % success_content
    
    return page_html


@app.route('/outages')
def outages():
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    
    rows = ''
    for o in OUTAGES:
        rows += '''
            <tr>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>
        '''.format(o['id'], o['device'], o['start'], o['end'], o['duration'])
    
    content = '''
        <div class="page-header">
            <h1>Network Outages</h1>
        </div>
        <div class="filter-panel">
            <form method="GET" action="/outages">
                <div class="filter-row">
                    <label>From:</label>
                    <input type="text" name="from" value="{}" placeholder="YYYY-MM-DD">
                    <label>To:</label>
                    <input type="text" name="to" value="{}" placeholder="YYYY-MM-DD">
                    <button type="submit">Filter</button>
                </div>
            </form>
        </div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Device</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                    <th>Duration</th>
                </tr>
            </thead>
            <tbody>
                {}
            </tbody>
        </table>
    '''.format(from_date, to_date, rows)
    
    page_html = BASE_TEMPLATE % content
    
    if from_date or to_date:
        test_input = from_date if from_date else to_date
        if check_xss(page_html, test_input):
            success_content = '''
                <div class="page-header">
                    <h1>Access Granted</h1>
                </div>
                <div class="alert alert-success">
                    <p>Security verification completed successfully.</p>
                    <p class="flag-display">{}</p>
                </div>
            '''.format(flag)
            return BASE_TEMPLATE % success_content
    
    return page_html


@app.route('/syslog')
def syslog():
    from_time = request.args.get('from', '')
    to_time = request.args.get('to', '')
    device = request.args.get('device', '')
    
    rows = ''
    for entry in SYSLOG_ENTRIES:
        severity_class = 'severity-' + entry['severity']
        rows += '''
            <tr>
                <td>{}</td>
                <td>{}</td>
                <td><span class="{}">{}</span></td>
                <td>{}</td>
            </tr>
        '''.format(entry['timestamp'], entry['device'], severity_class, entry['severity'], entry['message'])
    
    content = '''
        <div class="page-header">
            <h1>System Logs</h1>
        </div>
        <div class="filter-panel">
            <form method="GET" action="/syslog">
                <div class="filter-row">
                    <label>From:</label>
                    <input type="text" name="from" value="{}" placeholder="YYYY-MM-DD HH:MM">
                    <label>To:</label>
                    <input type="text" name="to" value="{}" placeholder="YYYY-MM-DD HH:MM">
                    <label>Device:</label>
                    <input type="text" name="device" value="{}" placeholder="Hostname">
                    <button type="submit">Filter</button>
                </div>
            </form>
        </div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Device</th>
                    <th>Severity</th>
                    <th>Message</th>
                </tr>
            </thead>
            <tbody>
                {}
            </tbody>
        </table>
    '''.format(from_time, to_time, device, rows)
    
    page_html = BASE_TEMPLATE % content
    
    if from_time or to_time or device:
        test_input = from_time if from_time else (to_time if to_time else device)
        if check_xss(page_html, test_input):
            success_content = '''
                <div class="page-header">
                    <h1>Access Granted</h1>
                </div>
                <div class="alert alert-success">
                    <p>Security verification completed successfully.</p>
                    <p class="flag-display">{}</p>
                </div>
            '''.format(flag)
            return BASE_TEMPLATE % success_content
    
    return page_html


@app.route('/health')
def health():
    view = request.args.get('view', 'overview')
    graph_type = request.args.get('graph_type', 'line')
    unit = request.args.get('unit', 'percent')
    device_class = request.args.get('class', 'all')
    
    content = '''
        <div class="page-header">
            <h1>Health Metrics</h1>
        </div>
        <div class="filter-panel">
            <form method="GET" action="/health">
                <div class="filter-row">
                    <label>View:</label>
                    <input type="text" name="view" value="{}" placeholder="overview">
                    <label>Graph Type:</label>
                    <input type="text" name="graph_type" value="{}" placeholder="line/bar">
                    <label>Unit:</label>
                    <input type="text" name="unit" value="{}" placeholder="percent/value">
                    <label>Class:</label>
                    <input type="text" name="class" value="{}" placeholder="all/servers/network">
                    <button type="submit">Apply</button>
                </div>
            </form>
        </div>
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>CPU Usage</h3>
                <div class="metric-value">45%</div>
                <div class="metric-bar"><div class="metric-fill" style="width: 45%"></div></div>
            </div>
            <div class="metric-card">
                <h3>Memory Usage</h3>
                <div class="metric-value">62%</div>
                <div class="metric-bar"><div class="metric-fill" style="width: 62%"></div></div>
            </div>
            <div class="metric-card">
                <h3>Network I/O</h3>
                <div class="metric-value">1.2 Gbps</div>
                <div class="metric-bar"><div class="metric-fill" style="width: 30%"></div></div>
            </div>
            <div class="metric-card">
                <h3>Disk Usage</h3>
                <div class="metric-value">78%</div>
                <div class="metric-bar"><div class="metric-fill" style="width: 78%"></div></div>
            </div>
        </div>
        <script>
            var config = {{
                view: '{}',
                graphType: '{}',
                unit: '{}',
                deviceClass: '{}'
            }};
            console.log('Health page loaded with config:', config);
        </script>
    '''.format(view, graph_type, unit, device_class, view, graph_type, unit, device_class)
    
    page_html = BASE_TEMPLATE % content
    
    if view != 'overview' or graph_type != 'line' or unit != 'percent' or device_class != 'all':
        test_inputs = [view, graph_type, unit, device_class]
        for inp in test_inputs:
            if inp and inp not in ['overview', 'line', 'percent', 'all']:
                if check_xss(page_html, inp):
                    success_content = '''
                        <div class="page-header">
                            <h1>Access Granted</h1>
                        </div>
                        <div class="alert alert-success">
                            <p>Security verification completed successfully.</p>
                            <p class="flag-display">{}</p>
                        </div>
                    '''.format(flag)
                    return BASE_TEMPLATE % success_content
                break
    
    return page_html


@app.errorhandler(404)
def not_found(e):
    content = '''
        <div class="error-page">
            <h1>404 - Page Not Found</h1>
            <p>The requested resource could not be found.</p>
            <a href="/">Return to Dashboard</a>
        </div>
    '''
    return BASE_TEMPLATE % content, 404


@app.errorhandler(500)
def internal_error(e):
    content = '''
        <div class="error-page">
            <h1>500 - Internal Server Error</h1>
            <p>An unexpected error occurred.</p>
            <a href="/">Return to Dashboard</a>
        </div>
    '''
    return BASE_TEMPLATE % content, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
