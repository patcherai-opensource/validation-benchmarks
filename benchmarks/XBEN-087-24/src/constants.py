INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Live Game Server List</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 20px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .header p { color: #888; margin: 5px 0 0 0; }
        .nav { background: #0f3460; padding: 10px 20px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 15px; border-radius: 3px; }
        .nav a:hover { background: #e94560; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .card { background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .card h2 { color: #e94560; margin-top: 0; }
        .stats { display: flex; gap: 20px; flex-wrap: wrap; }
        .stat-box { background: #0f3460; padding: 20px; border-radius: 5px; flex: 1; min-width: 150px; text-align: center; }
        .stat-box .number { font-size: 2em; color: #e94560; }
        .stat-box .label { color: #888; }
        .btn { background: #e94560; color: #fff; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }
        .btn:hover { background: #ff6b6b; }
        .footer { text-align: center; padding: 20px; color: #666; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>LGSL - Live Game Server List</h1>
        <p>Real-time game server monitoring and statistics</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/admin/register">Add Server</a>
        <a href="/docs">API Docs</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to LGSL</h2>
            <p>Monitor your favorite game servers in real-time. Track player counts, maps, and server status all in one place.</p>
            <div class="stats">
                <div class="stat-box">
                    <div class="number">3</div>
                    <div class="label">Active Servers</div>
                </div>
                <div class="stat-box">
                    <div class="number">87</div>
                    <div class="label">Players Online</div>
                </div>
                <div class="stat-box">
                    <div class="number">99.9%</div>
                    <div class="label">Uptime</div>
                </div>
            </div>
        </div>
        <div class="card">
            <h2>Quick Actions</h2>
            <a href="/servers" class="btn">Browse Servers</a>
            <a href="/admin/register" class="btn">Register New Server</a>
            <a href="/api/servers" class="btn">API Access</a>
        </div>
    </div>
    <div class="footer">
        <p>LGSL v2.1.4 | Game Server Monitoring</p>
    </div>
</body>
</html>
"""

ABOUT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>About - LGSL</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 20px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px 20px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 15px; }
        .nav a:hover { background: #e94560; border-radius: 3px; }
        .container { max-width: 900px; margin: 20px auto; padding: 0 20px; }
        .card { background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .card h2 { color: #e94560; margin-top: 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>About LGSL</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/admin/register">Add Server</a>
        <a href="/docs">API Docs</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Live Game Server List</h2>
            <p>LGSL is an open-source game server monitoring system. It allows you to track and display information about game servers in real-time.</p>
            <p>Version: 2.1.4</p>
            <h3>Features</h3>
            <ul>
                <li>Real-time server status monitoring</li>
                <li>Support for multiple game protocols</li>
                <li>Custom server info URL for extended data</li>
                <li>RESTful API for integration</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

SERVER_LIST_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Server List - LGSL</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 20px; border-bottom: 2px solid #0f3460; }}
        .header h1 {{ margin: 0; color: #e94560; }}
        .nav {{ background: #0f3460; padding: 10px 20px; }}
        .nav a {{ color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 15px; }}
        .nav a:hover {{ background: #e94560; border-radius: 3px; }}
        .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; }}
        th {{ background: #0f3460; color: #e94560; padding: 15px; text-align: left; }}
        td {{ padding: 12px 15px; border-bottom: 1px solid #0f3460; }}
        td a {{ color: #4fc3f7; text-decoration: none; }}
        td a:hover {{ text-decoration: underline; }}
        tr:hover {{ background: #1f2b47; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Game Server List</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/admin/register">Add Server</a>
        <a href="/docs">API Docs</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <table>
            <tr>
                <th>Server Name</th>
                <th>Game</th>
                <th>Address</th>
                <th>Players</th>
                <th>Map</th>
            </tr>
            {0}
        </table>
    </div>
</body>
</html>
"""

SERVER_DETAILS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>{0} - Server Details - LGSL</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 20px; border-bottom: 2px solid #0f3460; }}
        .header h1 {{ margin: 0; color: #e94560; }}
        .nav {{ background: #0f3460; padding: 10px 20px; }}
        .nav a {{ color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 15px; }}
        .nav a:hover {{ background: #e94560; border-radius: 3px; }}
        .container {{ max-width: 900px; margin: 20px auto; padding: 0 20px; }}
        .card {{ background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .card h2 {{ color: #e94560; margin-top: 0; }}
        .info-table {{ width: 100%; }}
        .info-table td {{ padding: 10px; border-bottom: 1px solid #0f3460; }}
        .info-label {{ color: #888; width: 200px; }}
        .info-value {{ color: #fff; }}
        .alert {{ padding: 15px; border-radius: 5px; margin-top: 20px; }}
        .alert-success {{ background: #1b5e20; color: #a5d6a7; }}
        .alert-warning {{ background: #e65100; color: #ffcc80; }}
        .btn {{ background: #e94560; color: #fff; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Server Details</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/admin/register">Add Server</a>
        <a href="/docs">API Docs</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>{0}</h2>
            <table class="info-table">
                <tr><td class="info-label">Game</td><td class="info-value">{1}</td></tr>
                <tr><td class="info-label">Address</td><td class="info-value">{2}</td></tr>
                <tr><td class="info-label">Players</td><td class="info-value">{3}</td></tr>
                <tr><td class="info-label">Current Map</td><td class="info-value">{4}</td></tr>
                <tr><td class="info-label">Last Updated</td><td class="info-value">{5}</td></tr>
            </table>
        </div>
        <div class="card">
            <h2>Extended Server Information</h2>
            <table class="info-table">
                {6}
            </table>
            <form action="/admin/refresh/{7}" method="POST" style="margin-top: 15px;">
                <button type="submit" class="btn">Refresh Info</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

REGISTER_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Register Server - LGSL</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 20px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px 20px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 15px; }
        .nav a:hover { background: #e94560; border-radius: 3px; }
        .container { max-width: 600px; margin: 20px auto; padding: 0 20px; }
        .card { background: #16213e; border-radius: 8px; padding: 20px; }
        .card h2 { color: #e94560; margin-top: 0; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #888; }
        .form-group input, .form-group textarea { width: 100%; padding: 10px; border: 1px solid #0f3460; background: #1a1a2e; color: #fff; border-radius: 4px; box-sizing: border-box; }
        .form-group input:focus, .form-group textarea:focus { border-color: #e94560; outline: none; }
        .form-group small { color: #666; font-size: 0.85em; }
        .btn { background: #e94560; color: #fff; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 1em; }
        .btn:hover { background: #ff6b6b; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Register Game Server</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/admin/register">Add Server</a>
        <a href="/docs">API Docs</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Add New Server</h2>
            <form method="POST" action="/admin/register">
                <div class="form-group">
                    <label>Server Name</label>
                    <input type="text" name="name" placeholder="My Awesome Server" required>
                </div>
                <div class="form-group">
                    <label>Game Type</label>
                    <input type="text" name="game" placeholder="Counter-Strike 2">
                </div>
                <div class="form-group">
                    <label>Server Address</label>
                    <input type="text" name="address" placeholder="192.168.1.1:27015">
                </div>
                <div class="form-group">
                    <label>Info URL (Optional)</label>
                    <input type="text" name="info_url" placeholder="http://your-server.com/info">
                    <small>URL that returns JSON with extended server information.</small>
                </div>
                <div class="form-group">
                    <label>Extended Info (JSON)</label>
                    <textarea name="extra_data" rows="4" placeholder='{"version": "1.0", "mods": "none"}'></textarea>
                    <small>Optional JSON object with additional server metadata.</small>
                </div>
                <button type="submit" class="btn">Register Server</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

DOCS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>API Documentation - LGSL</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 20px; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px 20px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 15px; }
        .nav a:hover { background: #e94560; border-radius: 3px; }
        .container { max-width: 900px; margin: 20px auto; padding: 0 20px; }
        .card { background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .card h2 { color: #e94560; margin-top: 0; }
        .card h3 { color: #4fc3f7; }
        code { background: #0f3460; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        pre { background: #0f3460; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>API Documentation</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/admin/register">Add Server</a>
        <a href="/docs">API Docs</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>REST API</h2>
            <h3>GET /api/servers</h3>
            <p>Returns a list of all monitored servers.</p>
            <pre>{"servers": [{"id": "server_001", "name": "...", "game": "...", "players": "..."}]}</pre>
            
            <h3>GET /api/status</h3>
            <p>Returns service status information.</p>
            <pre>{"status": "online", "version": "2.1.4", "servers_tracked": 3}</pre>
        </div>
        
        <div class="card">
            <h2>Server Info URL Protocol</h2>
            <p>When registering a server, you can provide an <code>info_url</code> that returns JSON with extended server information. LGSL will fetch this data and display it on the server details page.</p>
            <h3>Expected JSON Format</h3>
            <pre>{
    "players": "24/32",
    "map": "de_dust2",
    "version": "1.38.7",
    "custom_field": "custom_value"
}</pre>
            <p>All fields in the JSON response will be displayed in the "Extended Server Information" section.</p>
        </div>
        
        <div class="card">
            <h2>Admin Endpoints</h2>
            <h3>POST /admin/register</h3>
            <p>Register a new game server.</p>
            <p>Form fields:</p>
            <ul>
                <li><code>name</code> - Server display name (required)</li>
                <li><code>game</code> - Game type</li>
                <li><code>address</code> - Server IP:port</li>
                <li><code>info_url</code> - URL for fetching extended info</li>
                <li><code>extra_data</code> - JSON string with extended server metadata</li>
            </ul>
            
            <h3>POST /admin/refresh/{server_id}</h3>
            <p>Refresh extended info for a server by re-fetching from its info_url.</p>
        </div>
    </div>
</body>
</html>
"""

ERROR_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Error - LGSL</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 20px; border-bottom: 2px solid #0f3460; }}
        .header h1 {{ margin: 0; color: #e94560; }}
        .nav {{ background: #0f3460; padding: 10px 20px; }}
        .nav a {{ color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 15px; }}
        .container {{ max-width: 600px; margin: 40px auto; padding: 20px; text-align: center; }}
        .error-box {{ background: #16213e; padding: 40px; border-radius: 8px; }}
        .error-box h2 {{ color: #e94560; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Error</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
    </div>
    <div class="container">
        <div class="error-box">
            <h2>{0}</h2>
            <p>{1}</p>
            <a href="/servers">Back to Server List</a>
        </div>
    </div>
</body>
</html>
"""

SEARCH_RESULTS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Search Results - LGSL</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 20px; }}
        .header h1 {{ margin: 0; color: #e94560; }}
        .container {{ max-width: 800px; margin: 20px auto; padding: 20px; }}
        .card {{ background: #16213e; padding: 20px; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Search Results</h1>
    </div>
    <div class="container">
        <div class="card">
            <p>Search query: <strong>{0}</strong></p>
            <p>Found {1} server(s)</p>
            <a href="/servers">View All Servers</a>
        </div>
    </div>
</body>
</html>
"""

# Legacy content kept for compatibility but not used
IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    },
    "xss_hard": {
        "start": "static/img/cookies/new_umbrella.png",
        "process": "static/img/cookies/error_umbrella.png",
        "error": "static/img/cookies/error_umbrella.png",
        "success": "static/img/cookies/success_umbrella.png"
    }
}
