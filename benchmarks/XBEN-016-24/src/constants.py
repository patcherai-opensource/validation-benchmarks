INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMon - Network Monitoring System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .navbar { background: #16213e; padding: 15px 30px; display: flex; align-items: center; }
        .navbar .logo { font-size: 24px; font-weight: bold; color: #00d4ff; }
        .navbar .nav-links { margin-left: 50px; }
        .navbar .nav-links a { color: #aaa; text-decoration: none; margin-right: 20px; }
        .navbar .nav-links a:hover { color: #00d4ff; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .dashboard-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .card { background: #16213e; border-radius: 8px; padding: 20px; transition: transform 0.2s; }
        .card:hover { transform: translateY(-5px); }
        .card h3 { color: #00d4ff; margin-top: 0; }
        .card p { color: #888; }
        .card a { display: inline-block; margin-top: 10px; color: #00d4ff; text-decoration: none; }
        .card a:hover { text-decoration: underline; }
        .status-ok { color: #4caf50; }
        .status-warning { color: #ff9800; }
        .footer { text-align: center; padding: 20px; color: #666; margin-top: 50px; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">NetMon</div>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/devices">Devices</a>
            <a href="/health">Health</a>
            <a href="/wireless">Wireless</a>
        </div>
    </div>
    <div class="container">
        <h1>Network Monitoring Dashboard</h1>
        <p>Monitor your network infrastructure in real-time.</p>
        
        <div class="dashboard-cards">
            <div class="card">
                <h3>Devices</h3>
                <p>2 devices monitored</p>
                <p class="status-ok">All systems operational</p>
                <a href="/devices">View Devices &rarr;</a>
            </div>
            <div class="card">
                <h3>Health Sensors</h3>
                <p>Monitor CPU, memory, temperature</p>
                <p class="status-ok">All sensors normal</p>
                <a href="/health">View Health &rarr;</a>
            </div>
            <div class="card">
                <h3>Wireless Sensors</h3>
                <p>Signal strength, noise levels</p>
                <p class="status-ok">Wireless networks healthy</p>
                <a href="/wireless">View Wireless &rarr;</a>
            </div>
            <div class="card">
                <h3>API Access</h3>
                <p>RESTful API for automation</p>
                <p>Endpoint: /api/v0/</p>
                <a href="/api/v0/devices">API Docs &rarr;</a>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>NetMon v2.3.1 - Network Monitoring System</p>
    </div>
</body>
</html>
"""

WIRELESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMon - Wireless Sensors</title>
</head>
<body>
<h1>Wireless Sensors - {sensor_class}</h1>
<p>No sensors of type {sensor_class} found.</p>
</body>
</html>
"""

WIRELESS_PAGE_FULL = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMon - Wireless Sensors</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .navbar {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; }}
        .navbar .logo {{ font-size: 24px; font-weight: bold; color: #00d4ff; }}
        .navbar .nav-links {{ margin-left: 50px; }}
        .navbar .nav-links a {{ color: #aaa; text-decoration: none; margin-right: 20px; }}
        .navbar .nav-links a:hover {{ color: #00d4ff; }}
        .container {{ max-width: 1200px; margin: 40px auto; padding: 0 20px; }}
        .breadcrumb {{ color: #888; margin-bottom: 20px; }}
        .breadcrumb a {{ color: #00d4ff; text-decoration: none; }}
        .sensor-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }}
        .sensor-type {{ background: #16213e; padding: 15px; border-radius: 5px; cursor: pointer; }}
        .sensor-type:hover {{ background: #1f3460; }}
        .sensor-type.active {{ border-left: 3px solid #00d4ff; }}
        .alert {{ padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .alert-warning {{ background: #ff9800; color: #000; }}
        .alert-success {{ background: #4caf50; color: #fff; }}
        .alert-info {{ background: #2196f3; color: #fff; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ background: #16213e; }}
        .footer {{ text-align: center; padding: 20px; color: #666; margin-top: 50px; }}
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">NetMon</div>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/devices">Devices</a>
            <a href="/health">Health</a>
            <a href="/wireless">Wireless</a>
        </div>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> / <a href="/wireless">Wireless</a> / {sensor_class}
        </div>
        
        <h1>Wireless Sensors</h1>
        <p>Monitor wireless network signal quality and performance.</p>
        
        {result}
        
        <div class="sensor-grid">
            <a href="/wireless/signal" class="sensor-type">Signal Strength</a>
            <a href="/wireless/noise" class="sensor-type">Noise Level</a>
            <a href="/wireless/snr" class="sensor-type">SNR</a>
            <a href="/wireless/rate" class="sensor-type">Data Rate</a>
            <a href="/wireless/clients" class="sensor-type">Clients</a>
            <a href="/wireless/frequency" class="sensor-type">Frequency</a>
        </div>
        
        <h2>Current View: {sensor_class}</h2>
        <table>
            <thead>
                <tr>
                    <th>Device</th>
                    <th>Sensor</th>
                    <th>Value</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td colspan="4" style="text-align: center; color: #888;">
                        No sensors of type {sensor_class} found.
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="footer">
        <p>NetMon v2.3.1 - Network Monitoring System</p>
    </div>
</body>
</html>
"""

HEALTH_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMon - Health Sensors</title>
</head>
<body>
<h1>Health Sensors - {active_metric}</h1>
<p>No sensors of type {active_metric} found.</p>
</body>
</html>
"""

HEALTH_PAGE_FULL = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMon - Health Sensors</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .navbar {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; }}
        .navbar .logo {{ font-size: 24px; font-weight: bold; color: #00d4ff; }}
        .navbar .nav-links {{ margin-left: 50px; }}
        .navbar .nav-links a {{ color: #aaa; text-decoration: none; margin-right: 20px; }}
        .navbar .nav-links a:hover {{ color: #00d4ff; }}
        .container {{ max-width: 1200px; margin: 40px auto; padding: 0 20px; }}
        .breadcrumb {{ color: #888; margin-bottom: 20px; }}
        .breadcrumb a {{ color: #00d4ff; text-decoration: none; }}
        .sensor-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }}
        .sensor-type {{ background: #16213e; padding: 15px; border-radius: 5px; cursor: pointer; text-decoration: none; color: #eee; display: block; }}
        .sensor-type:hover {{ background: #1f3460; }}
        .sensor-type.active {{ border-left: 3px solid #00d4ff; }}
        .alert {{ padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .alert-warning {{ background: #ff9800; color: #000; }}
        .alert-success {{ background: #4caf50; color: #fff; }}
        .alert-info {{ background: #2196f3; color: #fff; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ background: #16213e; }}
        .footer {{ text-align: center; padding: 20px; color: #666; margin-top: 50px; }}
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">NetMon</div>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/devices">Devices</a>
            <a href="/health">Health</a>
            <a href="/wireless">Wireless</a>
        </div>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> / <a href="/health">Health</a> / {active_metric}
        </div>
        
        <h1>Device Health</h1>
        <p>Monitor device health metrics including CPU, memory, disk, and environmental sensors.</p>
        
        {result}
        
        <div class="sensor-grid">
            <a href="/health/processor" class="sensor-type">CPU Usage</a>
            <a href="/health/memory" class="sensor-type">Memory</a>
            <a href="/health/disk" class="sensor-type">Disk Space</a>
            <a href="/health/temperature" class="sensor-type">Temperature</a>
            <a href="/health/fanspeed" class="sensor-type">Fan Speed</a>
            <a href="/health/voltage" class="sensor-type">Voltage</a>
        </div>
        
        <h2>Current View: {active_metric}</h2>
        <table>
            <thead>
                <tr>
                    <th>Device</th>
                    <th>Sensor</th>
                    <th>Current</th>
                    <th>Warning</th>
                    <th>Critical</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td colspan="5" style="text-align: center; color: #888;">
                        No sensors of type {active_metric} found.
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="footer">
        <p>NetMon v2.3.1 - Network Monitoring System</p>
    </div>
</body>
</html>
"""

DEVICES_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMon - Devices</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .navbar { background: #16213e; padding: 15px 30px; display: flex; align-items: center; }
        .navbar .logo { font-size: 24px; font-weight: bold; color: #00d4ff; }
        .navbar .nav-links { margin-left: 50px; }
        .navbar .nav-links a { color: #aaa; text-decoration: none; margin-right: 20px; }
        .navbar .nav-links a:hover { color: #00d4ff; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .breadcrumb { color: #888; margin-bottom: 20px; }
        .breadcrumb a { color: #00d4ff; text-decoration: none; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #16213e; }
        .status-up { color: #4caf50; }
        .status-down { color: #f44336; }
        .footer { text-align: center; padding: 20px; color: #666; margin-top: 50px; }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="logo">NetMon</div>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/devices">Devices</a>
            <a href="/health">Health</a>
            <a href="/wireless">Wireless</a>
        </div>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> / Devices
        </div>
        
        <h1>Monitored Devices</h1>
        <p>Overview of all devices in your network.</p>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Hostname</th>
                    <th>IP Address</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Uptime</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>switch01.local</td>
                    <td>192.168.1.1</td>
                    <td>Network Switch</td>
                    <td class="status-up">Up</td>
                    <td>45 days</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>ap01.local</td>
                    <td>192.168.1.10</td>
                    <td>Access Point</td>
                    <td class="status-up">Up</td>
                    <td>12 days</td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="footer">
        <p>NetMon v2.3.1 - Network Monitoring System</p>
    </div>
</body>
</html>
"""

# Keep IMAGE_ROUTES for backwards compatibility (not used in new version)
IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    },
    "xss_easy_med": {
        "start": "static/img/cookies/new_triangle.png",
        "process": "static/img/cookies/error_triangle.png",
        "error": "static/img/cookies/error_triangle.png",
        "success": "static/img/cookies/success_triangle.png"
    },
    "xss_medium": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    },
    "xss_hard": {
        "start": "static/img/cookies/new_umbrella.png",
        "process": "static/img/cookies/error_umbrella.png",
        "error": "static/img/cookies/error_umbrella.png",
        "success": "static/img/cookies/success_umbrella.png"
    }
}
