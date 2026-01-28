# eZ Find CMS Portal - Constants and Templates

INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eZ Find - Content Management Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #fff; }
        .header { background: rgba(0,0,0,0.3); padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; color: #4da6ff; }
        .nav { display: flex; gap: 20px; }
        .nav a { color: #aaa; text-decoration: none; transition: color 0.3s; }
        .nav a:hover { color: #4da6ff; }
        .hero { text-align: center; padding: 80px 20px; }
        .hero h1 { font-size: 48px; margin-bottom: 20px; }
        .hero p { font-size: 18px; color: #aaa; margin-bottom: 40px; }
        .search-box { max-width: 600px; margin: 0 auto; position: relative; }
        .search-box input { width: 100%; padding: 15px 20px; font-size: 18px; border: none; border-radius: 30px; background: rgba(255,255,255,0.1); color: #fff; }
        .search-box input::placeholder { color: #888; }
        .search-box button { position: absolute; right: 5px; top: 5px; padding: 10px 25px; background: #4da6ff; color: #fff; border: none; border-radius: 25px; cursor: pointer; }
        .features { display: flex; justify-content: center; gap: 40px; padding: 60px 20px; }
        .feature { text-align: center; max-width: 200px; }
        .feature h3 { margin: 15px 0 10px; }
        .feature p { color: #888; font-size: 14px; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">eZ Find</div>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/content/search">Search</a>
            <a href="/browse">Browse</a>
            <a href="/sitemap">Sitemap</a>
            <a href="/help">Help</a>
            <a href="/admin">Admin</a>
        </div>
    </div>
    <div class="hero">
        <h1>Enterprise Content Search</h1>
        <p>Powered by Apache Solr - Fast, reliable, and intelligent search across your content repository</p>
        <form action="/content/search" method="GET" class="search-box">
            <input type="text" name="SearchText" placeholder="Search articles, documents, media...">
            <button type="submit">Search</button>
        </form>
    </div>
    <div class="features">
        <div class="feature">
            <h3>Full-Text Search</h3>
            <p>Advanced indexing with Solr integration</p>
        </div>
        <div class="feature">
            <h3>Spellcheck</h3>
            <p>Intelligent suggestions for better results</p>
        </div>
        <div class="feature">
            <h3>Faceted Navigation</h3>
            <p>Filter by category, date, and more</p>
        </div>
    </div>
    <div class="footer">
        <p>eZ Find Extension v5.4.2 | eZ Platform CMS | &copy; 2024</p>
    </div>
</body>
</html>
"""

SEARCH_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Results - eZ Find</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #fff; }}
        .header {{ background: rgba(0,0,0,0.3); padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #4da6ff; }}
        .nav {{ display: flex; gap: 20px; }}
        .nav a {{ color: #aaa; text-decoration: none; }}
        .nav a:hover {{ color: #4da6ff; }}
        .search-container {{ max-width: 800px; margin: 40px auto; padding: 0 20px; }}
        .search-form {{ display: flex; gap: 10px; margin-bottom: 30px; }}
        .search-form input {{ flex: 1; padding: 12px 20px; font-size: 16px; border: none; border-radius: 25px; background: rgba(255,255,255,0.1); color: #fff; }}
        .search-form button {{ padding: 12px 30px; background: #4da6ff; color: #fff; border: none; border-radius: 25px; cursor: pointer; }}
        .results {{ background: rgba(255,255,255,0.05); border-radius: 10px; padding: 30px; }}
        .no-results {{ color: #aaa; text-align: center; padding: 40px; }}
        .spellcheck {{ background: rgba(255,193,7,0.1); padding: 15px 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107; }}
        .spellcheck a {{ color: #ffc107; text-decoration: none; }}
        .spellcheck a:hover {{ text-decoration: underline; }}
        .flag-reveal {{ background: rgba(76, 175, 80, 0.2); padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #4CAF50; }}
        .flag-reveal h2 {{ color: #4CAF50; margin-bottom: 10px; }}
        .flag-reveal code {{ background: #000; padding: 5px 10px; border-radius: 4px; font-family: monospace; }}
        .footer {{ text-align: center; padding: 40px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <a href="/" class="logo">eZ Find</a>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/content/search">Search</a>
            <a href="/browse">Browse</a>
            <a href="/sitemap">Sitemap</a>
            <a href="/help">Help</a>
        </div>
    </div>
    <div class="search-container">
        <form action="/content/search" method="GET" class="search-form">
            <input type="text" name="SearchText" value="{search_value}" placeholder="Enter search terms...">
            <button type="submit">Search</button>
        </form>
        <div class="results">
            {search_results}
            {spellcheck_suggestion}
            {flag_result}
        </div>
    </div>
    <div class="footer">
        <p>eZ Find Extension v5.4.2 | Solr Search Engine</p>
    </div>
</body>
</html>
"""

ADMIN_LOGIN_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Login - eZ Find</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: rgba(255,255,255,0.05); padding: 40px; border-radius: 10px; width: 300px; }
        .login-box h2 { color: #4da6ff; margin-bottom: 20px; text-align: center; }
        .login-box input { width: 100%; padding: 10px; margin-bottom: 15px; border: none; border-radius: 5px; background: rgba(255,255,255,0.1); color: #fff; }
        .login-box button { width: 100%; padding: 10px; background: #4da6ff; color: #fff; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Admin Panel</h2>
        <form action="/admin/login" method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

SITEMAP_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sitemap - eZ Find</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; padding: 40px; }
        h1 { color: #4da6ff; margin-bottom: 30px; }
        ul { list-style: none; }
        li { margin: 10px 0; }
        a { color: #aaa; text-decoration: none; }
        a:hover { color: #4da6ff; }
    </style>
</head>
<body>
    <h1>Site Map</h1>
    <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/content/search">Search Portal</a>
            <ul>
                <li>Full-text search with Solr</li>
                <li>Spellcheck suggestions</li>
                <li>Advanced filters</li>
            </ul>
        </li>
        <li><a href="/browse">Browse Content</a></li>
        <li><a href="/api/v1/status">API Status</a></li>
        <li><a href="/api/v1/suggest">Search Suggestions API</a></li>
        <li><a href="/help">Help & Documentation</a></li>
        <li><a href="/admin">Admin Panel</a></li>
    </ul>
</body>
</html>
"""

HELP_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Help - eZ Find</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; padding: 40px; max-width: 800px; margin: 0 auto; }
        h1 { color: #4da6ff; margin-bottom: 30px; }
        h2 { color: #4da6ff; margin-top: 30px; font-size: 18px; }
        p { color: #aaa; line-height: 1.6; }
        code { background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 3px; }
        .back { display: inline-block; margin-top: 30px; color: #4da6ff; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Help & Documentation</h1>
    
    <h2>Search Syntax</h2>
    <p>Use the search box to find content across the repository. The search engine supports:</p>
    <ul style="color: #aaa; margin: 10px 0 10px 20px;">
        <li>Simple keyword searches</li>
        <li>Phrase searches using quotes: <code>"exact phrase"</code></li>
        <li>Boolean operators: AND, OR, NOT</li>
    </ul>
    
    <h2>Spellcheck Feature</h2>
    <p>The search engine automatically suggests corrections for misspelled queries. When no results are found, you may see a "Did you mean...?" suggestion powered by the Solr spellcheck component.</p>
    
    <h2>API Endpoints</h2>
    <p>Developers can use the following API endpoints:</p>
    <ul style="color: #aaa; margin: 10px 0 10px 20px;">
        <li><code>GET /api/v1/status</code> - Service health check</li>
        <li><code>GET /api/v1/suggest?q=query</code> - Search suggestions</li>
    </ul>
    
    <h2>Version Information</h2>
    <p>eZ Find Extension v5.4.2<br>Compatible with eZ Platform 3.x<br>Solr 8.x integration</p>
    
    <a href="/" class="back">&larr; Back to Home</a>
</body>
</html>
"""

BROWSE_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Browse - eZ Find</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #fff; padding: 40px; }}
        h1 {{ color: #4da6ff; margin-bottom: 30px; }}
        .category {{ color: #aaa; margin-bottom: 20px; }}
        .items {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }}
        .item {{ background: rgba(255,255,255,0.05); padding: 20px; border-radius: 8px; }}
        .item h3 {{ color: #4da6ff; margin-bottom: 10px; }}
        .item p {{ color: #888; font-size: 14px; }}
        .back {{ display: inline-block; margin-top: 30px; color: #4da6ff; text-decoration: none; }}
    </style>
</head>
<body>
    <h1>Browse Content</h1>
    <p class="category">Category: {category}</p>
    <div class="items">
        <div class="item">
            <h3>Getting Started Guide</h3>
            <p>Introduction to eZ Platform CMS</p>
        </div>
        <div class="item">
            <h3>API Documentation</h3>
            <p>REST API reference for developers</p>
        </div>
        <div class="item">
            <h3>Search Configuration</h3>
            <p>Configure Solr search settings</p>
        </div>
        <div class="item">
            <h3>User Management</h3>
            <p>Managing users and permissions</p>
        </div>
    </div>
    <a href="/" class="back">&larr; Back to Home</a>
</body>
</html>
"""

# Legacy template references (kept for compatibility but not used)
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
