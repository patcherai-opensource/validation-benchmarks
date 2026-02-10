INDEX_CONTENT = """
    	<html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>Dalgona Challenges</title>
        </head>

	        <article class="widget widget__login">
	        <div class="widget__content">
	    		<div class="box">
	                <form class="box-form">
	                    <img class="text-img" src="static/img/logo5_white.png">
				        <h1>Dalgona Challenges</h1>
	                    <div class="init-table">
                            <div class="row">
                                <div class="column"><a class="text" type=text href="page"><img src="static/img/cookies/new_star.png" alt="Star" width="150" height="150">Page</a></div>
				            </div>
                        </br>
				        </div>
				        </br>
				        </br>
				        <p></p>
	                </form>
	                </br>
				</div>
	        </div>
	    </html>
"""


XSS_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=name placeholder="Enter your name..." {2}>
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_POST = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="post">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=solution placeholder="Enter solution..." {2}>
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_TAG = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>
    
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=name placeholder="Enter your name...">
                    {2}
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_TAG_POST = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="post">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=solution placeholder="Enter solution...">
                    {2}
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_IFRAME = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">

                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=url placeholder="Enter the URL you want to visit...">
                    <iframe {2}></iframe>
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_TEXTAREA_POST = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="post">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <br>
                    <textarea name=name cols=50 rows=20 placeholder="Enter your name..."></textarea>
                    {2}
                    <br>
                    <input type=submit value="Submit">
                </form>
            </div>
        </div>
    </html>
"""

# Image routes

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

# LGSL-style Game Server List templates
LGSL_INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Live Game Server List</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #00d4ff; text-align: center; }
        .nav { text-align: center; margin: 20px 0; }
        .nav a { color: #00d4ff; text-decoration: none; margin: 0 15px; padding: 10px 20px; border: 1px solid #00d4ff; border-radius: 5px; }
        .nav a:hover { background: #00d4ff; color: #1a1a2e; }
        .info-box { background: #16213e; padding: 20px; border-radius: 10px; margin-top: 20px; }
        .info-box h2 { color: #00d4ff; }
        .info-box p { line-height: 1.6; }
        code { background: #0f3460; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>LGSL - Live Game Server List</h1>
        <div class="nav">
            <a href="/servers">View Servers</a>
            <a href="/register">Register Server</a>
        </div>
        <div class="info-box">
            <h2>Welcome to LGSL</h2>
            <p>This is a game server listing application. Server admins can register their game servers 
            and provide server information that will be displayed to visitors.</p>
            <p>When registering a server, you can provide JSON-formatted server information that will 
            be displayed on the server details page. For example:</p>
            <pre><code>{"GameMode": "Survival", "MaxPlayers": "32", "Map": "de_dust2"}</code></pre>
        </div>
    </div>
</body>
</html>
"""

LGSL_SERVERS_LIST = """
<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Server List</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #00d4ff; text-align: center; }}
        .nav {{ text-align: center; margin: 20px 0; }}
        .nav a {{ color: #00d4ff; text-decoration: none; margin: 0 15px; padding: 10px 20px; border: 1px solid #00d4ff; border-radius: 5px; }}
        .nav a:hover {{ background: #00d4ff; color: #1a1a2e; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: #16213e; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #00d4ff; }}
        tr:hover {{ background: #1a1a3e; }}
        a {{ color: #00d4ff; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Registered Game Servers</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/register">Register Server</a>
        </div>
        <table>
            <tr><th>ID</th><th>Server Name</th><th>Address</th><th>Actions</th></tr>
            {0}
        </table>
    </div>
</body>
</html>
"""

