INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>LGSL - Game Server Directory</title>
        </head>
        <body style="background-color: #1a1a2e; color: #eee; font-family: Arial, sans-serif;">
            <article class="widget widget__login">
            <div class="widget__content">
                <div class="box">
                    <div class="box-form" style="text-align: center; padding: 20px;">
                        <img class="text-img" src="static/img/logo5_white.png">
                        <h1>LGSL - Game Server Directory</h1>
                        <p>Live Game Server List - Browse and register game servers</p>
                        <div class="init-table">
                            <div class="row">
                                <div class="column">
                                    <a class="text" href="/servers">
                                        <img src="static/img/cookies/new_star.png" alt="Servers" width="150" height="150">
                                        <br>Browse Servers
                                    </a>
                                </div>
                                <div class="column">
                                    <a class="text" href="/register">
                                        <img src="static/img/cookies/new_triangle.png" alt="Register" width="150" height="150">
                                        <br>Register Server
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
    </html>
"""

SERVER_LIST_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>LGSL - Server List</title>
            <style>
                body {{ background-color: #1a1a2e; color: #eee; font-family: Arial, sans-serif; }}
                .container {{ max-width: 800px; margin: 50px auto; padding: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; border: 1px solid #444; text-align: left; }}
                th {{ background-color: #16213e; }}
                a {{ color: #4fc3f7; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                .btn {{ display: inline-block; padding: 10px 20px; background-color: #4fc3f7; color: #000; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Game Server List</h1>
                <p><a href="/" class="btn">Home</a> <a href="/register" class="btn">Register New Server</a></p>
                <table>
                    <tr><th>Server Name</th><th>URL</th></tr>
                    {0}
                </table>
            </div>
        </body>
    </html>
"""

REGISTER_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>LGSL - Register Server</title>
            <style>
                body { background-color: #1a1a2e; color: #eee; font-family: Arial, sans-serif; }
                .container { max-width: 600px; margin: 50px auto; padding: 20px; }
                input[type="text"], input[type="url"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #444; background-color: #16213e; color: #eee; }
                textarea { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #444; background-color: #16213e; color: #eee; height: 100px; }
                .btn { display: inline-block; padding: 10px 20px; background-color: #4fc3f7; color: #000; border: none; border-radius: 5px; cursor: pointer; }
                .btn:hover { background-color: #29b6f6; }
                a { color: #4fc3f7; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Register Game Server</h1>
                <p><a href="/">Home</a> | <a href="/servers">Server List</a></p>
                
                <h2>Option 1: Register by URL</h2>
                <p>Provide a URL to your server's /info endpoint (returns JSON)</p>
                <form method="POST" action="/register">
                    <input type="text" name="name" placeholder="Server Name (e.g., My Game Server)">
                    <input type="url" name="url" placeholder="Server Info URL (e.g., http://gameserver.com/info)">
                    <button type="submit" class="btn">Fetch & Register</button>
                </form>
                
                <hr style="margin: 30px 0; border-color: #444;">
                
                <h2>Option 2: Direct Submit</h2>
                <p>Directly submit server data as JSON</p>
                <form method="POST" action="/add_server">
                    <input type="text" name="name" placeholder="Server Name">
                    <textarea name="data" placeholder='{"Players": "24/32", "Map": "de_dust2", "GameMode": "Competitive"}'></textarea>
                    <button type="submit" class="btn">Submit Server Data</button>
                </form>
            </div>
        </body>
    </html>
"""

SERVER_DETAILS_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>LGSL - Server Details</title>
            <style>
                body {{ background-color: #1a1a2e; color: #eee; font-family: Arial, sans-serif; }}
                .container {{ max-width: 800px; margin: 50px auto; padding: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; border: 1px solid #444; text-align: left; }}
                th {{ background-color: #16213e; }}
                a {{ color: #4fc3f7; text-decoration: none; }}
                .btn {{ display: inline-block; padding: 10px 20px; background-color: #4fc3f7; color: #000; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Server Details: {0}</h1>
                <p>Source URL: {1}</p>
                <p><a href="/" class="btn">Home</a> <a href="/servers" class="btn">Back to List</a></p>
                
                <h2>Server Information</h2>
                <table>
                    <tr><th>Field</th><th>Value</th></tr>
                    {2}
                </table>
            </div>
        </body>
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
