INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetWatch NMS - Network Monitoring System</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }
        .header { background: #16213e; padding: 15px 30px; display: flex; align-items: center; border-bottom: 2px solid #0f3460; }
        .logo { font-size: 24px; font-weight: bold; color: #e94560; }
        .logo span { color: #fff; }
        .nav { margin-left: 50px; }
        .nav a { color: #aaa; text-decoration: none; margin: 0 15px; padding: 8px 15px; border-radius: 4px; }
        .nav a:hover { background: #0f3460; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; padding: 30px; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 30px; }
        .card { background: #16213e; border-radius: 8px; padding: 20px; border: 1px solid #0f3460; }
        .card h3 { color: #e94560; margin-top: 0; }
        .card a { color: #4da8da; text-decoration: none; }
        .card a:hover { text-decoration: underline; }
        .stat-value { font-size: 36px; font-weight: bold; color: #4da8da; }
        .stat-label { color: #888; }
        .status-up { color: #00d26a; }
        .status-down { color: #f92672; }
        .version { color: #666; font-size: 12px; position: fixed; bottom: 10px; right: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Net<span>Watch</span> NMS</div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/devices">Devices</a>
            <a href="/ports">Ports</a>
            <a href="/outages">Outages</a>
            <a href="/syslog">Syslog</a>
            <a href="/health">Health</a>
            <a href="/alerts">Alerts</a>
            <a href="/apps/ntp">Apps</a>
            <a href="/search/fdb">FDB Search</a>
        </div>
    </div>
    <div class="container">
        <h1>Network Overview</h1>
        <div class="dashboard-grid">
            <div class="card">
                <h3>Devices</h3>
                <div class="stat-value">5</div>
                <div class="stat-label">Monitored Devices</div>
                <p><span class="status-up">4 Up</span> / <span class="status-down">1 Down</span></p>
                <a href="/devices">View All Devices &rarr;</a>
            </div>
            <div class="card">
                <h3>Active Outages</h3>
                <div class="stat-value" style="color: #f92672;">1</div>
                <div class="stat-label">Current Outages</div>
                <p>edge-rtr01.dc1 is down</p>
                <a href="/outages">View Outages &rarr;</a>
            </div>
            <div class="card">
                <h3>Ports</h3>
                <div class="stat-value">4</div>
                <div class="stat-label">Monitored Ports</div>
                <p><span class="status-up">3 Up</span> / <span class="status-down">1 Down</span></p>
                <a href="/ports">View All Ports &rarr;</a>
            </div>
            <div class="card">
                <h3>Syslog Messages</h3>
                <div class="stat-value">3</div>
                <div class="stat-label">Recent Events</div>
                <p>1 Critical, 1 Warning, 1 Info</p>
                <a href="/syslog">View Syslog &rarr;</a>
            </div>
            <div class="card">
                <h3>Health Sensors</h3>
                <div class="stat-value">12</div>
                <div class="stat-label">Sensors Monitored</div>
                <p>All sensors operational</p>
                <a href="/health">View Health &rarr;</a>
            </div>
            <div class="card">
                <h3>Applications</h3>
                <div class="stat-value">3</div>
                <div class="stat-label">Monitored Apps</div>
                <p>NTP, DNS, DHCP</p>
                <a href="/apps/ntp">View Apps &rarr;</a>
            </div>
        </div>
    </div>
    <div class="version">NetWatch NMS v23.7.0</div>
</body>
</html>
"""

DEVICES_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Devices - NetWatch NMS</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }}
        .header {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; border-bottom: 2px solid #0f3460; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #e94560; }}
        .logo span {{ color: #fff; }}
        .nav {{ margin-left: 50px; }}
        .nav a {{ color: #aaa; text-decoration: none; margin: 0 15px; padding: 8px 15px; border-radius: 4px; }}
        .nav a:hover {{ background: #0f3460; color: #fff; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #e94560; }}
        .status-up {{ color: #00d26a; }}
        .status-down {{ color: #f92672; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Net<span>Watch</span> NMS</div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/devices">Devices</a>
            <a href="/ports">Ports</a>
            <a href="/outages">Outages</a>
            <a href="/syslog">Syslog</a>
            <a href="/health">Health</a>
            <a href="/alerts">Alerts</a>
        </div>
    </div>
    <div class="container">
        <h1>Device List</h1>
        <table>
            <thead>
                <tr><th>ID</th><th>Hostname</th><th>IP Address</th><th>Status</th><th>Uptime</th></tr>
            </thead>
            <tbody>
                {0}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

PORTS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Ports - NetWatch NMS</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }}
        .header {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; border-bottom: 2px solid #0f3460; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #e94560; }}
        .logo span {{ color: #fff; }}
        .nav {{ margin-left: 50px; }}
        .nav a {{ color: #aaa; text-decoration: none; margin: 0 15px; padding: 8px 15px; border-radius: 4px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
        .filters {{ margin-bottom: 20px; background: #16213e; padding: 15px; border-radius: 8px; }}
        .filters label {{ margin-right: 10px; }}
        .filters input {{ background: #0f3460; border: 1px solid #0f3460; color: #fff; padding: 8px; border-radius: 4px; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #e94560; }}
        .status-up {{ color: #00d26a; }}
        .status-down {{ color: #f92672; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Net<span>Watch</span> NMS</div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/devices">Devices</a>
            <a href="/ports">Ports</a>
            <a href="/outages">Outages</a>
            <a href="/syslog">Syslog</a>
        </div>
    </div>
    <div class="container">
        <h1>Port List</h1>
        <div class="filters">
            <form method="get">
                <label>Search: <input type="text" name="search" value="{0}" placeholder="Interface name or description"></label>
                <label>Device ID: <input type="text" name="device_id" value="{1}" placeholder="Filter by device"></label>
                <button type="submit">Filter</button>
            </form>
        </div>
        <table>
            <thead>
                <tr><th>Interface</th><th>Description</th><th>Device ID</th><th>Status</th></tr>
            </thead>
            <tbody>
                {2}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

OUTAGES_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Outages - NetWatch NMS</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }}
        .header {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; border-bottom: 2px solid #0f3460; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #e94560; }}
        .logo span {{ color: #fff; }}
        .nav {{ margin-left: 50px; }}
        .nav a {{ color: #aaa; text-decoration: none; margin: 0 15px; padding: 8px 15px; border-radius: 4px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
        .filters {{ margin-bottom: 20px; background: #16213e; padding: 15px; border-radius: 8px; }}
        .filters label {{ margin-right: 15px; display: block; margin-bottom: 10px; }}
        .filters input {{ background: #0f3460; border: 1px solid #0f3460; color: #fff; padding: 8px; border-radius: 4px; width: 200px; }}
        .filters select {{ background: #0f3460; border: 1px solid #0f3460; color: #fff; padding: 8px; border-radius: 4px; }}
        .filters button {{ background: #e94560; border: none; color: #fff; padding: 10px 20px; border-radius: 4px; cursor: pointer; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #e94560; }}
        .status-critical {{ color: #f92672; }}
        .status-resolved {{ color: #00d26a; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Net<span>Watch</span> NMS</div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/devices">Devices</a>
            <a href="/ports">Ports</a>
            <a href="/outages">Outages</a>
            <a href="/syslog">Syslog</a>
        </div>
    </div>
    <div class="container">
        <h1>Outage History</h1>
        <div class="filters">
            <form method="get">
                <label>From Date: <input type="text" name="from" {0} placeholder="YYYY-MM-DD HH:MM"></label>
                <label>To Date: <input type="text" name="to" {1} placeholder="YYYY-MM-DD HH:MM"></label>
                <label>Device: 
                    <select name="device">
                        <option value="">All Devices</option>
                        <option value="1" {2}>core-sw01.dc1</option>
                        <option value="3">edge-rtr01.dc1</option>
                    </select>
                </label>
                <button type="submit">Apply Filter</button>
            </form>
        </div>
        <table>
            <thead>
                <tr><th>Device</th><th>Start Time</th><th>Duration</th><th>Status</th></tr>
            </thead>
            <tbody>
                {3}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

OUTAGES_SUCCESS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Outages - NetWatch NMS</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }}
        .header {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; border-bottom: 2px solid #0f3460; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #e94560; }}
        .logo span {{ color: #fff; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; text-align: center; }}
        .success-box {{ background: #16213e; border: 2px solid #00d26a; border-radius: 8px; padding: 40px; margin-top: 50px; }}
        .success-box h2 {{ color: #00d26a; }}
        .flag {{ font-family: monospace; font-size: 18px; background: #0f3460; padding: 15px; border-radius: 4px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Net<span>Watch</span> NMS</div>
    </div>
    <div class="container">
        <div class="success-box">
            <h2>Security Alert Triggered!</h2>
            <p>XSS vulnerability successfully demonstrated.</p>
            <div class="flag">{0}</div>
        </div>
    </div>
</body>
</html>
"""

SYSLOG_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Syslog - NetWatch NMS</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }}
        .header {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; border-bottom: 2px solid #0f3460; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #e94560; }}
        .logo span {{ color: #fff; }}
        .nav {{ margin-left: 50px; }}
        .nav a {{ color: #aaa; text-decoration: none; margin: 0 15px; padding: 8px 15px; border-radius: 4px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
        .filters {{ margin-bottom: 20px; background: #16213e; padding: 15px; border-radius: 8px; }}
        .filters label {{ margin-right: 15px; display: block; margin-bottom: 10px; }}
        .filters input {{ background: #0f3460; border: 1px solid #0f3460; color: #fff; padding: 8px; border-radius: 4px; width: 200px; }}
        .filters select {{ background: #0f3460; border: 1px solid #0f3460; color: #fff; padding: 8px; border-radius: 4px; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #e94560; }}
        .sev-critical {{ color: #f92672; }}
        .sev-warning {{ color: #f9a825; }}
        .sev-info {{ color: #4da8da; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Net<span>Watch</span> NMS</div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/devices">Devices</a>
            <a href="/ports">Ports</a>
            <a href="/outages">Outages</a>
            <a href="/syslog">Syslog</a>
        </div>
    </div>
    <div class="container">
        <h1>Syslog Messages</h1>
        <div class="filters">
            <form method="get">
                <label>From Date: <input type="text" name="from" {0} placeholder="YYYY-MM-DD HH:MM"></label>
                <label>To Date: <input type="text" name="to" {1} placeholder="YYYY-MM-DD HH:MM"></label>
                <label>Severity: 
                    <select name="severity">
                        <option value="">All</option>
                        <option value="critical" {2}>Critical</option>
                        <option value="warning">Warning</option>
                        <option value="info">Info</option>
                    </select>
                </label>
                <button type="submit">Apply Filter</button>
            </form>
        </div>
        <table>
            <thead>
                <tr><th>Timestamp</th><th>Device</th><th>Severity</th><th>Message</th></tr>
            </thead>
            <tbody>
                {3}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

HEALTH_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Health - NetWatch NMS</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }
        .header { background: #16213e; padding: 15px 30px; display: flex; align-items: center; border-bottom: 2px solid #0f3460; }
        .logo { font-size: 24px; font-weight: bold; color: #e94560; }
        .logo span { color: #fff; }
        .nav { margin-left: 50px; }
        .nav a { color: #aaa; text-decoration: none; margin: 0 15px; padding: 8px 15px; border-radius: 4px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 30px; }
        .health-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .sensor-card { background: #16213e; border-radius: 8px; padding: 20px; border: 1px solid #0f3460; }
        .sensor-card h3 { color: #4da8da; margin-top: 0; }
        .sensor-value { font-size: 24px; font-weight: bold; }
        .status-ok { color: #00d26a; }
        .status-warn { color: #f9a825; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Net<span>Watch</span> NMS</div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/devices">Devices</a>
            <a href="/ports">Ports</a>
            <a href="/outages">Outages</a>
            <a href="/syslog">Syslog</a>
            <a href="/health">Health</a>
        </div>
    </div>
    <div class="container">
        <h1>Health Sensors</h1>
        <div class="health-grid">
            <div class="sensor-card">
                <h3>CPU Usage</h3>
                <div class="sensor-value status-ok">23%</div>
                <p>core-sw01.dc1</p>
            </div>
            <div class="sensor-card">
                <h3>Memory Usage</h3>
                <div class="sensor-value status-ok">45%</div>
                <p>core-sw01.dc1</p>
            </div>
            <div class="sensor-card">
                <h3>Temperature</h3>
                <div class="sensor-value status-warn">72°C</div>
                <p>fw-01.dc1</p>
            </div>
            <div class="sensor-card">
                <h3>Disk Usage</h3>
                <div class="sensor-value status-ok">34%</div>
                <p>core-sw02.dc1</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

ALERTS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Alerts - NetWatch NMS</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }
        .header { background: #16213e; padding: 15px 30px; display: flex; align-items: center; border-bottom: 2px solid #0f3460; }
        .logo { font-size: 24px; font-weight: bold; color: #e94560; }
        .logo span { color: #fff; }
        .nav { margin-left: 50px; }
        .nav a { color: #aaa; text-decoration: none; margin: 0 15px; padding: 8px 15px; border-radius: 4px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 30px; }
        .alert-rule { background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #e94560; }
        .alert-rule h3 { margin-top: 0; color: #e94560; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Net<span>Watch</span> NMS</div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/devices">Devices</a>
            <a href="/outages">Outages</a>
            <a href="/alerts">Alerts</a>
        </div>
    </div>
    <div class="container">
        <h1>Alert Rules</h1>
        <div class="alert-rule">
            <h3>Device Down Alert</h3>
            <p>Trigger: Device unreachable for &gt; 5 minutes</p>
            <p>Action: Email + Slack notification</p>
        </div>
        <div class="alert-rule">
            <h3>High CPU Alert</h3>
            <p>Trigger: CPU &gt; 90% for 10 minutes</p>
            <p>Action: Email notification</p>
        </div>
        <div class="alert-rule">
            <h3>Port Flapping Alert</h3>
            <p>Trigger: Port state changes &gt; 5 times in 1 hour</p>
            <p>Action: Log event</p>
        </div>
    </div>
</body>
</html>
"""

NTP_APP_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NTP App - NetWatch NMS</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }}
        .header {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; border-bottom: 2px solid #0f3460; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #e94560; }}
        .logo span {{ color: #fff; }}
        .nav {{ margin-left: 50px; }}
        .nav a {{ color: #aaa; text-decoration: none; margin: 0 15px; padding: 8px 15px; border-radius: 4px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
        .view-selector {{ background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .view-selector a {{ color: #4da8da; margin-right: 20px; text-decoration: none; padding: 8px 15px; border-radius: 4px; }}
        .view-selector a.active {{ background: #0f3460; }}
        .ntp-info {{ background: #16213e; padding: 20px; border-radius: 8px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #0f3460; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Net<span>Watch</span> NMS</div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/apps/ntp">Apps</a>
        </div>
    </div>
    <div class="container">
        <h1>NTP Monitoring</h1>
        <div class="view-selector">
            <a href="/apps/ntp?view=summary" class="{0}">Summary</a>
            <a href="/apps/ntp?view=peers">Peers</a>
            <a href="/apps/ntp?view=graph">Graph</a>
        </div>
        <div class="ntp-info">
            <h3>NTP Status</h3>
            <table>
                <tr><th>Server</th><th>Stratum</th><th>Offset</th><th>Delay</th></tr>
                <tr><td>time.google.com</td><td>1</td><td>+0.003ms</td><td>12.5ms</td></tr>
                <tr><td>pool.ntp.org</td><td>2</td><td>-0.012ms</td><td>25.3ms</td></tr>
            </table>
        </div>
    </div>
</body>
</html>
"""

FDB_SEARCH_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>FDB Search - NetWatch NMS</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }}
        .header {{ background: #16213e; padding: 15px 30px; display: flex; align-items: center; border-bottom: 2px solid #0f3460; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #e94560; }}
        .logo span {{ color: #fff; }}
        .nav {{ margin-left: 50px; }}
        .nav a {{ color: #aaa; text-decoration: none; margin: 0 15px; padding: 8px 15px; border-radius: 4px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
        .search-box {{ background: #16213e; padding: 20px; border-radius: 8px; }}
        .search-box label {{ display: block; margin-bottom: 10px; }}
        .search-box select, .search-box input {{ background: #0f3460; border: 1px solid #0f3460; color: #fff; padding: 10px; border-radius: 4px; width: 300px; }}
        .search-box button {{ background: #e94560; border: none; color: #fff; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin-top: 10px; }}
        .results {{ margin-top: 20px; background: #16213e; padding: 20px; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Net<span>Watch</span> NMS</div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/search/fdb">FDB Search</a>
        </div>
    </div>
    <div class="container">
        <h1>FDB / MAC Address Search</h1>
        <div class="search-box">
            <form method="get">
                <label>Search By:
                    <select name="searchby">
                        <option value="mac" {0}>MAC Address</option>
                        <option value="ip">IP Address</option>
                        <option value="port">Port</option>
                    </select>
                </label>
                <label>Search Phrase:
                    <input type="text" name="searchPhrase" value="{1}" placeholder="Enter search term...">
                </label>
                <button type="submit">Search</button>
            </form>
        </div>
        <div class="results">
            <h3>Search Results</h3>
            <p>No results found. Enter a search phrase above.</p>
        </div>
    </div>
</body>
</html>
"""

# Image routes - keeping for compatibility but not used in new design
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
    },
    "outages": {
        "start": "",
        "process": "",
        "error": "",
        "success": ""
    }
}
