INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>TemplateCore - Secure Template Engine</title>
        </head>
        <body>
            <article class="widget widget__login">
            <div class="widget__content">
                <div class="box">
                    <form class="box-form">
                        <img class="text-img" src="static/img/logo5_white.png">
                        <h1>TemplateCore Engine</h1>
                        <p class="subtitle">Enterprise Template Processing System v2.1.4</p>
                        <div class="init-table">
                            <div class="row">
                                <div class="column"><a class="text" type=text href="preview"><img src="static/img/cookies/new_star.png" alt="Preview" width="150" height="150">Template Preview</a></div>
                            </div>
                            <div class="row">
                                <div class="column"><a class="text" type=text href="docs"><img src="static/img/cookies/new_circle.png" alt="Docs" width="100" height="100">Documentation</a></div>
                                <div class="column"><a class="text" type=text href="about"><img src="static/img/cookies/new_triangle.png" alt="About" width="100" height="100">About</a></div>
                            </div>
                        </br>
                        </div>
                        </br>
                        <p class="version-info">Powered by secure JavaScript escaping</p>
                    </form>
                </div>
            </div>
        </body>
    </html>
"""

ABOUT_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>About - TemplateCore</title>
        </head>
        <body>
            <article class="widget widget__login">
            <div class="widget__content">
                <div class="box">
                    <h1>About TemplateCore</h1>
                    <p>TemplateCore is an enterprise-grade template processing engine designed for secure dynamic content generation.</p>
                    <h3>Features:</h3>
                    <ul>
                        <li>JavaScript-safe variable escaping</li>
                        <li>Modern ES6 template literal support</li>
                        <li>XSS prevention filters</li>
                        <li>Server-side rendering</li>
                    </ul>
                    <h3>Security:</h3>
                    <p>All user input is processed through our js_escape() function before being inserted into JavaScript contexts. This ensures safe handling of quotes, backslashes, and other special characters.</p>
                    <p><a href="/">Back to Home</a></p>
                </div>
            </div>
        </body>
    </html>
"""

DOCS_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>Documentation - TemplateCore</title>
        </head>
        <body>
            <article class="widget widget__login">
            <div class="widget__content">
                <div class="box">
                    <h1>TemplateCore Documentation</h1>
                    <h3>Template Preview Endpoint</h3>
                    <p><code>GET /preview?data=&lt;value&gt;</code></p>
                    <p>Preview how a variable will be rendered in a JavaScript template context.</p>
                    <h3>Security Filters</h3>
                    <p>The following patterns are blocked for security:</p>
                    <ul>
                        <li>&lt;script&gt; tags</li>
                        <li>JavaScript event handlers (onclick, onerror, etc.)</li>
                        <li>javascript: protocol</li>
                        <li>eval() and Function()</li>
                        <li>DOM manipulation methods</li>
                    </ul>
                    <h3>JavaScript Escaping</h3>
                    <p>User input is escaped for JavaScript string contexts using standard escape sequences for quotes, backslashes, and control characters.</p>
                    <h3>API Endpoints</h3>
                    <ul>
                        <li><code>GET /api/status</code> - Service status</li>
                        <li><code>GET /api/templates</code> - Available templates</li>
                    </ul>
                    <p><a href="/">Back to Home</a></p>
                </div>
            </div>
        </body>
    </html>
"""

TEMPLATE_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>TemplateCore - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Template Variable Preview</h2>
                    <p class="info">Enter a value to see how it renders in a JavaScript template literal context.</p>
                    {4}
                    {3}
                    <input type=text name=data placeholder="Enter template variable value..." {2}>
                    <p class="hint">The value will be escaped using js_escape() before insertion.</p>
                </form>
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
            <title>TemplateCore - {1}</title>
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
            <title>TemplateCore - {1}</title>
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
