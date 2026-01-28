# NetMonitor - Network Monitoring Dashboard
# Constants and HTML Templates

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMonitor - Network Monitoring Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .header { background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .header h1 { margin: 0; color: #0f9b8e; }
        .header span { color: #666; font-size: 12px; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .nav a { background: #0f3460; color: #e94560; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .nav a:hover { background: #e94560; color: white; }
        .card { background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 15px; }
        .card h3 { color: #0f9b8e; margin-top: 0; }
        .status-ok { color: #4caf50; }
        .status-warn { color: #ff9800; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #333; }
        th { color: #0f9b8e; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NetMonitor Dashboard</h1>
        <span>v2.3.7 - Network Monitoring System</span>
    </div>
    
    <div class="nav">
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/ports">Ports</a>
        <a href="/outages">Outages</a>
        <a href="/syslog">System Logs</a>
        <a href="/health">Health Status</a>
        <a href="/ntp">NTP Sync</a>
        <a href="/search">Search</a>
        <a href="/realtime">Realtime Stats</a>
        <a href="/about">About</a>
    </div>
    
    <div class="card">
        <h3>System Overview</h3>
        <table>
            <tr><th>Metric</th><th>Value</th><th>Status</th></tr>
            <tr><td>Active Devices</td><td>24</td><td class="status-ok">Online</td></tr>
            <tr><td>Monitored Ports</td><td>156</td><td class="status-ok">Healthy</td></tr>
            <tr><td>Open Alerts</td><td>3</td><td class="status-warn">Warning</td></tr>
            <tr><td>Uptime</td><td>99.97%</td><td class="status-ok">Normal</td></tr>
        </table>
    </div>
    
    <div class="card">
        <h3>Recent Activity</h3>
        <p>2024-01-15 10:23:45 - Device router-core-01 CPU usage high (78%)</p>
        <p>2024-01-15 10:15:32 - Port Gi0/1 on switch-floor2 went down</p>
        <p>2024-01-15 10:12:18 - NTP sync completed successfully</p>
    </div>
    
    <div class="footer">
        NetMonitor v2.3.7 | &copy; 2024 Network Operations Center
    </div>
</body>
</html>
"""

# Dashboard page
DASHBOARD_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMonitor - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .header { background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .header h1 { margin: 0; color: #0f9b8e; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .nav a { background: #0f3460; color: #e94560; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .nav a:hover { background: #e94560; color: white; }
        .card { background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 15px; }
        .card h3 { color: #0f9b8e; margin-top: 0; }
        input { padding: 8px; margin: 5px 0; border: 1px solid #333; background: #0f3460; color: #eee; border-radius: 4px; }
        button { padding: 8px 16px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .graph-placeholder { background: #0f3460; height: 200px; display: flex; align-items: center; justify-content: center; border-radius: 4px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NetMonitor - Dashboard</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/devices">Devices</a>
        <a href="/ports">Ports</a>
        <a href="/outages">Outages</a>
        <a href="/syslog">System Logs</a>
    </div>
    <div class="card">
        <h3>Quick Stats</h3>
        <div class="graph-placeholder">[Performance Graph - No data selected]</div>
    </div>
    <div class="card">
        <h3>Search Dashboard</h3>
        <form action="/dashboard" method="get">
            <input type="text" name="view" placeholder="View type..." value="{0}">
            <input type="text" name="graph" placeholder="Graph type..." value="{1}">
            <button type="submit">Update View</button>
        </form>
        {2}
    </div>
</body>
</html>
"""

# Devices page - safe (properly escaped)
DEVICES_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMonitor - Devices</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
        .header {{ background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: #0f9b8e; }}
        .nav {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
        .nav a {{ background: #0f3460; color: #e94560; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        .card {{ background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 15px; }}
        .card h3 {{ color: #0f9b8e; margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ color: #0f9b8e; }}
        input {{ padding: 8px; margin: 5px 0; border: 1px solid #333; background: #0f3460; color: #eee; border-radius: 4px; }}
        button {{ padding: 8px 16px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        .status-ok {{ color: #4caf50; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NetMonitor - Device List</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/ports">Ports</a>
        <a href="/outages">Outages</a>
    </div>
    <div class="card">
        <h3>Filter Devices</h3>
        <form action="/devices" method="get">
            <input type="text" name="device_id" placeholder="Device ID..." value="{device_id}">
            <input type="text" name="hostname" placeholder="Hostname..." value="{hostname}">
            <button type="submit">Filter</button>
        </form>
    </div>
    <div class="card">
        <h3>Device List</h3>
        <table>
            <tr><th>ID</th><th>Hostname</th><th>IP</th><th>Status</th></tr>
            <tr><td>1</td><td>router-core-01</td><td>10.0.0.1</td><td class="status-ok">Online</td></tr>
            <tr><td>2</td><td>switch-floor1</td><td>10.0.1.1</td><td class="status-ok">Online</td></tr>
            <tr><td>3</td><td>switch-floor2</td><td>10.0.2.1</td><td class="status-ok">Online</td></tr>
        </table>
        {message}
    </div>
</body>
</html>
"""

# Ports page - safe
PORTS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMonitor - Ports</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
        .header {{ background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: #0f9b8e; }}
        .nav {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
        .nav a {{ background: #0f3460; color: #e94560; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        .card {{ background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 15px; }}
        .card h3 {{ color: #0f9b8e; margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ color: #0f9b8e; }}
        input {{ padding: 8px; margin: 5px 0; border: 1px solid #333; background: #0f3460; color: #eee; border-radius: 4px; }}
        button {{ padding: 8px 16px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        .status-ok {{ color: #4caf50; }}
        .status-down {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NetMonitor - Port List</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/outages">Outages</a>
    </div>
    <div class="card">
        <h3>Filter Ports</h3>
        <form action="/ports" method="get">
            <input type="text" name="device_id" placeholder="Device ID..." value="{device_id}">
            <input type="text" name="state" placeholder="State (up/down)..." value="{state}">
            <button type="submit">Filter</button>
        </form>
    </div>
    <div class="card">
        <h3>Port Status</h3>
        <table>
            <tr><th>Device</th><th>Port</th><th>Speed</th><th>Status</th></tr>
            <tr><td>router-core-01</td><td>Gi0/0</td><td>1Gbps</td><td class="status-ok">Up</td></tr>
            <tr><td>router-core-01</td><td>Gi0/1</td><td>1Gbps</td><td class="status-ok">Up</td></tr>
            <tr><td>switch-floor2</td><td>Gi0/1</td><td>1Gbps</td><td class="status-down">Down</td></tr>
        </table>
        {message}
    </div>
</body>
</html>
"""

# Outages page - VULNERABLE - reflects 'from' and 'to' parameters unsafely
OUTAGES_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMonitor - Outages</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
        .header {{ background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: #0f9b8e; }}
        .nav {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
        .nav a {{ background: #0f3460; color: #e94560; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        .card {{ background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 15px; }}
        .card h3 {{ color: #0f9b8e; margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ color: #0f9b8e; }}
        input {{ padding: 8px; margin: 5px 0; border: 1px solid #333; background: #0f3460; color: #eee; border-radius: 4px; }}
        button {{ padding: 8px 16px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        .status-resolved {{ color: #4caf50; }}
        .status-active {{ color: #f44336; }}
        .result {{ margin-top: 15px; padding: 15px; background: #0f3460; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NetMonitor - Outage History</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/ports">Ports</a>
        <a href="/syslog">System Logs</a>
    </div>
    <div class="card">
        <h3>Date Range Filter</h3>
        <form action="/outages" method="get">
            <label>From: <input type="text" name="from" placeholder="YYYY-MM-DD" value="{from_date}"></label>
            <label>To: <input type="text" name="to" placeholder="YYYY-MM-DD" value="{to_date}"></label>
            <button type="submit">Search</button>
        </form>
    </div>
    <div class="card">
        <h3>Outage Records</h3>
        <table>
            <tr><th>Date</th><th>Device</th><th>Duration</th><th>Status</th></tr>
            <tr><td>2024-01-14</td><td>switch-floor2</td><td>2h 15m</td><td class="status-resolved">Resolved</td></tr>
            <tr><td>2024-01-10</td><td>router-edge-02</td><td>45m</td><td class="status-resolved">Resolved</td></tr>
            <tr><td>2024-01-05</td><td>firewall-main</td><td>10m</td><td class="status-resolved">Resolved</td></tr>
        </table>
        {result}
    </div>
</body>
</html>
"""

# Syslog page - safe (escaped)
SYSLOG_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMonitor - System Logs</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
        .header {{ background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: #0f9b8e; }}
        .nav {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
        .nav a {{ background: #0f3460; color: #e94560; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        .card {{ background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 15px; }}
        .card h3 {{ color: #0f9b8e; margin-top: 0; }}
        input {{ padding: 8px; margin: 5px 0; border: 1px solid #333; background: #0f3460; color: #eee; border-radius: 4px; }}
        button {{ padding: 8px 16px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        .log-entry {{ font-family: monospace; padding: 5px; border-bottom: 1px solid #333; }}
        .log-info {{ color: #4caf50; }}
        .log-warn {{ color: #ff9800; }}
        .log-error {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NetMonitor - System Logs</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/outages">Outages</a>
    </div>
    <div class="card">
        <h3>Log Filter</h3>
        <form action="/syslog" method="get">
            <input type="text" name="from" placeholder="From date..." value="{from_date}">
            <input type="text" name="to" placeholder="To date..." value="{to_date}">
            <input type="text" name="severity" placeholder="Severity..." value="{severity}">
            <button type="submit">Filter</button>
        </form>
    </div>
    <div class="card">
        <h3>Log Entries</h3>
        <div class="log-entry"><span class="log-info">[INFO]</span> 2024-01-15 10:23:45 router-core-01 - Interface state change</div>
        <div class="log-entry"><span class="log-warn">[WARN]</span> 2024-01-15 10:20:12 switch-floor2 - High CPU utilization</div>
        <div class="log-entry"><span class="log-error">[ERROR]</span> 2024-01-15 10:15:32 switch-floor2 - Link down on Gi0/1</div>
        <div class="log-entry"><span class="log-info">[INFO]</span> 2024-01-15 10:12:18 ntp-server - Sync completed</div>
        {message}
    </div>
</body>
</html>
"""

# Health page - safe
HEALTH_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMonitor - Health Status</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
        .header {{ background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: #0f9b8e; }}
        .nav {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
        .nav a {{ background: #0f3460; color: #e94560; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        .card {{ background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 15px; }}
        .card h3 {{ color: #0f9b8e; margin-top: 0; }}
        .metric {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #333; }}
        .status-ok {{ color: #4caf50; }}
        input {{ padding: 8px; margin: 5px 0; border: 1px solid #333; background: #0f3460; color: #eee; border-radius: 4px; }}
        button {{ padding: 8px 16px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NetMonitor - Health Status</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
    </div>
    <div class="card">
        <h3>Health View Settings</h3>
        <form action="/health" method="get">
            <input type="text" name="view" placeholder="View type..." value="{view}">
            <input type="text" name="graph_type" placeholder="Graph type..." value="{graph_type}">
            <button type="submit">Update</button>
        </form>
    </div>
    <div class="card">
        <h3>System Health Metrics</h3>
        <div class="metric"><span>CPU Utilization</span><span class="status-ok">23%</span></div>
        <div class="metric"><span>Memory Usage</span><span class="status-ok">45%</span></div>
        <div class="metric"><span>Disk Space</span><span class="status-ok">62%</span></div>
        <div class="metric"><span>Network I/O</span><span class="status-ok">Normal</span></div>
        {message}
    </div>
</body>
</html>
"""

# NTP page - safe
NTP_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMonitor - NTP Sync</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
        .header {{ background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: #0f9b8e; }}
        .nav {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
        .nav a {{ background: #0f3460; color: #e94560; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        .card {{ background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 15px; }}
        .card h3 {{ color: #0f9b8e; margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ color: #0f9b8e; }}
        .status-ok {{ color: #4caf50; }}
        input {{ padding: 8px; margin: 5px 0; border: 1px solid #333; background: #0f3460; color: #eee; border-radius: 4px; }}
        button {{ padding: 8px 16px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NetMonitor - NTP Synchronization</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/health">Health</a>
    </div>
    <div class="card">
        <h3>NTP Settings</h3>
        <form action="/ntp" method="get">
            <input type="text" name="view" placeholder="View..." value="{view}">
            <input type="text" name="graph" placeholder="Graph..." value="{graph}">
            <button type="submit">Update</button>
        </form>
    </div>
    <div class="card">
        <h3>NTP Servers</h3>
        <table>
            <tr><th>Server</th><th>Stratum</th><th>Offset</th><th>Status</th></tr>
            <tr><td>0.pool.ntp.org</td><td>2</td><td>+0.003s</td><td class="status-ok">Synced</td></tr>
            <tr><td>1.pool.ntp.org</td><td>2</td><td>-0.001s</td><td class="status-ok">Synced</td></tr>
        </table>
        {message}
    </div>
</body>
</html>
"""

# Search page - safe 
SEARCH_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMonitor - Search</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
        .header {{ background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: #0f9b8e; }}
        .nav {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
        .nav a {{ background: #0f3460; color: #e94560; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        .card {{ background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 15px; }}
        .card h3 {{ color: #0f9b8e; margin-top: 0; }}
        input {{ padding: 8px; margin: 5px 0; border: 1px solid #333; background: #0f3460; color: #eee; border-radius: 4px; }}
        button {{ padding: 8px 16px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NetMonitor - FDB Search</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
    </div>
    <div class="card">
        <h3>FDB Search</h3>
        <form action="/search" method="get">
            <input type="text" name="device_id" placeholder="Device ID..." value="{device_id}">
            <input type="text" name="searchby" placeholder="Search by..." value="{searchby}">
            <input type="text" name="searchPhrase" placeholder="Search phrase..." value="{searchPhrase}">
            <button type="submit">Search</button>
        </form>
    </div>
    <div class="card">
        <h3>Search Results</h3>
        <p>No results found. Use the form above to search.</p>
        {message}
    </div>
</body>
</html>
"""

# Realtime page - VULNERABLE (similar to outages)
REALTIME_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMonitor - Realtime Statistics</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .header { background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .header h1 { margin: 0; color: #0f9b8e; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .nav a { background: #0f3460; color: #e94560; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .nav a:hover { background: #e94560; color: white; }
        .card { background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 15px; }
        .card h3 { color: #0f9b8e; margin-top: 0; }
        input { padding: 8px; margin: 5px 0; border: 1px solid #333; background: #0f3460; color: #eee; border-radius: 4px; }
        button { padding: 8px 16px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .graph { background: #0f3460; height: 150px; display: flex; align-items: center; justify-content: center; border-radius: 4px; color: #666; margin-top: 10px; }
        .result { margin-top: 15px; padding: 15px; background: #0f3460; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NetMonitor - Realtime Port Statistics</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/devices">Devices</a>
        <a href="/ports">Ports</a>
    </div>
    <div class="card">
        <h3>Realtime Configuration</h3>
        <form action="/realtime" method="get">
            <label>Refresh Interval (ms): <input type="text" name="interval" placeholder="1000" value="{interval}"></label>
            <button type="submit">Apply</button>
        </form>
    </div>
    <div class="card">
        <h3>Live Statistics</h3>
        <p>Monitoring port traffic in realtime...</p>
        <div class="graph">[Realtime Graph - Interval: {interval}ms]</div>
        {result}
    </div>
</body>
</html>
"""

# About page
ABOUT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMonitor - About</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .header { background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .header h1 { margin: 0; color: #0f9b8e; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .nav a { background: #0f3460; color: #e94560; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .card { background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 15px; }
        .card h3 { color: #0f9b8e; margin-top: 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NetMonitor - About</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
    </div>
    <div class="card">
        <h3>About NetMonitor</h3>
        <p><strong>Version:</strong> 2.3.7</p>
        <p><strong>Build:</strong> 20240115-stable</p>
        <p>NetMonitor is a network monitoring solution designed for enterprise environments.</p>
        <p>Features include device monitoring, port statistics, outage tracking, and real-time alerting.</p>
    </div>
    <div class="card">
        <h3>System Information</h3>
        <p><strong>Backend:</strong> Python/Flask</p>
        <p><strong>Database:</strong> SQLite</p>
        <p><strong>License:</strong> Internal Use Only</p>
    </div>
</body>
</html>
"""

# Image routes - kept for compatibility
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
    "netmonitor": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    }
}
