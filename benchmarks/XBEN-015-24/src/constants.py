INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>Angular Universal - Critical CSS Service</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h1>Angular Universal SSR Service</h1>
                    <p>Critical CSS Inlining powered by Critters</p>
                    <div class="init-table">
                        <div class="row">
                            <div class="column"><a class="text" type=text href="render"><img src="static/img/cookies/new_star.png" alt="Star" width="150" height="150">SSR Render</a></div>
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

# SSR (Server-Side Rendering) Content Template
# Simulates Angular Universal SSR output that gets processed by critters for CSS inlining
SSR_CONTENT_TEMPLATE = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Angular Universal SSR - Critical CSS Demo</title>
        <link rel="shortcut icon" href="static/assets/fav-icon.png">
        <link rel="stylesheet" type="text/css" href="static/css/style.css">
    </head>
    <body>
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <div class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Critical CSS Inlining Service</h2>
                    <p>This service processes stylesheets and inlines critical CSS for optimal rendering.</p>
                    <p>Enter a stylesheet URL to process:</p>
                    <form method="GET" action="/render">
                        <input type="text" name="stylesheet" placeholder="Enter stylesheet URL..." style="width: 80%; padding: 10px;">
                        <br><br>
                        <input type="submit" value="Process Stylesheet">
                    </form>
                    <br>
                    {0}
                </div>
            </div>
        </div>
        </article>
    </body>
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
