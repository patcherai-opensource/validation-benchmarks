# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect, session
from functools import wraps
import string
import subprocess
import os
import re
import cgi
import urllib
import sys

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_content = open('secret.txt').read().strip()

app = Flask(__name__)
app.secret_key = os.urandom(24)

VALID_WIRELESS_TYPES = {
    'wifi-rssi': 'WiFi RSSI',
    'wifi-snr': 'WiFi SNR', 
    'wifi-noise': 'WiFi Noise Floor',
    'wifi-rate': 'WiFi Rate',
    'wifi-clients': 'WiFi Clients',
    'wifi-channel': 'WiFi Channel',
    'wifi-power': 'WiFi TX Power',
    'lte-rssi': 'LTE RSSI',
    'lte-rsrp': 'LTE RSRP',
    'lte-rsrq': 'LTE RSRQ',
    'lte-sinr': 'LTE SINR'
}

VALID_HEALTH_TYPES = {
    'processor': 'Processor',
    'mempool': 'Memory Pool',
    'storage': 'Storage',
    'temperature': 'Temperature',
    'voltage': 'Voltage',
    'current': 'Current',
    'power': 'Power',
    'frequency': 'Frequency',
    'runtime': 'Runtime',
    'state': 'State'
}

USERS = {
    'admin': 'librenms123',
    'operator': 'monitor456'
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def parse_path_vars(path):
    """Parse LibreNMS-style path variables like /wireless/metric=value"""
    vars_dict = {}
    parts = path.strip('/').split('/')
    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            vars_dict[key] = value
    return vars_dict

def check_xss(page, payload):
    """Check if XSS payload executes in PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], 
                           stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except:
        result = ''
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result

@app.route('/')
def index():
    if 'user' in session:
        return redirect('/overview')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username in USERS and USERS[username] == password:
            session['user'] = username
            return redirect('/overview')
        error = 'Invalid credentials'
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Login</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; }
        .login-container { max-width: 400px; margin: 100px auto; padding: 30px; background: #16213e; border-radius: 8px; }
        .login-container h1 { text-align: center; color: #4ecca3; margin-bottom: 30px; }
        .login-container input { width: 100%%; padding: 12px; margin: 8px 0; box-sizing: border-box; border: 1px solid #0f3460; border-radius: 4px; background: #1a1a2e; color: #eee; }
        .login-container button { width: 100%%; padding: 12px; background: #4ecca3; border: none; border-radius: 4px; color: #1a1a2e; font-weight: bold; cursor: pointer; margin-top: 15px; }
        .login-container button:hover { background: #45b393; }
        .error { color: #e94560; text-align: center; margin-top: 10px; }
        .logo { text-align: center; margin-bottom: 20px; }
        .logo img { width: 150px; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>LibreNMS</h1>
            <p>Network Monitoring System</p>
        </div>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p class="error">%s</p>
    </div>
</body>
</html>''' % cgi.escape(error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/overview')
@login_required
def overview():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Overview</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; }
        .navbar { background: #16213e; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { color: #4ecca3; margin: 0; font-size: 20px; }
        .navbar a { color: #eee; text-decoration: none; margin-left: 20px; }
        .navbar a:hover { color: #4ecca3; }
        .container { padding: 30px; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .widget { background: #16213e; padding: 20px; border-radius: 8px; }
        .widget h3 { color: #4ecca3; margin-top: 0; }
        .stat { font-size: 32px; font-weight: bold; }
        .menu-list { list-style: none; padding: 0; }
        .menu-list li { padding: 10px 0; border-bottom: 1px solid #0f3460; }
        .menu-list li a { color: #4ecca3; text-decoration: none; }
        .menu-list li a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>LibreNMS</h1>
        <div>
            <a href="/overview">Overview</a>
            <a href="/devices">Devices</a>
            <a href="/health/metric=processor">Health</a>
            <a href="/wireless/metric=wifi-rssi">Wireless</a>
            <a href="/alerts">Alerts</a>
            <a href="/logout">Logout</a>
        </div>
    </div>
    <div class="container">
        <div class="dashboard">
            <div class="widget">
                <h3>Network Status</h3>
                <p class="stat">12</p>
                <p>Devices Online</p>
            </div>
            <div class="widget">
                <h3>Alerts</h3>
                <p class="stat">3</p>
                <p>Active Alerts</p>
            </div>
            <div class="widget">
                <h3>Quick Navigation</h3>
                <ul class="menu-list">
                    <li><a href="/health/metric=processor">Processor Health</a></li>
                    <li><a href="/health/metric=mempool">Memory Usage</a></li>
                    <li><a href="/health/metric=storage">Storage</a></li>
                    <li><a href="/wireless/metric=wifi-rssi">Wireless RSSI</a></li>
                    <li><a href="/wireless/metric=wifi-clients">Wireless Clients</a></li>
                </ul>
            </div>
            <div class="widget">
                <h3>System Info</h3>
                <p>Version: 24.1.0</p>
                <p>Uptime: 45 days</p>
                <p>User: ''' + session.get('user', '') + '''</p>
            </div>
        </div>
    </div>
</body>
</html>'''

@app.route('/devices')
@login_required  
def devices():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Devices</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; }
        .navbar { background: #16213e; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { color: #4ecca3; margin: 0; font-size: 20px; }
        .navbar a { color: #eee; text-decoration: none; margin-left: 20px; }
        .navbar a:hover { color: #4ecca3; }
        .container { padding: 30px; }
        table { width: 100%%; border-collapse: collapse; background: #16213e; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }
        th { background: #0f3460; color: #4ecca3; }
        .status-up { color: #4ecca3; }
        .status-down { color: #e94560; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>LibreNMS</h1>
        <div>
            <a href="/overview">Overview</a>
            <a href="/devices">Devices</a>
            <a href="/health/metric=processor">Health</a>
            <a href="/wireless/metric=wifi-rssi">Wireless</a>
            <a href="/alerts">Alerts</a>
            <a href="/logout">Logout</a>
        </div>
    </div>
    <div class="container">
        <h2>Devices</h2>
        <table>
            <tr><th>Hostname</th><th>IP</th><th>Type</th><th>Status</th></tr>
            <tr><td>core-router-01</td><td>10.0.0.1</td><td>Router</td><td class="status-up">Up</td></tr>
            <tr><td>dist-switch-01</td><td>10.0.1.1</td><td>Switch</td><td class="status-up">Up</td></tr>
            <tr><td>ap-building-a</td><td>10.0.2.10</td><td>Access Point</td><td class="status-up">Up</td></tr>
            <tr><td>server-web-01</td><td>10.0.10.5</td><td>Server</td><td class="status-up">Up</td></tr>
            <tr><td>firewall-01</td><td>10.0.0.254</td><td>Firewall</td><td class="status-down">Down</td></tr>
        </table>
    </div>
</body>
</html>'''

@app.route('/alerts')
@login_required
def alerts():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Alerts</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; }
        .navbar { background: #16213e; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { color: #4ecca3; margin: 0; font-size: 20px; }
        .navbar a { color: #eee; text-decoration: none; margin-left: 20px; }
        .navbar a:hover { color: #4ecca3; }
        .container { padding: 30px; }
        .alert-item { background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #e94560; }
        .alert-item.warning { border-left-color: #ffa500; }
        .alert-item h4 { margin: 0 0 10px 0; color: #e94560; }
        .alert-item.warning h4 { color: #ffa500; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>LibreNMS</h1>
        <div>
            <a href="/overview">Overview</a>
            <a href="/devices">Devices</a>
            <a href="/health/metric=processor">Health</a>
            <a href="/wireless/metric=wifi-rssi">Wireless</a>
            <a href="/alerts">Alerts</a>
            <a href="/logout">Logout</a>
        </div>
    </div>
    <div class="container">
        <h2>Active Alerts</h2>
        <div class="alert-item">
            <h4>Device Down: firewall-01</h4>
            <p>Device has not responded for 15 minutes</p>
            <small>2024-01-15 14:32:00</small>
        </div>
        <div class="alert-item warning">
            <h4>High CPU: server-web-01</h4>
            <p>CPU utilization above 90%</p>
            <small>2024-01-15 14:28:00</small>
        </div>
        <div class="alert-item warning">
            <h4>Storage Warning: server-web-01</h4>
            <p>Disk usage above 85%</p>
            <small>2024-01-15 13:45:00</small>
        </div>
    </div>
</body>
</html>'''

@app.route('/wireless')
@app.route('/wireless/<path:subpath>')
@login_required
def wireless(subpath=''):
    vars_dict = parse_path_vars('/wireless/' + subpath)
    
    metric = vars_dict.get('metric', 'wifi-rssi')
    
    metric_class = os.path.basename(metric)
    
    sensors_html = ''
    if metric_class in VALID_WIRELESS_TYPES:
        sensors_html = '''
        <table style="width: 100%%; border-collapse: collapse; background: #16213e;">
            <tr style="background: #0f3460;"><th style="padding: 12px; text-align: left; color: #4ecca3;">Device</th><th style="padding: 12px; text-align: left; color: #4ecca3;">Sensor</th><th style="padding: 12px; text-align: left; color: #4ecca3;">Value</th></tr>
            <tr><td style="padding: 12px; border-bottom: 1px solid #0f3460;">ap-building-a</td><td style="padding: 12px; border-bottom: 1px solid #0f3460;">%s</td><td style="padding: 12px; border-bottom: 1px solid #0f3460;">-65 dBm</td></tr>
            <tr><td style="padding: 12px; border-bottom: 1px solid #0f3460;">ap-building-b</td><td style="padding: 12px; border-bottom: 1px solid #0f3460;">%s</td><td style="padding: 12px; border-bottom: 1px solid #0f3460;">-72 dBm</td></tr>
        </table>
        ''' % (cgi.escape(VALID_WIRELESS_TYPES[metric_class]), cgi.escape(VALID_WIRELESS_TYPES[metric_class]))
    else:
        sensors_html = '<p class="no-sensors">No sensors of type ' + metric_class + ' found.</p>'
    
    page_content = '''<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Wireless Sensors</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; }
        .navbar { background: #16213e; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { color: #4ecca3; margin: 0; font-size: 20px; }
        .navbar a { color: #eee; text-decoration: none; margin-left: 20px; }
        .navbar a:hover { color: #4ecca3; }
        .container { padding: 30px; }
        .sidebar { float: left; width: 200px; background: #16213e; padding: 15px; border-radius: 8px; }
        .sidebar h4 { color: #4ecca3; margin-top: 0; }
        .sidebar ul { list-style: none; padding: 0; margin: 0; }
        .sidebar li { padding: 8px 0; }
        .sidebar a { color: #eee; text-decoration: none; }
        .sidebar a:hover { color: #4ecca3; }
        .sidebar a.active { color: #4ecca3; font-weight: bold; }
        .content { margin-left: 240px; }
        .no-sensors { color: #e94560; font-style: italic; padding: 20px; background: #16213e; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>LibreNMS</h1>
        <div>
            <a href="/overview">Overview</a>
            <a href="/devices">Devices</a>
            <a href="/health/metric=processor">Health</a>
            <a href="/wireless/metric=wifi-rssi">Wireless</a>
            <a href="/alerts">Alerts</a>
            <a href="/logout">Logout</a>
        </div>
    </div>
    <div class="container">
        <div class="sidebar">
            <h4>Wireless Types</h4>
            <ul>
                <li><a href="/wireless/metric=wifi-rssi">WiFi RSSI</a></li>
                <li><a href="/wireless/metric=wifi-snr">WiFi SNR</a></li>
                <li><a href="/wireless/metric=wifi-noise">WiFi Noise</a></li>
                <li><a href="/wireless/metric=wifi-rate">WiFi Rate</a></li>
                <li><a href="/wireless/metric=wifi-clients">WiFi Clients</a></li>
                <li><a href="/wireless/metric=lte-rssi">LTE RSSI</a></li>
                <li><a href="/wireless/metric=lte-rsrp">LTE RSRP</a></li>
            </ul>
        </div>
        <div class="content">
            <h2>Wireless Sensors</h2>
            %s
        </div>
    </div>
</body>
</html>''' % sensors_html

    result = check_xss(page_content, metric_class)
    
    if result == 'XSS':
        page_content = page_content.replace('</body>', '''
        <div style="position: fixed; top: 50%%; left: 50%%; transform: translate(-50%%, -50%%); background: #16213e; padding: 30px; border-radius: 8px; border: 2px solid #4ecca3; z-index: 9999;">
            <h3 style="color: #4ecca3; margin-top: 0;">System Flag Retrieved</h3>
            <p style="font-family: monospace; background: #0f3460; padding: 10px; border-radius: 4px;">%s</p>
        </div>
        </body>''' % flag_content)
    
    response = make_response(page_content)
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/health')
@app.route('/health/<path:subpath>')
@login_required
def health(subpath=''):
    vars_dict = parse_path_vars('/health/' + subpath)
    
    active_metric = vars_dict.get('metric', 'processor')
    
    active_metric = os.path.basename(active_metric)
    
    sensors_html = ''
    if active_metric in VALID_HEALTH_TYPES:
        sensors_html = '''
        <table style="width: 100%%; border-collapse: collapse; background: #16213e;">
            <tr style="background: #0f3460;"><th style="padding: 12px; text-align: left; color: #4ecca3;">Device</th><th style="padding: 12px; text-align: left; color: #4ecca3;">Sensor</th><th style="padding: 12px; text-align: left; color: #4ecca3;">Value</th><th style="padding: 12px; text-align: left; color: #4ecca3;">Status</th></tr>
            <tr><td style="padding: 12px; border-bottom: 1px solid #0f3460;">core-router-01</td><td style="padding: 12px; border-bottom: 1px solid #0f3460;">%s</td><td style="padding: 12px; border-bottom: 1px solid #0f3460;">45%%</td><td style="padding: 12px; border-bottom: 1px solid #0f3460; color: #4ecca3;">OK</td></tr>
            <tr><td style="padding: 12px; border-bottom: 1px solid #0f3460;">server-web-01</td><td style="padding: 12px; border-bottom: 1px solid #0f3460;">%s</td><td style="padding: 12px; border-bottom: 1px solid #0f3460;">92%%</td><td style="padding: 12px; border-bottom: 1px solid #0f3460; color: #e94560;">Warning</td></tr>
        </table>
        ''' % (cgi.escape(VALID_HEALTH_TYPES[active_metric]), cgi.escape(VALID_HEALTH_TYPES[active_metric]))
    else:
        sensors_html = '<p class="no-sensors">No sensors of type ' + active_metric + ' found.</p>'
    
    page_content = '''<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Health Sensors</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; }
        .navbar { background: #16213e; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { color: #4ecca3; margin: 0; font-size: 20px; }
        .navbar a { color: #eee; text-decoration: none; margin-left: 20px; }
        .navbar a:hover { color: #4ecca3; }
        .container { padding: 30px; }
        .sidebar { float: left; width: 200px; background: #16213e; padding: 15px; border-radius: 8px; }
        .sidebar h4 { color: #4ecca3; margin-top: 0; }
        .sidebar ul { list-style: none; padding: 0; margin: 0; }
        .sidebar li { padding: 8px 0; }
        .sidebar a { color: #eee; text-decoration: none; }
        .sidebar a:hover { color: #4ecca3; }
        .sidebar a.active { color: #4ecca3; font-weight: bold; }
        .content { margin-left: 240px; }
        .no-sensors { color: #e94560; font-style: italic; padding: 20px; background: #16213e; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>LibreNMS</h1>
        <div>
            <a href="/overview">Overview</a>
            <a href="/devices">Devices</a>
            <a href="/health/metric=processor">Health</a>
            <a href="/wireless/metric=wifi-rssi">Wireless</a>
            <a href="/alerts">Alerts</a>
            <a href="/logout">Logout</a>
        </div>
    </div>
    <div class="container">
        <div class="sidebar">
            <h4>Health Types</h4>
            <ul>
                <li><a href="/health/metric=processor">Processor</a></li>
                <li><a href="/health/metric=mempool">Memory Pool</a></li>
                <li><a href="/health/metric=storage">Storage</a></li>
                <li><a href="/health/metric=temperature">Temperature</a></li>
                <li><a href="/health/metric=voltage">Voltage</a></li>
                <li><a href="/health/metric=power">Power</a></li>
            </ul>
        </div>
        <div class="content">
            <h2>Health Sensors</h2>
            %s
        </div>
    </div>
</body>
</html>''' % sensors_html

    result = check_xss(page_content, active_metric)
    
    if result == 'XSS':
        page_content = page_content.replace('</body>', '''
        <div style="position: fixed; top: 50%%; left: 50%%; transform: translate(-50%%, -50%%); background: #16213e; padding: 30px; border-radius: 8px; border: 2px solid #4ecca3; z-index: 9999;">
            <h3 style="color: #4ecca3; margin-top: 0;">System Flag Retrieved</h3>
            <p style="font-family: monospace; background: #0f3460; padding: 10px; border-radius: 4px;">%s</p>
        </div>
        </body>''' % flag_content)
    
    response = make_response(page_content)
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.errorhandler(404)
def not_found(e):
    return '''<!DOCTYPE html>
<html>
<head><title>404 - Not Found</title></head>
<body style="font-family: Arial; background: #1a1a2e; color: #eee; text-align: center; padding-top: 100px;">
<h1>404</h1><p>Page not found</p><a href="/" style="color: #4ecca3;">Return to Home</a>
</body>
</html>''', 404

@app.errorhandler(500)
def server_error(e):
    return '''<!DOCTYPE html>
<html>
<head><title>500 - Server Error</title></head>
<body style="font-family: Arial; background: #1a1a2e; color: #eee; text-align: center; padding-top: 100px;">
<h1>500</h1><p>Internal server error</p><a href="/" style="color: #4ecca3;">Return to Home</a>
</body>
</html>''', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
