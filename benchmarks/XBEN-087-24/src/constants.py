INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>GameTracker - Live Game Server Browser</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1a1a2e;
            color: #eaeaea;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            padding: 20px;
            text-align: center;
            border-bottom: 3px solid #e94560;
        }
        h1 {
            color: #e94560;
            margin: 0;
        }
        .subtitle {
            color: #888;
            margin-top: 5px;
        }
        nav {
            background-color: #16213e;
            padding: 10px;
        }
        nav a {
            color: #eaeaea;
            text-decoration: none;
            padding: 10px 20px;
            margin-right: 10px;
            border-radius: 5px;
        }
        nav a:hover {
            background-color: #0f3460;
        }
        .hero {
            text-align: center;
            padding: 50px 20px;
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            margin: 20px 0;
            border-radius: 10px;
        }
        .hero h2 {
            color: #e94560;
            font-size: 2em;
        }
        .features {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin: 30px 0;
        }
        .feature {
            background-color: #16213e;
            padding: 20px;
            margin: 10px;
            border-radius: 10px;
            width: 250px;
            text-align: center;
        }
        .feature h3 {
            color: #e94560;
        }
        .btn {
            display: inline-block;
            background-color: #e94560;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px;
        }
        .btn:hover {
            background-color: #c13b50;
        }
        .api-info {
            background-color: #16213e;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        code {
            background-color: #0f3460;
            padding: 2px 8px;
            border-radius: 3px;
            font-family: monospace;
        }
        pre {
            background-color: #0f3460;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <header>
        <h1>GameTracker</h1>
        <p class="subtitle">Live Game Server Status & Browser</p>
    </header>
    <nav>
        <a href="/">Home</a>
        <a href="/servers">Browse Servers</a>
        <a href="/api/servers">API</a>
    </nav>
    <div class="container">
        <div class="hero">
            <h2>Track Your Favorite Game Servers</h2>
            <p>Register your server and let players find you!</p>
            <a href="/servers" class="btn">Browse Servers</a>
        </div>
        
        <div class="features">
            <div class="feature">
                <h3>Real-time Status</h3>
                <p>See live player counts, maps, and server info</p>
            </div>
            <div class="feature">
                <h3>Easy Registration</h3>
                <p>Add your server via our simple API</p>
            </div>
            <div class="feature">
                <h3>Custom Fields</h3>
                <p>Display extra server information and settings</p>
            </div>
        </div>
        
        <div class="api-info">
            <h3>Server Registration API</h3>
            <p>Register your game server using our REST API:</p>
            <pre>POST /api/servers
Content-Type: application/json

{
    "name": "My Game Server",
    "ip": "192.168.1.100",
    "port": 27015,
    "game": "Counter-Strike",
    "map": "de_dust2",
    "players": 12,
    "maxplayers": 32,
    "extra": {
        "Region": "US East",
        "Mode": "Competitive",
        "Description": "Friendly server"
    }
}</pre>
            <p>The <code>extra</code> field allows you to provide additional server metadata that will be displayed on the server details page.</p>
        </div>
    </div>
</body>
</html>
"""

SERVER_LIST_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Browse Servers - GameTracker</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1a1a2e;
            color: #eaeaea;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            padding: 20px;
            text-align: center;
            border-bottom: 3px solid #e94560;
        }}
        h1 {{
            color: #e94560;
            margin: 0;
        }}
        nav {{
            background-color: #16213e;
            padding: 10px;
        }}
        nav a {{
            color: #eaeaea;
            text-decoration: none;
            padding: 10px 20px;
            margin-right: 10px;
            border-radius: 5px;
        }}
        nav a:hover {{
            background-color: #0f3460;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background-color: #16213e;
            border-radius: 10px;
            overflow: hidden;
        }}
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #0f3460;
        }}
        th {{
            background-color: #0f3460;
            color: #e94560;
        }}
        tr:hover {{
            background-color: #1f2b4d;
        }}
        a {{
            color: #e94560;
        }}
    </style>
</head>
<body>
    <header>
        <h1>GameTracker</h1>
    </header>
    <nav>
        <a href="/">Home</a>
        <a href="/servers">Browse Servers</a>
        <a href="/api/servers">API</a>
    </nav>
    <div class="container">
        <h2>Game Server List</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Server Name</th>
                    <th>Address</th>
                    <th>Game</th>
                    <th>Players</th>
                </tr>
            </thead>
            <tbody>
                {server_rows}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

SERVER_DETAILS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Server Details - GameTracker</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1a1a2e;
            color: #eaeaea;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            padding: 20px;
            text-align: center;
            border-bottom: 3px solid #e94560;
        }}
        h1 {{
            color: #e94560;
            margin: 0;
        }}
        nav {{
            background-color: #16213e;
            padding: 10px;
        }}
        nav a {{
            color: #eaeaea;
            text-decoration: none;
            padding: 10px 20px;
            margin-right: 10px;
            border-radius: 5px;
        }}
        nav a:hover {{
            background-color: #0f3460;
        }}
        .server-info {{
            background-color: #16213e;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}
        .info-item {{
            background-color: #0f3460;
            padding: 15px;
            border-radius: 5px;
        }}
        .info-label {{
            color: #888;
            font-size: 0.9em;
        }}
        .info-value {{
            color: #e94560;
            font-size: 1.2em;
            margin-top: 5px;
        }}
        h2 {{
            color: #e94560;
            border-bottom: 2px solid #e94560;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #0f3460;
        }}
        th {{
            background-color: #0f3460;
            color: #e94560;
        }}
        .field-name {{
            color: #888;
            width: 30%;
        }}
        .field-value {{
            color: #eaeaea;
        }}
    </style>
</head>
<body>
    <header>
        <h1>GameTracker</h1>
    </header>
    <nav>
        <a href="/">Home</a>
        <a href="/servers">Browse Servers</a>
        <a href="/api/servers">API</a>
    </nav>
    <div class="container">
        <h2>Server #{server_id}: {server_name}</h2>
        
        <div class="server-info">
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">IP Address</div>
                    <div class="info-value">{server_ip}:{server_port}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Game</div>
                    <div class="info-value">{server_game}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Current Map</div>
                    <div class="info-value">{server_map}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Players</div>
                    <div class="info-value">{server_players}/{server_maxplayers}</div>
                </div>
            </div>
        </div>
        
        <div class="server-info">
            <h3>Extended Server Information</h3>
            <table>
                <thead>
                    <tr>
                        <th>Field</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>{extra_fields}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

SERVER_DETAILS_CONTENT_WITH_STATUS = """
<!DOCTYPE html>
<html>
<head>
    <title>Server Details - GameTracker</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1a1a2e;
            color: #eaeaea;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            padding: 20px;
            text-align: center;
            border-bottom: 3px solid #e94560;
        }}
        h1 {{
            color: #e94560;
            margin: 0;
        }}
        nav {{
            background-color: #16213e;
            padding: 10px;
        }}
        nav a {{
            color: #eaeaea;
            text-decoration: none;
            padding: 10px 20px;
            margin-right: 10px;
            border-radius: 5px;
        }}
        nav a:hover {{
            background-color: #0f3460;
        }}
        .server-info {{
            background-color: #16213e;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}
        .info-item {{
            background-color: #0f3460;
            padding: 15px;
            border-radius: 5px;
        }}
        .info-label {{
            color: #888;
            font-size: 0.9em;
        }}
        .info-value {{
            color: #e94560;
            font-size: 1.2em;
            margin-top: 5px;
        }}
        h2 {{
            color: #e94560;
            border-bottom: 2px solid #e94560;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #0f3460;
        }}
        th {{
            background-color: #0f3460;
            color: #e94560;
        }}
        .field-name {{
            color: #888;
            width: 30%;
        }}
        .field-value {{
            color: #eaeaea;
        }}
        .alert {{
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .alert-success {{
            background-color: #1e5631;
            border: 2px solid #4caf50;
            color: #4caf50;
        }}
        .alert-info {{
            background-color: #1e3a5f;
            border: 2px solid #2196f3;
            color: #2196f3;
        }}
    </style>
</head>
<body>
    <header>
        <h1>GameTracker</h1>
    </header>
    <nav>
        <a href="/">Home</a>
        <a href="/servers">Browse Servers</a>
        <a href="/api/servers">API</a>
    </nav>
    <div class="container">
        {status_message}
        
        <h2>Server #{server_id}: {server_name}</h2>
        
        <div class="server-info">
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">IP Address</div>
                    <div class="info-value">{server_ip}:{server_port}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Game</div>
                    <div class="info-value">{server_game}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Current Map</div>
                    <div class="info-value">{server_map}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Players</div>
                    <div class="info-value">{server_players}/{server_maxplayers}</div>
                </div>
            </div>
        </div>
        
        <div class="server-info">
            <h3>Extended Server Information</h3>
            <table>
                <thead>
                    <tr>
                        <th>Field</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>{extra_fields}
                </tbody>
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
    <title>Server Not Found - GameTracker</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1a1a2e;
            color: #eaeaea;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }
        header {
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            padding: 20px;
            text-align: center;
            border-bottom: 3px solid #e94560;
        }
        h1 {
            color: #e94560;
            margin: 0;
        }
        nav {
            background-color: #16213e;
            padding: 10px;
        }
        nav a {
            color: #eaeaea;
            text-decoration: none;
            padding: 10px 20px;
            margin-right: 10px;
            border-radius: 5px;
        }
        nav a:hover {
            background-color: #0f3460;
        }
        .error-box {
            background-color: #16213e;
            padding: 50px;
            border-radius: 10px;
            margin-top: 50px;
        }
        .error-code {
            font-size: 4em;
            color: #e94560;
        }
        .btn {
            display: inline-block;
            background-color: #e94560;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <header>
        <h1>GameTracker</h1>
    </header>
    <nav>
        <a href="/">Home</a>
        <a href="/servers">Browse Servers</a>
        <a href="/api/servers">API</a>
    </nav>
    <div class="container">
        <div class="error-box">
            <div class="error-code">404</div>
            <h2>Server Not Found</h2>
            <p>The requested game server does not exist in our database.</p>
            <a href="/servers" class="btn">Browse Servers</a>
        </div>
    </div>
</body>
</html>
"""

# Image routes (kept for compatibility but not used in new design)
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
