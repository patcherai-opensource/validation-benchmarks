# CVE-2022-4068 inspired templates - LibreNMS-style user management

LIBRENMS_INDEX = """
<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Network Monitoring</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .container { max-width: 800px; margin: 50px auto; padding: 20px; }
        .header { text-align: center; padding: 40px 0; }
        .header h1 { color: #00aaff; margin-bottom: 10px; }
        .header p { color: #888; }
        .nav-box { background: #16213e; border-radius: 8px; padding: 30px; margin: 20px 0; }
        .nav-links { display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; }
        .nav-link { display: inline-block; padding: 15px 25px; background: #0f3460; color: #fff; text-decoration: none; border-radius: 5px; transition: background 0.3s; }
        .nav-link:hover { background: #00aaff; }
        .info-box { background: #0f3460; border-left: 4px solid #00aaff; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>&#x1F4C8; LibreNMS</h1>
            <p>Auto-discovering PHP/MySQL/SNMP based network monitoring</p>
        </div>
        
        <div class="nav-box">
            <div class="nav-links">
                <a class="nav-link" href="/login">&#x1F511; Login</a>
                <a class="nav-link" href="/register">&#x1F4DD; Register</a>
                <a class="nav-link" href="/api/v0/users">&#x1F4CB; API: List Users</a>
            </div>
        </div>
        
        <div class="info-box">
            <strong>Challenge:</strong> This system has a stored XSS vulnerability similar to CVE-2022-4068.
            <br><br>
            <strong>Goal:</strong> Register a user with a malicious username that will execute JavaScript when an admin views the user list.
            <br><br>
            <strong>Hint:</strong> After registering a malicious user, visit <code>/admin/users/simulate-view</code> to simulate an admin viewing the user list.
        </div>
    </div>
</body>
</html>
"""

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Login</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 400px; margin: 100px auto; padding: 20px; }}
        .login-box {{ background: #16213e; border-radius: 8px; padding: 30px; }}
        h2 {{ text-align: center; color: #00aaff; }}
        .form-group {{ margin-bottom: 15px; }}
        label {{ display: block; margin-bottom: 5px; color: #888; }}
        input[type="text"], input[type="password"] {{ width: 100%; padding: 10px; border: 1px solid #333; border-radius: 4px; background: #0f3460; color: #fff; box-sizing: border-box; }}
        button {{ width: 100%; padding: 12px; background: #00aaff; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
        button:hover {{ background: #0088cc; }}
        .error {{ background: #ff4444; color: #fff; padding: 10px; border-radius: 4px; margin-bottom: 15px; }}
        .links {{ text-align: center; margin-top: 20px; }}
        .links a {{ color: #00aaff; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <h2>&#x1F511; Login</h2>
            {error}
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
            <div class="links">
                <a href="/register">Create an account</a> | <a href="/">Home</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

REGISTER_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Register</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 400px; margin: 50px auto; padding: 20px; }}
        .register-box {{ background: #16213e; border-radius: 8px; padding: 30px; }}
        h2 {{ text-align: center; color: #00aaff; }}
        .form-group {{ margin-bottom: 15px; }}
        label {{ display: block; margin-bottom: 5px; color: #888; }}
        input[type="text"], input[type="email"], input[type="password"] {{ width: 100%; padding: 10px; border: 1px solid #333; border-radius: 4px; background: #0f3460; color: #fff; box-sizing: border-box; }}
        button {{ width: 100%; padding: 12px; background: #00aaff; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
        button:hover {{ background: #0088cc; }}
        .error {{ background: #ff4444; color: #fff; padding: 10px; border-radius: 4px; margin-bottom: 15px; }}
        .success {{ background: #00aa44; color: #fff; padding: 10px; border-radius: 4px; margin-bottom: 15px; }}
        .links {{ text-align: center; margin-top: 20px; }}
        .links a {{ color: #00aaff; }}
        .hint {{ background: #0f3460; border-left: 4px solid #ffaa00; padding: 10px; margin-bottom: 15px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="register-box">
            <h2>&#x1F4DD; Register User</h2>
            <div class="hint">
                <strong>Hint:</strong> The username field does not sanitize input. Try XSS payloads like:<br>
                <code>&lt;img src=x onerror=alert('XSS')&gt;</code>
            </div>
            {error}
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit">Register</button>
            </form>
            <div class="links">
                <a href="/login">Already have an account?</a> | <a href="/">Home</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 800px; margin: 50px auto; padding: 20px; }}
        .dashboard-box {{ background: #16213e; border-radius: 8px; padding: 30px; }}
        h2 {{ color: #00aaff; }}
        .nav {{ background: #0f3460; padding: 10px; margin-bottom: 20px; border-radius: 4px; }}
        .nav a {{ color: #00aaff; margin-right: 15px; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/admin/users">User Management</a>
            <a href="/logout">Logout</a>
        </div>
        <div class="dashboard-box">
            <h2>Welcome, {username}!</h2>
            <p>This is your dashboard.</p>
        </div>
    </div>
</body>
</html>
"""

ADMIN_USERS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - User Management</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 900px; margin: 50px auto; padding: 20px; }}
        .admin-box {{ background: #16213e; border-radius: 8px; padding: 30px; }}
        h2 {{ color: #00aaff; }}
        .nav {{ background: #0f3460; padding: 10px; margin-bottom: 20px; border-radius: 4px; }}
        .nav a {{ color: #00aaff; margin-right: 15px; text-decoration: none; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ background: #0f3460; }}
        tr:hover {{ background: #1f2940; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/dashboard">Dashboard</a>
            <a href="/logout">Logout</a>
        </div>
        <div class="admin-box">
            <h2>&#x1F465; User Management</h2>
            <table>
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Level</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {user_rows}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

ADMIN_USERS_PAGE_SIMULATED = """
<!DOCTYPE html>
<html>
<head>
    <title>LibreNMS - User Management (Admin View)</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 900px; margin: 50px auto; padding: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>User List</h2>
        <table>
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Level</th>
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

# Keep original INDEX_CONTENT for backwards compatibility
INDEX_CONTENT = LIBRENMS_INDEX

# Image routes (kept for compatibility)
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
