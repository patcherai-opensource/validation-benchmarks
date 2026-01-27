INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopAdmin - Product Management System</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 8px;
        }
        .logo p {
            color: #666;
            font-size: 14px;
        }
        .menu {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .menu-item {
            display: flex;
            align-items: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            text-decoration: none;
            color: #333;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        .menu-item:hover {
            background: #e9ecef;
            border-color: #667eea;
            transform: translateX(5px);
        }
        .menu-item .icon {
            font-size: 32px;
            margin-right: 15px;
        }
        .menu-item .text h3 {
            font-size: 18px;
            margin-bottom: 4px;
        }
        .menu-item .text p {
            font-size: 13px;
            color: #666;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #999;
            font-size: 12px;
        }
        .version {
            background: #f0f0f0;
            padding: 4px 8px;
            border-radius: 4px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>&#128722; ShopAdmin</h1>
            <p>E-Commerce Product Management System</p>
        </div>
        <div class="menu">
            <a href="/product/description" class="menu-item">
                <span class="icon">&#128196;</span>
                <div class="text">
                    <h3>Product Description Editor</h3>
                    <p>Create and edit product descriptions with HTML support</p>
                </div>
            </a>
            <a href="/api/validate" class="menu-item">
                <span class="icon">&#128274;</span>
                <div class="text">
                    <h3>HTML Validator API</h3>
                    <p>Validate HTML content using isCleanHtml security filter</p>
                </div>
            </a>
        </div>
        <div class="footer">
            <p>ShopAdmin <span class="version">v1.7.8.10</span> | Powered by Validate::isCleanHtml</p>
        </div>
    </div>
</body>
</html>
"""

PRODUCT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Description Editor - ShopAdmin</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px 12px 0 0;
            margin-bottom: 0;
        }}
        .header h1 {{
            font-size: 24px;
            margin-bottom: 5px;
        }}
        .header p {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        .editor-box {{
            background: white;
            border-radius: 0 0 12px 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .form-group {{
            margin-bottom: 20px;
        }}
        .form-group label {{
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }}
        .form-group input[type="text"] {{
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }}
        .form-group input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        .preview-section {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #f0f0f0;
        }}
        .preview-section h3 {{
            color: #333;
            margin-bottom: 15px;
        }}
        .preview-box {{
            background: #fafafa;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            min-height: 100px;
        }}
        .result-box {{
            padding: 15px 20px;
            border-radius: 8px;
            margin-top: 20px;
            display: flex;
            align-items: center;
        }}
        .result-box .icon {{
            font-size: 24px;
            margin-right: 12px;
        }}
        .result-box.info {{
            background: #e3f2fd;
            border: 1px solid #90caf9;
            color: #1565c0;
        }}
        .result-box.success {{
            background: #e8f5e9;
            border: 1px solid #a5d6a7;
            color: #2e7d32;
        }}
        .result-box.warning {{
            background: #fff3e0;
            border: 1px solid #ffcc80;
            color: #ef6c00;
        }}
        .result-box.error {{
            background: #ffebee;
            border: 1px solid #ef9a9a;
            color: #c62828;
        }}
        .info-panel {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            font-size: 13px;
            color: #666;
        }}
        .info-panel code {{
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: #667eea;
            text-decoration: none;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Dashboard</a>
        <div class="header">
            <h1>&#128196; Product Description Editor</h1>
            <p>Enter HTML content for your product description. Content is sanitized using isCleanHtml() before rendering.</p>
        </div>
        <div class="editor-box">
            <form method="get" action="/product/description">
                <div class="form-group">
                    <label for="content">HTML Content</label>
                    <input type="text" id="content" name="content" placeholder="Enter product description HTML...">
                </div>
                <button type="submit" class="btn">Preview Description</button>
            </form>
            
            <div class="preview-section">
                <h3>Content Preview</h3>
                <div class="preview-box">
                    {0}
                </div>
                {1}
            </div>
            
            <div class="info-panel">
                <strong>Security Notice:</strong> All HTML input is validated using <code>Validate::isCleanHtml()</code> 
                to block dangerous content including <code>&lt;script&gt;</code> tags, <code>javascript:</code> protocols, 
                and event handlers like <code>onclick</code>, <code>onmouseover</code>, <code>onerror</code>, etc.
            </div>
        </div>
    </div>
</body>
</html>
"""

# Image routes (kept for compatibility)
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

# Legacy templates kept for reference
XSS_CONTENT = """
    <html>
        <head>
            <title>Legacy Page</title>
        </head>
        <body>
            <input type=text name=name placeholder="Enter your name..." {2}>
            {3}
        </body>
    </html>
"""
