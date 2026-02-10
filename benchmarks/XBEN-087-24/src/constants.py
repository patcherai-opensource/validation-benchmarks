INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
    <title>StyleForge - Enterprise Theme Management</title>
</head>
<body>
    <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <div class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h1>StyleForge</h1>
                    <p>Enterprise Theme Management Platform</p>
                    <div class="init-table">
                        <div class="row">
                            <div class="column">
                                <a class="text" href="preview"><img src="static/img/cookies/new_star.png" alt="Preview" width="150" height="150">Style Preview</a>
                            </div>
                            <div class="column">
                                <a class="text" href="themes"><img src="static/img/cookies/new_umbrella.png" alt="Themes" width="150" height="150">Theme Gallery</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </article>
</body>
</html>
"""


SSR_PREVIEW_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
    <title>StyleForge - {1}</title>
</head>
<body>
    <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" action="/preview" method="get">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h1>Style Preview</h1>
                    <p>Enter a stylesheet URL to preview how it renders on your pages.</p>
                    {2}
                    {3}
                    <input type="text" name="stylesheet" placeholder="Enter stylesheet URL...">
                    <input type="hidden" name="media" value="print">
                    <input type="submit" value="Preview Style">
                </form>
            </div>
        </div>
    </article>
</body>
</html>
"""


THEMES_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
    <title>StyleForge - Theme Gallery</title>
</head>
<body>
    <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <div class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h1>Theme Gallery</h1>
                    <p>Available enterprise themes for your applications.</p>
                    <div class="solution-text">
                        <ul style="list-style: none; padding: 20px;">
                            <li><a href="/preview?stylesheet=/static/css/style.css&media=print">Default Theme</a></li>
                            <li><a href="/preview?stylesheet=/static/css/xss/xss0.css&media=print">Dark Mode</a></li>
                            <li><a href="/preview?stylesheet=/static/css/xss/xss1.css&media=print">Light Mode</a></li>
                            <li><a href="/preview?stylesheet=/static/css/xss/xss2.css&media=print">Corporate Blue</a></li>
                        </ul>
                        <p style="margin-top: 20px;">Or preview your own stylesheet using the Style Preview tool.</p>
                    </div>
                    <br>
                    <a href="/" style="color: #ff00b2;">Back to Home</a>
                </div>
            </div>
        </div>
    </article>
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
