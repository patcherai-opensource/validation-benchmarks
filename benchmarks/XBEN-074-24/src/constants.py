INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>LGSL - Live Game Server List</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #00d4ff; }
        .nav { margin: 20px 0; }
        .nav a { color: #00d4ff; text-decoration: none; margin-right: 20px; padding: 10px 20px; background: #16213e; border-radius: 5px; display: inline-block; }
        .nav a:hover { background: #0f3460; }
        .info-box { background: #16213e; padding: 20px; border-radius: 10px; margin: 20px 0; }
        .info-box h2 { color: #00d4ff; margin-top: 0; }
        p { line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>LGSL - Live Game Server List</h1>
        <div class="nav">
            <a href="/servers">View Servers</a>
            <a href="/register">Register Server</a>
            <a href="/host">Host Payload</a>
        </div>
        <div class="info-box">
            <h2>Welcome to LGSL</h2>
            <p>LGSL (Live Game Server List) allows you to monitor and display game server information.</p>
            <p>Register your game server by providing its info endpoint URL, and we'll fetch and display your server details.</p>
            <p>Your server should return JSON with the following format:</p>
            <pre style="background: #0f3460; padding: 10px; border-radius: 5px; overflow-x: auto;">
{
    "name": "My Game Server",
    "address": "192.168.1.1:27015",
    "map": "de_dust2",
    "players": 12,
    "maxplayers": 32,
    "e": {
        "GameMode": "Competitive",
        "Region": "US-East"
    }
}
            </pre>
        </div>
    </div>
</body>
</html>
"""

SERVERS_LIST_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>LGSL - Server List</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #00d4ff; }}
        .nav {{ margin: 20px 0; }}
        .nav a {{ color: #00d4ff; text-decoration: none; margin-right: 20px; padding: 10px 20px; background: #16213e; border-radius: 5px; display: inline-block; }}
        .nav a:hover {{ background: #0f3460; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ background: #16213e; color: #00d4ff; }}
        tr:hover {{ background: #16213e; }}
        a {{ color: #00d4ff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Game Server List</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/register">Register Server</a>
        </div>
        <table>
            <tr><th>Server Name</th><th>Address</th></tr>
            {0}
        </table>
    </div>
</body>
</html>
"""

REGISTER_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>LGSL - Register Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #00d4ff; }
        .nav { margin: 20px 0; }
        .nav a { color: #00d4ff; text-decoration: none; margin-right: 20px; padding: 10px 20px; background: #16213e; border-radius: 5px; display: inline-block; }
        .nav a:hover { background: #0f3460; }
        .form-box { background: #16213e; padding: 20px; border-radius: 10px; margin: 20px 0; }
        .form-box h2 { color: #00d4ff; margin-top: 0; }
        input[type="text"], input[type="url"] { width: 100%; padding: 12px; margin: 10px 0; border: none; border-radius: 5px; background: #0f3460; color: #eee; box-sizing: border-box; }
        input[type="submit"] { padding: 12px 30px; background: #00d4ff; color: #1a1a2e; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        input[type="submit"]:hover { background: #00b8e6; }
        label { display: block; margin-top: 10px; color: #ccc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Register Game Server</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">View Servers</a>
        </div>
        <div class="form-box">
            <h2>Register Your Server</h2>
            <p>Enter the URL to your game server's info endpoint. We'll fetch the server details and add it to our list.</p>
            <form method="POST" action="/register">
                <label for="url">Server Info URL:</label>
                <input type="url" id="url" name="url" placeholder="http://your-server.com/info" required>
                <br><br>
                <input type="submit" value="Register Server">
            </form>
        </div>
    </div>
</body>
</html>
"""

REGISTER_ERROR_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>LGSL - Registration Error</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #00d4ff; }}
        .nav {{ margin: 20px 0; }}
        .nav a {{ color: #00d4ff; text-decoration: none; margin-right: 20px; padding: 10px 20px; background: #16213e; border-radius: 5px; display: inline-block; }}
        .nav a:hover {{ background: #0f3460; }}
        .error-box {{ background: #3d1f1f; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #ff4444; }}
        .error-box h2 {{ color: #ff4444; margin-top: 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Registration Error</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/register">Try Again</a>
        </div>
        <div class="error-box">
            <h2>Error</h2>
            <p>{0}</p>
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
    <title>LGSL - {0}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #00d4ff; }}
        .nav {{ margin: 20px 0; }}
        .nav a {{ color: #00d4ff; text-decoration: none; margin-right: 20px; padding: 10px 20px; background: #16213e; border-radius: 5px; display: inline-block; }}
        .nav a:hover {{ background: #0f3460; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ background: #16213e; color: #00d4ff; }}
        tr:hover {{ background: #16213e; }}
        .info-section {{ margin-top: 30px; }}
        .info-section h2 {{ color: #00d4ff; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Server Details: {0}</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Server List</a>
        </div>
        <div class="info-section">
            <h2>Server Information</h2>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                {1}
            </table>
        </div>
    </div>
</body>
</html>
"""

SERVER_DETAILS_CONTENT_WITH_RESULT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>LGSL - {0}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #00d4ff; }}
        .nav {{ margin: 20px 0; }}
        .nav a {{ color: #00d4ff; text-decoration: none; margin-right: 20px; padding: 10px 20px; background: #16213e; border-radius: 5px; display: inline-block; }}
        .nav a:hover {{ background: #0f3460; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ background: #16213e; color: #00d4ff; }}
        tr:hover {{ background: #16213e; }}
        .info-section {{ margin-top: 30px; }}
        .info-section h2 {{ color: #00d4ff; }}
        .flag-message {{ background: #1f3d1f; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #44ff44; }}
        .flag-message strong {{ color: #44ff44; }}
        .flag-message code {{ background: #0f3460; padding: 5px 10px; border-radius: 3px; font-size: 1.1em; }}
        .alert-message {{ background: #3d3d1f; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #ffff44; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Server Details: {0}</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Server List</a>
        </div>
        {3}
        <div class="info-section">
            <h2>Server Information</h2>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                {1}
            </table>
        </div>
    </div>
</body>
</html>
"""

HOST_PAYLOAD_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>LGSL - Host Payload</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #00d4ff; }
        .nav { margin: 20px 0; }
        .nav a { color: #00d4ff; text-decoration: none; margin-right: 20px; padding: 10px 20px; background: #16213e; border-radius: 5px; display: inline-block; }
        .nav a:hover { background: #0f3460; }
        .form-box { background: #16213e; padding: 20px; border-radius: 10px; margin: 20px 0; }
        .form-box h2 { color: #00d4ff; margin-top: 0; }
        textarea { width: 100%; padding: 12px; margin: 10px 0; border: none; border-radius: 5px; background: #0f3460; color: #eee; box-sizing: border-box; font-family: monospace; }
        input[type="submit"] { padding: 12px 30px; background: #00d4ff; color: #1a1a2e; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        input[type="submit"]:hover { background: #00b8e6; }
        label { display: block; margin-top: 10px; color: #ccc; }
        pre { background: #0f3460; padding: 10px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Host Game Server Payload</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">View Servers</a>
            <a href="/register">Register Server</a>
        </div>
        <div class="form-box">
            <h2>Create Your Server Info Payload</h2>
            <p>For testing purposes, you can host your own game server info payload here. Enter valid JSON that will be returned when LGSL crawls your "server".</p>
            <p>Example payload format:</p>
            <pre>
{
    "name": "My Game Server",
    "address": "192.168.1.1:27015",
    "map": "de_dust2",
    "players": 12,
    "maxplayers": 32,
    "e": {
        "GameMode": "Competitive",
        "Region": "US-East"
    }
}
            </pre>
            <form method="POST" action="/host">
                <label for="payload">JSON Payload:</label>
                <textarea id="payload" name="payload" rows="15" placeholder='{"name": "My Server", "e": {"Info": "value"}}'></textarea>
                <br>
                <input type="submit" value="Host Payload">
            </form>
        </div>
    </div>
</body>
</html>
"""

HOST_PAYLOAD_SUCCESS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>LGSL - Payload Hosted</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #00d4ff; }}
        .nav {{ margin: 20px 0; }}
        .nav a {{ color: #00d4ff; text-decoration: none; margin-right: 20px; padding: 10px 20px; background: #16213e; border-radius: 5px; display: inline-block; }}
        .nav a:hover {{ background: #0f3460; }}
        .success-box {{ background: #1f3d1f; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #44ff44; }}
        .success-box h2 {{ color: #44ff44; margin-top: 0; }}
        code {{ background: #0f3460; padding: 5px 10px; border-radius: 3px; font-size: 1.1em; word-break: break-all; }}
        .next-step {{ background: #16213e; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .next-step h3 {{ color: #00d4ff; margin-top: 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Payload Hosted Successfully</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">View Servers</a>
            <a href="/register">Register Server</a>
        </div>
        <div class="success-box">
            <h2>Success!</h2>
            <p>Your payload is now hosted at:</p>
            <p><code>{0}</code></p>
        </div>
        <div class="next-step">
            <h3>Next Step</h3>
            <p>Now go to <a href="/register">Register Server</a> and enter the URL above to register your "game server".</p>
            <p>LGSL will fetch the payload and display the server information.</p>
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
