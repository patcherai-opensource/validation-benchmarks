# NetWatch - Network Monitoring Dashboard
# HTML Templates

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetWatch - Network Monitoring Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e8e8e8;
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }
        .header {
            background: #0f3460;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .header h1 {
            margin: 0;
            color: #00d9ff;
        }
        .header span {
            color: #888;
            font-size: 14px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .card {
            background: #1f4068;
            border-radius: 10px;
            padding: 25px;
            text-decoration: none;
            color: inherit;
            transition: transform 0.2s, box-shadow 0.2s;
            border: 1px solid #2a5082;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,217,255,0.2);
            border-color: #00d9ff;
        }
        .card h3 {
            color: #00d9ff;
            margin-top: 0;
        }
        .card p {
            color: #aaa;
            margin-bottom: 0;
        }
        .icon {
            font-size: 40px;
            margin-bottom: 15px;
        }
        .status-bar {
            background: #0a1628;
            padding: 10px 20px;
            font-size: 12px;
            color: #666;
        }
        .status-bar .online {
            color: #00ff88;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>&#128225; NetWatch</h1>
        <span>Network Monitoring Dashboard v2.3.7</span>
    </div>
    <div class="status-bar">
        System Status: <span class="online">&#9679; Online</span> | Last Sync: Just now | Monitored Devices: 42
    </div>
    <div class="container">
        <h2>Quick Access</h2>
        <div class="dashboard-grid">
            <a href="/outages" class="card">
                <div class="icon">&#9888;</div>
                <h3>Network Outages</h3>
                <p>View and filter network outage history by date range</p>
            </a>
            <a href="/syslog" class="card">
                <div class="icon">&#128196;</div>
                <h3>Syslog Viewer</h3>
                <p>Browse system logs filtered by device and date</p>
            </a>
            <a href="/ports" class="card">
                <div class="icon">&#128268;</div>
                <h3>Port Status</h3>
                <p>Monitor port status across all network devices</p>
            </a>
            <a href="/health" class="card">
                <div class="icon">&#128154;</div>
                <h3>Health Check</h3>
                <p>System health and monitoring status</p>
            </a>
        </div>
    </div>
</body>
</html>
"""

OUTAGES_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetWatch - Network Outages</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e8e8e8;
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }}
        .header {{
            background: #0f3460;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        .header h1 {{
            margin: 0;
            color: #00d9ff;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
        }}
        .form-group {{
            margin-bottom: 20px;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 8px;
            color: #00d9ff;
        }}
        .form-group input {{
            width: 100%;
            padding: 12px;
            border: 1px solid #2a5082;
            border-radius: 5px;
            background: #1f4068;
            color: #e8e8e8;
            font-size: 14px;
            box-sizing: border-box;
        }}
        .form-group input:focus {{
            outline: none;
            border-color: #00d9ff;
        }}
        .btn {{
            background: #00d9ff;
            color: #1a1a2e;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }}
        .btn:hover {{
            background: #00b8d4;
        }}
        .alert {{
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .alert-success {{
            background: #004d40;
            border: 1px solid #00ff88;
            color: #00ff88;
        }}
        .alert-warning {{
            background: #4a3f00;
            border: 1px solid #ffd700;
            color: #ffd700;
        }}
        .alert-info {{
            background: #003d5b;
            border: 1px solid #00d9ff;
            color: #00d9ff;
        }}
        .breadcrumb {{
            margin-bottom: 20px;
            color: #666;
        }}
        .breadcrumb a {{
            color: #00d9ff;
            text-decoration: none;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #2a5082;
        }}
        th {{
            background: #0f3460;
            color: #00d9ff;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>&#9888; Network Outages</h1>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Dashboard</a> &raquo; Network Outages
        </div>
        
        <form method="GET" action="/outages">
            <div class="form-group">
                <label for="from">From Date:</label>
                <input type="text" id="from" name="from" value="{0}" placeholder="YYYY-MM-DD HH:MM:SS">
            </div>
            <div class="form-group">
                <label for="to">To Date:</label>
                <input type="text" id="to" name="to" value="{1}" placeholder="YYYY-MM-DD HH:MM:SS">
            </div>
            <button type="submit" class="btn">Search Outages</button>
        </form>
        
        {2}
        
        <table>
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
                    <td colspan="5" style="text-align: center; color: #666;">Enter date range to search outages</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""

SYSLOG_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetWatch - Syslog Viewer</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e8e8e8;
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }}
        .header {{
            background: #0f3460;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        .header h1 {{
            margin: 0;
            color: #00d9ff;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
        }}
        .form-row {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .form-group {{
            flex: 1;
            min-width: 200px;
            margin-bottom: 20px;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 8px;
            color: #00d9ff;
        }}
        .form-group input {{
            width: 100%;
            padding: 12px;
            border: 1px solid #2a5082;
            border-radius: 5px;
            background: #1f4068;
            color: #e8e8e8;
            font-size: 14px;
            box-sizing: border-box;
        }}
        .btn {{
            background: #00d9ff;
            color: #1a1a2e;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }}
        .alert {{
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .alert-success {{
            background: #004d40;
            border: 1px solid #00ff88;
            color: #00ff88;
        }}
        .alert-warning {{
            background: #4a3f00;
            border: 1px solid #ffd700;
            color: #ffd700;
        }}
        .alert-info {{
            background: #003d5b;
            border: 1px solid #00d9ff;
            color: #00d9ff;
        }}
        .breadcrumb {{
            margin-bottom: 20px;
            color: #666;
        }}
        .breadcrumb a {{
            color: #00d9ff;
            text-decoration: none;
        }}
        .log-area {{
            background: #0a1628;
            border: 1px solid #2a5082;
            border-radius: 5px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            min-height: 200px;
            margin-top: 20px;
            white-space: pre-wrap;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>&#128196; Syslog Viewer</h1>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Dashboard</a> &raquo; Syslog Viewer
        </div>
        
        <form method="GET" action="/syslog">
            <div class="form-row">
                <div class="form-group">
                    <label for="from">From:</label>
                    <input type="text" id="from" name="from" value="{0}" placeholder="YYYY-MM-DD">
                </div>
                <div class="form-group">
                    <label for="to">To:</label>
                    <input type="text" id="to" name="to" value="{1}" placeholder="YYYY-MM-DD">
                </div>
                <div class="form-group">
                    <label for="device">Device:</label>
                    <input type="text" id="device" name="device" value="{2}" placeholder="hostname or IP">
                </div>
            </div>
            <button type="submit" class="btn">Filter Logs</button>
        </form>
        
        {3}
        
        <div class="log-area">
[Syslog Viewer]
Enter filter criteria and click "Filter Logs" to search.
        </div>
    </div>
</body>
</html>
"""

PORTS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetWatch - Port Status</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e8e8e8;
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }}
        .header {{
            background: #0f3460;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        .header h1 {{
            margin: 0;
            color: #00d9ff;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
        }}
        .form-row {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .form-group {{
            flex: 1;
            min-width: 200px;
            margin-bottom: 20px;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 8px;
            color: #00d9ff;
        }}
        .form-group input, .form-group select {{
            width: 100%;
            padding: 12px;
            border: 1px solid #2a5082;
            border-radius: 5px;
            background: #1f4068;
            color: #e8e8e8;
            font-size: 14px;
            box-sizing: border-box;
        }}
        .btn {{
            background: #00d9ff;
            color: #1a1a2e;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }}
        .alert {{
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .alert-success {{
            background: #004d40;
            border: 1px solid #00ff88;
            color: #00ff88;
        }}
        .alert-warning {{
            background: #4a3f00;
            border: 1px solid #ffd700;
            color: #ffd700;
        }}
        .alert-info {{
            background: #003d5b;
            border: 1px solid #00d9ff;
            color: #00d9ff;
        }}
        .breadcrumb {{
            margin-bottom: 20px;
            color: #666;
        }}
        .breadcrumb a {{
            color: #00d9ff;
            text-decoration: none;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #2a5082;
        }}
        th {{
            background: #0f3460;
            color: #00d9ff;
        }}
    </style>
    <script>
        // Port monitoring JavaScript
        var config = {{
            device_id: '{0}',
            hostname: '{1}',
            state: '{2}'
        }};
        
        function loadPortData() {{
            console.log('Loading ports for device: ' + config.device_id);
        }}
    </script>
</head>
<body>
    <div class="header">
        <h1>&#128268; Port Status</h1>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Dashboard</a> &raquo; Port Status
        </div>
        
        <form method="GET" action="/ports">
            <div class="form-row">
                <div class="form-group">
                    <label for="device_id">Device ID:</label>
                    <input type="text" id="device_id" name="device_id" value="{0}" placeholder="Enter device ID">
                </div>
                <div class="form-group">
                    <label for="hostname">Hostname:</label>
                    <input type="text" id="hostname" name="hostname" value="{1}" placeholder="Enter hostname">
                </div>
                <div class="form-group">
                    <label for="state">State:</label>
                    <select id="state" name="state">
                        <option value="all">All</option>
                        <option value="up">Up</option>
                        <option value="down">Down</option>
                    </select>
                </div>
            </div>
            <button type="submit" class="btn">Search Ports</button>
        </form>
        
        {3}
        
        <table>
            <thead>
                <tr>
                    <th>Port</th>
                    <th>Interface</th>
                    <th>Speed</th>
                    <th>Status</th>
                    <th>Last Change</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td colspan="5" style="text-align: center; color: #666;">Enter search criteria to list ports</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""

# Legacy constants kept for compatibility (not used in new version)
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
