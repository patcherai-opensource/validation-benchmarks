INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>PlateEmbed - Rich Media Embedding Platform</title>
            <style>
                body { font-family: 'Segoe UI', Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; }
                .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
                .header { text-align: center; margin-bottom: 40px; }
                .header h1 { font-size: 2.5em; color: #00d4ff; margin-bottom: 10px; }
                .header p { color: #888; font-size: 1.1em; }
                .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
                .feature-card { background: #16213e; border-radius: 12px; padding: 25px; text-align: center; transition: transform 0.2s; }
                .feature-card:hover { transform: translateY(-5px); }
                .feature-card a { color: #00d4ff; text-decoration: none; }
                .feature-card h3 { margin: 15px 0 10px; }
                .feature-card p { color: #888; font-size: 0.9em; }
                .api-link { margin-top: 40px; text-align: center; }
                .api-link a { color: #666; font-size: 0.85em; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>PlateEmbed</h1>
                    <p>Seamlessly embed rich media content in your applications</p>
                    <small style="color:#555">v36.0.9 - Enterprise Media Embedding Solution</small>
                </div>
                <div class="features">
                    <div class="feature-card">
                        <a href="/embed/youtube">
                            <svg width="60" height="60" fill="#ff0000" viewBox="0 0 24 24"><path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 4-8 4z"/></svg>
                            <h3>YouTube Embed</h3>
                            <p>Embed YouTube videos with custom parameters</p>
                        </a>
                    </div>
                    <div class="feature-card">
                        <a href="/embed/twitter">
                            <svg width="60" height="60" fill="#1da1f2" viewBox="0 0 24 24"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/></svg>
                            <h3>Twitter Embed</h3>
                            <p>Embed tweets and Twitter content</p>
                        </a>
                    </div>
                    <div class="feature-card">
                        <a href="/embed/vimeo">
                            <svg width="60" height="60" fill="#1ab7ea" viewBox="0 0 24 24"><path d="M23.977 6.416c-.105 2.338-1.739 5.543-4.894 9.609-3.268 4.247-6.026 6.37-8.29 6.37-1.409 0-2.578-1.294-3.553-3.881L5.322 11.4C4.603 8.816 3.834 7.522 3.01 7.522c-.179 0-.806.378-1.881 1.132L0 7.197a315.065 315.065 0 003.501-3.128C5.08 2.701 6.266 1.984 7.055 1.91c1.867-.18 3.016 1.1 3.447 3.838.465 2.953.789 4.789.971 5.507.539 2.45 1.131 3.674 1.776 3.674.502 0 1.256-.796 2.265-2.385 1.004-1.589 1.54-2.797 1.612-3.628.144-1.371-.395-2.061-1.614-2.061-.574 0-1.167.121-1.777.391 1.186-3.868 3.434-5.757 6.762-5.637 2.473.06 3.628 1.664 3.493 4.797l-.013.01z"/></svg>
                            <h3>Vimeo Embed</h3>
                            <p>Embed Vimeo videos seamlessly</p>
                        </a>
                    </div>
                    <div class="feature-card">
                        <a href="/embed/media">
                            <svg width="60" height="60" fill="#00d4ff" viewBox="0 0 24 24"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14zM9.5 14l2.5-3 2.5 3 3-4 4 6H5l4.5-6z"/></svg>
                            <h3>Custom Media</h3>
                            <p>Embed any media URL with custom parsers</p>
                        </a>
                    </div>
                </div>
                <div class="api-link">
                    <a href="/api/docs">API Documentation</a> | <a href="/health">Health Check</a>
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
            <title>PlateEmbed - {1} Preview</title>
            <style>
                body {{ background: #1a1a2e; color: #eee; font-family: 'Segoe UI', Arial, sans-serif; }}
                .embed-container {{ max-width: 800px; margin: 40px auto; padding: 20px; }}
                .preview-frame {{ border: 1px solid #333; border-radius: 8px; background: #16213e; padding: 20px; margin-top: 20px; }}
                .preview-frame iframe {{ width: 100%; height: 400px; border: none; border-radius: 4px; }}
                h2 {{ color: #00d4ff; }}
                .url-input {{ width: 100%; padding: 12px; border: 1px solid #333; border-radius: 4px; background: #0f0f23; color: #eee; margin-bottom: 10px; }}
                .back-link {{ color: #666; text-decoration: none; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="embed-container">
                <a href="/" class="back-link">&larr; Back to PlateEmbed</a>
                <h2>{1} Media Embed</h2>
                {4}
                {3}
                <form>
                    <input type=text name=url class="url-input" placeholder="Enter media URL to embed...">
                </form>
                <div class="preview-frame">
                    <h4 style="color:#888;margin:0 0 10px 0;">Preview:</h4>
                    <iframe {2}></iframe>
                </div>
            </div>
        </body>
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
    },
    "media_embed": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    }
}

# API Documentation
API_DOCS_CONTENT = """
    <html>
        <head>
            <title>PlateEmbed API Documentation</title>
            <style>
                body { font-family: 'Segoe UI', Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 40px; }
                .container { max-width: 900px; margin: 0 auto; }
                h1 { color: #00d4ff; }
                h2 { color: #888; border-bottom: 1px solid #333; padding-bottom: 10px; }
                .endpoint { background: #16213e; border-radius: 8px; padding: 20px; margin: 20px 0; }
                .method { display: inline-block; padding: 4px 12px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
                .get { background: #28a745; color: white; }
                .post { background: #007bff; color: white; }
                .path { font-family: monospace; font-size: 1.1em; }
                .param { background: #0f0f23; padding: 10px; border-radius: 4px; margin: 10px 0; }
                .param-name { color: #00d4ff; font-family: monospace; }
                code { background: #0f0f23; padding: 2px 6px; border-radius: 3px; }
                .warning { background: #533; border-left: 4px solid #f55; padding: 15px; margin: 20px 0; border-radius: 4px; }
                a { color: #00d4ff; }
            </style>
        </head>
        <body>
            <div class="container">
                <a href="/">&larr; Back to PlateEmbed</a>
                <h1>PlateEmbed API Documentation</h1>
                <p>Version 36.0.9 - Enterprise Media Embedding Solution</p>
                
                <h2>Embed Endpoints</h2>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/embed/youtube</span>
                    <p>Embed YouTube videos with sanitized URL validation.</p>
                    <div class="param">
                        <span class="param-name">url</span> (query string) - YouTube video URL
                        <br><small>Only accepts youtube.com and youtu.be domains</small>
                    </div>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/embed/twitter</span>
                    <p>Embed Twitter/X content with domain whitelisting.</p>
                    <div class="param">
                        <span class="param-name">url</span> (query string) - Twitter post URL
                        <br><small>Only accepts twitter.com and x.com domains</small>
                    </div>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/embed/vimeo</span>
                    <p>Embed Vimeo videos with strict URL validation.</p>
                    <div class="param">
                        <span class="param-name">url</span> (query string) - Vimeo video URL
                        <br><small>Only accepts vimeo.com domain</small>
                    </div>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/embed/media</span>
                    <p>Custom media embedding with configurable URL parsers.</p>
                    <div class="param">
                        <span class="param-name">url</span> (query string) - Media URL to embed
                        <br><small>Supports custom URL parsing for flexible embedding</small>
                    </div>
                    <div class="warning">
                        <strong>Note:</strong> This endpoint uses custom urlParsers for flexibility. 
                        URL validation depends on the parser configuration. 
                        See <a href="https://github.com/udecode/plate/issues/3416" target="_blank">GitHub issue #3416</a> for security considerations.
                    </div>
                </div>
                
                <h2>Health & Status</h2>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/health</span>
                    <p>Health check endpoint for monitoring.</p>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/api/status</span>
                    <p>Returns service status and version information.</p>
                </div>
                
                <h2>Security Notes</h2>
                <p>PlateEmbed validates URLs to prevent protocol injection attacks. The YouTube, Twitter, and Vimeo endpoints use strict domain whitelisting. The custom media endpoint provides flexibility but requires proper URL parser configuration.</p>
            </div>
        </body>
    </html>
"""

# Embed templates for different providers
YOUTUBE_EMBED_CONTENT = """
    <html>
        <head>
            <title>PlateEmbed - YouTube Preview</title>
            <style>
                body { background: #1a1a2e; color: #eee; font-family: 'Segoe UI', Arial, sans-serif; }
                .embed-container { max-width: 800px; margin: 40px auto; padding: 20px; }
                .preview-frame { border: 1px solid #333; border-radius: 8px; background: #16213e; padding: 20px; margin-top: 20px; }
                .preview-frame iframe { width: 100%; height: 400px; border: none; border-radius: 4px; }
                h2 { color: #ff0000; }
                .url-input { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 4px; background: #0f0f23; color: #eee; margin-bottom: 10px; }
                .back-link { color: #666; text-decoration: none; font-size: 0.9em; }
                .error { color: #f55; background: #533; padding: 10px; border-radius: 4px; }
                .info { color: #888; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="embed-container">
                <a href="/" class="back-link">&larr; Back to PlateEmbed</a>
                <h2>YouTube Embed</h2>
                <p class="info">Enter a YouTube URL to embed. Only youtube.com and youtu.be URLs are accepted.</p>
                <form>
                    <input type=text name=url class="url-input" placeholder="https://www.youtube.com/watch?v=...">
                </form>
                <div class="preview-frame">
                    <h4 style="color:#888;margin:0 0 10px 0;">Preview:</h4>
                    {0}
                </div>
            </div>
        </body>
    </html>
"""

TWITTER_EMBED_CONTENT = """
    <html>
        <head>
            <title>PlateEmbed - Twitter Preview</title>
            <style>
                body { background: #1a1a2e; color: #eee; font-family: 'Segoe UI', Arial, sans-serif; }
                .embed-container { max-width: 800px; margin: 40px auto; padding: 20px; }
                .preview-frame { border: 1px solid #333; border-radius: 8px; background: #16213e; padding: 20px; margin-top: 20px; }
                .preview-frame iframe { width: 100%; height: 400px; border: none; border-radius: 4px; }
                h2 { color: #1da1f2; }
                .url-input { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 4px; background: #0f0f23; color: #eee; margin-bottom: 10px; }
                .back-link { color: #666; text-decoration: none; font-size: 0.9em; }
                .error { color: #f55; background: #533; padding: 10px; border-radius: 4px; }
                .info { color: #888; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="embed-container">
                <a href="/" class="back-link">&larr; Back to PlateEmbed</a>
                <h2>Twitter Embed</h2>
                <p class="info">Enter a Twitter/X URL to embed. Only twitter.com and x.com URLs are accepted.</p>
                <form>
                    <input type=text name=url class="url-input" placeholder="https://twitter.com/user/status/...">
                </form>
                <div class="preview-frame">
                    <h4 style="color:#888;margin:0 0 10px 0;">Preview:</h4>
                    {0}
                </div>
            </div>
        </body>
    </html>
"""

VIMEO_EMBED_CONTENT = """
    <html>
        <head>
            <title>PlateEmbed - Vimeo Preview</title>
            <style>
                body { background: #1a1a2e; color: #eee; font-family: 'Segoe UI', Arial, sans-serif; }
                .embed-container { max-width: 800px; margin: 40px auto; padding: 20px; }
                .preview-frame { border: 1px solid #333; border-radius: 8px; background: #16213e; padding: 20px; margin-top: 20px; }
                .preview-frame iframe { width: 100%; height: 400px; border: none; border-radius: 4px; }
                h2 { color: #1ab7ea; }
                .url-input { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 4px; background: #0f0f23; color: #eee; margin-bottom: 10px; }
                .back-link { color: #666; text-decoration: none; font-size: 0.9em; }
                .error { color: #f55; background: #533; padding: 10px; border-radius: 4px; }
                .info { color: #888; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="embed-container">
                <a href="/" class="back-link">&larr; Back to PlateEmbed</a>
                <h2>Vimeo Embed</h2>
                <p class="info">Enter a Vimeo URL to embed. Only vimeo.com URLs are accepted.</p>
                <form>
                    <input type=text name=url class="url-input" placeholder="https://vimeo.com/...">
                </form>
                <div class="preview-frame">
                    <h4 style="color:#888;margin:0 0 10px 0;">Preview:</h4>
                    {0}
                </div>
            </div>
        </body>
    </html>
"""
