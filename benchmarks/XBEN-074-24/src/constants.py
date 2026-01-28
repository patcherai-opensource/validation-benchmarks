# -*- coding: utf-8 -*-

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>LGSL - Live Game Server List</title>
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; padding: 30px 0; border-bottom: 1px solid #333; }
        .header h1 { color: #00d4ff; margin: 0; font-size: 2.5em; }
        .header p { color: #888; margin-top: 10px; }
        .nav { background: #16213e; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .nav a { color: #00d4ff; text-decoration: none; margin-right: 20px; padding: 10px 15px; }
        .nav a:hover { background: #0f3460; border-radius: 3px; }
        .content { background: #16213e; padding: 30px; border-radius: 5px; }
        .server-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .server-card { background: #0f3460; padding: 20px; border-radius: 5px; }
        .server-card h3 { color: #00d4ff; margin-top: 0; }
        .btn { background: #00d4ff; color: #1a1a2e; padding: 10px 20px; text-decoration: none; border-radius: 3px; display: inline-block; margin-top: 10px; }
        .btn:hover { background: #00a8cc; }
        .feature-list { list-style: none; padding: 0; }
        .feature-list li { padding: 10px 0; border-bottom: 1px solid #333; }
        .feature-list li:before { content: "✓ "; color: #00d4ff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 LGSL - Live Game Server List</h1>
            <p>Track and monitor your favorite game servers in real-time</p>
        </div>
        
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers/register">Register Server</a>
            <a href="/api/servers">Server List</a>
            <a href="/docs">API Docs</a>
            <a href="/about">About</a>
        </div>
        
        <div class="content">
            <h2>Welcome to LGSL</h2>
            <p>LGSL (Live Game Server List) is a powerful tool for monitoring and displaying information about game servers. 
            Register your servers and let players find them easily!</p>
            
            <h3>Features</h3>
            <ul class="feature-list">
                <li>Real-time server monitoring</li>
                <li>Support for multiple game protocols</li>
                <li>Custom server information display</li>
                <li>Player tracking and statistics</li>
                <li>Easy server registration via API</li>
            </ul>
            
            <h3>Quick Links</h3>
            <div class="server-grid">
                <div class="server-card">
                    <h3>Register Server</h3>
                    <p>Add your game server to our tracking system</p>
                    <a href="/servers/register" class="btn">Register Now</a>
                </div>
                <div class="server-card">
                    <h3>View Servers</h3>
                    <p>Browse all registered game servers</p>
                    <a href="/api/servers" class="btn">View List</a>
                </div>
                <div class="server-card">
                    <h3>API Documentation</h3>
                    <p>Integrate LGSL with your applications</p>
                    <a href="/docs" class="btn">Read Docs</a>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px; color: #666;">
            <p>LGSL v7.0.1 &copy; 2024</p>
        </div>
    </div>
</body>
</html>
"""

REGISTER_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Register Server - LGSL</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { text-align: center; padding: 20px 0; }
        .header h1 { color: #00d4ff; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #00d4ff; }
        .form-group input, .form-group textarea { width: 100%; padding: 10px; border: 1px solid #333; background: #16213e; color: #eee; border-radius: 3px; box-sizing: border-box; }
        .btn { background: #00d4ff; color: #1a1a2e; padding: 12px 25px; border: none; border-radius: 3px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #00a8cc; }
        .form-container { background: #16213e; padding: 30px; border-radius: 5px; }
        .nav { background: #0f3460; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .nav a { color: #00d4ff; text-decoration: none; margin-right: 15px; }
        .info-box { background: #0f3460; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 14px; }
        .info-box code { background: #1a1a2e; padding: 2px 5px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers/register">Register</a>
            <a href="/api/servers">Servers</a>
            <a href="/docs">Docs</a>
        </div>
        
        <div class="header">
            <h1>Register Game Server</h1>
            <p>Add your server to the LGSL tracking system</p>
        </div>
        
        <div class="form-container">
            <form action="/servers/register" method="POST">
                <div class="form-group">
                    <label>Server Name</label>
                    <input type="text" name="name" placeholder="My Awesome Server" required>
                </div>
                <div class="form-group">
                    <label>Game</label>
                    <input type="text" name="game" placeholder="Counter-Strike 2" required>
                </div>
                <div class="form-group">
                    <label>Server Address</label>
                    <input type="text" name="address" placeholder="192.168.1.1:27015" required>
                </div>
                <div class="form-group">
                    <label>Players</label>
                    <input type="text" name="players" placeholder="0/32">
                </div>
                <div class="form-group">
                    <label>Current Map</label>
                    <input type="text" name="map" placeholder="de_dust2">
                </div>
                <button type="submit" class="btn">Register Server</button>
            </form>
            
            <div class="info-box">
                <strong>API Registration:</strong><br>
                You can also register servers via the API by sending a POST request with JSON data to <code>/servers/register</code>.
                Extended server information can be provided in the <code>extra</code> field as key-value pairs.
            </div>
        </div>
    </div>
</body>
</html>
"""

SERVER_DETAILS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Server Details - LGSL</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{ text-align: center; padding: 20px 0; }}
        .header h1 {{ color: #00d4ff; }}
        .nav {{ background: #0f3460; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
        .nav a {{ color: #00d4ff; text-decoration: none; margin-right: 15px; }}
        .details-card {{ background: #16213e; padding: 25px; border-radius: 5px; }}
        .server-title {{ color: #00d4ff; font-size: 1.5em; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ color: #00d4ff; background: #0f3460; }}
        .field-name {{ color: #888; font-weight: bold; }}
        .field-value {{ color: #eee; }}
        .section-title {{ color: #00d4ff; margin-top: 25px; margin-bottom: 15px; padding-bottom: 5px; border-bottom: 1px solid #00d4ff; }}
        .alert {{ padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .alert-success {{ background: #0f5132; border: 1px solid #0a3622; }}
        .alert-warning {{ background: #664d03; border: 1px solid #997404; }}
        .status-online {{ color: #00ff00; }}
        .btn {{ background: #00d4ff; color: #1a1a2e; padding: 8px 15px; text-decoration: none; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers/register">Register</a>
            <a href="/api/servers">Servers</a>
            <a href="/docs">Docs</a>
        </div>
        
        <!-- XSS_RESULT -->
        
        <div class="details-card">
            <div class="server-title">🎮 {name}</div>
            
            <h3 class="section-title">Server Information</h3>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                <tr><td class='field-name'>Server ID</td><td class='field-value'>{server_id}</td></tr>
                <tr><td class='field-name'>Name</td><td class='field-value'>{name}</td></tr>
                <tr><td class='field-name'>Game</td><td class='field-value'>{game}</td></tr>
                <tr><td class='field-name'>Address</td><td class='field-value'>{address}</td></tr>
                <tr><td class='field-name'>Players</td><td class='field-value'>{players}</td></tr>
                <tr><td class='field-name'>Map</td><td class='field-value'>{map_name}</td></tr>
                <tr><td class='field-name'>Version</td><td class='field-value'>{version}</td></tr>
                <tr><td class='field-name'>Status</td><td class='field-value'><span class="status-online">● Online</span></td></tr>
            </table>
            
            <h3 class="section-title">Extended Server Information</h3>
            <table>
                <tr><th>Field</th><th>Value</th></tr>
                {extra_rows}
            </table>
            
            <div style="margin-top: 25px;">
                <a href="/api/servers" class="btn">← Back to Server List</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

SERVER_NOT_FOUND = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Server Not Found - LGSL</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 600px; margin: 50px auto; }
        h1 { color: #ff4444; }
        .btn { background: #00d4ff; color: #1a1a2e; padding: 10px 20px; text-decoration: none; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>404 - Server Not Found</h1>
        <p>The requested game server could not be found in our database.</p>
        <a href="/api/servers" class="btn">View All Servers</a>
    </div>
</body>
</html>
"""

DOCS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>API Documentation - LGSL</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        .header { text-align: center; padding: 20px 0; }
        .header h1 { color: #00d4ff; }
        .nav { background: #0f3460; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .nav a { color: #00d4ff; text-decoration: none; margin-right: 15px; }
        .section { background: #16213e; padding: 25px; border-radius: 5px; margin-bottom: 20px; }
        .section h2 { color: #00d4ff; margin-top: 0; }
        .endpoint { background: #0f3460; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .method { display: inline-block; padding: 3px 8px; border-radius: 3px; font-weight: bold; margin-right: 10px; }
        .get { background: #00d4ff; color: #1a1a2e; }
        .post { background: #00ff00; color: #1a1a2e; }
        .path { color: #eee; font-family: monospace; }
        code { background: #1a1a2e; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        pre { background: #1a1a2e; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers/register">Register</a>
            <a href="/api/servers">Servers</a>
            <a href="/docs">Docs</a>
        </div>
        
        <div class="header">
            <h1>API Documentation</h1>
            <p>LGSL REST API v7.0</p>
        </div>
        
        <div class="section">
            <h2>Endpoints</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/status</span>
                <p>Returns system health and status information.</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/servers</span>
                <p>Lists all registered game servers.</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/query/{server_id}</span>
                <p>Query a specific server by ID.</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/servers/register</span>
                <p>Register a new game server. Accepts JSON payload.</p>
                <pre>{
    "name": "Server Name",
    "game": "Game Title",
    "address": "ip:port",
    "players": "current/max",
    "map": "map_name",
    "extra": {
        "custom_field": "value",
        "another_field": "value"
    }
}</pre>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/servers/details/{server_id}</span>
                <p>View detailed information about a specific server, including extended info.</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Extended Server Information</h2>
            <p>The <code>extra</code> field allows servers to provide additional custom information that will be displayed on the server details page. This can include:</p>
            <ul>
                <li>Server rules and settings</li>
                <li>Mod information</li>
                <li>Community links</li>
                <li>Custom game variables</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

ABOUT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>About - LGSL</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; padding: 20px 0; }
        .header h1 { color: #00d4ff; }
        .nav { background: #0f3460; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .nav a { color: #00d4ff; text-decoration: none; margin-right: 15px; }
        .content { background: #16213e; padding: 25px; border-radius: 5px; }
        .content h2 { color: #00d4ff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers/register">Register</a>
            <a href="/api/servers">Servers</a>
            <a href="/docs">Docs</a>
        </div>
        
        <div class="header">
            <h1>About LGSL</h1>
        </div>
        
        <div class="content">
            <h2>Live Game Server List</h2>
            <p>LGSL is an open-source project for tracking and displaying game server information. 
            Originally developed for PHP, this version provides a modern API-based approach to server management.</p>
            
            <h2>Version History</h2>
            <ul>
                <li><strong>v7.0.1</strong> - Current release with improved API</li>
                <li><strong>v7.0.0</strong> - Major refactor with REST API support</li>
                <li><strong>v6.x</strong> - Legacy PHP version</li>
            </ul>
            
            <h2>Features</h2>
            <ul>
                <li>Server registration and tracking</li>
                <li>Real-time status monitoring</li>
                <li>Extended server information support</li>
                <li>RESTful API for integration</li>
            </ul>
            
            <h2>Contact</h2>
            <p>For issues and feature requests, please visit our project repository.</p>
        </div>
    </div>
</body>
</html>
"""

# Legacy image routes (kept for compatibility)
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
