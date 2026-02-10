INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>LGSL - Game Server List</title>
        </head>
        <body style="background: #1a1a2e; color: #eee; font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 800px; margin: 0 auto;">
                <h1>LGSL - Game Server List</h1>
                <p>A lightweight game server list application for tracking your favorite game servers.</p>
                <nav style="margin: 20px 0;">
                    <a href="/servers" style="color: #00adb5; margin-right: 20px;">View Servers</a>
                    <a href="/register" style="color: #00adb5;">Register Server</a>
                </nav>
                <hr style="border-color: #333;">
                <p style="color: #888; font-size: 12px;">LGSL v6.x - Game Server Monitoring</p>
            </div>
        </body>
    </html>
"""

SERVER_LIST_PAGE = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>LGSL - Server List</title>
        </head>
        <body style="background: #1a1a2e; color: #eee; font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 800px; margin: 0 auto;">
                <h1>Registered Game Servers</h1>
                <a href="/" style="color: #00adb5;">Back to Home</a> | 
                <a href="/register" style="color: #00adb5;">Register New Server</a>
                <table style="width: 100%; margin-top: 20px; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #16213e;">
                            <th style="padding: 10px; text-align: left; border: 1px solid #333;">Server Name</th>
                            <th style="padding: 10px; text-align: left; border: 1px solid #333;">IP</th>
                            <th style="padding: 10px; text-align: left; border: 1px solid #333;">Port</th>
                        </tr>
                    </thead>
                    <tbody>
                        {0}
                    </tbody>
                </table>
                <p style="color: #888; margin-top: 20px;">Click on a server name to view details.</p>
            </div>
        </body>
    </html>
"""

REGISTER_PAGE = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>LGSL - Register Server</title>
        </head>
        <body style="background: #1a1a2e; color: #eee; font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 800px; margin: 0 auto;">
                <h1>Register Game Server</h1>
                <a href="/" style="color: #00adb5;">Back to Home</a> | 
                <a href="/servers" style="color: #00adb5;">View Servers</a>
                
                <div style="margin-top: 20px; padding: 20px; background: #16213e; border-radius: 8px;">
                    <h3>Register via Form</h3>
                    <form method="POST" action="/register">
                        <div style="margin-bottom: 15px;">
                            <label>Server Name:</label><br>
                            <input type="text" name="name" style="width: 100%; padding: 8px; margin-top: 5px; background: #1a1a2e; border: 1px solid #333; color: #eee;">
                        </div>
                        <div style="margin-bottom: 15px;">
                            <label>IP Address:</label><br>
                            <input type="text" name="ip" style="width: 100%; padding: 8px; margin-top: 5px; background: #1a1a2e; border: 1px solid #333; color: #eee;">
                        </div>
                        <div style="margin-bottom: 15px;">
                            <label>Port:</label><br>
                            <input type="text" name="port" style="width: 100%; padding: 8px; margin-top: 5px; background: #1a1a2e; border: 1px solid #333; color: #eee;">
                        </div>
                        <div style="margin-bottom: 15px;">
                            <label>Extra Fields (JSON object for server info):</label><br>
                            <textarea name="extra_fields" rows="4" style="width: 100%; padding: 8px; margin-top: 5px; background: #1a1a2e; border: 1px solid #333; color: #eee;" placeholder='{"Players": "10/32", "Map": "de_dust2"}'></textarea>
                        </div>
                        <button type="submit" style="padding: 10px 20px; background: #00adb5; border: none; color: #fff; cursor: pointer;">Register Server</button>
                    </form>
                </div>
                
                <div style="margin-top: 20px; padding: 20px; background: #16213e; border-radius: 8px;">
                    <h3>Register via API (JSON)</h3>
                    <p>POST to <code>/register</code> with Content-Type: application/json</p>
                    <pre style="background: #1a1a2e; padding: 10px; overflow-x: auto;">
{
    "name": "My Game Server",
    "ip": "192.168.1.100",
    "port": "27015",
    "extra": {
        "Players": "10/32",
        "Map": "de_dust2",
        "GameMode": "Competitive"
    }
}
                    </pre>
                </div>
            </div>
        </body>
    </html>
"""

SERVER_DETAILS_PAGE = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>LGSL - Server Details: {0}</title>
        </head>
        <body style="background: #1a1a2e; color: #eee; font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 800px; margin: 0 auto;">
                <h1>Server Details</h1>
                <a href="/" style="color: #00adb5;">Back to Home</a> | 
                <a href="/servers" style="color: #00adb5;">View All Servers</a>
                
                <div style="margin-top: 20px; padding: 20px; background: #16213e; border-radius: 8px;">
                    <h2>{0}</h2>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; border: 1px solid #333; width: 150px;"><strong>IP Address</strong></td>
                            <td style="padding: 10px; border: 1px solid #333;">{1}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #333;"><strong>Port</strong></td>
                            <td style="padding: 10px; border: 1px solid #333;">{2}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="margin-top: 20px; padding: 20px; background: #16213e; border-radius: 8px;">
                    <h3>Server Information</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        {3}
                    </table>
                </div>
            </div>
        </body>
    </html>
"""

VERIFICATION_SUCCESS = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <title>LGSL - Verification Success</title>
        </head>
        <body style="background: #1a1a2e; color: #eee; font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 800px; margin: 0 auto; text-align: center;">
                <h1 style="color: #00ff00;">XSS Verified!</h1>
                <p>The stored XSS vulnerability was successfully exploited.</p>
                <div style="background: #16213e; padding: 20px; border-radius: 8px; margin-top: 20px;">
                    <p>Flag: <code style="color: #00adb5; font-size: 18px;">{0}</code></p>
                </div>
                <a href="/" style="color: #00adb5; margin-top: 20px; display: inline-block;">Back to Home</a>
            </div>
        </body>
    </html>
"""

VERIFICATION_PARTIAL = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <title>LGSL - Verification Partial</title>
        </head>
        <body style="background: #1a1a2e; color: #eee; font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 800px; margin: 0 auto; text-align: center;">
                <h1 style="color: #ffa500;">Almost There!</h1>
                <p>An alert was triggered, but with the wrong message: <code>{0}</code></p>
                <p>Expected: <code>XSS</code></p>
                <a href="/" style="color: #00adb5; margin-top: 20px; display: inline-block;">Back to Home</a>
            </div>
        </body>
    </html>
"""

VERIFICATION_FAILED = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <title>LGSL - Verification Failed</title>
        </head>
        <body style="background: #1a1a2e; color: #eee; font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 800px; margin: 0 auto; text-align: center;">
                <h1 style="color: #ff0000;">Verification Failed</h1>
                <p>No XSS alert was detected. Make sure your payload triggers: <code>alert('XSS')</code></p>
                <a href="/" style="color: #00adb5; margin-top: 20px; display: inline-block;">Back to Home</a>
            </div>
        </body>
    </html>
"""

# Legacy templates (kept for compatibility but not used)
XSS_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>s
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
