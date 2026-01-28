# NetWatch NMS - Network Monitoring System Templates

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetWatch NMS - Network Monitoring</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; display: flex; align-items: center; }
        .header h1 { margin: 0; color: #0f9; font-size: 24px; }
        .header .version { color: #666; margin-left: 10px; font-size: 12px; }
        .nav { background: #0f4c75; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }
        .nav a:hover { background: #3282b8; }
        .container { padding: 30px; max-width: 1200px; margin: 0 auto; }
        .card { background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .card h2 { margin-top: 0; color: #0f9; border-bottom: 1px solid #333; padding-bottom: 10px; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat-box { background: #16213e; border-radius: 8px; padding: 20px; text-align: center; }
        .stat-box .number { font-size: 36px; font-weight: bold; color: #0f9; }
        .stat-box .label { color: #888; margin-top: 5px; }
        .footer { background: #16213e; padding: 15px 30px; text-align: center; color: #666; margin-top: 50px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NetWatch NMS</h1>
        <span class="version">v24.1.0</span>
    </div>
    <div class="nav">
        <a href="/">Overview</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/wireless">Wireless</a>
        <a href="/health">Health</a>
        <a href="/alerts">Alerts</a>
        <a href="/graphs">Graphs</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <div class="stats">
            <div class="stat-box">
                <div class="number">5</div>
                <div class="label">Total Devices</div>
            </div>
            <div class="stat-box">
                <div class="number">4</div>
                <div class="label">Devices Up</div>
            </div>
            <div class="stat-box">
                <div class="number">1</div>
                <div class="label">Devices Down</div>
            </div>
            <div class="stat-box">
                <div class="number">2</div>
                <div class="label">Active Alerts</div>
            </div>
        </div>
        <div class="card">
            <h2>Welcome to NetWatch NMS</h2>
            <p>NetWatch NMS is a comprehensive network monitoring solution that provides real-time visibility into your network infrastructure.</p>
            <p>Use the navigation above to access different monitoring features:</p>
            <ul>
                <li><strong>Devices</strong> - View and manage monitored devices</li>
                <li><strong>Wireless</strong> - Monitor wireless access points and metrics</li>
                <li><strong>Health</strong> - Check system health sensors (CPU, memory, storage)</li>
                <li><strong>Alerts</strong> - View active and historical alerts</li>
                <li><strong>Graphs</strong> - Generate performance graphs</li>
            </ul>
        </div>
        <div class="card">
            <h2>Quick Status</h2>
            <p>System Status: <span style="color: #0f9;">Operational</span></p>
            <p>Last Poll: 2 minutes ago</p>
            <p>Uptime: 45 days, 12 hours, 33 minutes</p>
        </div>
    </div>
    <div class="footer">
        &copy; 2024 NetWatch NMS - Network Monitoring System
    </div>
</body>
</html>
"""

DASHBOARD_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - NetWatch NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; display: flex; align-items: center; }
        .header h1 { margin: 0; color: #0f9; font-size: 24px; }
        .nav { background: #0f4c75; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }
        .nav a:hover { background: #3282b8; }
        .container { padding: 30px; max-width: 1200px; margin: 0 auto; }
        .card { background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .card h2 { margin-top: 0; color: #0f9; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #0f4c75; }
        .status-up { color: #0f9; }
        .status-down { color: #f55; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NetWatch NMS</h1>
    </div>
    <div class="nav">
        <a href="/">Overview</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/wireless">Wireless</a>
        <a href="/health">Health</a>
        <a href="/alerts">Alerts</a>
        <a href="/graphs">Graphs</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Network Dashboard</h2>
            <p>Real-time overview of your network infrastructure.</p>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>Total Bandwidth</td>
                    <td>847 Mbps</td>
                    <td class="status-up">Normal</td>
                </tr>
                <tr>
                    <td>Active Sessions</td>
                    <td>1,247</td>
                    <td class="status-up">Normal</td>
                </tr>
                <tr>
                    <td>CPU Average</td>
                    <td>42%</td>
                    <td class="status-up">Normal</td>
                </tr>
                <tr>
                    <td>Memory Usage</td>
                    <td>68%</td>
                    <td class="status-up">Normal</td>
                </tr>
            </table>
        </div>
    </div>
</body>
</html>
"""

DEVICES_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Devices - NetWatch NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; }}
        .header h1 {{ margin: 0; color: #0f9; font-size: 24px; }}
        .nav {{ background: #0f4c75; padding: 10px 30px; }}
        .nav a {{ color: #fff; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }}
        .nav a:hover {{ background: #3282b8; }}
        .container {{ padding: 30px; max-width: 1200px; margin: 0 auto; }}
        .card {{ background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .card h2 {{ margin-top: 0; color: #0f9; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ background: #0f4c75; }}
        .status-up {{ color: #0f9; }}
        .status-down {{ color: #f55; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NetWatch NMS</h1>
    </div>
    <div class="nav">
        <a href="/">Overview</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/wireless">Wireless</a>
        <a href="/health">Health</a>
        <a href="/alerts">Alerts</a>
        <a href="/graphs">Graphs</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>All Devices</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Hostname</th>
                    <th>IP Address</th>
                    <th>Type</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>1</td>
                    <td>router-core-01</td>
                    <td>192.168.1.1</td>
                    <td>router</td>
                    <td class="status-up">Up</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>switch-access-01</td>
                    <td>192.168.1.10</td>
                    <td>switch</td>
                    <td class="status-up">Up</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>ap-floor1-01</td>
                    <td>192.168.1.100</td>
                    <td>wireless</td>
                    <td class="status-up">Up</td>
                </tr>
                <tr>
                    <td>4</td>
                    <td>ap-floor2-01</td>
                    <td>192.168.1.101</td>
                    <td>wireless</td>
                    <td class="status-down">Down</td>
                </tr>
                <tr>
                    <td>5</td>
                    <td>server-web-01</td>
                    <td>192.168.2.10</td>
                    <td>server</td>
                    <td class="status-up">Up</td>
                </tr>
            </table>
        </div>
    </div>
</body>
</html>
"""

WIRELESS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Wireless Sensors - NetWatch NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; }}
        .header h1 {{ margin: 0; color: #0f9; font-size: 24px; }}
        .nav {{ background: #0f4c75; padding: 10px 30px; }}
        .nav a {{ color: #fff; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }}
        .nav a:hover {{ background: #3282b8; }}
        .container {{ padding: 30px; max-width: 1200px; margin: 0 auto; }}
        .card {{ background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .card h2 {{ margin-top: 0; color: #0f9; }}
        .alert {{ padding: 15px; border-radius: 4px; margin: 15px 0; }}
        .alert-warning {{ background: #856404; border: 1px solid #ffc107; color: #fff; }}
        .alert-success {{ background: #155724; border: 1px solid #28a745; color: #fff; }}
        .metric-nav {{ margin: 20px 0; }}
        .metric-nav a {{ color: #0f9; margin-right: 15px; text-decoration: none; padding: 5px 10px; border: 1px solid #0f9; border-radius: 4px; }}
        .metric-nav a:hover {{ background: #0f9; color: #000; }}
        .sensor-data {{ background: #1a1a2e; padding: 15px; border-radius: 4px; margin: 15px 0; }}
        .sensor-data h4 {{ margin-top: 0; color: #0f9; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NetWatch NMS</h1>
    </div>
    <div class="nav">
        <a href="/">Overview</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/wireless">Wireless</a>
        <a href="/health">Health</a>
        <a href="/alerts">Alerts</a>
        <a href="/graphs">Graphs</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Wireless Sensors {metric_display}</h2>
            <div class="metric-nav">
                <strong>Select Metric:</strong>
                <a href="/wireless?metric=ap-count">AP Count</a>
                <a href="/wireless?metric=clients">Clients</a>
                <a href="/wireless?metric=quality">Quality</a>
                <a href="/wireless?metric=power">Power</a>
                <a href="/wireless?metric=snr">SNR</a>
                <a href="/wireless?metric=errors">Errors</a>
            </div>
            {sensor_content}
        </div>
    </div>
</body>
</html>
"""

WIRELESS_OVERVIEW = """
<div class="sensor-data">
    <h4>Wireless Overview</h4>
    <p>Select a metric type above to view sensor data, or use the metric parameter:</p>
    <code>/wireless?metric=&lt;type&gt;</code>
    <p>Available metrics: ap-count, clients, quality, power, noise-floor, rate, frequency, channel, snr, errors</p>
</div>
<div class="sensor-data">
    <h4>Access Points Summary</h4>
    <p>Total APs: 2</p>
    <p>APs Up: 1</p>
    <p>APs Down: 1</p>
</div>
"""

HEALTH_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Health Sensors - NetWatch NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; }}
        .header h1 {{ margin: 0; color: #0f9; font-size: 24px; }}
        .nav {{ background: #0f4c75; padding: 10px 30px; }}
        .nav a {{ color: #fff; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }}
        .nav a:hover {{ background: #3282b8; }}
        .container {{ padding: 30px; max-width: 1200px; margin: 0 auto; }}
        .card {{ background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .card h2 {{ margin-top: 0; color: #0f9; }}
        .alert {{ padding: 15px; border-radius: 4px; margin: 15px 0; }}
        .alert-warning {{ background: #856404; border: 1px solid #ffc107; color: #fff; }}
        .alert-success {{ background: #155724; border: 1px solid #28a745; color: #fff; }}
        .metric-nav {{ margin: 20px 0; }}
        .metric-nav a {{ color: #0f9; margin-right: 15px; text-decoration: none; padding: 5px 10px; border: 1px solid #0f9; border-radius: 4px; }}
        .metric-nav a:hover {{ background: #0f9; color: #000; }}
        .sensor-data {{ background: #1a1a2e; padding: 15px; border-radius: 4px; margin: 15px 0; }}
        .sensor-data h4 {{ margin-top: 0; color: #0f9; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NetWatch NMS</h1>
    </div>
    <div class="nav">
        <a href="/">Overview</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/wireless">Wireless</a>
        <a href="/health">Health</a>
        <a href="/alerts">Alerts</a>
        <a href="/graphs">Graphs</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Health Sensors {metric_display}</h2>
            <div class="metric-nav">
                <strong>Select Metric:</strong>
                <a href="/health?metric=processor">Processor</a>
                <a href="/health?metric=mempool">Memory</a>
                <a href="/health?metric=storage">Storage</a>
                <a href="/health?metric=temperature">Temperature</a>
                <a href="/health?metric=fans">Fans</a>
                <a href="/health?metric=voltage">Voltage</a>
            </div>
            {sensor_content}
        </div>
    </div>
</body>
</html>
"""

HEALTH_OVERVIEW = """
<div class="sensor-data">
    <h4>Health Overview</h4>
    <p>Select a metric type above to view sensor data, or use the metric parameter:</p>
    <code>/health?metric=&lt;type&gt;</code>
    <p>Available metrics: processor, mempool, storage, temperature, fans, voltage, current, power, load, state</p>
</div>
<div class="sensor-data">
    <h4>System Health Summary</h4>
    <p>Overall Status: <span style="color: #0f9;">Healthy</span></p>
    <p>Active Sensors: 47</p>
    <p>Sensors in Warning: 2</p>
    <p>Sensors Critical: 0</p>
</div>
"""

ALERTS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Alerts - NetWatch NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; display: flex; align-items: center; }
        .header h1 { margin: 0; color: #0f9; font-size: 24px; }
        .nav { background: #0f4c75; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }
        .nav a:hover { background: #3282b8; }
        .container { padding: 30px; max-width: 1200px; margin: 0 auto; }
        .card { background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .card h2 { margin-top: 0; color: #0f9; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #0f4c75; }
        .severity-warning { color: #ffc107; }
        .severity-critical { color: #f55; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NetWatch NMS</h1>
    </div>
    <div class="nav">
        <a href="/">Overview</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/wireless">Wireless</a>
        <a href="/health">Health</a>
        <a href="/alerts">Alerts</a>
        <a href="/graphs">Graphs</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Active Alerts</h2>
            <table>
                <tr>
                    <th>Time</th>
                    <th>Device</th>
                    <th>Alert</th>
                    <th>Severity</th>
                </tr>
                <tr>
                    <td>2024-01-15 14:32:00</td>
                    <td>ap-floor2-01</td>
                    <td>Device unreachable</td>
                    <td class="severity-critical">Critical</td>
                </tr>
                <tr>
                    <td>2024-01-15 12:15:00</td>
                    <td>server-web-01</td>
                    <td>High memory usage (85%)</td>
                    <td class="severity-warning">Warning</td>
                </tr>
            </table>
        </div>
    </div>
</body>
</html>
"""

SETTINGS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Settings - NetWatch NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 15px 30px; display: flex; align-items: center; }
        .header h1 { margin: 0; color: #0f9; font-size: 24px; }
        .nav { background: #0f4c75; padding: 10px 30px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }
        .nav a:hover { background: #3282b8; }
        .container { padding: 30px; max-width: 1200px; margin: 0 auto; }
        .card { background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .card h2 { margin-top: 0; color: #0f9; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #888; }
        .form-group input, .form-group select { width: 300px; padding: 8px; background: #1a1a2e; border: 1px solid #333; color: #eee; border-radius: 4px; }
        .btn { padding: 10px 20px; background: #0f4c75; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #3282b8; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NetWatch NMS</h1>
    </div>
    <div class="nav">
        <a href="/">Overview</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/wireless">Wireless</a>
        <a href="/health">Health</a>
        <a href="/alerts">Alerts</a>
        <a href="/graphs">Graphs</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>System Settings</h2>
            <div class="form-group">
                <label>Polling Interval (seconds)</label>
                <input type="number" value="300" disabled>
            </div>
            <div class="form-group">
                <label>Alert Email</label>
                <input type="email" value="admin@example.com" disabled>
            </div>
            <div class="form-group">
                <label>Time Zone</label>
                <select disabled>
                    <option>UTC</option>
                </select>
            </div>
            <p style="color: #888;">Settings are read-only in demo mode.</p>
        </div>
    </div>
</body>
</html>
"""

GRAPHS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Graphs - NetWatch NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; }}
        .header h1 {{ margin: 0; color: #0f9; font-size: 24px; }}
        .nav {{ background: #0f4c75; padding: 10px 30px; }}
        .nav a {{ color: #fff; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }}
        .nav a:hover {{ background: #3282b8; }}
        .container {{ padding: 30px; max-width: 1200px; margin: 0 auto; }}
        .card {{ background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .card h2 {{ margin-top: 0; color: #0f9; }}
        .graph-placeholder {{ background: #1a1a2e; height: 300px; display: flex; align-items: center; justify-content: center; border: 1px dashed #333; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NetWatch NMS</h1>
    </div>
    <div class="nav">
        <a href="/">Overview</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/wireless">Wireless</a>
        <a href="/health">Health</a>
        <a href="/alerts">Alerts</a>
        <a href="/graphs">Graphs</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Performance Graph</h2>
            <p>Device ID: {device_id} | Graph Type: {graph_type}</p>
            <div class="graph-placeholder">
                <span style="color: #666;">Graph visualization placeholder</span>
            </div>
            <p style="margin-top: 15px; color: #888;">Use parameters: /graphs?id=&lt;device_id&gt;&amp;type=&lt;graph_type&gt;</p>
        </div>
    </div>
</body>
</html>
"""

SEARCH_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Search - NetWatch NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; }}
        .header h1 {{ margin: 0; color: #0f9; font-size: 24px; }}
        .nav {{ background: #0f4c75; padding: 10px 30px; }}
        .nav a {{ color: #fff; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }}
        .nav a:hover {{ background: #3282b8; }}
        .container {{ padding: 30px; max-width: 1200px; margin: 0 auto; }}
        .card {{ background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .card h2 {{ margin-top: 0; color: #0f9; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NetWatch NMS</h1>
    </div>
    <div class="nav">
        <a href="/">Overview</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/wireless">Wireless</a>
        <a href="/health">Health</a>
        <a href="/alerts">Alerts</a>
        <a href="/graphs">Graphs</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Search Results</h2>
            <p>Search query: {query}</p>
            <p style="color: #888;">No results found for your query.</p>
        </div>
    </div>
</body>
</html>
"""

# Legacy constants kept for compatibility (not used in new implementation)
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
