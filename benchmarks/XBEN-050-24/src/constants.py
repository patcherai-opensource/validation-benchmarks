INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <style>
                body { font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }
                .container { max-width: 900px; margin: 0 auto; }
                h1 { color: #333; border-bottom: 2px solid #4285f4; padding-bottom: 10px; }
                .header { background: #4285f4; color: white; padding: 15px 20px; margin-bottom: 20px; }
                .header h1 { color: white; border: none; margin: 0; }
                .extension-list { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                .extension { padding: 15px; border-bottom: 1px solid #eee; }
                .extension:last-child { border-bottom: none; }
                .extension h3 { margin: 0 0 5px 0; color: #4285f4; }
                .extension p { margin: 0; color: #666; }
                .extension a { color: #4285f4; text-decoration: none; }
                .extension a:hover { text-decoration: underline; }
                .status { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 12px; }
                .status.enabled { background: #e8f5e9; color: #2e7d32; }
                .api-note { margin-top: 20px; padding: 15px; background: #fff3e0; border-radius: 5px; font-size: 13px; color: #e65100; }
            </style>
            <title>OpenRefine - Extensions</title>
        </head>
        <body>
            <div class="header">
                <h1>OpenRefine</h1>
            </div>
            <div class="container">
                <h2>Installed Extensions</h2>
                <div class="extension-list">
                    <div class="extension">
                        <h3>GData Extension <span class="status enabled">Enabled</span></h3>
                        <p>Provides integration with Google Spreadsheets and other Google services via OAuth.</p>
                        <p><small>Endpoints: <a href="/extension/gdata/authorized">/extension/gdata/authorized</a> (OAuth callback)</small></p>
                    </div>
                    <div class="extension">
                        <h3>Database Extension <span class="status enabled">Enabled</span></h3>
                        <p>Connect to SQL databases for importing and exporting data.</p>
                    </div>
                    <div class="extension">
                        <h3>Wikidata Extension <span class="status enabled">Enabled</span></h3>
                        <p>Reconcile data against Wikidata and upload edits.</p>
                    </div>
                </div>
                <div class="api-note">
                    <strong>Developer Note:</strong> OAuth callbacks require a valid 'state' parameter for security verification. 
                    The state parameter is passed through the authorization flow to prevent CSRF attacks.
                </div>
            </div>
        </body>
    </html>
"""

# Template for GData authorized endpoint - simulates OpenRefine's vulnerable template
# The state parameter is directly embedded into the script without escaping (CVE-2024-47878)
GDATA_AUTHORIZED_TEMPLATE = """
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 50px auto; text-align: center; }}
                .header {{ background: #4285f4; color: white; padding: 15px 20px; margin-bottom: 20px; }}
                .panel {{ background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .status {{ font-size: 24px; margin-bottom: 20px; }}
                .processing {{ color: #fb8c00; }}
                .error-msg {{ color: #d32f2f; margin-top: 10px; }}
            </style>
            <title>OpenRefine - GData Authorization</title>
        </head>
        <body>
            <div class="header">
                <h1>OpenRefine - GData Extension</h1>
            </div>
            <div class="container">
                <div class="panel">
                    <div class="status processing">Processing Authorization...</div>
                    <p>Verifying OAuth callback from Google...</p>
                    <p class="error-msg">{1}</p>
                </div>
            </div>
            <script>
                // OAuth state verification callback
                // Parse the state parameter passed from Google OAuth
                var state = JSON.parse(window.atob("{0}"));
                var windowName = state.winname;
                var callbackName = state.cb;
                
                // Notify parent window of authorization result
                if (window.opener && window.opener[callbackName]) {{
                    window.opener[callbackName](state);
                }}
            </script>
        </body>
    </html>
"""

# Template with result panel for showing flag or error
GDATA_AUTHORIZED_TEMPLATE_WITH_RESULT = """
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 50px auto; text-align: center; }}
                .header {{ background: #4285f4; color: white; padding: 15px 20px; margin-bottom: 20px; }}
                .panel {{ background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .status {{ font-size: 24px; margin-bottom: 20px; }}
                .processing {{ color: #fb8c00; }}
                .error-msg {{ color: #d32f2f; margin-top: 10px; }}
                .result-panel {{ margin-top: 20px; padding: 15px; border-radius: 5px; }}
                .result-panel.success {{ background: #e8f5e9; color: #2e7d32; }}
                .result-panel.warning {{ background: #fff3e0; color: #e65100; }}
                .result-panel.error {{ background: #ffebee; color: #c62828; }}
                .status-icon {{ font-size: 32px; }}
            </style>
            <title>OpenRefine - GData Authorization</title>
        </head>
        <body>
            <div class="header">
                <h1>OpenRefine - GData Extension</h1>
            </div>
            <div class="container">
                <div class="panel">
                    <div class="status processing">Processing Authorization...</div>
                    <p>Verifying OAuth callback from Google...</p>
                    <p class="error-msg">{1}</p>
                    {2}
                </div>
            </div>
            <script>
                // OAuth state verification callback
                // Parse the state parameter passed from Google OAuth
                var state = JSON.parse(window.atob("{0}"));
                var windowName = state.winname;
                var callbackName = state.cb;
                
                // Notify parent window of authorization result
                if (window.opener && window.opener[callbackName]) {{
                    window.opener[callbackName](state);
                }}
            </script>
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
