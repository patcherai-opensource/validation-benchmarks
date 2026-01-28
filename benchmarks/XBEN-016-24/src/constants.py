INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Live Game Server List</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #e94560; }
        .nav { background: #16213e; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .nav a { color: #e94560; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .hero { background: #16213e; padding: 40px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
        .hero h2 { color: #e94560; margin-bottom: 10px; }
        .features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .feature { background: #16213e; padding: 20px; border-radius: 5px; }
        .feature h3 { color: #e94560; }
        footer { margin-top: 40px; text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Server List</a>
            <a href="/admin">Admin</a>
            <a href="/docs">API Docs</a>
        </div>
        <div class="hero">
            <h1>LGSL - Live Game Server List</h1>
            <h2>Monitor Your Game Servers in Real-Time</h2>
            <p>Track player counts, server status, and game information across all your gaming infrastructure.</p>
        </div>
        <div class="features">
            <div class="feature">
                <h3>Real-Time Monitoring</h3>
                <p>Get instant updates on server status, player counts, and game maps.</p>
            </div>
            <div class="feature">
                <h3>Multi-Game Support</h3>
                <p>Support for Counter-Strike, Team Fortress, Minecraft, and 100+ other games.</p>
            </div>
            <div class="feature">
                <h3>Easy Integration</h3>
                <p>Simple REST API for registering and querying game servers.</p>
            </div>
        </div>
        <footer>
            <p>LGSL v6.2.1 | &copy; 2024 Game Server Solutions</p>
        </footer>
    </div>
</body>
</html>
"""


SERVERS_LIST_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Server List - LGSL</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #e94560; }}
        .nav {{ background: #16213e; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .nav a {{ color: #e94560; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #e94560; }}
        tr:hover {{ background: #0f3460; }}
        a {{ color: #e94560; }}
        .status-online {{ color: #4ade80; }}
        .status-offline {{ color: #f87171; }}
        footer {{ margin-top: 40px; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Server List</a>
            <a href="/admin">Admin</a>
            <a href="/docs">API Docs</a>
        </div>
        <h1>Game Server List</h1>
        <table>
            <thead>
                <tr>
                    <th>Server Name</th>
                    <th>Game</th>
                    <th>Map</th>
                    <th>Players</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {0}
            </tbody>
        </table>
        <footer>
            <p>LGSL v6.2.1 | &copy; 2024 Game Server Solutions</p>
        </footer>
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
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1, h2 {{ color: #e94560; }}
        .nav {{ background: #16213e; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .nav a {{ color: #e94560; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
        .server-card {{ background: #16213e; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }}
        .info-item {{ padding: 10px; background: #0f3460; border-radius: 5px; }}
        .info-label {{ color: #e94560; font-weight: bold; margin-bottom: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #e94560; }}
        .status-online {{ color: #4ade80; }}
        .status-offline {{ color: #f87171; }}
        footer {{ margin-top: 40px; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Server List</a>
            <a href="/admin">Admin</a>
            <a href="/docs">API Docs</a>
        </div>
        <h1>Server Details</h1>
        <div class="server-card">
            <h2>{0}</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Game</div>
                    <div>{1}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Current Map</div>
                    <div>{2}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Players</div>
                    <div>{3}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Status</div>
                    <div class="status-{4}">{4}</div>
                </div>
            </div>
        </div>
        <div class="server-card">
            <h2>Extended Server Information</h2>
            <table>
                <thead>
                    <tr>
                        <th>Property</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    {5}
                </tbody>
            </table>
        </div>
        <footer>
            <p>Server ID: {6} | LGSL v6.2.1</p>
        </footer>
    </div>
</body>
</html>
"""


ADMIN_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel - LGSL</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #e94560; }
        .nav { background: #16213e; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .nav a { color: #e94560; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .login-box { background: #16213e; padding: 30px; border-radius: 10px; max-width: 400px; margin: 50px auto; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: none; border-radius: 5px; background: #0f3460; color: #eee; }
        button { width: 100%; padding: 12px; background: #e94560; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #d63850; }
        .error { color: #f87171; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Server List</a>
            <a href="/admin">Admin</a>
            <a href="/docs">API Docs</a>
        </div>
        <div class="login-box">
            <h1>Admin Login</h1>
            <form method="POST" action="/admin/login">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p class="error">Admin panel is currently disabled for maintenance.</p>
        </div>
    </div>
</body>
</html>
"""


API_DOCS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>API Documentation - LGSL</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 1000px; margin: 0 auto; }
        h1, h2, h3 { color: #e94560; }
        .nav { background: #16213e; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .nav a { color: #e94560; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .endpoint { background: #16213e; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .method { display: inline-block; padding: 5px 10px; border-radius: 3px; font-weight: bold; margin-right: 10px; }
        .method-get { background: #4ade80; color: #000; }
        .method-post { background: #60a5fa; color: #000; }
        .path { font-family: monospace; font-size: 16px; }
        pre { background: #0f3460; padding: 15px; border-radius: 5px; overflow-x: auto; }
        code { color: #4ade80; }
        footer { margin-top: 40px; text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Server List</a>
            <a href="/admin">Admin</a>
            <a href="/docs">API Docs</a>
        </div>
        <h1>LGSL API Documentation</h1>
        <p>REST API for managing and querying game servers.</p>
        
        <div class="endpoint">
            <h3><span class="method method-get">GET</span><span class="path">/api/status</span></h3>
            <p>Check API health status.</p>
            <pre><code>curl http://localhost:8080/api/status</code></pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method method-get">GET</span><span class="path">/api/servers</span></h3>
            <p>List all registered server IDs.</p>
            <pre><code>curl http://localhost:8080/api/servers</code></pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method method-get">GET</span><span class="path">/api/servers/{server_id}</span></h3>
            <p>Get details for a specific server.</p>
            <pre><code>curl http://localhost:8080/api/servers/srv001</code></pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method method-post">POST</span><span class="path">/api/servers/register</span></h3>
            <p>Register a new game server. The server info is stored and displayed on the server details page.</p>
            <h4>Request Body:</h4>
            <pre><code>{
  "name": "My Game Server",
  "game": "Counter-Strike 2",
  "map": "de_dust2",
  "players": "12/24",
  "status": "online",
  "info": {
    "version": "1.38.7.2",
    "VAC": "Secure",
    "region": "US-East",
    "description": "Custom server info fields"
  }
}</code></pre>
            <h4>Example:</h4>
            <pre><code>curl -X POST http://localhost:8080/api/servers/register \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Test Server","game":"CS2","info":{"mode":"competitive"}}'</code></pre>
        </div>
        
        <footer>
            <p>LGSL v6.2.1 | &copy; 2024 Game Server Solutions</p>
        </footer>
    </div>
</body>
</html>
"""


# Legacy content kept for compatibility
XSS_CONTENT = """
    <html>
        <head>
            <title>Legacy Page</title>
        </head>
        <body>
            <p>This page has been deprecated.</p>
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
