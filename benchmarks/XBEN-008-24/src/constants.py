INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eZContent - Enterprise Content Management</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .header {
            background: rgba(255,255,255,0.95);
            padding: 20px 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
        }
        .tagline {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        .container {
            max-width: 900px;
            margin: 60px auto;
            padding: 40px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .search-box {
            display: flex;
            margin-bottom: 30px;
        }
        .search-input {
            flex: 1;
            padding: 15px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 5px 0 0 5px;
            outline: none;
        }
        .search-input:focus {
            border-color: #667eea;
        }
        .search-btn {
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 0 5px 5px 0;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        .search-btn:hover {
            background: #5568d3;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        .feature {
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .feature h3 {
            margin-top: 0;
            color: #667eea;
        }
        .nav-links {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        .nav-links a {
            color: #667eea;
            text-decoration: none;
            margin-right: 20px;
        }
        .nav-links a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">eZContent</div>
        <div class="tagline">Enterprise Content Management System</div>
    </div>
    <div class="container">
        <h1>Welcome to eZContent Search</h1>
        <p class="subtitle">Find documents, articles, and content across your organization</p>
        
        <form action="/content/search" method="get" class="search-box">
            <input type="text" name="SearchText" class="search-input" placeholder="Search for content..." required>
            <button type="submit" class="search-btn">Search</button>
        </form>
        
        <div class="features">
            <div class="feature">
                <h3>Fast Search</h3>
                <p>Powered by advanced indexing technology for instant results</p>
            </div>
            <div class="feature">
                <h3>Smart Suggestions</h3>
                <p>Get helpful spell-check suggestions when searching</p>
            </div>
            <div class="feature">
                <h3>Content Discovery</h3>
                <p>Explore related content and recommendations</p>
            </div>
        </div>
        
        <div class="nav-links">
            <a href="/about">About</a>
            <a href="/help">Help</a>
            <a href="/api/status">API Status</a>
            <a href="/admin">Admin</a>
        </div>
    </div>
</body>
</html>
"""

SEARCH_RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Results - eZContent</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f6fa;
            min-height: 100vh;
        }
        .header {
            background: white;
            padding: 15px 40px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 30px;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            text-decoration: none;
        }
        .search-form {
            display: flex;
            flex: 1;
            max-width: 600px;
        }
        .search-input {
            flex: 1;
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 4px 0 0 4px;
            font-size: 14px;
        }
        .search-btn {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 0 4px 4px 0;
            cursor: pointer;
        }
        .container {
            max-width: 800px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .result-count {
            color: #666;
            margin-bottom: 20px;
        }
        .spellcheck-suggestion {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .spellcheck-suggestion a {
            color: #667eea;
            font-weight: bold;
        }
        .result-item {
            background: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .result-title {
            color: #667eea;
            font-size: 18px;
            margin-bottom: 5px;
        }
        .result-url {
            color: #0d6efd;
            font-size: 13px;
            margin-bottom: 8px;
        }
        .result-snippet {
            color: #666;
            font-size: 14px;
            line-height: 1.5;
        }
        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        .flag-section {
            background: #d4edda;
            border: 1px solid #28a745;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
            text-align: center;
        }
        .error-msg {
            background: #f8d7da;
            border: 1px solid #dc3545;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="/" class="logo">eZContent</a>
        <form action="/content/search" method="get" class="search-form">
            <input type="text" name="SearchText" class="search-input" placeholder="Search..." value="{query_escaped}">
            <button type="submit" class="search-btn">Search</button>
        </form>
    </div>
    <div class="container">
        {error_section}
        {spellcheck_section}
        {result_section}
        {flag_section}
    </div>
</body>
</html>
"""

ABOUT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>About - eZContent</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f5f6fa; }
        .container { max-width: 700px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
        h1 { color: #667eea; }
        a { color: #667eea; }
    </style>
</head>
<body>
    <div class="container">
        <h1>About eZContent</h1>
        <p>eZContent is an enterprise content management system based on the eZ Platform architecture.</p>
        <p>Version: 5.4.14</p>
        <p>Build: 2019.03.15</p>
        <h2>Features</h2>
        <ul>
            <li>Full-text search with Solr integration</li>
            <li>Spell-check and search suggestions</li>
            <li>Multi-language support</li>
            <li>REST API access</li>
        </ul>
        <p><a href="/">Back to Search</a></p>
    </div>
</body>
</html>
"""

HELP_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Help - eZContent</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f5f6fa; }
        .container { max-width: 700px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
        h1 { color: #667eea; }
        a { color: #667eea; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Search Help</h1>
        <h2>Search Endpoints</h2>
        <p>The primary search endpoint is <code>/content/search</code> with parameter <code>SearchText</code>.</p>
        <h2>Search Tips</h2>
        <ul>
            <li>Use quotes for exact phrase matching</li>
            <li>Use + to require a term</li>
            <li>Use - to exclude a term</li>
        </ul>
        <h2>Spellcheck</h2>
        <p>If your search term appears to have a typo, the system will suggest corrections using the "Did you mean...?" feature.</p>
        <p><a href="/">Back to Search</a></p>
    </div>
</body>
</html>
"""

ADMIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Login - eZContent</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f5f6fa; }
        .container { max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
        h1 { color: #667eea; text-align: center; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #5568d3; }
        .back { text-align: center; margin-top: 20px; }
        .back a { color: #667eea; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Login</h1>
        <form method="post" action="/admin/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <div class="back"><a href="/">Back to Search</a></div>
    </div>
</body>
</html>
"""

API_STATUS = {
    "status": "operational",
    "version": "5.4.14",
    "services": {
        "search": "online",
        "spellcheck": "online", 
        "content": "online"
    },
    "endpoints": [
        "/content/search",
        "/api/status",
        "/api/suggest"
    ]
}

# Image routes (kept for compatibility but not used in new design)
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
