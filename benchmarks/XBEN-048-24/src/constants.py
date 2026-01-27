# WagtailCMS Admin Interface Templates

INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>WagtailCMS - Content Management</title>
            <style>
                body { font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; margin: 0; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                h1 { color: #00d4ff; }
                a { color: #00d4ff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .card { background: #16213e; padding: 20px; border-radius: 8px; margin: 10px 0; }
                .nav { display: flex; gap: 20px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>WagtailCMS</h1>
                <p>Welcome to WagtailCMS - An open-source content management system built on Django.</p>
                <div class="card">
                    <h3>Quick Links</h3>
                    <ul>
                        <li><a href="/admin">Admin Dashboard</a></li>
                        <li><a href="/admin/pages">Manage Pages</a></li>
                        <li><a href="/admin/pages/create">Create New Page</a></li>
                    </ul>
                </div>
                <div class="card">
                    <h3>Features</h3>
                    <p>ModelAdmin provides a flexible way to add any model in your project to the Wagtail admin.</p>
                </div>
            </div>
        </body>
    </html>
"""

ADMIN_DASHBOARD_CONTENT = """
    <html>
        <head>
            <title>WagtailCMS Admin</title>
            <style>
                body { font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; margin: 0; padding: 20px; }
                .container { max-width: 900px; margin: 0 auto; }
                h1 { color: #00d4ff; }
                a { color: #00d4ff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .card { background: #16213e; padding: 20px; border-radius: 8px; margin: 10px 0; }
                .nav { background: #0f3460; padding: 10px 20px; border-radius: 4px; margin-bottom: 20px; }
                .nav a { margin-right: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/admin">Dashboard</a>
                    <a href="/admin/pages">Pages</a>
                </div>
                <h1>Admin Dashboard</h1>
                <div class="card">
                    <h3>ModelAdmin</h3>
                    <p>ModelAdmin module allows Wagtail administrator users to create, inspect, and manage any model.</p>
                    <ul>
                        <li><a href="/admin/pages">View All Pages</a></li>
                        <li><a href="/admin/pages/create">Create New Page</a></li>
                    </ul>
                </div>
                <div class="card">
                    <h3>Recent Activity</h3>
                    <p>Use the pages management to inspect existing pages or create new content.</p>
                </div>
            </div>
        </body>
    </html>
"""

ADMIN_PAGES_LIST_CONTENT = """
    <html>
        <head>
            <title>Pages - WagtailCMS Admin</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; margin: 0; padding: 20px; }}
                .container {{ max-width: 900px; margin: 0 auto; }}
                h1 {{ color: #00d4ff; }}
                a {{ color: #00d4ff; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                .nav {{ background: #0f3460; padding: 10px 20px; border-radius: 4px; margin-bottom: 20px; }}
                .nav a {{ margin-right: 20px; }}
                table {{ width: 100%; border-collapse: collapse; background: #16213e; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }}
                th {{ background: #0f3460; }}
                .btn {{ background: #00d4ff; color: #000; padding: 5px 10px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/admin">Dashboard</a>
                    <a href="/admin/pages">Pages</a>
                </div>
                <h1>Pages</h1>
                <p><a href="/admin/pages/create" class="btn">+ Create New Page</a></p>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Actions</th>
                    </tr>
                    {0}
                </table>
            </div>
        </body>
    </html>
"""

CREATE_PAGE_CONTENT = """
    <html>
        <head>
            <title>Create Page - WagtailCMS Admin</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                h1 {{ color: #00d4ff; }}
                a {{ color: #00d4ff; text-decoration: none; }}
                .nav {{ background: #0f3460; padding: 10px 20px; border-radius: 4px; margin-bottom: 20px; }}
                .nav a {{ margin-right: 20px; }}
                .form-group {{ margin-bottom: 15px; }}
                label {{ display: block; margin-bottom: 5px; }}
                input[type="text"], textarea, select {{ width: 100%; padding: 10px; border: none; border-radius: 4px; background: #16213e; color: #fff; }}
                textarea {{ height: 100px; }}
                .btn {{ background: #00d4ff; color: #000; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
                .btn:hover {{ background: #00b8e6; }}
                .info {{ background: #16213e; padding: 15px; border-radius: 4px; margin-bottom: 20px; border-left: 4px solid #00d4ff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/admin">Dashboard</a>
                    <a href="/admin/pages">Pages</a>
                </div>
                <h1>Create New Page</h1>
                <div class="info">
                    <strong>Editor Mode:</strong> Create content that will be reviewed by administrators.
                </div>
                <form method="POST" action="/admin/pages/create">
                    <div class="form-group">
                        <label for="title">Page Title:</label>
                        <input type="text" id="title" name="title" placeholder="Enter page title..." required>
                    </div>
                    <div class="form-group">
                        <label for="content">Content:</label>
                        <textarea id="content" name="content" placeholder="Enter page content..."></textarea>
                    </div>
                    <div class="form-group">
                        <label for="parent">Parent Page:</label>
                        <select id="parent" name="parent">
                            {0}
                        </select>
                    </div>
                    <button type="submit" class="btn">Create Page</button>
                </form>
            </div>
        </body>
    </html>
"""

PAGE_CREATED_CONTENT = """
    <html>
        <head>
            <title>Page Created - WagtailCMS Admin</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                h1 {{ color: #00d4ff; }}
                a {{ color: #00d4ff; text-decoration: none; }}
                .nav {{ background: #0f3460; padding: 10px 20px; border-radius: 4px; margin-bottom: 20px; }}
                .nav a {{ margin-right: 20px; }}
                .success {{ background: #16213e; padding: 20px; border-radius: 4px; border-left: 4px solid #00ff88; }}
                .actions {{ margin-top: 20px; }}
                .btn {{ background: #00d4ff; color: #000; padding: 10px 20px; border-radius: 4px; display: inline-block; margin-right: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/admin">Dashboard</a>
                    <a href="/admin/pages">Pages</a>
                </div>
                <h1>Page Created Successfully</h1>
                <div class="success">
                    <p><strong>Title:</strong> {0}</p>
                    <p><strong>Page ID:</strong> {1}</p>
                    <p>Your page has been created and is now visible to administrators.</p>
                </div>
                <div class="actions">
                    <a href="/admin/pages/{1}/inspect" class="btn">Inspect Page</a>
                    <a href="/admin/pages/{1}/choose-parent" class="btn">Choose Parent</a>
                    <a href="/admin/pages/create" class="btn">Create Another</a>
                </div>
            </div>
        </body>
    </html>
"""

INSPECT_PAGE_CONTENT = """
    <html>
        <head>
            <title>Inspect Page - WagtailCMS Admin</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; margin: 0; padding: 20px; }}
                .container {{ max-width: 700px; margin: 0 auto; }}
                h1 {{ color: #00d4ff; }}
                a {{ color: #00d4ff; text-decoration: none; }}
                .nav {{ background: #0f3460; padding: 10px 20px; border-radius: 4px; margin-bottom: 20px; }}
                .nav a {{ margin-right: 20px; }}
                .detail-card {{ background: #16213e; padding: 20px; border-radius: 8px; margin: 10px 0; }}
                .field {{ margin-bottom: 15px; }}
                .field-label {{ color: #888; font-size: 12px; text-transform: uppercase; }}
                .field-value {{ font-size: 16px; margin-top: 5px; }}
                .title-display {{ font-size: 24px; color: #00d4ff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/admin">Dashboard</a>
                    <a href="/admin/pages">Pages</a>
                </div>
                <h1>Inspect Page</h1>
                <div class="detail-card">
                    <div class="field">
                        <div class="field-label">Title</div>
                        <div class="field-value title-display">{0}</div>
                    </div>
                    <div class="field">
                        <div class="field-label">Page ID</div>
                        <div class="field-value">{1}</div>
                    </div>
                    <div class="field">
                        <div class="field-label">Content</div>
                        <div class="field-value">{2}</div>
                    </div>
                    <div class="field">
                        <div class="field-label">Created By</div>
                        <div class="field-value">{3}</div>
                    </div>
                </div>
                <p><a href="/admin/pages/{1}/choose-parent">Choose Parent Page</a> | <a href="/admin/pages">Back to Pages</a></p>
            </div>
        </body>
    </html>
"""

INSPECT_PAGE_SUCCESS_CONTENT = """
    <html>
        <head>
            <title>Inspect Page - WagtailCMS Admin</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; margin: 0; padding: 20px; }}
                .container {{ max-width: 700px; margin: 0 auto; }}
                h1 {{ color: #00d4ff; }}
                a {{ color: #00d4ff; text-decoration: none; }}
                .nav {{ background: #0f3460; padding: 10px 20px; border-radius: 4px; margin-bottom: 20px; }}
                .nav a {{ margin-right: 20px; }}
                .detail-card {{ background: #16213e; padding: 20px; border-radius: 8px; margin: 10px 0; }}
                .field {{ margin-bottom: 15px; }}
                .field-label {{ color: #888; font-size: 12px; text-transform: uppercase; }}
                .field-value {{ font-size: 16px; margin-top: 5px; }}
                .flag-box {{ background: #004d40; padding: 20px; border-radius: 8px; border: 2px solid #00ff88; margin: 20px 0; }}
                .flag {{ font-family: monospace; font-size: 18px; color: #00ff88; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/admin">Dashboard</a>
                    <a href="/admin/pages">Pages</a>
                </div>
                <h1>Inspect Page</h1>
                <div class="flag-box">
                    <h3>XSS Vulnerability Exploited!</h3>
                    <p>Congratulations! You have successfully exploited a stored XSS vulnerability.</p>
                    <p class="flag">Flag: {4}</p>
                </div>
                <div class="detail-card">
                    <div class="field">
                        <div class="field-label">Title</div>
                        <div class="field-value">{0}</div>
                    </div>
                    <div class="field">
                        <div class="field-label">Page ID</div>
                        <div class="field-value">{1}</div>
                    </div>
                    <div class="field">
                        <div class="field-label">Content</div>
                        <div class="field-value">{2}</div>
                    </div>
                    <div class="field">
                        <div class="field-label">Created By</div>
                        <div class="field-value">{3}</div>
                    </div>
                </div>
            </div>
        </body>
    </html>
"""

CHOOSE_PARENT_CONTENT = """
    <html>
        <head>
            <title>Choose Parent Page - WagtailCMS Admin</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; margin: 0; padding: 20px; }}
                .container {{ max-width: 700px; margin: 0 auto; }}
                h1 {{ color: #00d4ff; }}
                a {{ color: #00d4ff; text-decoration: none; }}
                .nav {{ background: #0f3460; padding: 10px 20px; border-radius: 4px; margin-bottom: 20px; }}
                .nav a {{ margin-right: 20px; }}
                .breadcrumb {{ background: #16213e; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
                .breadcrumb-label {{ color: #888; font-size: 12px; margin-bottom: 5px; }}
                .card {{ background: #16213e; padding: 20px; border-radius: 8px; }}
                select {{ width: 100%; padding: 10px; border: none; border-radius: 4px; background: #0f3460; color: #fff; margin: 10px 0; }}
                .btn {{ background: #00d4ff; color: #000; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/admin">Dashboard</a>
                    <a href="/admin/pages">Pages</a>
                </div>
                <h1>Choose Parent Page</h1>
                <div class="breadcrumb">
                    <div class="breadcrumb-label">Current Location:</div>
                    <div>{0}</div>
                </div>
                <div class="card">
                    <p>Select a new parent page for this item (ID: {1}):</p>
                    <form method="POST" action="/admin/pages/{1}/update-parent">
                        <select name="new_parent">
                            {2}
                        </select>
                        <button type="submit" class="btn">Update Parent</button>
                    </form>
                </div>
                <p><a href="/admin/pages/{1}/inspect">Back to Inspect</a> | <a href="/admin/pages">Back to Pages</a></p>
            </div>
        </body>
    </html>
"""

CHOOSE_PARENT_SUCCESS_CONTENT = """
    <html>
        <head>
            <title>Choose Parent Page - WagtailCMS Admin</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; margin: 0; padding: 20px; }}
                .container {{ max-width: 700px; margin: 0 auto; }}
                h1 {{ color: #00d4ff; }}
                a {{ color: #00d4ff; text-decoration: none; }}
                .nav {{ background: #0f3460; padding: 10px 20px; border-radius: 4px; margin-bottom: 20px; }}
                .nav a {{ margin-right: 20px; }}
                .flag-box {{ background: #004d40; padding: 20px; border-radius: 8px; border: 2px solid #00ff88; margin: 20px 0; }}
                .flag {{ font-family: monospace; font-size: 18px; color: #00ff88; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/admin">Dashboard</a>
                    <a href="/admin/pages">Pages</a>
                </div>
                <h1>Choose Parent Page</h1>
                <div class="flag-box">
                    <h3>XSS Vulnerability Exploited!</h3>
                    <p>Congratulations! You have successfully exploited a stored XSS vulnerability in the breadcrumb display.</p>
                    <p class="flag">Flag: {2}</p>
                </div>
                <p>Page: {0} (ID: {1})</p>
                <p><a href="/admin/pages">Back to Pages</a></p>
            </div>
        </body>
    </html>
"""

# Keep original image routes for compatibility
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
