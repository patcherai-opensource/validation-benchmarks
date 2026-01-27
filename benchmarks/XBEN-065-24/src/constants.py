INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NetMon - Network Monitoring System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: #1a1a2e;
            color: #eee;
        }
        .navbar {
            background: #16213e;
            padding: 10px 20px;
            border-bottom: 2px solid #0f3460;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .navbar h1 {
            margin: 0;
            color: #00d4ff;
            font-size: 24px;
        }
        .nav-links a {
            color: #aaa;
            text-decoration: none;
            margin-left: 20px;
            transition: color 0.3s;
        }
        .nav-links a:hover {
            color: #00d4ff;
        }
        .container {
            padding: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .card {
            background: #16213e;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #0f3460;
        }
        .card h2 {
            color: #00d4ff;
            margin-top: 0;
            font-size: 18px;
            border-bottom: 1px solid #0f3460;
            padding-bottom: 10px;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #0f3460;
        }
        .status-ok { color: #00ff88; }
        .status-warn { color: #ffaa00; }
        .menu-link {
            display: block;
            padding: 12px 15px;
            color: #aaa;
            text-decoration: none;
            border-radius: 4px;
            margin: 5px 0;
            transition: all 0.3s;
        }
        .menu-link:hover {
            background: #0f3460;
            color: #00d4ff;
        }
        .version {
            color: #666;
            font-size: 12px;
            text-align: center;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>NetMon</h1>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/outages">Outages</a>
            <a href="/syslog">Syslog</a>
            <a href="/ports">Ports</a>
        </div>
    </div>
    <div class="container">
        <h2>System Overview</h2>
        <div class="dashboard">
            <div class="card">
                <h2>Quick Navigation</h2>
                <a class="menu-link" href="/outages">&#128268; Outage Reports</a>
                <a class="menu-link" href="/syslog">&#128221; System Logs</a>
                <a class="menu-link" href="/ports">&#128279; Port Status</a>
            </div>
            <div class="card">
                <h2>System Status</h2>
                <div class="status-item">
                    <span>Active Devices</span>
                    <span class="status-ok">24 Online</span>
                </div>
                <div class="status-item">
                    <span>Alerts</span>
                    <span class="status-warn">3 Pending</span>
                </div>
                <div class="status-item">
                    <span>Uptime</span>
                    <span class="status-ok">99.7%</span>
                </div>
            </div>
            <div class="card">
                <h2>Recent Activity</h2>
                <div class="status-item">
                    <span>Router-01 backup complete</span>
                </div>
                <div class="status-item">
                    <span>Switch-04 port scan finished</span>
                </div>
                <div class="status-item">
                    <span>Firewall rules updated</span>
                </div>
            </div>
        </div>
        <p class="version">NetMon v23.7.0 - Network Monitoring Dashboard</p>
    </div>
</body>
</html>
"""

# Outages page - vulnerable to XSS via 'from' and 'to' parameters in input value attributes
OUTAGES_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NetMon - Outage Reports</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: #1a1a2e;
            color: #eee;
        }}
        .navbar {{
            background: #16213e;
            padding: 10px 20px;
            border-bottom: 2px solid #0f3460;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .navbar h1 {{
            margin: 0;
            color: #00d4ff;
            font-size: 24px;
        }}
        .nav-links a {{
            color: #aaa;
            text-decoration: none;
            margin-left: 20px;
            transition: color 0.3s;
        }}
        .nav-links a:hover {{
            color: #00d4ff;
        }}
        .container {{
            padding: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .filter-form {{
            background: #16213e;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #0f3460;
            margin-bottom: 20px;
        }}
        .filter-form h2 {{
            color: #00d4ff;
            margin-top: 0;
            font-size: 18px;
            border-bottom: 1px solid #0f3460;
            padding-bottom: 10px;
        }}
        .form-row {{
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}
        .form-group {{
            flex: 1;
            min-width: 200px;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 5px;
            color: #aaa;
        }}
        .form-group input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #0f3460;
            background: #1a1a2e;
            color: #eee;
            border-radius: 4px;
            box-sizing: border-box;
        }}
        .btn {{
            background: #00d4ff;
            color: #1a1a2e;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }}
        .btn:hover {{
            background: #00a8cc;
        }}
        .results {{
            background: #16213e;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #0f3460;
        }}
        .results h2 {{
            color: #00d4ff;
            margin-top: 0;
            font-size: 18px;
            border-bottom: 1px solid #0f3460;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #0f3460;
        }}
        th {{
            color: #00d4ff;
            background: #0f3460;
        }}
        .status-down {{ color: #ff4444; }}
        .status-up {{ color: #00ff88; }}
        .version {{
            color: #666;
            font-size: 12px;
            text-align: center;
            margin-top: 40px;
        }}
        .result-message {{
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
        }}
        .success {{ background: #00ff8822; border: 1px solid #00ff88; }}
        .error {{ background: #ff444422; border: 1px solid #ff4444; }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>NetMon</h1>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/outages">Outages</a>
            <a href="/syslog">Syslog</a>
            <a href="/ports">Ports</a>
        </div>
    </div>
    <div class="container">
        <div class="filter-form">
            <h2>Filter Outage Reports</h2>
            <form method="GET" action="/outages">
                <div class="form-row">
                    <div class="form-group">
                        <label for="from">From Date:</label>
                        <input type="text" id="from" name="from" placeholder="YYYY-MM-DD" value="{0}">
                    </div>
                    <div class="form-group">
                        <label for="to">To Date:</label>
                        <input type="text" id="to" name="to" placeholder="YYYY-MM-DD" value="{1}">
                    </div>
                </div>
                <button type="submit" class="btn">Filter Results</button>
            </form>
        </div>
        <div class="results">
            <h2>Outage History</h2>
            {2}
            <table>
                <tr>
                    <th>Device</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                    <th>Duration</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>Router-GW01</td>
                    <td>2024-01-15 08:23:00</td>
                    <td>2024-01-15 08:45:00</td>
                    <td>22 min</td>
                    <td class="status-up">Resolved</td>
                </tr>
                <tr>
                    <td>Switch-Core02</td>
                    <td>2024-01-14 14:00:00</td>
                    <td>2024-01-14 14:12:00</td>
                    <td>12 min</td>
                    <td class="status-up">Resolved</td>
                </tr>
                <tr>
                    <td>Server-DB03</td>
                    <td>2024-01-13 03:15:00</td>
                    <td>2024-01-13 03:18:00</td>
                    <td>3 min</td>
                    <td class="status-up">Resolved</td>
                </tr>
            </table>
        </div>
        <p class="version">NetMon v23.7.0 - Network Monitoring Dashboard</p>
    </div>
</body>
</html>
"""

SYSLOG_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NetMon - System Logs</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: #1a1a2e;
            color: #eee;
        }}
        .navbar {{
            background: #16213e;
            padding: 10px 20px;
            border-bottom: 2px solid #0f3460;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .navbar h1 {{
            margin: 0;
            color: #00d4ff;
            font-size: 24px;
        }}
        .nav-links a {{
            color: #aaa;
            text-decoration: none;
            margin-left: 20px;
            transition: color 0.3s;
        }}
        .container {{
            padding: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .card {{
            background: #16213e;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #0f3460;
        }}
        .card h2 {{
            color: #00d4ff;
            margin-top: 0;
        }}
        .log-entry {{
            font-family: monospace;
            padding: 5px;
            border-bottom: 1px solid #0f3460;
        }}
        .version {{
            color: #666;
            font-size: 12px;
            text-align: center;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>NetMon</h1>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/outages">Outages</a>
            <a href="/syslog">Syslog</a>
            <a href="/ports">Ports</a>
        </div>
    </div>
    <div class="container">
        <div class="card">
            <h2>System Logs</h2>
            <div class="log-entry">2024-01-15 10:23:45 [INFO] System health check passed</div>
            <div class="log-entry">2024-01-15 10:22:30 [INFO] User admin logged in</div>
            <div class="log-entry">2024-01-15 10:20:15 [WARN] High CPU usage on Server-APP01</div>
            <div class="log-entry">2024-01-15 10:15:00 [INFO] Backup completed successfully</div>
        </div>
        <p class="version">NetMon v23.7.0 - Network Monitoring Dashboard</p>
    </div>
</body>
</html>
"""

PORTS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NetMon - Port Status</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: #1a1a2e;
            color: #eee;
        }}
        .navbar {{
            background: #16213e;
            padding: 10px 20px;
            border-bottom: 2px solid #0f3460;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .navbar h1 {{
            margin: 0;
            color: #00d4ff;
            font-size: 24px;
        }}
        .nav-links a {{
            color: #aaa;
            text-decoration: none;
            margin-left: 20px;
            transition: color 0.3s;
        }}
        .container {{
            padding: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .card {{
            background: #16213e;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #0f3460;
        }}
        .card h2 {{
            color: #00d4ff;
            margin-top: 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #0f3460;
        }}
        th {{
            color: #00d4ff;
            background: #0f3460;
        }}
        .status-up {{ color: #00ff88; }}
        .status-down {{ color: #ff4444; }}
        .version {{
            color: #666;
            font-size: 12px;
            text-align: center;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>NetMon</h1>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/outages">Outages</a>
            <a href="/syslog">Syslog</a>
            <a href="/ports">Ports</a>
        </div>
    </div>
    <div class="container">
        <div class="card">
            <h2>Port Status Overview</h2>
            <table>
                <tr>
                    <th>Device</th>
                    <th>Port</th>
                    <th>Speed</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>Switch-01</td>
                    <td>Gi0/1</td>
                    <td>1 Gbps</td>
                    <td class="status-up">Up</td>
                </tr>
                <tr>
                    <td>Switch-01</td>
                    <td>Gi0/2</td>
                    <td>1 Gbps</td>
                    <td class="status-up">Up</td>
                </tr>
                <tr>
                    <td>Router-01</td>
                    <td>Eth0</td>
                    <td>10 Gbps</td>
                    <td class="status-up">Up</td>
                </tr>
            </table>
        </div>
        <p class="version">NetMon v23.7.0 - Network Monitoring Dashboard</p>
    </div>
</body>
</html>
"""
