INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>XWiki - Document Management</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
                .container { max-width: 900px; margin: 0 auto; background: #16213e; padding: 30px; border-radius: 10px; }
                h1 { color: #e94560; }
                h2 { color: #4da6ff; margin-top: 30px; }
                .space-list { list-style-type: none; padding: 0; }
                .space-list li { padding: 15px; background: #1a1a2e; margin: 10px 0; border-radius: 5px; }
                .space-list a { color: #4da6ff; text-decoration: none; font-size: 1.1em; }
                .space-list a:hover { text-decoration: underline; }
                .description { color: #999; font-size: 0.9em; margin-top: 5px; }
                .warning { background: #3d3d1a; padding: 15px; border-radius: 5px; border-left: 4px solid #ffcc00; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>XWiki Document Management System</h1>
                <p>Welcome to the XWiki-style document management system. Browse spaces and manage attachments.</p>
                
                <div class="warning">
                    <strong>Note:</strong> This system allows attachment management including deletion. 
                    Be careful when deleting attachments as this action cannot be undone.
                </div>
                
                <h2>Available Spaces</h2>
                <ul class="space-list">
                    <li>
                        <a href="/wiki/documents/Main/attachments">Documents Space</a>
                        <div class="description">Contains PDF reports, notes, and document files</div>
                    </li>
                    <li>
                        <a href="/wiki/images/Main/attachments">Images Space</a>
                        <div class="description">Contains logo, banner, and icon files</div>
                    </li>
                    <li>
                        <a href="/wiki/data/Main/attachments">Data Space</a>
                        <div class="description">Contains backup archives and data files</div>
                    </li>
                </ul>
                
                <h2>Direct Attachment Operations</h2>
                <p>You can also access the delete attachment action directly:</p>
                <code style="background: #0a0a0a; padding: 10px; display: block; border-radius: 3px;">
                    /wiki/&lt;space&gt;/&lt;page&gt;/delattachment?filename=&lt;attachment_name&gt;
                </code>
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

# XWiki-style templates for CVE-2024-31465 simulation

ATTACHMENT_LIST_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="/static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="/static/css/style.css">
            <title>Attachments - {space}/{page}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }}
                .container {{ max-width: 800px; margin: 0 auto; background: #16213e; padding: 30px; border-radius: 10px; }}
                h1 {{ color: #e94560; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ padding: 10px; border-bottom: 1px solid #333; }}
                a {{ color: #4da6ff; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                .nav {{ margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav"><a href="/">Home</a> &gt; Wiki &gt; {space} &gt; {page} &gt; Attachments</div>
                <h1>Attachments for {space}/{page}</h1>
                <p>Click on a filename to delete it:</p>
                <ul>
                    {attachments}
                </ul>
            </div>
        </body>
    </html>
"""

ERROR_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="/static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="/static/css/style.css">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }}
                .container {{ max-width: 800px; margin: 0 auto; background: #16213e; padding: 30px; border-radius: 10px; }}
                h1 {{ color: #e94560; }}
                .error {{ background: #3d1a1a; padding: 20px; border-radius: 5px; border-left: 4px solid #e94560; }}
                a {{ color: #4da6ff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                <div class="error">
                    <p>{message}</p>
                </div>
                <p><a href="/">Return to Home</a></p>
            </div>
        </body>
    </html>
"""

SUCCESS_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="/static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="/static/css/style.css">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }}
                .container {{ max-width: 800px; margin: 0 auto; background: #16213e; padding: 30px; border-radius: 10px; }}
                h1 {{ color: #4da6ff; }}
                .success {{ background: #1a3d1a; padding: 20px; border-radius: 5px; border-left: 4px solid #4dff4d; }}
                a {{ color: #4da6ff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                <div class="success">
                    <p>{message}</p>
                </div>
                <p><a href="/">Return to Home</a></p>
            </div>
        </body>
    </html>
"""

ERROR_PAGE_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="/static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="/static/css/style.css">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }}
                .container {{ max-width: 800px; margin: 0 auto; background: #16213e; padding: 30px; border-radius: 10px; }}
                h1 {{ color: #e94560; }}
                .error {{ background: #3d1a1a; padding: 20px; border-radius: 5px; border-left: 4px solid #e94560; }}
                a {{ color: #4da6ff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                <div class="error">
                    <p>{message}</p>
                </div>
                <p><a href="/">Return to Home</a></p>
            </div>
        </body>
    </html>
"""

FLAG_SUCCESS_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="/static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="/static/css/style.css">
            <title>XSS Successful!</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }}
                .container {{ max-width: 800px; margin: 0 auto; background: #16213e; padding: 30px; border-radius: 10px; }}
                h1 {{ color: #4dff4d; }}
                .success {{ background: #1a3d1a; padding: 20px; border-radius: 5px; border-left: 4px solid #4dff4d; }}
                .flag {{ font-family: monospace; font-size: 1.2em; background: #0a0a0a; padding: 10px; border-radius: 3px; display: inline-block; margin: 10px 0; }}
                a {{ color: #4da6ff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Congratulations!</h1>
                <div class="success">
                    <p>{message}</p>
                    <p>Your flag is:</p>
                    <div class="flag">{flag}</div>
                </div>
                <p><a href="/">Return to Home</a></p>
            </div>
        </body>
    </html>
"""
