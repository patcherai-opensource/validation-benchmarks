# NetMonitor - Network Monitoring System Constants

INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetMonitor - Network Monitoring System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; color: #eee; }
        .navbar { background: #16213e; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0f3460; }
        .navbar h1 { color: #e94560; font-size: 1.5rem; }
        .navbar nav a { color: #eee; text-decoration: none; margin-left: 1.5rem; padding: 0.5rem 1rem; border-radius: 4px; transition: background 0.3s; }
        .navbar nav a:hover { background: #0f3460; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .hero { text-align: center; padding: 3rem 0; }
        .hero h2 { font-size: 2.5rem; margin-bottom: 1rem; color: #e94560; }
        .hero p { font-size: 1.2rem; color: #94a3b8; margin-bottom: 2rem; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin: 2rem 0; }
        .stat-card { background: #16213e; padding: 1.5rem; border-radius: 8px; text-align: center; border: 1px solid #0f3460; }
        .stat-card h3 { font-size: 2rem; color: #e94560; }
        .stat-card p { color: #94a3b8; margin-top: 0.5rem; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
        .feature-card { background: #16213e; padding: 1.5rem; border-radius: 8px; border: 1px solid #0f3460; }
        .feature-card h4 { color: #e94560; margin-bottom: 0.5rem; }
        .feature-card p { color: #94a3b8; font-size: 0.9rem; }
        .feature-card a { display: inline-block; margin-top: 1rem; color: #e94560; text-decoration: none; }
        .footer { text-align: center; padding: 2rem; color: #64748b; font-size: 0.85rem; border-top: 1px solid #0f3460; margin-top: 3rem; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>NetMonitor</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/dashboard">Dashboard</a>
            <a href="/devices">Devices</a>
            <a href="/ports">Ports</a>
            <a href="/outages">Outages</a>
            <a href="/alerts">Alerts</a>
            <a href="/health">Health</a>
            <a href="/syslog">Syslog</a>
            <a href="/login">Login</a>
        </nav>
    </div>
    <div class="container">
        <div class="hero">
            <h2>Network Infrastructure Monitoring</h2>
            <p>Real-time monitoring, alerting, and analytics for your network devices</p>
        </div>
        <div class="stats">
            <div class="stat-card"><h3>147</h3><p>Devices Monitored</p></div>
            <div class="stat-card"><h3>2,341</h3><p>Active Ports</p></div>
            <div class="stat-card"><h3>99.7%</h3><p>Uptime</p></div>
            <div class="stat-card"><h3>12</h3><p>Active Alerts</p></div>
        </div>
        <div class="features">
            <div class="feature-card">
                <h4>Device Management</h4>
                <p>Monitor routers, switches, servers, and other network devices with SNMP polling.</p>
                <a href="/devices">View Devices &rarr;</a>
            </div>
            <div class="feature-card">
                <h4>Port Statistics</h4>
                <p>Real-time port utilization, error counters, and traffic analysis.</p>
                <a href="/ports">View Ports &rarr;</a>
            </div>
            <div class="feature-card">
                <h4>Outage Tracking</h4>
                <p>Track network outages and device downtime with detailed reporting.</p>
                <a href="/outages">View Outages &rarr;</a>
            </div>
            <div class="feature-card">
                <h4>Health Monitoring</h4>
                <p>Monitor CPU, memory, disk, and temperature sensors across all devices.</p>
                <a href="/health">View Health &rarr;</a>
            </div>
            <div class="feature-card">
                <h4>Syslog Analysis</h4>
                <p>Centralized syslog collection and analysis from network devices.</p>
                <a href="/syslog">View Syslog &rarr;</a>
            </div>
            <div class="feature-card">
                <h4>FDB Search</h4>
                <p>Search forwarding database entries across your network infrastructure.</p>
                <a href="/search/fdb">Search FDB &rarr;</a>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>NetMonitor v2.3.7 | Open Source Network Monitoring</p>
    </div>
</body>
</html>
"""

COMMON_STYLE = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; color: #eee; }
    .navbar { background: #16213e; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0f3460; }
    .navbar h1 { color: #e94560; font-size: 1.5rem; }
    .navbar nav a { color: #eee; text-decoration: none; margin-left: 1.5rem; padding: 0.5rem 1rem; border-radius: 4px; transition: background 0.3s; }
    .navbar nav a:hover { background: #0f3460; }
    .container { max-width: 1000px; margin: 2rem auto; padding: 0 1rem; }
    .page-title { font-size: 2rem; margin-bottom: 1.5rem; color: #e94560; }
    .form-group { margin-bottom: 1.5rem; }
    .form-group label { display: block; margin-bottom: 0.5rem; color: #94a3b8; }
    .form-group input[type="text"], .form-group input[type="date"] { width: 100%; padding: 0.75rem; background: #16213e; border: 1px solid #0f3460; border-radius: 4px; color: #eee; }
    .form-group input:focus { outline: none; border-color: #e94560; }
    .btn { padding: 0.75rem 1.5rem; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; }
    .btn:hover { background: #d63651; }
    .alert { padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
    .alert-success { background: #0f5132; border: 1px solid #198754; color: #d1e7dd; }
    .alert-danger { background: #842029; border: 1px solid #dc3545; color: #f8d7da; }
    .alert-warning { background: #664d03; border: 1px solid #ffc107; color: #fff3cd; }
    .data-table { width: 100%; background: #16213e; border-radius: 4px; overflow: hidden; margin-top: 1rem; }
    .data-table th, .data-table td { padding: 1rem; text-align: left; border-bottom: 1px solid #0f3460; }
    .data-table th { background: #0f3460; color: #e94560; }
    .data-table tr:hover { background: #1e2a47; }
</style>
"""

NAVBAR = """
<div class="navbar">
    <h1>NetMonitor</h1>
    <nav>
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/ports">Ports</a>
        <a href="/outages">Outages</a>
        <a href="/alerts">Alerts</a>
        <a href="/health">Health</a>
        <a href="/syslog">Syslog</a>
        <a href="/login">Login</a>
    </nav>
</div>
"""

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - NetMonitor</title>
    {style}
</head>
<body>
    {navbar}
    <div class="container">
        <h2 class="page-title">Login</h2>
        {error}
        <form method="POST">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="text" name="password" required>
            </div>
            <button class="btn" type="submit">Login</button>
        </form>
    </div>
</body>
</html>
""".format(style=COMMON_STYLE, navbar=NAVBAR, error='{error}')

DASHBOARD_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - NetMonitor</title>
    {style}
</head>
<body>
    {navbar}
    <div class="container">
        <h2 class="page-title">System Dashboard</h2>
        <p>Monitor your entire network infrastructure from a single dashboard.</p>
        <div style="margin-top: 2rem;">
            <h3 style="color: #e94560; margin-bottom: 1rem;">Recent Activity</h3>
            <div style="background: #16213e; padding: 1rem; border-radius: 4px;">
                <p style="color: #94a3b8;">No recent alerts</p>
            </div>
        </div>
    </div>
</body>
</html>
""".format(style=COMMON_STYLE, navbar=NAVBAR)

DEVICES_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Devices - NetMonitor</title>
    {style}
</head>
<body>
    {navbar}
    <div class="container">
        <h2 class="page-title">Network Devices</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Hostname</th>
                    <th>IP Address</th>
                    <th>Status</th>
                    <th>Uptime</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>router-core-01</td>
                    <td>192.168.1.1</td>
                    <td style="color: #198754;">Up</td>
                    <td>45d 12h</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>switch-dist-02</td>
                    <td>192.168.1.10</td>
                    <td style="color: #198754;">Up</td>
                    <td>67d 5h</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
""".format(style=COMMON_STYLE, navbar=NAVBAR)

PORTS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ports - NetMonitor</title>
    {style}
</head>
<body>
    {navbar}
    <div class="container">
        <h2 class="page-title">Port Statistics</h2>
        <form method="GET">
            <div class="form-group">
                <label>Device ID:</label>
                <input type="text" name="device_id" value="{device_id}">
            </div>
            <div class="form-group">
                <label>Hostname:</label>
                <input type="text" name="hostname" value="{hostname}">
            </div>
            <div class="form-group">
                <label>State:</label>
                <input type="text" name="state" value="{state}">
            </div>
            <button class="btn" type="submit">Filter</button>
        </form>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Port</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Speed</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>GigabitEthernet0/1</td>
                    <td>Uplink to Core</td>
                    <td style="color: #198754;">Up</td>
                    <td>1000 Mbps</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
""".format(style=COMMON_STYLE, navbar=NAVBAR, device_id='{device_id}', hostname='{hostname}', state='{state}')

HEALTH_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Health Monitoring - NetMonitor</title>
    {style}
</head>
<body>
    {navbar}
    <div class="container">
        <h2 class="page-title">Health Monitoring</h2>
        <form method="GET">
            <div class="form-group">
                <label>View:</label>
                <input type="text" name="view" value="{view}">
            </div>
            <div class="form-group">
                <label>Graph Type:</label>
                <input type="text" name="graph_type" value="{graph_type}">
            </div>
            <div class="form-group">
                <label>Unit:</label>
                <input type="text" name="unit" value="{unit}">
            </div>
            <button class="btn" type="submit">Update</button>
        </form>
    </div>
</body>
</html>
""".format(style=COMMON_STYLE, navbar=NAVBAR, view='{view}', graph_type='{graph_type}', unit='{unit}')

SYSLOG_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Syslog - NetMonitor</title>
    {style}
</head>
<body>
    {navbar}
    <div class="container">
        <h2 class="page-title">Syslog Messages</h2>
        <form method="GET">
            <div class="form-group">
                <label>From Date:</label>
                <input type="text" name="from" value="{from_date}" placeholder="YYYY-MM-DD">
            </div>
            <div class="form-group">
                <label>To Date:</label>
                <input type="text" name="to" value="{to_date}" placeholder="YYYY-MM-DD">
            </div>
            <div class="form-group">
                <label>Device:</label>
                <input type="text" name="device" value="{device}">
            </div>
            <button class="btn" type="submit">Search</button>
        </form>
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
                <tr>
                    <td>2024-01-28 10:15:32</td>
                    <td>router-01</td>
                    <td>INFO</td>
                    <td>Interface GigabitEthernet0/1 is up</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
""".format(style=COMMON_STYLE, navbar=NAVBAR, from_date='{from_date}', to_date='{to_date}', device='{device}')

# VULNERABLE PAGES - Outages
OUTAGES_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Outages - NetMonitor</title>
    {style}
</head>
<body>
    {navbar}
    <div class="container">
        <h2 class="page-title">Network Outages</h2>
        <form method="GET" action="/outages">
            <div class="form-group">
                <label>From Date:</label>
                <input type="text" name="from" value="{from_date}" placeholder="YYYY-MM-DD" autofocus>
            </div>
            <div class="form-group">
                <label>To Date:</label>
                <input type="text" name="to" value="{to_date}" placeholder="YYYY-MM-DD">
            </div>
            <button class="btn" type="submit">Search Outages</button>
        </form>
    </div>
</body>
</html>
""".format(style=COMMON_STYLE, navbar=NAVBAR, from_date='{from_date}', to_date='{to_date}')

OUTAGES_PAGE_WITH_RESULT = """
<!DOCTYPE html>
<html>
<head>
    <title>Outages - NetMonitor</title>
    {style}
</head>
<body>
    {navbar}
    <div class="container">
        <h2 class="page-title">Network Outages</h2>
        {result}
        <form method="GET" action="/outages">
            <div class="form-group">
                <label>From Date:</label>
                <input type="text" name="from" value="{from_date}" placeholder="YYYY-MM-DD" autofocus>
            </div>
            <div class="form-group">
                <label>To Date:</label>
                <input type="text" name="to" value="{to_date}" placeholder="YYYY-MM-DD">
            </div>
            <button class="btn" type="submit">Search Outages</button>
        </form>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Device</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                    <th>Duration</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>router-core-01</td>
                    <td>2024-01-15 03:22:14</td>
                    <td>2024-01-15 03:45:08</td>
                    <td>22m 54s</td>
                    <td style="color: #198754;">Resolved</td>
                </tr>
                <tr>
                    <td>switch-dist-05</td>
                    <td>2024-01-20 14:10:33</td>
                    <td>2024-01-20 14:12:17</td>
                    <td>1m 44s</td>
                    <td style="color: #198754;">Resolved</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
""".format(style=COMMON_STYLE, navbar=NAVBAR, from_date='{from_date}', to_date='{to_date}', result='{result}')

FDB_SEARCH_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>FDB Search - NetMonitor</title>
    {style}
</head>
<body>
    {navbar}
    <div class="container">
        <h2 class="page-title">Forwarding Database Search</h2>
        <form method="GET">
            <div class="form-group">
                <label>Device ID:</label>
                <input type="text" name="device_id" value="{device_id}">
            </div>
            <div class="form-group">
                <label>Search By:</label>
                <input type="text" name="searchby" value="{searchby}">
            </div>
            <div class="form-group">
                <label>Search Phrase:</label>
                <input type="text" name="searchPhrase" value="{searchPhrase}">
            </div>
            <button class="btn" type="submit">Search</button>
        </form>
    </div>
</body>
</html>
""".format(style=COMMON_STYLE, navbar=NAVBAR, device_id='{device_id}', searchby='{searchby}', searchPhrase='{searchPhrase}')

NTP_APP_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>NTP Statistics - NetMonitor</title>
    {style}
</head>
<body>
    {navbar}
    <div class="container">
        <h2 class="page-title">NTP Application Statistics</h2>
        <form method="GET">
            <div class="form-group">
                <label>View:</label>
                <input type="text" name="view" value="{view}">
            </div>
            <div class="form-group">
                <label>Graph:</label>
                <input type="text" name="graph" value="{graph}">
            </div>
            <button class="btn" type="submit">Update</button>
        </form>
    </div>
</body>
</html>
""".format(style=COMMON_STYLE, navbar=NAVBAR, view='{view}', graph='{graph}')

ALERTS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Alerts - NetMonitor</title>
    {style}
</head>
<body>
    {navbar}
    <div class="container">
        <h2 class="page-title">Active Alerts</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Device</th>
                    <th>Message</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="color: #ffc107;">Warning</td>
                    <td>switch-access-12</td>
                    <td>High CPU usage (85%)</td>
                    <td>10m ago</td>
                </tr>
                <tr>
                    <td style="color: #dc3545;">Critical</td>
                    <td>router-edge-03</td>
                    <td>Link down on interface Gi0/24</td>
                    <td>3h ago</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
""".format(style=COMMON_STYLE, navbar=NAVBAR)

ABOUT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>About - NetMonitor</title>
    {style}
</head>
<body>
    {navbar}
    <div class="container">
        <h2 class="page-title">About NetMonitor</h2>
        <p>NetMonitor v2.3.7</p>
        <p style="margin-top: 1rem; color: #94a3b8;">Open-source network monitoring and management platform.</p>
        <p style="margin-top: 1rem; color: #94a3b8;">Built with Flask and PhantomJS for comprehensive network infrastructure monitoring.</p>
    </div>
</body>
</html>
""".format(style=COMMON_STYLE, navbar=NAVBAR)

# Image routes (kept for compatibility with check_xss function)
IMAGE_ROUTES = {
    "monitoring": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    }
}
