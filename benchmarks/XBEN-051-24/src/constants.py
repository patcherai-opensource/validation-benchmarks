# LibreNMS-style Network Monitoring Dashboard Templates

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Network Monitoring</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
    <style>
        body { background-color: #1a1a2e; color: #eee; }
        .navbar { background-color: #16213e !important; }
        .card { background-color: #0f3460; border: none; }
        .sidebar { background-color: #16213e; min-height: 100vh; padding-top: 20px; }
        .sidebar a { color: #ccc; padding: 10px 15px; display: block; }
        .sidebar a:hover { background-color: #0f3460; color: #fff; text-decoration: none; }
        .main-content { padding: 20px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <a class="navbar-brand" href="/">LibreNMS</a>
        <span class="navbar-text">Network Monitoring System</span>
    </nav>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar">
                <h5 class="text-muted px-3">Overview</h5>
                <a href="/">Dashboard</a>
                <a href="/outages">Outages</a>
                <a href="/syslog">Syslog</a>
            </div>
            <div class="col-md-10 main-content">
                <div class="card p-4">
                    <h4>Welcome to LibreNMS</h4>
                    <p>Network Monitoring Dashboard</p>
                    <hr style="border-color: #333;">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="card p-3 mb-3">
                                <h5><a href="/outages" style="color: #e94560;">Outages</a></h5>
                                <p class="text-muted">View network outage history</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card p-3 mb-3">
                                <h5><a href="/syslog" style="color: #e94560;">Syslog</a></h5>
                                <p class="text-muted">View system logs</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Vulnerable template - simulates LibreNMS outages.inc.php
# User input in 'from' and 'to' parameters is directly embedded without htmlspecialchars()
OUTAGES_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Outages</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #1a1a2e; color: #eee; }}
        .navbar {{ background-color: #16213e !important; }}
        .card {{ background-color: #0f3460; border: none; }}
        .sidebar {{ background-color: #16213e; min-height: 100vh; padding-top: 20px; }}
        .sidebar a {{ color: #ccc; padding: 10px 15px; display: block; }}
        .sidebar a:hover {{ background-color: #0f3460; color: #fff; text-decoration: none; }}
        .main-content {{ padding: 20px; }}
        .form-control {{ background-color: #16213e; color: #eee; border-color: #333; }}
        .btn-primary {{ background-color: #e94560; border-color: #e94560; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <a class="navbar-brand" href="/">LibreNMS</a>
        <span class="navbar-text">Network Monitoring System</span>
    </nav>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar">
                <h5 class="text-muted px-3">Overview</h5>
                <a href="/">Dashboard</a>
                <a href="/outages">Outages</a>
                <a href="/syslog">Syslog</a>
            </div>
            <div class="col-md-10 main-content">
                <div class="card p-4">
                    <h4>Outages History</h4>
                    <p class="text-muted">View historical network outages by date range</p>
                    <hr style="border-color: #333;">
                    
                    <form method="GET" action="/outages" class="mb-4">
                        <div class="form-row">
                            <div class="col-md-4">
                                <label>From Date</label>
                                <!-- VULNERABLE: User input directly in value attribute without htmlspecialchars() -->
                                <input type="text" class="form-control" name="from" placeholder="YYYY-MM-DD" value="{0}">
                            </div>
                            <div class="col-md-4">
                                <label>To Date</label>
                                <!-- VULNERABLE: User input directly in value attribute without htmlspecialchars() -->
                                <input type="text" class="form-control" name="to" placeholder="YYYY-MM-DD" value="{1}">
                            </div>
                            <div class="col-md-4">
                                <label>&nbsp;</label>
                                <button type="submit" class="btn btn-primary btn-block">Search</button>
                            </div>
                        </div>
                    </form>
                    
                    {2}
                    
                    <table class="table table-dark table-striped">
                        <thead>
                            <tr>
                                <th>Device</th>
                                <th>Start Time</th>
                                <th>End Time</th>
                                <th>Duration</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>router-core-01</td>
                                <td>2024-01-15 03:22:00</td>
                                <td>2024-01-15 03:45:00</td>
                                <td>23 min</td>
                            </tr>
                            <tr>
                                <td>switch-access-12</td>
                                <td>2024-01-14 11:05:00</td>
                                <td>2024-01-14 11:12:00</td>
                                <td>7 min</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Vulnerable template - simulates LibreNMS syslog.inc.php
SYSLOG_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Syslog</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
    <style>
        body {{ background-color: #1a1a2e; color: #eee; }}
        .navbar {{ background-color: #16213e !important; }}
        .card {{ background-color: #0f3460; border: none; }}
        .sidebar {{ background-color: #16213e; min-height: 100vh; padding-top: 20px; }}
        .sidebar a {{ color: #ccc; padding: 10px 15px; display: block; }}
        .sidebar a:hover {{ background-color: #0f3460; color: #fff; text-decoration: none; }}
        .main-content {{ padding: 20px; }}
        .form-control {{ background-color: #16213e; color: #eee; border-color: #333; }}
        .btn-primary {{ background-color: #e94560; border-color: #e94560; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <a class="navbar-brand" href="/">LibreNMS</a>
        <span class="navbar-text">Network Monitoring System</span>
    </nav>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar">
                <h5 class="text-muted px-3">Overview</h5>
                <a href="/">Dashboard</a>
                <a href="/outages">Outages</a>
                <a href="/syslog">Syslog</a>
            </div>
            <div class="col-md-10 main-content">
                <div class="card p-4">
                    <h4>System Logs</h4>
                    <p class="text-muted">View system log entries by date range</p>
                    <hr style="border-color: #333;">
                    
                    <form method="GET" action="/syslog" class="mb-4">
                        <div class="form-row">
                            <div class="col-md-4">
                                <label>From Date</label>
                                <!-- VULNERABLE: User input directly in value attribute without htmlspecialchars() -->
                                <input type="text" class="form-control" name="from" placeholder="YYYY-MM-DD" value="{0}">
                            </div>
                            <div class="col-md-4">
                                <label>To Date</label>
                                <!-- VULNERABLE: User input directly in value attribute without htmlspecialchars() -->
                                <input type="text" class="form-control" name="to" placeholder="YYYY-MM-DD" value="{1}">
                            </div>
                            <div class="col-md-4">
                                <label>&nbsp;</label>
                                <button type="submit" class="btn btn-primary btn-block">Search</button>
                            </div>
                        </div>
                    </form>
                    
                    {2}
                    
                    <table class="table table-dark table-striped">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Device</th>
                                <th>Program</th>
                                <th>Message</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>2024-01-15 14:22:01</td>
                                <td>router-core-01</td>
                                <td>sshd</td>
                                <td>Accepted publickey for admin</td>
                            </tr>
                            <tr>
                                <td>2024-01-15 14:21:55</td>
                                <td>switch-dist-03</td>
                                <td>kernel</td>
                                <td>Interface GigabitEthernet0/1 changed state to up</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

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