LGSL_REGISTER_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Register Server</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { color: #00d4ff; text-align: center; }
        .nav { text-align: center; margin: 20px 0; }
        .nav a { color: #00d4ff; text-decoration: none; margin: 0 15px; padding: 10px 20px; border: 1px solid #00d4ff; border-radius: 5px; }
        .nav a:hover { background: #00d4ff; color: #1a1a2e; }
        form { background: #16213e; padding: 30px; border-radius: 10px; }
        label { display: block; margin-bottom: 5px; color: #00d4ff; }
        input[type="text"], textarea { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #0f3460; border-radius: 5px; background: #0f3460; color: #eee; box-sizing: border-box; }
        textarea { height: 100px; font-family: monospace; }
        input[type="submit"] { background: #00d4ff; color: #1a1a2e; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        input[type="submit"]:hover { background: #00b8d9; }
        .hint { font-size: 12px; color: #888; margin-top: -10px; margin-bottom: 15px; }
        .error { color: #ff4444; padding: 10px; background: #4a1515; border-radius: 5px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Register Game Server</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">View Servers</a>
        </div>
        <form method="POST" action="/register">
            <label for="name">Server Name:</label>
            <input type="text" id="name" name="name" placeholder="My Awesome Server" required>
            
            <label for="address">Server Address:</label>
            <input type="text" id="address" name="address" placeholder="192.168.1.100:27015" required>
            
            <label for="info">Server Info (JSON):</label>
            <textarea id="info" name="info" placeholder='{"GameMode": "Survival", "MaxPlayers": "32"}'></textarea>
            <p class="hint">Provide server information in JSON format. This will be displayed on the server details page.</p>
            
            <input type="submit" value="Register Server">
        </form>
    </div>
</body>
</html>
"""

LGSL_SERVER_DETAILS = """
<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Server Details #{0}</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #00d4ff; text-align: center; }}
        h2 {{ color: #00d4ff; border-bottom: 1px solid #0f3460; padding-bottom: 10px; }}
        .nav {{ text-align: center; margin: 20px 0; }}
        .nav a {{ color: #00d4ff; text-decoration: none; margin: 0 15px; padding: 10px 20px; border: 1px solid #00d4ff; border-radius: 5px; }}
        .nav a:hover {{ background: #00d4ff; color: #1a1a2e; }}
        .server-info {{ background: #16213e; padding: 20px; border-radius: 10px; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #00d4ff; width: 30%; }}
        a {{ color: #00d4ff; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Server Details</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Back to List</a>
        </div>
        <div class="server-info">
            <h2>{1}</h2>
            <p><strong>Address:</strong> {2}</p>
            <h3>Server Information</h3>
            <table>
                <tr><th>Field</th><th>Value</th></tr>
                {3}
            </table>
        </div>
    </div>
</body>
</html>
"""

LGSL_SERVER_DETAILS_WITH_FLAG = """
<!DOCTYPE html>
<html>
<head>
    <title>LGSL - Server Details #{0}</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #00d4ff; text-align: center; }}
        h2 {{ color: #00d4ff; border-bottom: 1px solid #0f3460; padding-bottom: 10px; }}
        .nav {{ text-align: center; margin: 20px 0; }}
        .nav a {{ color: #00d4ff; text-decoration: none; margin: 0 15px; padding: 10px 20px; border: 1px solid #00d4ff; border-radius: 5px; }}
        .nav a:hover {{ background: #00d4ff; color: #1a1a2e; }}
        .server-info {{ background: #16213e; padding: 20px; border-radius: 10px; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #00d4ff; width: 30%; }}
        a {{ color: #00d4ff; }}
        .flag-message {{ background: #0a4a0a; border: 2px solid #00ff00; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center; }}
        .flag-message h2 {{ color: #00ff00; }}
        .flag-message code {{ background: #003300; padding: 10px 20px; font-size: 18px; display: inline-block; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Server Details</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Back to List</a>
        </div>
        {4}
        <div class="server-info">
            <h2>{1}</h2>
            <p><strong>Address:</strong> {2}</p>
            <h3>Server Information</h3>
            <table>
                <tr><th>Field</th><th>Value</th></tr>
                {3}
            </table>
        </div>
    </div>
</body>
</html>
"""
