INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>ShopWave CMS - Admin Panel</title>
            <style>
                body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eaeaea; margin: 0; padding: 20px; }
                .admin-header { background: #16213e; padding: 20px; margin-bottom: 20px; border-radius: 8px; }
                .admin-header h1 { margin: 0; color: #e94560; }
                .admin-nav { display: flex; gap: 20px; margin-top: 15px; }
                .admin-nav a { color: #eaeaea; text-decoration: none; padding: 10px 20px; background: #0f3460; border-radius: 5px; }
                .admin-nav a:hover { background: #e94560; }
                .dashboard-card { background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                .dashboard-card h3 { color: #e94560; margin-top: 0; }
                .feature-list { list-style: none; padding: 0; }
                .feature-list li { padding: 8px 0; border-bottom: 1px solid #0f3460; }
                .feature-list li:last-child { border-bottom: none; }
                .btn-primary { display: inline-block; background: #e94560; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin-top: 10px; }
                .btn-primary:hover { background: #c73e54; }
            </style>
        </head>
        <body>
            <div class="admin-header">
                <h1>ShopWave CMS</h1>
                <p>E-Commerce Content Management System v2.4.1</p>
                <div class="admin-nav">
                    <a href="/">Dashboard</a>
                    <a href="/admin/product/preview">Product Editor</a>
                    <a href="/api/validate">API Docs</a>
                </div>
            </div>
            
            <div class="dashboard-card">
                <h3>Welcome to ShopWave Admin</h3>
                <p>Manage your e-commerce content with our powerful HTML editor.</p>
                <ul class="feature-list">
                    <li><strong>Product Description Editor</strong> - Preview HTML content before publishing</li>
                    <li><strong>HTML Sanitization</strong> - Built-in security validation using isCleanHtml()</li>
                    <li><strong>API Integration</strong> - Validate content programmatically</li>
                </ul>
                <a href="/admin/product/preview" class="btn-primary">Open Product Editor</a>
            </div>
            
            <div class="dashboard-card">
                <h3>Security Notice</h3>
                <p>All HTML content is validated using our isCleanHtml() sanitization method. 
                   Dangerous elements like &lt;script&gt; tags and common event handlers are blocked.</p>
                <p><em>Supported safe HTML: &lt;p&gt;, &lt;div&gt;, &lt;span&gt;, &lt;a&gt;, &lt;img&gt;, &lt;b&gt;, &lt;i&gt;, &lt;u&gt;, etc.</em></p>
            </div>
        </body>
    </html>
"""


PREVIEW_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss21.css">
            <title>ShopWave - {0}</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eaeaea; margin: 0; padding: 20px; }}
                .admin-header {{ background: #16213e; padding: 20px; margin-bottom: 20px; border-radius: 8px; }}
                .admin-header h1 {{ margin: 0; color: #e94560; }}
                .editor-container {{ background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .editor-container h3 {{ color: #e94560; margin-top: 0; }}
                .preview-box {{ background: #0f3460; padding: 15px; border-radius: 5px; margin-top: 15px; min-height: 100px; }}
                .preview-label {{ font-size: 12px; color: #888; margin-bottom: 5px; }}
                .result-panel {{ background: #16213e; padding: 15px; border-radius: 5px; margin-top: 15px; }}
                .result-panel.success {{ border-left: 4px solid #4caf50; }}
                .result-panel.error {{ border-left: 4px solid #f44336; }}
                .result-panel.warning {{ border-left: 4px solid #ff9800; }}
                .preview-info {{ color: #eaeaea; }}
                input[type=text] {{ width: 100%; padding: 12px; background: #0f3460; border: 1px solid #e94560; color: #eaeaea; border-radius: 5px; font-size: 14px; }}
                input[type=text]:focus {{ outline: none; border-color: #fff; }}
                .hint {{ font-size: 12px; color: #888; margin-top: 8px; }}
                .admin-nav {{ display: flex; gap: 20px; margin-top: 15px; }}
                .admin-nav a {{ color: #eaeaea; text-decoration: none; padding: 10px 20px; background: #0f3460; border-radius: 5px; }}
                .admin-nav a:hover {{ background: #e94560; }}
            </style>
        </head>
        <body>
            <div class="admin-header">
                <h1>ShopWave CMS</h1>
                <p>Product Description Editor</p>
                <div class="admin-nav">
                    <a href="/">Dashboard</a>
                    <a href="/admin/product/preview">Product Editor</a>
                </div>
            </div>
            
            <div class="editor-container">
                <h3>HTML Content Editor</h3>
                <p>Enter HTML content for your product description. Content is sanitized using isCleanHtml() before rendering.</p>
                
                <form method="GET" action="/admin/product/preview">
                    <input type="text" name="description" placeholder="Enter HTML content (e.g., <b>Bold text</b>, <img src='...'>, <a href='...'>Link</a>)" value="">
                    <p class="hint">Tip: Use the description parameter to preview HTML content. Blocked: script, onclick, onerror, etc.</p>
                </form>
                
                {3}
                
                <div class="preview-box">
                    <div class="preview-label">Preview Output:</div>
                    {1}
                </div>
                
                {2}
            </div>
        </body>
    </html>
"""

# Keep other constants for compatibility but they won't be used
XSS_CONTENT = PREVIEW_CONTENT

XSS_CONTENT_POST = PREVIEW_CONTENT

XSS_CONTENT_TAG = PREVIEW_CONTENT

XSS_CONTENT_TAG_POST = PREVIEW_CONTENT

XSS_CONTENT_IFRAME = PREVIEW_CONTENT

XSS_CONTENT_TEXTAREA_POST = PREVIEW_CONTENT

# Image routes (keeping for compatibility with check_xss function)
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
