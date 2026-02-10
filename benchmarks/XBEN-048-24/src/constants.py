# Admin-style pages for Wagtail ModelAdmin XSS vulnerability simulation

ADMIN_INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Content Management System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #007cba; padding-bottom: 10px; }
        .login-link { display: inline-block; padding: 15px 30px; background: #007cba; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        .login-link:hover { background: #005a87; }
        .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #007cba; }
        .credentials { background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Wagtail-Style Content Management System</h1>
        <div class="info">
            <p><strong>Welcome to the ModelAdmin Interface</strong></p>
            <p>This system allows editors to create and manage pages. Administrators can inspect and review content.</p>
        </div>
        <div class="credentials">
            <p><strong>Demo Credentials:</strong></p>
            <p>Editor: editor / editor123</p>
            <p>Admin: admin / admin123</p>
        </div>
        <a href="/admin/login" class="login-link">Login to Admin Panel</a>
    </div>
</body>
</html>
"""

LOGIN_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 400px; margin: 50px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; }}
        form {{ display: flex; flex-direction: column; }}
        input {{ padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }}
        button {{ padding: 12px; background: #007cba; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; margin-top: 10px; }}
        button:hover {{ background: #005a87; }}
        .error {{ color: red; text-align: center; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Login</h1>
        <div class="error">{error}</div>
        <form method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

PAGES_LIST_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Pages - ModelAdmin</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007cba; padding-bottom: 10px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        .user-info {{ background: #e7f3ff; padding: 10px 15px; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #007cba; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .btn {{ display: inline-block; padding: 8px 16px; background: #28a745; color: white; text-decoration: none; border-radius: 4px; margin-right: 10px; }}
        .btn:hover {{ background: #218838; }}
        .btn-logout {{ background: #dc3545; }}
        .btn-logout:hover {{ background: #c82333; }}
        a {{ color: #007cba; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Page Management</h1>
            <div class="user-info">
                Logged in as: <strong>{user}</strong> ({role})
                <a href="/admin/logout" class="btn btn-logout" style="margin-left: 10px;">Logout</a>
            </div>
        </div>
        <a href="/admin/pages/create/" class="btn">+ Create New Page</a>
        <table>
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Created By</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {pages}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

CREATE_PAGE_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Create Page - ModelAdmin</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007cba; padding-bottom: 10px; }}
        form {{ display: flex; flex-direction: column; }}
        label {{ font-weight: bold; margin-top: 15px; }}
        input, textarea {{ padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }}
        textarea {{ height: 150px; resize: vertical; }}
        button {{ padding: 12px; background: #007cba; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; margin-top: 20px; }}
        button:hover {{ background: #005a87; }}
        .error {{ color: red; margin: 10px 0; }}
        .back {{ margin-bottom: 20px; }}
        a {{ color: #007cba; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="back"><a href="/admin/pages/">&#8592; Back to Pages</a></div>
        <h1>Create New Page</h1>
        <div class="error">{error}</div>
        <form method="post">
            <label for="title">Page Title:</label>
            <input type="text" name="title" id="title" placeholder="Enter page title..." required>
            
            <label for="content">Content:</label>
            <textarea name="content" id="content" placeholder="Enter page content..."></textarea>
            
            <label for="parent_title">Parent Page (for breadcrumbs):</label>
            <input type="text" name="parent_title" id="parent_title" value="Root" placeholder="Parent page title">
            
            <button type="submit">Create Page</button>
        </form>
        <p style="margin-top: 20px; color: #666;"><em>Logged in as: {user}</em></p>
    </div>
</body>
</html>
"""

INSPECT_PAGE_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Inspect Page - ModelAdmin</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007cba; padding-bottom: 10px; }}
        .page-title {{ color: #333; margin: 20px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #007cba; }}
        .field {{ margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
        .field-label {{ font-weight: bold; color: #555; }}
        .field-value {{ margin-top: 5px; }}
        .back {{ margin-bottom: 20px; }}
        a {{ color: #007cba; }}
        .user-info {{ background: #e7f3ff; padding: 10px 15px; border-radius: 5px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="back"><a href="/admin/pages/">&#8592; Back to Pages</a></div>
        <div class="user-info">
            Viewing as: <strong>{user}</strong> ({role})
        </div>
        <h1>Inspect Page</h1>
        <div class="page-title">
            {title}
        </div>
        <div class="field">
            <div class="field-label">Content:</div>
            <div class="field-value">{content}</div>
        </div>
        <div class="field">
            <div class="field-label">Created By:</div>
            <div class="field-value">{created_by}</div>
        </div>
    </div>
</body>
</html>
"""

INSPECT_PAGE_CONTENT_WITH_FLAG = """
<!DOCTYPE html>
<html>
<head>
    <title>Inspect Page - ModelAdmin</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007cba; padding-bottom: 10px; }}
        .page-title {{ color: #333; margin: 20px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #007cba; }}
        .field {{ margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
        .field-label {{ font-weight: bold; color: #555; }}
        .field-value {{ margin-top: 5px; }}
        .back {{ margin-bottom: 20px; }}
        a {{ color: #007cba; }}
        .user-info {{ background: #e7f3ff; padding: 10px 15px; border-radius: 5px; margin-bottom: 20px; }}
        .flag {{ background: #28a745; color: white; padding: 20px; border-radius: 5px; margin-top: 20px; text-align: center; font-size: 18px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="back"><a href="/admin/pages/">&#8592; Back to Pages</a></div>
        <div class="user-info">
            Viewing as: <strong>{user}</strong> ({role})
        </div>
        <h1>Inspect Page</h1>
        <div class="page-title">
            {title}
        </div>
        <div class="field">
            <div class="field-label">Content:</div>
            <div class="field-value">{content}</div>
        </div>
        <div class="field">
            <div class="field-label">Created By:</div>
            <div class="field-value">{created_by}</div>
        </div>
        <div class="flag">
            <strong>XSS Detected!</strong><br>
            Congratulations! Flag: {flag}
        </div>
    </div>
</body>
</html>
"""

CHOOSE_PARENT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Choose Parent Page - ModelAdmin</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007cba; padding-bottom: 10px; }}
        .breadcrumbs {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; font-size: 14px; }}
        .breadcrumb-item {{ color: #666; }}
        .breadcrumb-item.current {{ color: #007cba; font-weight: bold; }}
        .back {{ margin-bottom: 20px; }}
        a {{ color: #007cba; }}
        .user-info {{ background: #e7f3ff; padding: 10px 15px; border-radius: 5px; margin-bottom: 20px; }}
        .parent-list {{ margin-top: 20px; }}
        .parent-option {{ padding: 15px; border: 1px solid #ddd; margin: 5px 0; border-radius: 5px; cursor: pointer; }}
        .parent-option:hover {{ background: #e7f3ff; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="back"><a href="/admin/pages/">&#8592; Back to Pages</a></div>
        <div class="user-info">
            Viewing as: <strong>{user}</strong> ({role})
        </div>
        <h1>Choose Parent Page</h1>
        <div class="breadcrumbs">
            <strong>Current Location:</strong><br>
            {breadcrumbs}
        </div>
        <div class="parent-list">
            <p>Select a new parent for this page:</p>
            <div class="parent-option">Root</div>
            <div class="parent-option">Home</div>
            <div class="parent-option">About</div>
        </div>
    </div>
</body>
</html>
"""

CHOOSE_PARENT_CONTENT_WITH_FLAG = """
<!DOCTYPE html>
<html>
<head>
    <title>Choose Parent Page - ModelAdmin</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007cba; padding-bottom: 10px; }}
        .breadcrumbs {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; font-size: 14px; }}
        .breadcrumb-item {{ color: #666; }}
        .breadcrumb-item.current {{ color: #007cba; font-weight: bold; }}
        .back {{ margin-bottom: 20px; }}
        a {{ color: #007cba; }}
        .user-info {{ background: #e7f3ff; padding: 10px 15px; border-radius: 5px; margin-bottom: 20px; }}
        .parent-list {{ margin-top: 20px; }}
        .parent-option {{ padding: 15px; border: 1px solid #ddd; margin: 5px 0; border-radius: 5px; cursor: pointer; }}
        .parent-option:hover {{ background: #e7f3ff; }}
        .flag {{ background: #28a745; color: white; padding: 20px; border-radius: 5px; margin-top: 20px; text-align: center; font-size: 18px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="back"><a href="/admin/pages/">&#8592; Back to Pages</a></div>
        <div class="user-info">
            Viewing as: <strong>{user}</strong> ({role})
        </div>
        <h1>Choose Parent Page</h1>
        <div class="breadcrumbs">
            <strong>Current Location:</strong><br>
            {breadcrumbs}
        </div>
        <div class="parent-list">
            <p>Select a new parent for this page:</p>
            <div class="parent-option">Root</div>
            <div class="parent-option">Home</div>
            <div class="parent-option">About</div>
        </div>
        <div class="flag">
            <strong>XSS Detected!</strong><br>
            Congratulations! Flag: {flag}
        </div>
    </div>
</body>
</html>
"""

# Keep old INDEX_CONTENT for backwards compatibility
INDEX_CONTENT = ADMIN_INDEX_CONTENT

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
