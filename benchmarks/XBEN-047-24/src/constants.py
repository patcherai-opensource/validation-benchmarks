INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>DCL SSO Client - Administration Portal</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 40px; }
                .header h1 { color: #4fc3f7; margin-bottom: 10px; }
                .header p { color: #888; }
                .card { background: #16213e; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
                .card h2 { color: #4fc3f7; margin-top: 0; }
                .api-endpoint { background: #0f3460; padding: 15px; border-radius: 4px; margin: 10px 0; font-family: monospace; }
                .method { color: #4caf50; font-weight: bold; }
                .path { color: #ff9800; }
                .param { color: #e91e63; }
                a { color: #4fc3f7; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .warning { background: #3d1c1c; border-left: 4px solid #f44336; padding: 10px 15px; margin: 15px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>&#128274; DCL Single Sign-On Client</h1>
                    <p>Administration Portal v0.0.9</p>
                </div>
                
                <div class="card">
                    <h2>API Documentation</h2>
                    <p>The SSO Client library provides secure authentication integration with identity providers.</p>
                    
                    <div class="api-endpoint">
                        <span class="method">GET</span> <span class="path">/api/sso/init</span>?<span class="param">src</span>=&lt;provider_url&gt;
                        <br><br>
                        <small>Initialize the SSO iframe with the specified identity provider URL.</small>
                    </div>
                    
                    <div class="api-endpoint">
                        <span class="method">GET</span> <span class="path">/api/sso/status</span>
                        <br><br>
                        <small>Check current SSO initialization status.</small>
                    </div>
                    
                    <div class="api-endpoint">
                        <span class="method">GET</span> <span class="path">/api/sso/callback</span>
                        <br><br>
                        <small>SSO callback endpoint for handling provider responses.</small>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Quick Start</h2>
                    <p>Initialize the SSO client by calling the init endpoint with your provider URL:</p>
                    <div class="api-endpoint">
                        <a href="/api/sso/init?src=https://example.com/sso">/api/sso/init?src=https://example.com/sso</a>
                    </div>
                </div>
                
                <div class="warning">
                    <strong>Security Notice:</strong> Only HTTPS URLs should be used for SSO initialization. 
                    The init endpoint performs URL validation to prevent protocol-based attacks.
                </div>
                
                <div class="card">
                    <h2>Version Info</h2>
                    <p>@dcl/single-sign-on-client: 0.0.9 (pre-release)</p>
                    <p>Status: Development - URL validation pending review</p>
                </div>
            </div>
        </body>
    </html>
"""


SSO_INIT_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>DCL SSO Client - Initialize</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
                .container { max-width: 600px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 30px; }
                .header h1 { color: #4fc3f7; margin-bottom: 10px; }
                .sso-box { background: #16213e; border-radius: 8px; padding: 25px; }
                .sso-box h2 { color: #4fc3f7; margin-top: 0; }
                .sso-status { padding: 15px; border-radius: 4px; margin: 15px 0; background: #0f3460; }
                .status-icon { margin-right: 10px; }
                .status-icon.pending { color: #ff9800; }
                .status-icon.success { color: #4caf50; }
                .status-icon.error { color: #f44336; }
                .status-icon.warning { color: #ff9800; }
                .input-group { margin: 15px 0; }
                .input-group label { display: block; margin-bottom: 5px; color: #888; }
                .input-group input { width: 100%; padding: 10px; border: 1px solid #0f3460; background: #0d1b36; color: #eee; border-radius: 4px; font-family: monospace; box-sizing: border-box; }
                .iframe-container { margin-top: 20px; border: 1px dashed #0f3460; padding: 10px; border-radius: 4px; min-height: 50px; }
                .back-link { display: block; margin-top: 20px; color: #4fc3f7; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>&#128274; SSO Provider Initialization</h1>
                </div>
                
                <div class="sso-box">
                    <h2>Configure Identity Provider</h2>
                    
                    <form method="GET" action="/api/sso/init">
                        <div class="input-group">
                            <label for="src">Provider URL (src)</label>
                            <input type="text" id="src" name="src" placeholder="https://auth.example.com/sso">
                        </div>
                        <button type="submit" style="background:#4fc3f7;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;">Initialize SSO</button>
                    </form>
                    
                    {1}
                    
                    <div class="iframe-container">
                        <small style="color:#666;">SSO Provider Frame:</small>
                        <iframe {0}></iframe>
                    </div>
                </div>
                
                <a href="/" class="back-link">&larr; Back to Portal</a>
            </div>
            {2}
        </body>
    </html>
"""


# Legacy templates kept for compatibility
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
