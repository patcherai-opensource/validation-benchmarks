# Game Server Listing System (GSLS) Constants
# A server monitoring dashboard for game servers

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>GSLS - Game Server Listing System</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { color: #00ff88; text-align: center; }
        .nav { background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .nav a { color: #00ff88; margin-right: 20px; text-decoration: none; }
        .nav a:hover { text-decoration: underline; }
        .panel { background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .panel h2 { color: #00ff88; margin-top: 0; }
        .api-docs { background: #0f3460; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .api-docs code { background: #1a1a2e; padding: 2px 6px; border-radius: 3px; }
        .endpoint { color: #e94560; font-weight: bold; }
        pre { background: #0f3460; padding: 10px; border-radius: 5px; overflow-x: auto; }
        .server-list { list-style: none; padding: 0; }
        .server-list li { background: #0f3460; padding: 10px; margin: 5px 0; border-radius: 5px; }
        .server-list li a { color: #00ff88; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Game Server Listing System (GSLS)</h1>
        <p style="text-align: center; color: #888;">Monitor and track your favorite game servers</p>
        
        <div class="nav">
            <a href="/">Home</a>
            <a href="/api/servers">View Servers (API)</a>
        </div>
        
        <div class="panel">
            <h2>Welcome to GSLS</h2>
            <p>GSLS is a game server monitoring system that allows server operators to register their servers and players to browse server information.</p>
            <p>Server owners can register their servers via the API and all server details will be displayed on individual server pages.</p>
        </div>
        
        <div class="panel">
            <h2>API Documentation</h2>
            
            <div class="api-docs">
                <p><span class="endpoint">GET</span> <code>/api/servers</code></p>
                <p>List all registered game servers.</p>
            </div>
            
            <div class="api-docs">
                <p><span class="endpoint">POST</span> <code>/api/servers/register</code></p>
                <p>Register a new game server. Accepts JSON with server details.</p>
                <p>Required fields: <code>name</code>, <code>game</code>, <code>address</code></p>
                <p>Optional fields: <code>players</code>, <code>map</code>, <code>extra</code> (object with additional server info)</p>
                <pre>{
  "name": "My Server",
  "game": "Counter-Strike",
  "address": "192.168.1.1:27015",
  "players": "16/32",
  "map": "de_dust2",
  "extra": {
    "ModVersion": "1.2.3",
    "GameMode": "Competitive"
  }
}</pre>
            </div>
            
            <div class="api-docs">
                <p><span class="endpoint">GET</span> <code>/server/{id}</code></p>
                <p>View detailed information about a specific server. The extra fields are displayed in a table format.</p>
            </div>
        </div>
        
        <div class="panel">
            <h2>Recent Servers</h2>
            <p>Use the <a href="/api/servers" style="color: #00ff88;">API endpoint</a> to see all registered servers, then visit <code>/server/{id}</code> to view details.</p>
        </div>
    </div>
</body>
</html>
"""


SERVER_DETAILS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>GSLS - Server #{server_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #00ff88; }}
        .nav {{ background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .nav a {{ color: #00ff88; margin-right: 20px; text-decoration: none; }}
        .nav a:hover {{ text-decoration: underline; }}
        .panel {{ background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .panel h2 {{ color: #00ff88; margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #00ff88; }}
        .field-name {{ font-weight: bold; color: #e94560; width: 30%; }}
        .field-value {{ color: #eee; }}
        .server-status {{ display: inline-block; padding: 5px 10px; border-radius: 3px; background: #00ff88; color: #000; }}
        .flag-banner {{ background: #e94560; color: white; padding: 15px; border-radius: 5px; margin: 10px 0; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/api/servers">View Servers (API)</a>
        </div>
        
        <h1>Server Details: {name}</h1>
        <span class="server-status">Online</span>
        
        <div class="panel">
            <h2>Basic Information</h2>
            <table>
                <tr><td class="field-name">Server ID</td><td class="field-value">{server_id}</td></tr>
                <tr><td class="field-name">Server Name</td><td class="field-value">{name}</td></tr>
                <tr><td class="field-name">Game</td><td class="field-value">{game}</td></tr>
                <tr><td class="field-name">Address</td><td class="field-value">{address}</td></tr>
                <tr><td class="field-name">Players</td><td class="field-value">{players}</td></tr>
                <tr><td class="field-name">Current Map</td><td class="field-value">{map}</td></tr>
            </table>
        </div>
        
        <div class="panel">
            <h2>Extended Server Information</h2>
            <table>
                {extra_rows}
            </table>
        </div>
    </div>
</body>
</html>
"""


SERVER_NOT_FOUND_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>GSLS - Server Not Found</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; text-align: center; }
        h1 { color: #e94560; }
        .nav { background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .nav a { color: #00ff88; margin-right: 20px; text-decoration: none; }
        .panel { background: #16213e; padding: 40px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/api/servers">View Servers (API)</a>
        </div>
        <div class="panel">
            <h1>404 - Server Not Found</h1>
            <p>The requested server does not exist or has been removed.</p>
            <p><a href="/" style="color: #00ff88;">Return to Home</a></p>
        </div>
    </div>
</body>
</html>
"""


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
