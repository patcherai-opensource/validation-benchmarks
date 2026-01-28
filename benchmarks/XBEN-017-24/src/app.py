# encoding=utf8

from flask import Flask, request, redirect, jsonify
import subprocess
import os
import cgi
import sys
import json
import time

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# In-memory storage for port groups (simulating database)
port_groups = []
# Sample ports data
ports = [
    {"id": 1, "name": "eth0", "device": "router-01", "speed": "1Gbps", "status": "up", "groups": []},
    {"id": 2, "name": "eth1", "device": "router-01", "speed": "10Gbps", "status": "up", "groups": []},
    {"id": 3, "name": "ge-0/0/0", "device": "switch-01", "speed": "1Gbps", "status": "down", "groups": []},
    {"id": 4, "name": "ge-0/0/1", "device": "switch-01", "speed": "1Gbps", "status": "up", "groups": []},
    {"id": 5, "name": "FastEthernet0/1", "device": "switch-02", "speed": "100Mbps", "status": "up", "groups": []},
]

def check_xss_on_page(page_html):
    """Use PhantomJS to check if XSS is triggered on rendered page"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = ""
    try:
        of = open(fn, 'w')
        of.write(page_html)
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

# ============ Main Dashboard ============
@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>NetMonitor - Network Monitoring System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 10px; }
        .nav a:hover { background: #e94560; border-radius: 3px; }
        .container { padding: 30px; }
        .card { background: #16213e; padding: 20px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #e94560; }
        .stats { display: flex; gap: 20px; flex-wrap: wrap; }
        .stat-box { background: #0f3460; padding: 20px; border-radius: 5px; min-width: 150px; text-align: center; }
        .stat-box h3 { margin: 0; color: #e94560; font-size: 2em; }
        .stat-box p { margin: 5px 0 0 0; color: #aaa; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NetMonitor v2.4.1</h1>
    </div>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/ports">Ports</a>
        <a href="/alerts">Alerts</a>
        <a href="/settings">Settings</a>
        <a href="/api/status">API Status</a>
    </div>
    <div class="container">
        <h2>Dashboard Overview</h2>
        <div class="stats">
            <div class="stat-box"><h3>5</h3><p>Active Devices</p></div>
            <div class="stat-box"><h3>23</h3><p>Monitored Ports</p></div>
            <div class="stat-box"><h3>2</h3><p>Active Alerts</p></div>
            <div class="stat-box"><h3>99.8%</h3><p>Uptime</p></div>
        </div>
        <div class="card">
            <h3>Recent Activity</h3>
            <p>&#8226; Port ge-0/0/0 on switch-01 went down - 2 hours ago</p>
            <p>&#8226; New device router-02 discovered - 5 hours ago</p>
            <p>&#8226; Threshold alert cleared on eth0 - 1 day ago</p>
        </div>
        <div class="card">
            <h3>Quick Links</h3>
            <p><a href="/devices" style="color:#e94560">Manage Devices</a> | <a href="/ports" style="color:#e94560">View Ports</a> | <a href="/settings/port-groups" style="color:#e94560">Port Groups</a></p>
        </div>
    </div>
</body>
</html>'''

# ============ Devices Page (noise) ============
@app.route('/devices')
def devices():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Devices - NetMonitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 10px; }
        .nav a:hover { background: #e94560; border-radius: 3px; }
        .container { padding: 30px; }
        table { width: 100%; border-collapse: collapse; background: #16213e; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }
        th { background: #0f3460; }
        .status-up { color: #4caf50; }
        .status-down { color: #f44336; }
    </style>
</head>
<body>
    <div class="header"><h1>NetMonitor v2.4.1</h1></div>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/ports">Ports</a>
        <a href="/alerts">Alerts</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <h2>Device Management</h2>
        <table>
            <tr><th>Hostname</th><th>IP Address</th><th>Type</th><th>Status</th><th>Ports</th></tr>
            <tr><td>router-01</td><td>192.168.1.1</td><td>Router</td><td class="status-up">Online</td><td>24</td></tr>
            <tr><td>switch-01</td><td>192.168.1.10</td><td>Switch</td><td class="status-up">Online</td><td>48</td></tr>
            <tr><td>switch-02</td><td>192.168.1.11</td><td>Switch</td><td class="status-up">Online</td><td>24</td></tr>
            <tr><td>firewall-01</td><td>192.168.1.254</td><td>Firewall</td><td class="status-up">Online</td><td>8</td></tr>
            <tr><td>server-01</td><td>192.168.1.100</td><td>Server</td><td class="status-down">Offline</td><td>4</td></tr>
        </table>
    </div>
</body>
</html>'''

# ============ Ports Page (noise) ============
@app.route('/ports')
def ports_page():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Ports - NetMonitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 10px; }
        .nav a:hover { background: #e94560; border-radius: 3px; }
        .container { padding: 30px; }
        table { width: 100%; border-collapse: collapse; background: #16213e; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }
        th { background: #0f3460; }
        .status-up { color: #4caf50; }
        .status-down { color: #f44336; }
    </style>
</head>
<body>
    <div class="header"><h1>NetMonitor v2.4.1</h1></div>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/ports">Ports</a>
        <a href="/alerts">Alerts</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <h2>Port Overview</h2>
        <p>To manage port groups and assignments, visit <a href="/settings/port-groups" style="color:#e94560">Port Group Settings</a></p>
        <table>
            <tr><th>Port</th><th>Device</th><th>Speed</th><th>Status</th><th>Traffic In</th><th>Traffic Out</th></tr>
            <tr><td>eth0</td><td>router-01</td><td>1Gbps</td><td class="status-up">Up</td><td>1.2 GB/s</td><td>800 MB/s</td></tr>
            <tr><td>eth1</td><td>router-01</td><td>10Gbps</td><td class="status-up">Up</td><td>4.5 GB/s</td><td>3.2 GB/s</td></tr>
            <tr><td>ge-0/0/0</td><td>switch-01</td><td>1Gbps</td><td class="status-down">Down</td><td>0</td><td>0</td></tr>
            <tr><td>ge-0/0/1</td><td>switch-01</td><td>1Gbps</td><td class="status-up">Up</td><td>500 MB/s</td><td>450 MB/s</td></tr>
            <tr><td>FastEthernet0/1</td><td>switch-02</td><td>100Mbps</td><td class="status-up">Up</td><td>45 MB/s</td><td>32 MB/s</td></tr>
        </table>
    </div>
</body>
</html>'''

# ============ Alerts Page (noise) ============
@app.route('/alerts')
def alerts():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Alerts - NetMonitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 10px; }
        .nav a:hover { background: #e94560; border-radius: 3px; }
        .container { padding: 30px; }
        .alert { padding: 15px; margin: 10px 0; border-radius: 5px; }
        .alert-critical { background: #d32f2f; }
        .alert-warning { background: #f57c00; }
        .alert-info { background: #1976d2; }
    </style>
</head>
<body>
    <div class="header"><h1>NetMonitor v2.4.1</h1></div>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/ports">Ports</a>
        <a href="/alerts">Alerts</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <h2>Active Alerts</h2>
        <div class="alert alert-critical">
            <strong>CRITICAL:</strong> Port ge-0/0/0 on switch-01 is DOWN - Detected 2 hours ago
        </div>
        <div class="alert alert-warning">
            <strong>WARNING:</strong> High CPU utilization on router-01 (85%) - Detected 30 minutes ago
        </div>
        <div class="alert alert-info">
            <strong>INFO:</strong> Scheduled maintenance window starts in 4 hours
        </div>
    </div>
</body>
</html>'''

# ============ Settings Page ============
@app.route('/settings')
def settings():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Settings - NetMonitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 10px; }
        .nav a:hover { background: #e94560; border-radius: 3px; }
        .container { padding: 30px; }
        .settings-menu { list-style: none; padding: 0; }
        .settings-menu li { background: #16213e; margin: 10px 0; border-radius: 5px; }
        .settings-menu a { display: block; padding: 15px 20px; color: #eee; text-decoration: none; }
        .settings-menu a:hover { background: #0f3460; }
    </style>
</head>
<body>
    <div class="header"><h1>NetMonitor v2.4.1</h1></div>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/ports">Ports</a>
        <a href="/alerts">Alerts</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <h2>System Settings</h2>
        <ul class="settings-menu">
            <li><a href="/settings/general">General Settings</a></li>
            <li><a href="/settings/users">User Management</a></li>
            <li><a href="/settings/snmp">SNMP Configuration</a></li>
            <li><a href="/settings/port-groups">Port Groups</a></li>
            <li><a href="/settings/alerting">Alert Rules</a></li>
            <li><a href="/settings/api">API Access</a></li>
        </ul>
    </div>
</body>
</html>'''

# ============ General Settings (noise) ============
@app.route('/settings/general')
def settings_general():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>General Settings - NetMonitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 10px; }
        .container { padding: 30px; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; }
        input, select { padding: 10px; width: 300px; background: #16213e; border: 1px solid #0f3460; color: #eee; }
        button { padding: 10px 20px; background: #e94560; border: none; color: white; cursor: pointer; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="header"><h1>NetMonitor v2.4.1</h1></div>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <h2>General Settings</h2>
        <form>
            <div class="form-group">
                <label>System Name</label>
                <input type="text" value="NetMonitor-Primary">
            </div>
            <div class="form-group">
                <label>Timezone</label>
                <select><option>UTC</option><option>America/New_York</option><option>Europe/London</option></select>
            </div>
            <div class="form-group">
                <label>Polling Interval (seconds)</label>
                <input type="number" value="300">
            </div>
            <button type="button">Save Changes</button>
        </form>
    </div>
</body>
</html>'''

# ============ Port Groups Management - VULNERABLE ENDPOINT ============
@app.route('/settings/port-groups')
def port_groups_page():
    groups_html = ""
    for i, group in enumerate(port_groups):
        # VULNERABILITY: group['name'] is rendered without escaping
        groups_html += '<tr><td>{}</td><td>{}</td><td>{}</td><td><a href="/settings/port-groups/delete/{}" style="color:#e94560">Delete</a></td></tr>'.format(
            i + 1, group['name'], group.get('description', ''), i
        )
    
    if not groups_html:
        groups_html = '<tr><td colspan="4">No port groups defined. Create one below.</td></tr>'
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Port Groups - NetMonitor</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 15px 30px; border-bottom: 2px solid #0f3460; }}
        .header h1 {{ margin: 0; color: #e94560; }}
        .nav {{ background: #0f3460; padding: 10px 30px; }}
        .nav a {{ color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 10px; }}
        .nav a:hover {{ background: #e94560; border-radius: 3px; }}
        .container {{ padding: 30px; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; margin-bottom: 30px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; }}
        .form-group {{ margin: 15px 0; }}
        label {{ display: block; margin-bottom: 5px; }}
        input {{ padding: 10px; width: 300px; background: #16213e; border: 1px solid #0f3460; color: #eee; }}
        button {{ padding: 10px 20px; background: #e94560; border: none; color: white; cursor: pointer; margin-top: 15px; }}
        .card {{ background: #16213e; padding: 20px; margin: 15px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header"><h1>NetMonitor v2.4.1</h1></div>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/ports">Ports</a>
        <a href="/alerts">Alerts</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <h2>Port Group Management</h2>
        <p>Port groups allow you to organize and manage ports collectively for alerting and reporting.</p>
        
        <h3>Existing Port Groups</h3>
        <table>
            <tr><th>ID</th><th>Group Name</th><th>Description</th><th>Actions</th></tr>
            {groups}
        </table>
        
        <div class="card">
            <h3>Create New Port Group</h3>
            <form action="/settings/port-groups/create" method="POST">
                <div class="form-group">
                    <label for="name">Group Name</label>
                    <input type="text" id="name" name="name" placeholder="Enter group name" required>
                </div>
                <div class="form-group">
                    <label for="description">Description</label>
                    <input type="text" id="description" name="desc" placeholder="Optional description">
                </div>
                <button type="submit">Create Port Group</button>
            </form>
        </div>
    </div>
</body>
</html>'''.format(groups=groups_html)

# ============ Create Port Group - VULNERABLE ============
@app.route('/settings/port-groups/create', methods=['POST'])
def create_port_group():
    name = request.form.get('name', '')
    desc = request.form.get('desc', '')
    
    if not name:
        return redirect('/settings/port-groups')
    
    # Store the port group (no sanitization - this is the vulnerability)
    port_groups.append({
        'name': name,
        'description': desc,
        'created': time.time()
    })
    
    return redirect('/settings/port-groups')

# ============ Delete Port Group ============
@app.route('/settings/port-groups/delete/<int:group_id>')
def delete_port_group(group_id):
    if 0 <= group_id < len(port_groups):
        port_groups.pop(group_id)
    return redirect('/settings/port-groups')

# ============ Port Settings for Device - VULNERABLE PAGE (where XSS triggers) ============
@app.route('/device/<device_name>/ports')
def device_port_settings(device_name):
    device_ports = [p for p in ports if p['device'] == device_name]
    
    # Build the port settings table with port group dropdown
    port_group_options = ""
    for i, group in enumerate(port_groups):
        # VULNERABILITY: group name is inserted directly into HTML without escaping
        port_group_options += '<option value="{}">{}</option>'.format(i, group['name'])
    
    rows_html = ""
    for port in device_ports:
        rows_html += '''<tr>
            <td>{name}</td>
            <td>{speed}</td>
            <td class="status-{status}">{status}</td>
            <td>
                <select class="port-group-select">
                    <option value="">-- Select Group --</option>
                    {options}
                </select>
            </td>
        </tr>'''.format(name=port['name'], speed=port['speed'], status=port['status'], options=port_group_options)
    
    if not rows_html:
        rows_html = '<tr><td colspan="4">No ports found for this device.</td></tr>'
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Port Settings - {device} - NetMonitor</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 15px 30px; border-bottom: 2px solid #0f3460; }}
        .header h1 {{ margin: 0; color: #e94560; }}
        .nav {{ background: #0f3460; padding: 10px 30px; }}
        .nav a {{ color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 10px; }}
        .nav a:hover {{ background: #e94560; border-radius: 3px; }}
        .container {{ padding: 30px; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; }}
        .status-up {{ color: #4caf50; }}
        .status-down {{ color: #f44336; }}
        select {{ padding: 8px; background: #0f3460; border: 1px solid #16213e; color: #eee; }}
        button {{ padding: 10px 20px; background: #e94560; border: none; color: white; cursor: pointer; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="header"><h1>NetMonitor v2.4.1</h1></div>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/ports">Ports</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <h2>Port Settings - {device}</h2>
        <p>Configure port group assignments and settings for this device.</p>
        <table>
            <tr><th>Port</th><th>Speed</th><th>Status</th><th>Assigned Group</th></tr>
            {rows}
        </table>
        <button onclick="alert('Settings saved!')">Save Changes</button>
    </div>
</body>
</html>'''.format(device=cgi.escape(device_name), rows=rows_html)

# ============ Verification Endpoint - Check for XSS ============
@app.route('/verify-settings')
def verify_settings():
    """Simulates another user viewing the port settings page - triggers XSS verification"""
    if not port_groups:
        return jsonify({
            "status": "error",
            "message": "No port groups exist. Create a port group first at /settings/port-groups"
        })
    
    # Build the page that would be shown to another user viewing port settings
    port_group_options = ""
    for i, group in enumerate(port_groups):
        # This is where the stored XSS payload would execute
        port_group_options += '<option value="{}">{}</option>'.format(i, group['name'])
    
    page_html = '''<!DOCTYPE html>
<html>
<head><title>Port Settings - NetMonitor</title></head>
<body>
<h1>Port Settings</h1>
<select>
    <option value="">-- Select Group --</option>
    {}
</select>
</body>
</html>'''.format(port_group_options)
    
    # Use PhantomJS to check if XSS is triggered
    result = check_xss_on_page(page_html)
    
    if result == 'XSS':
        return jsonify({
            "status": "success", 
            "message": "XSS detected! Flag: " + flag
        })
    elif result:
        return jsonify({
            "status": "partial",
            "message": "Alert triggered with: '{}' - but needs to be exactly 'XSS'".format(cgi.escape(result))
        })
    else:
        return jsonify({
            "status": "failed",
            "message": "No XSS detected. Make sure your payload triggers an alert with 'XSS'"
        })

# ============ API Endpoints ============
@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "online",
        "version": "2.4.1",
        "uptime": "15 days, 4 hours",
        "endpoints": [
            "/api/devices",
            "/api/ports", 
            "/api/alerts",
            "/api/port-groups"
        ]
    })

@app.route('/api/devices')
def api_devices():
    return jsonify({
        "devices": [
            {"hostname": "router-01", "ip": "192.168.1.1", "type": "router"},
            {"hostname": "switch-01", "ip": "192.168.1.10", "type": "switch"},
            {"hostname": "switch-02", "ip": "192.168.1.11", "type": "switch"},
        ]
    })

@app.route('/api/ports')
def api_ports():
    return jsonify({"ports": ports})

@app.route('/api/port-groups')
def api_port_groups():
    return jsonify({"port_groups": port_groups})

@app.route('/api/alerts')
def api_alerts():
    return jsonify({
        "alerts": [
            {"severity": "critical", "message": "Port ge-0/0/0 down", "device": "switch-01"},
            {"severity": "warning", "message": "High CPU utilization", "device": "router-01"}
        ]
    })

# ============ Other Settings Pages (noise) ============
@app.route('/settings/users')
def settings_users():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>User Management - NetMonitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; }
        .container { padding: 30px; }
        table { width: 100%; border-collapse: collapse; background: #16213e; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }
        th { background: #0f3460; }
    </style>
</head>
<body>
    <div class="header"><h1>NetMonitor v2.4.1</h1></div>
    <div class="nav"><a href="/">Dashboard</a><a href="/settings">Settings</a></div>
    <div class="container">
        <h2>User Management</h2>
        <table>
            <tr><th>Username</th><th>Role</th><th>Last Login</th></tr>
            <tr><td>admin</td><td>Administrator</td><td>2024-01-15 10:30:00</td></tr>
            <tr><td>operator</td><td>Operator</td><td>2024-01-15 09:15:00</td></tr>
            <tr><td>viewer</td><td>Read-only</td><td>2024-01-14 16:45:00</td></tr>
        </table>
    </div>
</body>
</html>'''

@app.route('/settings/snmp')
def settings_snmp():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>SNMP Configuration - NetMonitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; }
        .container { padding: 30px; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; }
        input { padding: 10px; width: 300px; background: #16213e; border: 1px solid #0f3460; color: #eee; }
        button { padding: 10px 20px; background: #e94560; border: none; color: white; cursor: pointer; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="header"><h1>NetMonitor v2.4.1</h1></div>
    <div class="nav"><a href="/">Dashboard</a><a href="/settings">Settings</a></div>
    <div class="container">
        <h2>SNMP Configuration</h2>
        <form>
            <div class="form-group"><label>SNMP Version</label><select style="padding:10px;background:#16213e;border:1px solid #0f3460;color:#eee"><option>v2c</option><option>v3</option></select></div>
            <div class="form-group"><label>Community String</label><input type="password" value="public"></div>
            <div class="form-group"><label>Timeout (seconds)</label><input type="number" value="5"></div>
            <button type="button">Save Configuration</button>
        </form>
    </div>
</body>
</html>'''

@app.route('/settings/alerting')
def settings_alerting():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Alert Rules - NetMonitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; }
        .container { padding: 30px; }
        table { width: 100%; border-collapse: collapse; background: #16213e; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }
        th { background: #0f3460; }
    </style>
</head>
<body>
    <div class="header"><h1>NetMonitor v2.4.1</h1></div>
    <div class="nav"><a href="/">Dashboard</a><a href="/settings">Settings</a></div>
    <div class="container">
        <h2>Alert Rules</h2>
        <table>
            <tr><th>Rule Name</th><th>Condition</th><th>Severity</th><th>Enabled</th></tr>
            <tr><td>Port Down</td><td>port.status == down</td><td>Critical</td><td>Yes</td></tr>
            <tr><td>High CPU</td><td>device.cpu > 80%</td><td>Warning</td><td>Yes</td></tr>
            <tr><td>High Memory</td><td>device.memory > 90%</td><td>Warning</td><td>Yes</td></tr>
            <tr><td>Interface Errors</td><td>port.errors > 100</td><td>Info</td><td>No</td></tr>
        </table>
    </div>
</body>
</html>'''

@app.route('/settings/api')
def settings_api():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>API Access - NetMonitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; }
        .container { padding: 30px; }
        .card { background: #16213e; padding: 20px; margin: 15px 0; border-radius: 5px; }
        code { background: #0f3460; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="header"><h1>NetMonitor v2.4.1</h1></div>
    <div class="nav"><a href="/">Dashboard</a><a href="/settings">Settings</a></div>
    <div class="container">
        <h2>API Access</h2>
        <div class="card">
            <h3>Available Endpoints</h3>
            <p><code>GET /api/status</code> - System status</p>
            <p><code>GET /api/devices</code> - List devices</p>
            <p><code>GET /api/ports</code> - List ports</p>
            <p><code>GET /api/alerts</code> - List alerts</p>
            <p><code>GET /api/port-groups</code> - List port groups</p>
        </div>
        <div class="card">
            <h3>Authentication</h3>
            <p>API authentication is currently disabled for development purposes.</p>
        </div>
    </div>
</body>
</html>'''

# ============ Robots.txt ============
@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

if __name__ == '__main__':
    app.run(debug=True)
