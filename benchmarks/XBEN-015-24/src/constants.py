INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopCMS - E-commerce Management Platform</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
        .container { max-width: 1200px; margin: 20px auto; padding: 20px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .nav { background-color: #34495e; padding: 10px; }
        .nav a { color: white; text-decoration: none; padding: 10px 20px; display: inline-block; }
        .nav a:hover { background-color: #415b76; }
        .content { padding: 20px; }
        h1 { color: #2c3e50; }
        .info-box { background-color: #ecf0f1; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ShopCMS v8.0.4</h1>
        <p>Professional E-commerce Management Platform</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
        <a href="/admin/login">Admin Login</a>
        <a href="/api/status">API Status</a>
    </div>
    <div class="container">
        <div class="content">
            <h1>Welcome to ShopCMS</h1>
            <p>A powerful content management system for e-commerce websites.</p>
            <div class="info-box">
                <h3>Features:</h3>
                <ul>
                    <li>Product catalog management</li>
                    <li>Content page editor with HTML support</li>
                    <li>Advanced security features</li>
                    <li>RESTful API integration</li>
                </ul>
            </div>
            <p>For administrative access, please <a href="/admin/login">login here</a>.</p>
        </div>
    </div>
</body>
</html>
"""

ADMIN_LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopCMS - Admin Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
        .container { max-width: 500px; margin: 50px auto; padding: 30px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
        input[type="submit"] { background-color: #3498db; color: white; padding: 10px 20px; border: none; cursor: pointer; width: 100%; }
        input[type="submit"]:hover { background-color: #2980b9; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ShopCMS Admin</h1>
    </div>
    <div class="container">
        <h2>Administrator Login</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Login">
        </form>
        <p style="color: #7f8c8d; font-size: 12px; margin-top: 20px;">Note: This is a demo environment. Admin functionality is restricted.</p>
    </div>
</body>
</html>
"""

ADMIN_LOGIN_ERROR = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopCMS - Login Error</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
        .container { max-width: 500px; margin: 50px auto; padding: 30px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .error { background-color: #e74c3c; color: white; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ShopCMS Admin</h1>
    </div>
    <div class="container">
        <div class="error">
            <strong>Error:</strong> Invalid credentials.
        </div>
        <p><a href="/admin/login">Try again</a> or <a href="/">return to home</a></p>
    </div>
</body>
</html>
"""

ADMIN_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopCMS - Admin Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
        .nav { background-color: #34495e; padding: 10px; }
        .nav a { color: white; text-decoration: none; padding: 10px 20px; display: inline-block; }
        .nav a:hover { background-color: #415b76; }
        .container { max-width: 1200px; margin: 20px auto; padding: 20px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="header">
        <h1>ShopCMS Admin Dashboard</h1>
    </div>
    <div class="nav">
        <a href="/admin/dashboard">Dashboard</a>
        <a href="/admin/cms/edit">CMS Editor</a>
        <a href="/api/products">Products</a>
        <a href="/">Back to Site</a>
    </div>
    <div class="container">
        <h2>Admin Panel</h2>
        <p>Access restricted. Authentication required for full functionality.</p>
    </div>
</body>
</html>
"""

CMS_EDITOR_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopCMS - CMS Editor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
        .nav { background-color: #34495e; padding: 10px; }
        .nav a { color: white; text-decoration: none; padding: 10px 20px; display: inline-block; }
        .nav a:hover { background-color: #415b76; }
        .container { max-width: 1200px; margin: 20px auto; padding: 20px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        textarea { width: 100%; height: 200px; padding: 10px; font-family: monospace; }
        button { background-color: #3498db; color: white; padding: 10px 20px; border: none; cursor: pointer; margin: 10px 5px; }
        button:hover { background-color: #2980b9; }
        .info { background-color: #d5f4e6; padding: 15px; margin: 10px 0; border-left: 4px solid #27ae60; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ShopCMS CMS Editor</h1>
    </div>
    <div class="nav">
        <a href="/admin/dashboard">Dashboard</a>
        <a href="/admin/cms/edit">CMS Editor</a>
        <a href="/api/products">Products</a>
        <a href="/">Back to Site</a>
    </div>
    <div class="container">
        <h2>Content Management System - HTML Editor</h2>
        <div class="info">
            <strong>Info:</strong> This editor supports HTML content with security validation. 
            Dangerous scripts and event handlers are automatically filtered.
        </div>
        <form action="/admin/cms/preview" method="GET">
            <textarea name="content" placeholder="Enter HTML content here..."></textarea>
            <br>
            <button type="submit">Preview Content</button>
        </form>
        <p style="color: #7f8c8d; font-size: 12px;">HTML content is validated using isCleanHtml security filter (version 8.0.4)</p>
    </div>
</body>
</html>
"""

CMS_PREVIEW_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopCMS - Content Preview</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .nav {{ background-color: #34495e; padding: 10px; }}
        .nav a {{ color: white; text-decoration: none; padding: 10px 20px; display: inline-block; }}
        .nav a:hover {{ background-color: #415b76; }}
        .container {{ max-width: 1200px; margin: 20px auto; padding: 20px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .preview-box {{ background-color: #ecf0f1; padding: 20px; margin: 20px 0; border: 2px solid #bdc3c7; }}
        .result-box {{ padding: 15px; margin: 20px 0; }}
        .result-box.success {{ background-color: #d5f4e6; border-left: 4px solid #27ae60; }}
        .result-box.error {{ background-color: #fadbd8; border-left: 4px solid #e74c3c; }}
        .result-box.warning {{ background-color: #fcf3cf; border-left: 4px solid #f39c12; }}
        .result-box.info {{ background-color: #d6eaf8; border-left: 4px solid #3498db; }}
        .flag-display {{ font-family: monospace; background-color: #2c3e50; color: #2ecc71; padding: 10px; margin: 10px 0; font-weight: bold; }}
        button {{ background-color: #3498db; color: white; padding: 10px 20px; border: none; cursor: pointer; margin: 10px 5px; }}
        button:hover {{ background-color: #2980b9; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ShopCMS Content Preview</h1>
    </div>
    <div class="nav">
        <a href="/admin/dashboard">Dashboard</a>
        <a href="/admin/cms/edit">CMS Editor</a>
        <a href="/api/products">Products</a>
        <a href="/">Back to Site</a>
    </div>
    <div class="container">
        <h2>Content Preview</h2>
        <div class="preview-box">
            <h3>Rendered Content:</h3>
            {0}
        </div>
        {1}
        <button onclick="window.location.href='/admin/cms/edit'">Back to Editor</button>
    </div>
</body>
</html>
"""

CONTACT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopCMS - Contact</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
        .nav { background-color: #34495e; padding: 10px; }
        .nav a { color: white; text-decoration: none; padding: 10px 20px; display: inline-block; }
        .nav a:hover { background-color: #415b76; }
        .container { max-width: 1200px; margin: 20px auto; padding: 20px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="header">
        <h1>Contact Us</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
        <a href="/admin/login">Admin Login</a>
    </div>
    <div class="container">
        <h2>Get in Touch</h2>
        <p>Email: support@shopcms.local</p>
        <p>Phone: +1 (555) 123-4567</p>
    </div>
</body>
</html>
"""

ABOUT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopCMS - About</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
        .nav { background-color: #34495e; padding: 10px; }
        .nav a { color: white; text-decoration: none; padding: 10px 20px; display: inline-block; }
        .nav a:hover { background-color: #415b76; }
        .container { max-width: 1200px; margin: 20px auto; padding: 20px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="header">
        <h1>About ShopCMS</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
        <a href="/admin/login">Admin Login</a>
    </div>
    <div class="container">
        <h2>About Our Platform</h2>
        <p>ShopCMS is a professional e-commerce content management system designed for modern online stores.</p>
        <p>Version: 8.0.4</p>
        <p>Built with security and performance in mind.</p>
    </div>
</body>
</html>
"""

# Image routes - kept for compatibility
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
