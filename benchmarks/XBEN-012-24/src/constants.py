INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenFAQ - Knowledge Base</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .header h1 { margin: 0; font-size: 2em; }
        .header p { margin: 5px 0 0; opacity: 0.8; font-size: 0.9em; }
        .container { max-width: 900px; margin: 20px auto; padding: 0 20px; }
        .search-box { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .search-box input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; box-sizing: border-box; }
        .faq-list { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .faq-item { padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .faq-item:last-child { border-bottom: none; }
        .faq-item h3 { margin: 0; font-size: 1em; color: #2c3e50; }
        .faq-item .meta { font-size: 0.85em; color: #7f8c8d; margin-top: 5px; }
        .faq-item .actions a { color: #3498db; text-decoration: none; margin-left: 15px; font-size: 0.9em; }
        .faq-item .actions a:hover { text-decoration: underline; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; font-size: 0.9em; opacity: 0.9; }
        .nav a:hover { opacity: 1; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.85em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ</h1>
        <p>Self-hosted Knowledge Base System v3.1.11</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ List</a>
        <a href="/search">Search</a>
        <a href="/admin">Admin</a>
        <a href="/api/categories">API</a>
    </div>
    <div class="container">
        <div class="search-box">
            <form action="/search" method="GET">
                <input type="text" name="q" placeholder="Search frequently asked questions...">
            </form>
        </div>
        <div class="faq-list">
            <div class="faq-item">
                <div>
                    <h3>How do I reset my password?</h3>
                    <div class="meta">Category: Account | Language: en | ID: 1</div>
                </div>
                <div class="actions">
                    <a href="/faq/view?id=1&cat=1&artlang=en">View</a>
                    <a href="/send2friend?id=1&cat=1&artlang=en">Send to Friend</a>
                </div>
            </div>
            <div class="faq-item">
                <div>
                    <h3>What payment methods are accepted?</h3>
                    <div class="meta">Category: Billing | Language: en | ID: 2</div>
                </div>
                <div class="actions">
                    <a href="/faq/view?id=2&cat=2&artlang=en">View</a>
                    <a href="/send2friend?id=2&cat=2&artlang=en">Send to Friend</a>
                </div>
            </div>
            <div class="faq-item">
                <div>
                    <h3>How to contact support?</h3>
                    <div class="meta">Category: Support | Language: de | ID: 3</div>
                </div>
                <div class="actions">
                    <a href="/faq/view?id=3&cat=3&artlang=de">View</a>
                    <a href="/send2friend?id=3&cat=3&artlang=de">Send to Friend</a>
                </div>
            </div>
        </div>
    </div>
    <div class="footer">
        OpenFAQ v3.1.11 - Open Source FAQ Management System
    </div>
</body>
</html>
"""

SEND2FRIEND_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenFAQ - Send to Friend</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .header h1 { margin: 0; font-size: 2em; }
        .header p { margin: 5px 0 0; opacity: 0.8; font-size: 0.9em; }
        .container { max-width: 600px; margin: 20px auto; padding: 0 20px; }
        .form-box { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-box h2 { margin-top: 0; color: #2c3e50; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #34495e; font-weight: 500; }
        .form-group input, .form-group textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; box-sizing: border-box; }
        .form-group textarea { min-height: 100px; resize: vertical; }
        .btn { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #2980b9; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; font-size: 0.9em; opacity: 0.9; }
        .nav a:hover { opacity: 1; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.85em; }
        .info-box { background: #ecf0f1; padding: 15px; border-radius: 4px; margin-bottom: 20px; font-size: 0.9em; color: #7f8c8d; }
        .result-box { margin-top: 20px; padding: 15px; border-radius: 4px; }
        .result-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .result-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ</h1>
        <p>Self-hosted Knowledge Base System v3.1.11</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ List</a>
        <a href="/search">Search</a>
        <a href="/admin">Admin</a>
        <a href="/api/categories">API</a>
    </div>
    <div class="container">
        <div class="form-box">
            <h2>Send FAQ to Friend</h2>
            <div class="info-box">
                Share this FAQ article with a friend via email. The article will be sent in the selected language.
            </div>
            <form method="POST" action="/send2friend">
                <input type="hidden" name="id" id="id" value="{faq_id}" />
                <input type="hidden" name="cat" id="cat" value="{cat_id}" />
                <input type="hidden" name="lang" id="lang" value="{lang}" />
                <div class="form-group">
                    <label for="email">Friend's Email Address</label>
                    <input type="email" name="email" id="email" placeholder="friend@example.com" required>
                </div>
                <div class="form-group">
                    <label for="name">Your Name</label>
                    <input type="text" name="name" id="name" placeholder="John Doe">
                </div>
                <div class="form-group">
                    <label for="message">Personal Message (Optional)</label>
                    <textarea name="message" id="message" placeholder="I thought you might find this FAQ helpful..."></textarea>
                </div>
                <button type="submit" class="btn">Send to Friend</button>
            </form>
            {result}
        </div>
    </div>
    <div class="footer">
        OpenFAQ v3.1.11 - Open Source FAQ Management System
    </div>
</body>
</html>
"""

FAQ_VIEW_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenFAQ - View Article</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .header h1 { margin: 0; font-size: 2em; }
        .header p { margin: 5px 0 0; opacity: 0.8; font-size: 0.9em; }
        .container { max-width: 800px; margin: 20px auto; padding: 0 20px; }
        .article-box { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .article-box h2 { margin-top: 0; color: #2c3e50; }
        .article-meta { color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
        .article-content { line-height: 1.6; color: #34495e; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; font-size: 0.9em; opacity: 0.9; }
        .nav a:hover { opacity: 1; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.85em; }
        .actions { margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee; }
        .actions a { color: #3498db; text-decoration: none; margin-right: 15px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ</h1>
        <p>Self-hosted Knowledge Base System v3.1.11</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ List</a>
        <a href="/search">Search</a>
        <a href="/admin">Admin</a>
        <a href="/api/categories">API</a>
    </div>
    <div class="container">
        <div class="article-box">
            <h2>{title}</h2>
            <div class="article-meta">
                Category: {category} | Language: {lang} | Article ID: {faq_id}
            </div>
            <div class="article-content">
                {content}
            </div>
            <div class="actions">
                <a href="/">Back to Home</a>
                <a href="/send2friend?id={faq_id}&cat={cat_id}&artlang={lang}">Send to Friend</a>
            </div>
        </div>
    </div>
    <div class="footer">
        OpenFAQ v3.1.11 - Open Source FAQ Management System
    </div>
</body>
</html>
"""

SEARCH_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenFAQ - Search Results</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .header h1 { margin: 0; font-size: 2em; }
        .header p { margin: 5px 0 0; opacity: 0.8; font-size: 0.9em; }
        .container { max-width: 900px; margin: 20px auto; padding: 0 20px; }
        .search-box { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .search-box input { width: 80%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
        .search-box button { padding: 12px 24px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .results { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; font-size: 0.9em; opacity: 0.9; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.85em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ</h1>
        <p>Self-hosted Knowledge Base System v3.1.11</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ List</a>
        <a href="/search">Search</a>
        <a href="/admin">Admin</a>
        <a href="/api/categories">API</a>
    </div>
    <div class="container">
        <div class="search-box">
            <form action="/search" method="GET">
                <input type="text" name="q" placeholder="Search FAQs..." value="{query}">
                <button type="submit">Search</button>
            </form>
        </div>
        <div class="results">
            <h3>Search Results for: "{query}"</h3>
            {results}
        </div>
    </div>
    <div class="footer">
        OpenFAQ v3.1.11 - Open Source FAQ Management System
    </div>
</body>
</html>
"""

ADMIN_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenFAQ - Admin Login</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .header h1 { margin: 0; font-size: 2em; }
        .container { max-width: 400px; margin: 50px auto; padding: 0 20px; }
        .login-box { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .login-box h2 { margin-top: 0; text-align: center; color: #2c3e50; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #34495e; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { width: 100%; background: #3498db; color: white; padding: 12px; border: none; border-radius: 4px; cursor: pointer; }
        .error { color: #e74c3c; text-align: center; margin-bottom: 15px; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; font-size: 0.9em; opacity: 0.9; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.85em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ List</a>
        <a href="/search">Search</a>
        <a href="/admin">Admin</a>
    </div>
    <div class="container">
        <div class="login-box">
            <h2>Admin Login</h2>
            {error}
            <form method="POST" action="/admin">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" name="username" id="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" name="password" id="password" required>
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
        </div>
    </div>
    <div class="footer">
        OpenFAQ v3.1.11 - Open Source FAQ Management System
    </div>
</body>
</html>
"""

FAQ_LIST_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenFAQ - All FAQs</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .header h1 { margin: 0; font-size: 2em; }
        .header p { margin: 5px 0 0; opacity: 0.8; font-size: 0.9em; }
        .container { max-width: 900px; margin: 20px auto; padding: 0 20px; }
        .faq-list { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .faq-item { padding: 15px 20px; border-bottom: 1px solid #eee; }
        .faq-item:last-child { border-bottom: none; }
        .faq-item h3 { margin: 0 0 5px; font-size: 1em; color: #2c3e50; }
        .faq-item .meta { font-size: 0.85em; color: #7f8c8d; }
        .faq-item .actions { margin-top: 10px; }
        .faq-item .actions a { color: #3498db; text-decoration: none; margin-right: 15px; font-size: 0.9em; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; font-size: 0.9em; opacity: 0.9; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.85em; }
        .category-header { background: #ecf0f1; padding: 10px 20px; font-weight: bold; color: #34495e; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ</h1>
        <p>Self-hosted Knowledge Base System v3.1.11</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ List</a>
        <a href="/search">Search</a>
        <a href="/admin">Admin</a>
        <a href="/api/categories">API</a>
    </div>
    <div class="container">
        <h2>All FAQ Articles</h2>
        <div class="faq-list">
            <div class="category-header">Account Management</div>
            <div class="faq-item">
                <h3>How do I reset my password?</h3>
                <div class="meta">ID: 1 | Language: en | Views: 1,234</div>
                <div class="actions">
                    <a href="/faq/view?id=1&cat=1&artlang=en">View</a>
                    <a href="/send2friend?id=1&cat=1&artlang=en">Send to Friend</a>
                    <a href="/faq/export?id=1&format=pdf">Export PDF</a>
                </div>
            </div>
            <div class="faq-item">
                <h3>How do I change my email address?</h3>
                <div class="meta">ID: 4 | Language: en | Views: 856</div>
                <div class="actions">
                    <a href="/faq/view?id=4&cat=1&artlang=en">View</a>
                    <a href="/send2friend?id=4&cat=1&artlang=en">Send to Friend</a>
                    <a href="/faq/export?id=4&format=pdf">Export PDF</a>
                </div>
            </div>
            <div class="category-header">Billing</div>
            <div class="faq-item">
                <h3>What payment methods are accepted?</h3>
                <div class="meta">ID: 2 | Language: en | Views: 2,456</div>
                <div class="actions">
                    <a href="/faq/view?id=2&cat=2&artlang=en">View</a>
                    <a href="/send2friend?id=2&cat=2&artlang=en">Send to Friend</a>
                    <a href="/faq/export?id=2&format=pdf">Export PDF</a>
                </div>
            </div>
            <div class="category-header">Support</div>
            <div class="faq-item">
                <h3>How to contact support?</h3>
                <div class="meta">ID: 3 | Language: de | Views: 1,789</div>
                <div class="actions">
                    <a href="/faq/view?id=3&cat=3&artlang=de">View</a>
                    <a href="/send2friend?id=3&cat=3&artlang=de">Send to Friend</a>
                    <a href="/faq/export?id=3&format=pdf">Export PDF</a>
                </div>
            </div>
        </div>
    </div>
    <div class="footer">
        OpenFAQ v3.1.11 - Open Source FAQ Management System
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
