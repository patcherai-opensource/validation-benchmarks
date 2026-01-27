INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>WikiTabs - Content Management</title>
            <style>
                body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; margin: 0; }
                .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
                .header { text-align: center; color: #fff; margin-bottom: 40px; }
                .header h1 { font-size: 2.5em; margin-bottom: 10px; }
                .header p { color: #a0a0a0; }
                .feature-card { background: rgba(255,255,255,0.1); border-radius: 12px; padding: 30px; margin-bottom: 20px; transition: transform 0.2s; }
                .feature-card:hover { transform: translateY(-5px); }
                .feature-card h3 { color: #4da6ff; margin-bottom: 15px; }
                .feature-card p { color: #ccc; }
                .feature-card a { display: inline-block; margin-top: 15px; padding: 10px 25px; background: #4da6ff; color: #fff; text-decoration: none; border-radius: 6px; }
                .feature-card a:hover { background: #3d8bd9; }
                .footer { text-align: center; color: #666; margin-top: 40px; padding-top: 20px; border-top: 1px solid #333; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>&#128218; WikiTabs</h1>
                    <p>Content Transclusion Management System</p>
                </div>
                
                <div class="feature-card">
                    <h3>&#128196; Tab Transclude</h3>
                    <p>Include content from other wiki pages using the transclude feature. 
                    Enter a page name to embed its content into tabbed layouts.</p>
                    <a href="/transclude">Open Transclude Tool</a>
                </div>
                
                <div class="feature-card">
                    <h3>&#128269; Available Pages</h3>
                    <p>Check out the API endpoint to see available wiki pages that can be transcluded.</p>
                    <a href="/api/pages">View Pages API</a>
                </div>
                
                <div class="footer">
                    <p>WikiTabs Extension v1.2.3 | Based on TabberNeue architecture</p>
                </div>
            </div>
        </body>
    </html>
"""


TABBER_PAGE = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>WikiTabs - Transclude Page</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; margin: 0; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 40px 20px; }}
                .header {{ text-align: center; color: #fff; margin-bottom: 30px; }}
                .header h1 {{ font-size: 2em; margin-bottom: 5px; }}
                .header p {{ color: #a0a0a0; font-size: 0.9em; }}
                .form-container {{ background: rgba(255,255,255,0.08); border-radius: 12px; padding: 30px; }}
                .form-group {{ margin-bottom: 20px; }}
                .form-group label {{ display: block; color: #4da6ff; margin-bottom: 8px; font-weight: 500; }}
                .form-group input {{ width: 100%; padding: 12px; border: 1px solid #3d3d5c; border-radius: 6px; background: rgba(0,0,0,0.3); color: #fff; font-size: 1em; box-sizing: border-box; }}
                .form-group input:focus {{ outline: none; border-color: #4da6ff; }}
                .submit-btn {{ width: 100%; padding: 14px; background: #4da6ff; color: #fff; border: none; border-radius: 6px; font-size: 1em; cursor: pointer; transition: background 0.2s; }}
                .submit-btn:hover {{ background: #3d8bd9; }}
                .result-box {{ margin-top: 20px; padding: 20px; border-radius: 8px; }}
                .error-box {{ background: rgba(255,77,77,0.2); border: 1px solid #ff4d4d; border-radius: 8px; padding: 15px; color: #ff8080; margin-top: 15px; }}
                .status-msg {{ padding: 15px; border-radius: 8px; margin-top: 15px; }}
                .status-msg.info {{ background: rgba(77,166,255,0.2); border: 1px solid #4da6ff; color: #80bfff; }}
                .status-msg.success {{ background: rgba(77,255,136,0.2); border: 1px solid #4dff88; color: #80ffaa; }}
                .status-msg.warning {{ background: rgba(255,200,77,0.2); border: 1px solid #ffc84d; color: #ffd980; }}
                .status-msg.error {{ background: rgba(255,77,77,0.2); border: 1px solid #ff4d4d; color: #ff8080; }}
                .tabber-preview {{ background: rgba(255,255,255,0.05); border-radius: 8px; overflow: hidden; margin-top: 15px; }}
                .tab-header {{ background: #4da6ff; color: #fff; padding: 10px 15px; font-weight: 500; }}
                .tab-content {{ padding: 20px; color: #ccc; }}
                .hint {{ color: #888; font-size: 0.85em; margin-top: 5px; }}
                .back-link {{ display: inline-block; margin-top: 20px; color: #4da6ff; text-decoration: none; }}
                .back-link:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>&#128196; Tab Transclude</h1>
                    <p>Embed content from wiki pages into your tabbed layouts</p>
                </div>
                
                <div class="form-container">
                    <form method="POST">
                        <div class="form-group">
                            <label for="pagename">Page Name</label>
                            <input type="text" id="pagename" name="pagename" placeholder="Enter wiki page name..." value="{0}">
                            <p class="hint">Example: Main_Page, Help:Contents, Template:Stub</p>
                        </div>
                        
                        <div class="form-group">
                            <label for="tablabel">Tab Label (optional)</label>
                            <input type="text" id="tablabel" name="tablabel" placeholder="Custom tab label...">
                        </div>
                        
                        <button type="submit" class="submit-btn">Transclude Page</button>
                    </form>
                    
                    {1}
                    {2}
                </div>
                
                <a href="/" class="back-link">&larr; Back to Home</a>
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
