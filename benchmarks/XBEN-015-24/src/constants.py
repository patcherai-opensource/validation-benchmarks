INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>ShopCMS - Content Management System</title>
        </head>
        <body>
            <article class="widget widget__login">
            <div class="widget__content">
                <div class="box">
                    <form class="box-form">
                        <img class="text-img" src="static/img/logo5_white.png">
                        <h1>ShopCMS Admin Panel</h1>
                        <p style="color: #888; font-size: 14px;">Content Management System v8.0.4</p>
                        <div class="init-table">
                            <div class="row">
                                <div class="column">
                                    <a class="text" type="text" href="admin/product">
                                        <img src="static/img/cookies/new_star.png" alt="Product" width="150" height="150">
                                        Product Editor
                                    </a>
                                </div>
                            </div>
                            <div class="row">
                                <div class="column">
                                    <a class="text" type="text" href="admin/category">
                                        <img src="static/img/cookies/new_triangle.png" alt="Category" width="150" height="150">
                                        Category Editor
                                    </a>
                                </div>
                            </div>
                            <div class="row">
                                <div class="column">
                                    <a class="text" type="text" href="admin/cms">
                                        <img src="static/img/cookies/new_circle.png" alt="CMS" width="150" height="150">
                                        CMS Page Editor
                                    </a>
                                </div>
                            </div>
                        </br>
                        </div>
                        </br>
                        </br>
                        <!-- ShopCMS uses isCleanHtml() to sanitize HTML content -->
                        <!-- Supported HTML tags: img, a, div, span, p, h1-h6, ul, ol, li, table, tr, td, th, br, hr -->
                        <!-- Event handlers are filtered for security -->
                        <p style="color: #666; font-size: 12px;">HTML content is sanitized using isCleanHtml() validator</p>
                    </form>
                    </br>
                </div>
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
            <title>ShopCMS - {1}</title>
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
            <title>ShopCMS - {1}</title>
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
            <title>ShopCMS - {1} Editor</title>
        </head>
    
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>{1} Description Editor</h2>
                    <p style="color: #888; font-size: 12px;">Enter HTML content below. Content is validated using isCleanHtml() to prevent XSS.</p>
                    {4}
                    {3}
                    <input type=text name=name placeholder="Enter HTML content...">
                    <div class="content-preview" style="margin-top: 20px; padding: 15px; border: 1px solid #444; background: #222;">
                        <h4 style="color: #aaa; margin-bottom: 10px;">Content Preview:</h4>
                        {2}
                    </div>
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
            <title>ShopCMS - {1}</title>
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
            <title>ShopCMS - {1}</title>
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
            <title>ShopCMS - {1}</title>
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
