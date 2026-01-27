INDEX_CONTENT = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <link rel="shortcut icon" href="static/assets/fav-icon.png">
        <link rel="stylesheet" type="text/css" href="static/css/style.css">
        <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
        <title>GTemplate Preview Service</title>
        <style>
            .feature-box { background: #2a2a2a; padding: 20px; margin: 10px; border-radius: 8px; }
            .feature-box h3 { color: #4CAF50; }
            .feature-box p { color: #ccc; font-size: 14px; }
            .api-section { text-align: left; margin-top: 20px; }
            code { background: #1a1a1a; padding: 2px 6px; border-radius: 4px; color: #f5a623; }
        </style>
    </head>
    <body>
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <div class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h1>GTemplate Preview Service</h1>
                    <p style="color:#aaa;">A lightweight HTML template rendering engine with built-in XSS protection</p>
                    
                    <div class="feature-box">
                        <h3>Link Preview API</h3>
                        <p>Generate preview links from your content safely.</p>
                        <div class="api-section">
                            <p><strong>Endpoint:</strong> <code>GET /render</code></p>
                            <p><strong>Parameters:</strong></p>
                            <ul style="text-align:left;color:#ccc;">
                                <li><code>content</code> - The URL or content to link to</li>
                                <li><code>title</code> - Optional page title (default: "Preview")</li>
                            </ul>
                            <p><strong>Example:</strong> <code>/render?content=https://example.com</code></p>
                        </div>
                    </div>
                    
                    <div class="feature-box">
                        <h3>Security Features</h3>
                        <p>Our template engine escapes dangerous HTML characters to prevent XSS:</p>
                        <ul style="text-align:left;color:#ccc;">
                            <li><code>&lt;</code> becomes <code>&amp;lt;</code></li>
                            <li><code>&gt;</code> becomes <code>&amp;gt;</code></li>
                            <li><code>&amp;</code> becomes <code>&amp;amp;</code></li>
                        </ul>
                        <p style="color:#888;font-size:12px;margin-top:10px;">Your content is safely embedded in anchor href attributes.</p>
                    </div>
                    
                    <p style="margin-top:20px;"><a href="/render" style="color:#4CAF50;">Try the Link Preview &rarr;</a></p>
                </div>
            </div>
        </div>
    </body>
</html>
"""


RENDER_TEMPLATE = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <link rel="shortcut icon" href="static/assets/fav-icon.png">
        <link rel="stylesheet" type="text/css" href="static/css/style.css">
        <link rel="stylesheet" type="text/css" href="static/css/xss/xss22.css">
        <title>GTemplate - {0}</title>
    </head>
    <body>
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <div class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h2>Link Preview</h2>
                    {2}
                    <div style="background:#1a1a1a;padding:15px;border-radius:8px;margin:15px 0;text-align:left;">
                        <p style="color:#888;margin-bottom:10px;">Generated Link:</p>
                        <div style="color:#fff;font-family:monospace;" id="output">
                            <a href="{1}" style="color:#4CAF50;">Click to visit: {1}</a>
                        </div>
                    </div>
                    <form style="margin-top:20px;">
                        <input type="text" name="content" placeholder="Enter URL or content..." style="width:80%;padding:10px;">
                        <input type="hidden" name="title" value="{0}">
                        <button type="submit" style="padding:10px 20px;background:#4CAF50;border:none;color:#fff;cursor:pointer;">Generate Link</button>
                    </form>
                    <p style="color:#666;font-size:12px;margin-top:15px;">Content is HTML-escaped before embedding in the href attribute.</p>
                </div>
            </div>
        </div>
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
