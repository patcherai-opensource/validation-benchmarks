INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>Universal CMS - Server-Side Rendering Platform</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background: #f5f5f5; }
        .hero { text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .hero h1 { font-size: 2.5em; margin-bottom: 10px; }
        .hero p { font-size: 1.2em; opacity: 0.9; }
        .features { display: flex; justify-content: center; gap: 40px; padding: 40px 20px; flex-wrap: wrap; }
        .feature { text-align: center; max-width: 250px; }
        .feature h3 { color: #333; }
        .feature p { color: #666; }
        .cta { text-align: center; padding: 40px; }
        .cta a { background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 1.1em; }
        .cta a:hover { background: #5a6fd6; }
        footer { text-align: center; padding: 20px; color: #888; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="hero">
        <h1>Universal CMS</h1>
        <p>Fast, SEO-optimized server-side rendering with critical CSS inlining</p>
    </div>
    
    <div class="features">
        <div class="feature">
            <h3>Server-Side Rendering</h3>
            <p>Pre-render pages on the server for faster initial load and better SEO.</p>
        </div>
        <div class="feature">
            <h3>Critical CSS Inlining</h3>
            <p>Automatically inline above-the-fold CSS for optimal performance.</p>
        </div>
        <div class="feature">
            <h3>Custom Themes</h3>
            <p>Apply custom stylesheets to personalize your rendered content.</p>
        </div>
    </div>
    
    <div class="cta">
        <a href="/render">Try the Page Renderer</a>
    </div>
    
    <footer>
        <p>Universal CMS v16.1.1 - Powered by critical CSS optimization</p>
    </footer>
</body>
</html>
"""

SSR_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>Universal CMS - Rendered Page</title>
</head>
<body>
    <div class="rendered-content">
        <p>{0}</p>
    </div>
</body>
</html>
"""

SSR_PAGE_WITH_RESULT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>Universal CMS - Server-Side Rendering</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; }}
        .header h1 {{ margin: 0; font-size: 1.5em; }}
        .header a {{ color: white; text-decoration: none; opacity: 0.8; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h2 {{ margin-top: 0; color: #333; }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; margin-bottom: 5px; color: #555; font-weight: 500; }}
        .form-group input, .form-group textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
        .form-group textarea {{ height: 100px; resize: vertical; }}
        .btn {{ background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
        .btn:hover {{ background: #5a6fd6; }}
        .preview {{ background: #fafafa; border: 1px solid #eee; padding: 15px; border-radius: 4px; min-height: 50px; }}
        .result {{ margin-top: 20px; padding: 15px; border-radius: 4px; }}
        .info {{ background: #e3f2fd; color: #1565c0; padding: 10px; border-radius: 4px; margin-bottom: 15px; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Universal CMS - Page Renderer</h1>
        <a href="/">&#8592; Back to Home</a>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>Server-Side Rendering with Critical CSS</h2>
            <p class="info">Enter your page content and optionally specify a stylesheet URL. Our SSR engine will render your page with optimized critical CSS inlining.</p>
            
            <form method="get" action="/render">
                <div class="form-group">
                    <label for="content">Page Content</label>
                    <textarea name="content" id="content" placeholder="Enter your page content here...">{0}</textarea>
                </div>
                
                <div class="form-group">
                    <label for="stylesheet">Custom Stylesheet URL (optional)</label>
                    <input type="text" name="stylesheet" id="stylesheet" placeholder="https://example.com/styles.css">
                </div>
                
                <button type="submit" class="btn">Render Page</button>
            </form>
        </div>
        
        <div class="card">
            <h2>Render Result</h2>
            <div class="preview">
                {1}
            </div>
        </div>
    </div>
</body>
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
