INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>GameTrack - Server Monitoring</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 20px; text-align: center; border-bottom: 3px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .header p { color: #aaa; margin-top: 10px; }
        .nav { background: #0f3460; padding: 10px; text-align: center; }
        .nav a { color: #fff; text-decoration: none; margin: 0 20px; padding: 10px 20px; border-radius: 5px; }
        .nav a:hover { background: #e94560; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .hero { text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%); border-radius: 10px; margin-bottom: 40px; }
        .hero h2 { font-size: 2.5em; color: #e94560; margin-bottom: 20px; }
        .hero p { font-size: 1.2em; color: #aaa; max-width: 600px; margin: 0 auto; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .feature { background: #16213e; padding: 30px; border-radius: 10px; text-align: center; }
        .feature h3 { color: #e94560; }
        .cta-btn { display: inline-block; background: #e94560; color: #fff; padding: 15px 30px; border-radius: 5px; text-decoration: none; margin-top: 20px; font-weight: bold; }
        .cta-btn:hover { background: #ff6b6b; }
        .footer { text-align: center; padding: 20px; color: #666; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>GameTrack</h1>
        <p>Real-time Game Server Monitoring Platform</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/register">Add Server</a>
        <a href="/about">About</a>
        <a href="/docs">API Docs</a>
    </div>
    <div class="container">
        <div class="hero">
            <h2>Monitor Your Game Servers</h2>
            <p>Track player counts, server status, and performance metrics in real-time. Join thousands of server administrators who trust GameTrack.</p>
            <a href="/servers" class="cta-btn">Browse Servers</a>
        </div>
        <div class="features">
            <div class="feature">
                <h3>Real-time Monitoring</h3>
                <p>Get instant updates on server status, player counts, and performance metrics with our polling system.</p>
            </div>
            <div class="feature">
                <h3>Easy Registration</h3>
                <p>Add your server in seconds. Just provide your server details and we'll start tracking immediately.</p>
            </div>
            <div class="feature">
                <h3>Detailed Analytics</h3>
                <p>View comprehensive server information including extended metadata and custom fields.</p>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>GameTrack v2.4.1 | Server Monitoring Platform</p>
    </div>
</body>
</html>
"""

ABOUT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>About - GameTrack</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 20px; text-align: center; border-bottom: 3px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px; text-align: center; }
        .nav a { color: #fff; text-decoration: none; margin: 0 20px; padding: 10px 20px; border-radius: 5px; }
        .nav a:hover { background: #e94560; }
        .container { max-width: 800px; margin: 40px auto; padding: 20px; background: #16213e; border-radius: 10px; }
        h2 { color: #e94560; }
    </style>
</head>
<body>
    <div class="header">
        <h1>GameTrack</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/register">Add Server</a>
        <a href="/about">About</a>
        <a href="/docs">API Docs</a>
    </div>
    <div class="container">
        <h2>About GameTrack</h2>
        <p>GameTrack is a comprehensive game server monitoring platform designed for gaming communities.</p>
        <h3>Features</h3>
        <ul>
            <li>Real-time server status monitoring</li>
            <li>Player count tracking</li>
            <li>Extended server information display</li>
            <li>Easy server registration</li>
            <li>RESTful API for integration</li>
        </ul>
        <h3>How it Works</h3>
        <p>When you register a server, our system polls your server for information and displays it on the server details page. The extended information fields are fetched directly from your server and displayed to visitors.</p>
        <h3>Version</h3>
        <p>GameTrack v2.4.1</p>
    </div>
</body>
</html>
"""

SERVER_LIST_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Server List - GameTrack</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 20px; text-align: center; border-bottom: 3px solid #0f3460; }}
        .header h1 {{ margin: 0; color: #e94560; }}
        .nav {{ background: #0f3460; padding: 10px; text-align: center; }}
        .nav a {{ color: #fff; text-decoration: none; margin: 0 20px; padding: 10px 20px; border-radius: 5px; }}
        .nav a:hover {{ background: #e94560; }}
        .container {{ max-width: 1200px; margin: 40px auto; padding: 0 20px; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; border-radius: 10px; overflow: hidden; }}
        th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #e94560; }}
        tr:hover {{ background: #1f2b47; }}
        a {{ color: #e94560; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .status-online {{ color: #4caf50; }}
        .status-offline {{ color: #f44336; }}
        .status-pending {{ color: #ff9800; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GameTrack</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/register">Add Server</a>
        <a href="/about">About</a>
        <a href="/docs">API Docs</a>
    </div>
    <div class="container">
        <h2>Registered Servers</h2>
        <table>
            <tr>
                <th>Server Name</th>
                <th>Game</th>
                <th>Players</th>
                <th>Status</th>
                <th>Details</th>
            </tr>
            {server_rows}
        </table>
    </div>
</body>
</html>
"""

SERVER_ROW_TEMPLATE = """
<tr>
    <td>{name}</td>
    <td>{game}</td>
    <td>{players}</td>
    <td class="status-{status}">{status}</td>
    <td><a href="/server/{id}">View Details</a></td>
</tr>
"""

SERVER_DETAILS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>{name} - GameTrack</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 20px; text-align: center; border-bottom: 3px solid #0f3460; }}
        .header h1 {{ margin: 0; color: #e94560; }}
        .nav {{ background: #0f3460; padding: 10px; text-align: center; }}
        .nav a {{ color: #fff; text-decoration: none; margin: 0 20px; padding: 10px 20px; border-radius: 5px; }}
        .nav a:hover {{ background: #e94560; }}
        .container {{ max-width: 800px; margin: 40px auto; padding: 20px; }}
        .server-card {{ background: #16213e; padding: 30px; border-radius: 10px; }}
        .server-title {{ color: #e94560; font-size: 1.8em; margin-bottom: 20px; }}
        .info-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .info-table td {{ padding: 12px; border-bottom: 1px solid #0f3460; }}
        .info-table td:first-child {{ color: #aaa; width: 30%; }}
        .extended-info {{ margin-top: 30px; }}
        .extended-info h3 {{ color: #e94560; }}
        .status-online {{ color: #4caf50; }}
        .status-offline {{ color: #f44336; }}
        .status-pending {{ color: #ff9800; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GameTrack</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/register">Add Server</a>
        <a href="/about">About</a>
        <a href="/docs">API Docs</a>
    </div>
    <div class="container">
        <div class="server-card">
            <div class="server-title">{name}</div>
            <table class="info-table">
                <tr><td>Game</td><td>{game}</td></tr>
                <tr><td>IP Address</td><td>{ip}</td></tr>
                <tr><td>Port</td><td>{port}</td></tr>
                <tr><td>Players</td><td>{players}</td></tr>
                <tr><td>Current Map</td><td>{map}</td></tr>
                <tr><td>Status</td><td class="status-{status}">{status}</td></tr>
            </table>
            <div class="extended-info">
                <h3>Extended Server Information</h3>
                <table class="info-table">
                    {extended_info}
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

REGISTER_SERVER_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Register Server - GameTrack</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 20px; text-align: center; border-bottom: 3px solid #0f3460; }}
        .header h1 {{ margin: 0; color: #e94560; }}
        .nav {{ background: #0f3460; padding: 10px; text-align: center; }}
        .nav a {{ color: #fff; text-decoration: none; margin: 0 20px; padding: 10px 20px; border-radius: 5px; }}
        .nav a:hover {{ background: #e94560; }}
        .container {{ max-width: 600px; margin: 40px auto; padding: 20px; }}
        .form-card {{ background: #16213e; padding: 30px; border-radius: 10px; }}
        h2 {{ color: #e94560; }}
        label {{ display: block; margin-top: 15px; color: #aaa; }}
        input, textarea {{ width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #0f3460; border-radius: 5px; background: #1a1a2e; color: #fff; box-sizing: border-box; }}
        input:focus, textarea:focus {{ outline: none; border-color: #e94560; }}
        button {{ background: #e94560; color: #fff; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; margin-top: 20px; font-size: 1em; }}
        button:hover {{ background: #ff6b6b; }}
        .success {{ background: #4caf50; color: #fff; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .error {{ background: #f44336; color: #fff; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .flag-reveal {{ background: #e94560; color: #fff; padding: 20px; border-radius: 5px; margin-top: 20px; font-family: monospace; }}
        .info-text {{ color: #888; font-size: 0.9em; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GameTrack</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/register">Add Server</a>
        <a href="/about">About</a>
        <a href="/docs">API Docs</a>
    </div>
    <div class="container">
        <div class="form-card">
            <h2>Register Your Server</h2>
            {message}
            {result}
            <form method="POST">
                <label>Server Name *</label>
                <input type="text" name="server_name" placeholder="My Awesome Server" required>
                
                <label>Game *</label>
                <input type="text" name="game" placeholder="e.g., Counter-Strike 2, Minecraft">
                
                <label>Server IP *</label>
                <input type="text" name="ip" placeholder="192.168.1.1">
                
                <label>Port</label>
                <input type="text" name="port" placeholder="27015" value="27015">
                
                <label>Description</label>
                <textarea name="description" rows="4" placeholder="Describe your server..."></textarea>
                <p class="info-text">This will be displayed on your server's details page.</p>
                
                <button type="submit">Register Server</button>
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
    <title>API Documentation - GameTrack</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: #16213e; padding: 20px; text-align: center; border-bottom: 3px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .nav { background: #0f3460; padding: 10px; text-align: center; }
        .nav a { color: #fff; text-decoration: none; margin: 0 20px; padding: 10px 20px; border-radius: 5px; }
        .nav a:hover { background: #e94560; }
        .container { max-width: 800px; margin: 40px auto; padding: 20px; }
        .endpoint { background: #16213e; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .method { display: inline-block; padding: 5px 10px; border-radius: 3px; font-weight: bold; margin-right: 10px; }
        .get { background: #4caf50; }
        .post { background: #2196f3; }
        .path { color: #e94560; font-family: monospace; }
        pre { background: #0f3460; padding: 15px; border-radius: 5px; overflow-x: auto; }
        h2 { color: #e94560; }
        h3 { color: #aaa; }
    </style>
</head>
<body>
    <div class="header">
        <h1>GameTrack</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/servers">Server List</a>
        <a href="/register">Add Server</a>
        <a href="/about">About</a>
        <a href="/docs">API Docs</a>
    </div>
    <div class="container">
        <h2>API Documentation</h2>
        <p>GameTrack provides a RESTful API for programmatic access to server information.</p>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/status</span>
            <p>Returns the platform status.</p>
            <pre>{"status": "operational", "version": "2.4.1", "servers_tracked": 3}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/servers</span>
            <p>Returns a list of all registered servers.</p>
            <pre>{"servers": [{"id": "srv-001", "name": "...", "game": "...", "status": "..."}]}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/server/{id}</span>
            <p>Returns detailed information about a specific server, including extended metadata.</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/register</span>
            <p>Register a new server. Required fields: server_name, game, ip. Optional: port, description.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/health</span>
            <p>Health check endpoint.</p>
            <pre>{"status": "healthy"}</pre>
        </div>
    </div>
</body>
</html>
"""

# Keep some legacy constants for compatibility (not used but prevents import errors)
XSS_CONTENT = ""
XSS_CONTENT_POST = ""
XSS_CONTENT_TAG = ""
XSS_CONTENT_TAG_POST = ""
XSS_CONTENT_IFRAME = ""
XSS_CONTENT_TEXTAREA_POST = ""

IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    }
}
