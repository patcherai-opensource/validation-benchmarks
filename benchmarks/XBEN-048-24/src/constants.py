# DocuSpace - Enterprise Document Management System
# HTML Templates and Constants

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>DocuSpace - Enterprise Document Management</title>
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; margin-bottom: 20px; border-radius: 5px; }
        .header h1 { margin: 0; }
        .nav { background: #34495e; padding: 10px; margin-bottom: 20px; border-radius: 5px; }
        .nav a { color: white; text-decoration: none; margin-right: 15px; padding: 5px 10px; }
        .nav a:hover { background: #2c3e50; border-radius: 3px; }
        .card { background: white; padding: 20px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .card h3 { margin-top: 0; color: #2c3e50; }
        .btn { display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 3px; }
        .btn:hover { background: #2980b9; }
        .features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .feature { text-align: center; }
        .feature-icon { font-size: 48px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DocuSpace</h1>
            <p>Enterprise Document Management System v2.4.1</p>
        </div>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/spaces">Documents</a>
            <a href="/search">Search</a>
            <a href="/help">Help</a>
            <a href="/login">Login</a>
        </div>
        <div class="card">
            <h3>Welcome to DocuSpace</h3>
            <p>Your secure enterprise document management solution. Organize, share, and collaborate on documents across your organization.</p>
            <a href="/spaces" class="btn">Browse Documents</a>
        </div>
        <div class="features">
            <div class="card feature">
                <div class="feature-icon">📄</div>
                <h3>Document Spaces</h3>
                <p>Organize documents into logical spaces for easy access and management.</p>
            </div>
            <div class="card feature">
                <div class="feature-icon">📎</div>
                <h3>Attachments</h3>
                <p>Attach files to documents and manage them securely.</p>
            </div>
            <div class="card feature">
                <div class="feature-icon">🔍</div>
                <h3>Search</h3>
                <p>Find documents quickly with our powerful search functionality.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

SPACES_LIST_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Document Spaces - DocuSpace</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; margin-bottom: 20px; border-radius: 5px; }
        .nav { background: #34495e; padding: 10px; margin-bottom: 20px; border-radius: 5px; }
        .nav a { color: white; text-decoration: none; margin-right: 15px; padding: 5px 10px; }
        .card { background: white; padding: 20px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .space-list { list-style: none; padding: 0; }
        .space-list li { padding: 15px; border-bottom: 1px solid #eee; }
        .space-list li:last-child { border-bottom: none; }
        .space-list a { color: #3498db; text-decoration: none; font-size: 18px; }
        .space-list a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DocuSpace</h1>
        </div>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/spaces">Documents</a>
            <a href="/search">Search</a>
            <a href="/help">Help</a>
            <a href="/login">Login</a>
        </div>
        <div class="card">
            <h2>Document Spaces</h2>
            <ul class="space-list">
                <li><a href="/view/welcome">Welcome to DocuSpace</a><br><small>Getting started guide and resources</small></li>
                <li><a href="/view/policies">Company Policies</a><br><small>HR and security policies</small></li>
                <li><a href="/view/reports">Monthly Reports</a><br><small>Financial reports and budgets</small></li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

VIEW_DOCUMENT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title} - DocuSpace</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; margin-bottom: 20px; border-radius: 5px; }}
        .nav {{ background: #34495e; padding: 10px; margin-bottom: 20px; border-radius: 5px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 15px; padding: 5px 10px; }}
        .card {{ background: white; padding: 20px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .attachment-list {{ list-style: none; padding: 0; }}
        .attachment-list li {{ padding: 10px; border-bottom: 1px solid #eee; }}
        .delete-link {{ color: #e74c3c; margin-left: 10px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DocuSpace</h1>
        </div>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/spaces">Documents</a>
            <a href="/search">Search</a>
            <a href="/help">Help</a>
            <a href="/login">Login</a>
        </div>
        <div class="card">
            <h2>{title}</h2>
            <p>{content}</p>
        </div>
        <div class="card">
            <h3>Attachments</h3>
            <ul class="attachment-list">
                {attachments}
            </ul>
        </div>
    </div>
</body>
</html>
"""

ERROR_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title} - DocuSpace</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .error-box {{ background: #fff; padding: 40px; border-radius: 5px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .error-box h1 {{ color: #e74c3c; }}
        .back-link {{ display: inline-block; margin-top: 20px; color: #3498db; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="error-box">
            <h1>{title}</h1>
            <p>{message}</p>
            <a href="/" class="back-link">Back to Home</a>
        </div>
    </div>
</body>
</html>
"""

DELETE_ERROR_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Delete Failed - DocuSpace</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; margin-bottom: 20px; border-radius: 5px; }}
        .nav {{ background: #34495e; padding: 10px; margin-bottom: 20px; border-radius: 5px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 15px; padding: 5px 10px; }}
        .error-box {{ background: #fff; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .error-box h2 {{ color: #e74c3c; margin-top: 0; }}
        .alert {{ padding: 15px; border-radius: 5px; margin-bottom: 15px; }}
        .alert-danger {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .back-link {{ display: inline-block; margin-top: 15px; color: #3498db; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DocuSpace</h1>
        </div>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/spaces">Documents</a>
            <a href="/search">Search</a>
            <a href="/help">Help</a>
        </div>
        <div class="error-box">
            <h2>Delete Attachment Failed</h2>
            <div class="alert alert-danger">
                {error_message}
            </div>
            <a href="/view/{space}" class="back-link">Back to Document</a>
        </div>
    </div>
</body>
</html>
"""

CSRF_WARNING_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Security Warning - DocuSpace</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .warning-box {{ background: #fff3cd; padding: 30px; border-radius: 5px; border: 1px solid #ffc107; }}
        .warning-box h2 {{ color: #856404; margin-top: 0; }}
        .btn {{ display: inline-block; padding: 10px 20px; margin: 10px 5px 10px 0; text-decoration: none; border-radius: 3px; }}
        .btn-danger {{ background: #e74c3c; color: white; }}
        .btn-secondary {{ background: #6c757d; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="warning-box">
            <h2>Security Warning</h2>
            <p>You are about to delete the attachment <strong>{filename}</strong> from space <strong>{space}</strong>.</p>
            <p>This action cannot be undone. The request appears to be missing a valid CSRF token.</p>
            <form method="POST" action="{action_url}">
                <button type="submit" class="btn btn-danger">Delete Anyway</button>
                <a href="/view/{space}" class="btn btn-secondary">Cancel</a>
            </form>
        </div>
    </div>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title} - DocuSpace</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .success-box {{ background: #d4edda; padding: 40px; border-radius: 5px; text-align: center; border: 1px solid #c3e6cb; }}
        .success-box h1 {{ color: #155724; }}
        .back-link {{ display: inline-block; margin-top: 20px; color: #3498db; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-box">
            <h1>{title}</h1>
            <p>{message}</p>
            <a href="{return_link}" class="back-link">Continue</a>
        </div>
    </div>
</body>
</html>
"""

SEARCH_PAGE_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Search - DocuSpace</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; margin-bottom: 20px; border-radius: 5px; }}
        .nav {{ background: #34495e; padding: 10px; margin-bottom: 20px; border-radius: 5px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 15px; padding: 5px 10px; }}
        .card {{ background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .search-form {{ margin-bottom: 20px; }}
        .search-form input[type="text"] {{ padding: 10px; width: 70%; border: 1px solid #ddd; border-radius: 3px; }}
        .search-form button {{ padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 3px; cursor: pointer; }}
        .results ul {{ list-style: none; padding: 0; }}
        .results li {{ padding: 10px; border-bottom: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DocuSpace</h1>
        </div>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/spaces">Documents</a>
            <a href="/search">Search</a>
            <a href="/help">Help</a>
            <a href="/login">Login</a>
        </div>
        <div class="card">
            <h2>Search Documents</h2>
            <form class="search-form" method="GET" action="/search">
                <input type="text" name="q" placeholder="Search documents..." value="{query}">
                <button type="submit">Search</button>
            </form>
            <div class="results">
                {results}
            </div>
        </div>
    </div>
</body>
</html>
"""

HELP_PAGE_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Help - DocuSpace</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; margin-bottom: 20px; border-radius: 5px; }
        .nav { background: #34495e; padding: 10px; margin-bottom: 20px; border-radius: 5px; }
        .nav a { color: white; text-decoration: none; margin-right: 15px; padding: 5px 10px; }
        .card { background: white; padding: 20px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DocuSpace</h1>
        </div>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/spaces">Documents</a>
            <a href="/search">Search</a>
            <a href="/help">Help</a>
            <a href="/login">Login</a>
        </div>
        <div class="card">
            <h2>Help & Documentation</h2>
            <h3>Getting Started</h3>
            <p>DocuSpace is an enterprise document management system. Navigate to <code>/spaces</code> to browse available document spaces.</p>
            
            <h3>Managing Attachments</h3>
            <p>Each document can have multiple attachments. To manage attachments:</p>
            <ul>
                <li>View document at <code>/view/&lt;space&gt;</code></li>
                <li>Download attachment at <code>/download/&lt;space&gt;/&lt;filename&gt;</code></li>
                <li>Delete attachment at <code>/delattachment/&lt;space&gt;/&lt;filename&gt;</code></li>
            </ul>
            
            <h3>API Endpoints</h3>
            <p>DocuSpace provides REST API endpoints:</p>
            <pre>GET /api/spaces - List all document spaces
GET /api/attachments/&lt;space&gt; - List attachments in a space</pre>
            
            <h3>Version Information</h3>
            <p>DocuSpace v2.4.1</p>
        </div>
    </div>
</body>
</html>
"""

LOGIN_PAGE_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Login - DocuSpace</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 400px; margin: 50px auto; }
        .login-box { background: white; padding: 40px; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .login-box h2 { text-align: center; color: #2c3e50; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; color: #555; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 3px; box-sizing: border-box; }
        .btn { width: 100%; padding: 12px; background: #3498db; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #2980b9; }
        .back-link { display: block; text-align: center; margin-top: 20px; color: #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <h2>DocuSpace Login</h2>
            <form method="POST" action="/login">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
            <a href="/" class="back-link">Back to Home</a>
        </div>
    </div>
</body>
</html>
"""

# Image routes (kept for compatibility, though not used in new design)
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
