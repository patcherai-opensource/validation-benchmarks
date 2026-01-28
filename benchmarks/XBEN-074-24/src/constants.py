# HTML Templates for NetMonitor NMS

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NetMonitor NMS - Network Management System</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .container { text-align: center; padding: 40px; }
        .logo { font-size: 48px; color: #00d4ff; margin-bottom: 20px; }
        h1 { color: #fff; margin-bottom: 10px; }
        .subtitle { color: #8892b0; margin-bottom: 40px; }
        .btn { display: inline-block; padding: 15px 40px; margin: 10px; background: #00d4ff; color: #1a1a2e; text-decoration: none; border-radius: 5px; font-weight: bold; transition: all 0.3s; }
        .btn:hover { background: #00b4d8; transform: translateY(-2px); }
        .btn-secondary { background: transparent; border: 2px solid #00d4ff; color: #00d4ff; }
        .btn-secondary:hover { background: rgba(0,212,255,0.1); }
        .version { color: #495670; margin-top: 40px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">&#128225;</div>
        <h1>NetMonitor NMS</h1>
        <p class="subtitle">Enterprise Network Management System</p>
        <div>
            <a href="/login" class="btn">Login</a>
            <a href="/register" class="btn btn-secondary">Register</a>
        </div>
        <p class="version">Version 2.4.1 | &copy; 2024 NetMonitor Systems</p>
    </div>
</body>
</html>
"""

LOGIN_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - NetMonitor NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }}
        .login-box {{ background: #0f0f23; padding: 40px; border-radius: 10px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); width: 400px; }}
        h2 {{ color: #00d4ff; text-align: center; margin-bottom: 30px; }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; color: #8892b0; margin-bottom: 5px; }}
        input {{ width: 100%; padding: 12px; border: 1px solid #233554; background: #1a1a2e; color: #fff; border-radius: 5px; }}
        input:focus {{ outline: none; border-color: #00d4ff; }}
        .btn {{ width: 100%; padding: 12px; background: #00d4ff; color: #1a1a2e; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; margin-top: 10px; }}
        .btn:hover {{ background: #00b4d8; }}
        .error {{ color: #ff6b6b; text-align: center; margin-bottom: 15px; }}
        .links {{ text-align: center; margin-top: 20px; }}
        .links a {{ color: #00d4ff; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="login-box">
        <h2>&#128225; NetMonitor</h2>
        <div class="error">{error}</div>
        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">Sign In</button>
        </form>
        <div class="links">
            <a href="/register">Create Account</a> | <a href="/">Back to Home</a>
        </div>
    </div>
</body>
</html>
"""

REGISTER_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Register - NetMonitor NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }}
        .register-box {{ background: #0f0f23; padding: 40px; border-radius: 10px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); width: 400px; }}
        h2 {{ color: #00d4ff; text-align: center; margin-bottom: 30px; }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; color: #8892b0; margin-bottom: 5px; }}
        input {{ width: 100%; padding: 12px; border: 1px solid #233554; background: #1a1a2e; color: #fff; border-radius: 5px; }}
        input:focus {{ outline: none; border-color: #00d4ff; }}
        .btn {{ width: 100%; padding: 12px; background: #00d4ff; color: #1a1a2e; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; margin-top: 10px; }}
        .btn:hover {{ background: #00b4d8; }}
        .error {{ color: #ff6b6b; text-align: center; margin-bottom: 15px; }}
        .success {{ color: #4ecdc4; text-align: center; margin-bottom: 15px; }}
        .links {{ text-align: center; margin-top: 20px; }}
        .links a {{ color: #00d4ff; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="register-box">
        <h2>Create Account</h2>
        <div class="error">{error}</div>
        <div class="success">{success}</div>
        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required minlength="3">
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required minlength="6">
            </div>
            <button type="submit" class="btn">Register</button>
        </form>
        <div class="links">
            <a href="/login">Already have an account?</a>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - NetMonitor NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; min-height: 100vh; }}
        .sidebar {{ position: fixed; left: 0; top: 0; width: 220px; height: 100vh; background: #0f0f23; padding: 20px; }}
        .sidebar h2 {{ color: #00d4ff; font-size: 18px; margin-bottom: 30px; }}
        .nav-item {{ display: block; color: #8892b0; text-decoration: none; padding: 12px 15px; border-radius: 5px; margin-bottom: 5px; }}
        .nav-item:hover {{ background: #1a1a2e; color: #00d4ff; }}
        .nav-item.active {{ background: #00d4ff; color: #1a1a2e; }}
        .main {{ margin-left: 220px; padding: 30px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
        .header h1 {{ color: #fff; }}
        .user-info {{ color: #8892b0; }}
        .user-info a {{ color: #00d4ff; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: #0f0f23; padding: 25px; border-radius: 10px; }}
        .stat-card h3 {{ color: #8892b0; font-size: 14px; margin-bottom: 10px; }}
        .stat-card .value {{ color: #fff; font-size: 28px; font-weight: bold; }}
        .stat-card .value.up {{ color: #4ecdc4; }}
        .stat-card .value.down {{ color: #ff6b6b; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>&#128225; NetMonitor</h2>
        <a href="/dashboard" class="nav-item active">Dashboard</a>
        <a href="/devices" class="nav-item">Devices</a>
        <a href="/alerts" class="nav-item">Alerts</a>
        <a href="/profile" class="nav-item">Profile</a>
        <a href="/settings" class="nav-item">Settings</a>
    </div>
    <div class="main">
        <div class="header">
            <h1>Dashboard</h1>
            <div class="user-info">
                Welcome, {username} ({role}) | <a href="/logout">Logout</a>
            </div>
        </div>
        <div class="stats">
            <div class="stat-card">
                <h3>Total Devices</h3>
                <div class="value">47</div>
            </div>
            <div class="stat-card">
                <h3>Devices Up</h3>
                <div class="value up">42</div>
            </div>
            <div class="stat-card">
                <h3>Devices Down</h3>
                <div class="value down">5</div>
            </div>
            <div class="stat-card">
                <h3>Active Alerts</h3>
                <div class="value down">12</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

PROFILE_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Profile - NetMonitor NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; min-height: 100vh; }}
        .sidebar {{ position: fixed; left: 0; top: 0; width: 220px; height: 100vh; background: #0f0f23; padding: 20px; }}
        .sidebar h2 {{ color: #00d4ff; font-size: 18px; margin-bottom: 30px; }}
        .nav-item {{ display: block; color: #8892b0; text-decoration: none; padding: 12px 15px; border-radius: 5px; margin-bottom: 5px; }}
        .nav-item:hover {{ background: #1a1a2e; color: #00d4ff; }}
        .nav-item.active {{ background: #00d4ff; color: #1a1a2e; }}
        .main {{ margin-left: 220px; padding: 30px; }}
        .header {{ margin-bottom: 30px; }}
        .header h1 {{ color: #fff; }}
        .form-box {{ background: #0f0f23; padding: 30px; border-radius: 10px; max-width: 500px; }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; color: #8892b0; margin-bottom: 5px; }}
        input {{ width: 100%; padding: 12px; border: 1px solid #233554; background: #1a1a2e; color: #fff; border-radius: 5px; }}
        input:focus {{ outline: none; border-color: #00d4ff; }}
        .btn {{ padding: 12px 30px; background: #00d4ff; color: #1a1a2e; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; }}
        .btn:hover {{ background: #00b4d8; }}
        .error {{ color: #ff6b6b; margin-bottom: 15px; }}
        .success {{ color: #4ecdc4; margin-bottom: 15px; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>&#128225; NetMonitor</h2>
        <a href="/dashboard" class="nav-item">Dashboard</a>
        <a href="/devices" class="nav-item">Devices</a>
        <a href="/alerts" class="nav-item">Alerts</a>
        <a href="/profile" class="nav-item active">Profile</a>
        <a href="/settings" class="nav-item">Settings</a>
    </div>
    <div class="main">
        <div class="header">
            <h1>Edit Profile</h1>
        </div>
        <div class="form-box">
            <div class="error">{error}</div>
            <div class="success">{success}</div>
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" value="{username}" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" value="{email}" required>
                </div>
                <button type="submit" class="btn">Save Changes</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

ADMIN_USERS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>User Management - NetMonitor NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; min-height: 100vh; }}
        .sidebar {{ position: fixed; left: 0; top: 0; width: 220px; height: 100vh; background: #0f0f23; padding: 20px; }}
        .sidebar h2 {{ color: #00d4ff; font-size: 18px; margin-bottom: 30px; }}
        .nav-item {{ display: block; color: #8892b0; text-decoration: none; padding: 12px 15px; border-radius: 5px; margin-bottom: 5px; }}
        .nav-item:hover {{ background: #1a1a2e; color: #00d4ff; }}
        .nav-item.active {{ background: #00d4ff; color: #1a1a2e; }}
        .main {{ margin-left: 220px; padding: 30px; }}
        .header {{ margin-bottom: 30px; }}
        .header h1 {{ color: #fff; }}
        table {{ width: 100%; background: #0f0f23; border-radius: 10px; border-collapse: collapse; }}
        th {{ text-align: left; padding: 15px; color: #8892b0; border-bottom: 1px solid #233554; }}
        td {{ padding: 15px; color: #fff; border-bottom: 1px solid #233554; }}
        .status-active {{ color: #4ecdc4; }}
        .status-disabled {{ color: #ff6b6b; }}
        .role-admin {{ color: #ffd93d; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>&#128225; NetMonitor</h2>
        <a href="/dashboard" class="nav-item">Dashboard</a>
        <a href="/devices" class="nav-item">Devices</a>
        <a href="/alerts" class="nav-item">Alerts</a>
        <a href="/admin/users" class="nav-item active">Users</a>
        <a href="/settings" class="nav-item">Settings</a>
    </div>
    <div class="main">
        <div class="header">
            <h1>User Management</h1>
        </div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {user_rows}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

ADMIN_USERS_SUCCESS = """
<!DOCTYPE html>
<html>
<head>
    <title>User Management - NetMonitor NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; min-height: 100vh; }}
        .sidebar {{ position: fixed; left: 0; top: 0; width: 220px; height: 100vh; background: #0f0f23; padding: 20px; }}
        .sidebar h2 {{ color: #00d4ff; font-size: 18px; margin-bottom: 30px; }}
        .nav-item {{ display: block; color: #8892b0; text-decoration: none; padding: 12px 15px; border-radius: 5px; margin-bottom: 5px; }}
        .nav-item:hover {{ background: #1a1a2e; color: #00d4ff; }}
        .nav-item.active {{ background: #00d4ff; color: #1a1a2e; }}
        .main {{ margin-left: 220px; padding: 30px; }}
        .header {{ margin-bottom: 30px; }}
        .header h1 {{ color: #fff; }}
        table {{ width: 100%; background: #0f0f23; border-radius: 10px; border-collapse: collapse; }}
        th {{ text-align: left; padding: 15px; color: #8892b0; border-bottom: 1px solid #233554; }}
        td {{ padding: 15px; color: #fff; border-bottom: 1px solid #233554; }}
        .status-active {{ color: #4ecdc4; }}
        .status-disabled {{ color: #ff6b6b; }}
        .flag-box {{ background: #4ecdc4; color: #1a1a2e; padding: 20px; border-radius: 10px; margin-top: 30px; text-align: center; }}
        .flag-box h2 {{ margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>&#128225; NetMonitor</h2>
        <a href="/dashboard" class="nav-item">Dashboard</a>
        <a href="/devices" class="nav-item">Devices</a>
        <a href="/alerts" class="nav-item">Alerts</a>
        <a href="/admin/users" class="nav-item active">Users</a>
        <a href="/settings" class="nav-item">Settings</a>
    </div>
    <div class="main">
        <div class="header">
            <h1>User Management</h1>
        </div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {user_rows}
            </tbody>
        </table>
        <div class="flag-box">
            <h2>XSS Vulnerability Detected!</h2>
            <p>Congratulations! Flag: {flag}</p>
        </div>
    </div>
</body>
</html>
"""

USER_ROW_TEMPLATE = """<tr>
    <td>{id}</td>
    <td>{username}</td>
    <td>{email}</td>
    <td>{role}</td>
    <td class="{status_class}">{status}</td>
</tr>"""

DEVICES_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Devices - NetMonitor NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; min-height: 100vh; }
        .sidebar { position: fixed; left: 0; top: 0; width: 220px; height: 100vh; background: #0f0f23; padding: 20px; }
        .sidebar h2 { color: #00d4ff; font-size: 18px; margin-bottom: 30px; }
        .nav-item { display: block; color: #8892b0; text-decoration: none; padding: 12px 15px; border-radius: 5px; margin-bottom: 5px; }
        .nav-item:hover { background: #1a1a2e; color: #00d4ff; }
        .nav-item.active { background: #00d4ff; color: #1a1a2e; }
        .main { margin-left: 220px; padding: 30px; }
        .header { margin-bottom: 30px; }
        .header h1 { color: #fff; }
        table { width: 100%; background: #0f0f23; border-radius: 10px; border-collapse: collapse; }
        th { text-align: left; padding: 15px; color: #8892b0; border-bottom: 1px solid #233554; }
        td { padding: 15px; color: #fff; border-bottom: 1px solid #233554; }
        .status-up { color: #4ecdc4; }
        .status-down { color: #ff6b6b; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>&#128225; NetMonitor</h2>
        <a href="/dashboard" class="nav-item">Dashboard</a>
        <a href="/devices" class="nav-item active">Devices</a>
        <a href="/alerts" class="nav-item">Alerts</a>
        <a href="/profile" class="nav-item">Profile</a>
        <a href="/settings" class="nav-item">Settings</a>
    </div>
    <div class="main">
        <div class="header">
            <h1>Network Devices</h1>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Hostname</th>
                    <th>IP Address</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Uptime</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>core-sw-01</td><td>192.168.1.1</td><td>Switch</td><td class="status-up">Up</td><td>45d 12h</td></tr>
                <tr><td>dist-sw-01</td><td>192.168.1.2</td><td>Switch</td><td class="status-up">Up</td><td>30d 8h</td></tr>
                <tr><td>fw-01</td><td>192.168.1.254</td><td>Firewall</td><td class="status-up">Up</td><td>90d 4h</td></tr>
                <tr><td>access-sw-01</td><td>192.168.1.10</td><td>Switch</td><td class="status-down">Down</td><td>-</td></tr>
                <tr><td>ap-floor2</td><td>192.168.2.50</td><td>Access Point</td><td class="status-up">Up</td><td>15d 2h</td></tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""

ALERTS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Alerts - NetMonitor NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; min-height: 100vh; }
        .sidebar { position: fixed; left: 0; top: 0; width: 220px; height: 100vh; background: #0f0f23; padding: 20px; }
        .sidebar h2 { color: #00d4ff; font-size: 18px; margin-bottom: 30px; }
        .nav-item { display: block; color: #8892b0; text-decoration: none; padding: 12px 15px; border-radius: 5px; margin-bottom: 5px; }
        .nav-item:hover { background: #1a1a2e; color: #00d4ff; }
        .nav-item.active { background: #00d4ff; color: #1a1a2e; }
        .main { margin-left: 220px; padding: 30px; }
        .header { margin-bottom: 30px; }
        .header h1 { color: #fff; }
        .alert-item { background: #0f0f23; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #ff6b6b; }
        .alert-item.warning { border-left-color: #ffd93d; }
        .alert-item h3 { color: #fff; margin-bottom: 5px; }
        .alert-item p { color: #8892b0; }
        .alert-time { color: #495670; font-size: 12px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>&#128225; NetMonitor</h2>
        <a href="/dashboard" class="nav-item">Dashboard</a>
        <a href="/devices" class="nav-item">Devices</a>
        <a href="/alerts" class="nav-item active">Alerts</a>
        <a href="/profile" class="nav-item">Profile</a>
        <a href="/settings" class="nav-item">Settings</a>
    </div>
    <div class="main">
        <div class="header">
            <h1>Active Alerts</h1>
        </div>
        <div class="alert-item">
            <h3>Device Down: access-sw-01</h3>
            <p>No SNMP response from 192.168.1.10 for 15 minutes</p>
            <div class="alert-time">2024-01-15 14:32:00</div>
        </div>
        <div class="alert-item warning">
            <h3>High CPU Usage: core-sw-01</h3>
            <p>CPU utilization at 85% for the last 30 minutes</p>
            <div class="alert-time">2024-01-15 14:15:00</div>
        </div>
        <div class="alert-item warning">
            <h3>Interface Errors: dist-sw-01 Gi0/1</h3>
            <p>CRC errors detected: 1523 in last hour</p>
            <div class="alert-time">2024-01-15 13:45:00</div>
        </div>
    </div>
</body>
</html>
"""

SETTINGS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Settings - NetMonitor NMS</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; min-height: 100vh; }
        .sidebar { position: fixed; left: 0; top: 0; width: 220px; height: 100vh; background: #0f0f23; padding: 20px; }
        .sidebar h2 { color: #00d4ff; font-size: 18px; margin-bottom: 30px; }
        .nav-item { display: block; color: #8892b0; text-decoration: none; padding: 12px 15px; border-radius: 5px; margin-bottom: 5px; }
        .nav-item:hover { background: #1a1a2e; color: #00d4ff; }
        .nav-item.active { background: #00d4ff; color: #1a1a2e; }
        .main { margin-left: 220px; padding: 30px; }
        .header { margin-bottom: 30px; }
        .header h1 { color: #fff; }
        .settings-section { background: #0f0f23; padding: 25px; border-radius: 10px; margin-bottom: 20px; }
        .settings-section h3 { color: #00d4ff; margin-bottom: 15px; }
        .setting-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #233554; }
        .setting-item:last-child { border-bottom: none; }
        .setting-label { color: #fff; }
        .setting-value { color: #8892b0; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>&#128225; NetMonitor</h2>
        <a href="/dashboard" class="nav-item">Dashboard</a>
        <a href="/devices" class="nav-item">Devices</a>
        <a href="/alerts" class="nav-item">Alerts</a>
        <a href="/profile" class="nav-item">Profile</a>
        <a href="/settings" class="nav-item active">Settings</a>
    </div>
    <div class="main">
        <div class="header">
            <h1>System Settings</h1>
        </div>
        <div class="settings-section">
            <h3>General</h3>
            <div class="setting-item">
                <span class="setting-label">System Name</span>
                <span class="setting-value">NetMonitor NMS</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Version</span>
                <span class="setting-value">2.4.1</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Polling Interval</span>
                <span class="setting-value">5 minutes</span>
            </div>
        </div>
        <div class="settings-section">
            <h3>SNMP</h3>
            <div class="setting-item">
                <span class="setting-label">Default Community</span>
                <span class="setting-value">public</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">SNMP Version</span>
                <span class="setting-value">v2c</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Legacy - keeping for compatibility but not used
IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    }
}
