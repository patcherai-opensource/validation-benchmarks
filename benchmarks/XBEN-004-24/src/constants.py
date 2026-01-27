INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <title>ShopCore Admin Panel</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    padding: 40px;
                }
                h1 {
                    color: #333;
                    margin-bottom: 10px;
                }
                .subtitle {
                    color: #666;
                    margin-bottom: 30px;
                }
                .nav-link {
                    display: block;
                    padding: 15px 20px;
                    background: #f8f9fa;
                    border-radius: 5px;
                    color: #495057;
                    text-decoration: none;
                    margin-bottom: 10px;
                    transition: all 0.3s ease;
                }
                .nav-link:hover {
                    background: #667eea;
                    color: white;
                }
                .icon {
                    margin-right: 10px;
                }
                .version {
                    color: #999;
                    font-size: 12px;
                    margin-top: 30px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>ShopCore Admin Panel</h1>
                <p class="subtitle">E-commerce Content Management System</p>
                
                <a href="/admin/products/validate" class="nav-link">
                    <span class="icon">&#128221;</span> Product Description Validator
                </a>
                
                <p class="version">ShopCore CMS v2.4.1 - Admin Portal</p>
            </div>
        </body>
    </html>
"""

PRODUCT_VALIDATOR_PAGE = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>ShopCore - Product Description Validator</title>
        <style>
            @keyframes validateAnimation {{
                from {{ opacity: 1; transform: scale(1); }}
                to {{ opacity: 0.8; transform: scale(0.98); }}
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                padding: 40px;
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
            }}
            .subtitle {{
                color: #666;
                margin-bottom: 30px;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 600;
            }}
            textarea {{
                width: 100%;
                min-height: 200px;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                font-family: 'Courier New', monospace;
                resize: vertical;
                box-sizing: border-box;
            }}
            textarea:focus {{
                outline: none;
                border-color: #667eea;
            }}
            .btn {{
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s ease;
            }}
            .btn:hover {{
                background: #5a67d8;
            }}
            .result-panel {{
                margin-top: 20px;
                padding: 20px;
                border-radius: 8px;
                background: #f8f9fa;
                text-align: center;
            }}
            .result-panel.success {{
                background: #d4edda;
                color: #155724;
            }}
            .result-panel.error {{
                background: #f8d7da;
                color: #721c24;
            }}
            .result-panel.warning {{
                background: #fff3cd;
                color: #856404;
            }}
            .status-icon {{
                font-size: 48px;
            }}
            .preview-section {{
                margin-top: 30px;
                padding: 20px;
                border: 2px dashed #e0e0e0;
                border-radius: 8px;
                background: #fafafa;
            }}
            .preview-label {{
                color: #666;
                font-size: 12px;
                text-transform: uppercase;
                margin-bottom: 10px;
            }}
            .preview-content {{
                animation-name: validateAnimation;
            }}
            .info-box {{
                background: #e7f3ff;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 0 5px 5px 0;
            }}
            .info-box h3 {{
                margin: 0 0 10px 0;
                color: #333;
            }}
            .info-box p {{
                margin: 0;
                color: #666;
                font-size: 14px;
            }}
            .back-link {{
                color: #667eea;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">&larr; Back to Admin Panel</a>
            <h1>Product Description Validator</h1>
            <p class="subtitle">Validate HTML content before publishing to your store</p>
            
            <div class="info-box">
                <h3>Content Security Check</h3>
                <p>This tool validates product descriptions to ensure they are safe for display. 
                   HTML content is filtered to prevent malicious scripts and event handlers.</p>
            </div>
            
            <form method="post">
                <div class="form-group">
                    <label for="description">Product Description (HTML)</label>
                    <textarea name="description" id="description" placeholder="Enter your product description HTML here...">{0}</textarea>
                </div>
                <button type="submit" class="btn">Validate Content</button>
            </form>
            
            {1}
            
            {2}
            
            <div class="preview-section">
                <div class="preview-label">Content Preview</div>
                <div class="preview-content">{0}</div>
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
