INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eZ Content Management - Home</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; }
        .header h1 { margin: 0; font-size: 24px; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .search-box { background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .search-box h2 { margin-top: 0; color: #2c3e50; }
        .search-input { width: 70%; padding: 10px; font-size: 16px; border: 1px solid #ddd; border-radius: 3px; }
        .search-btn { padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 16px; }
        .search-btn:hover { background: #2980b9; }
        .content-section { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .content-section h3 { color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .footer { background: #2c3e50; color: white; text-align: center; padding: 15px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>eZ Content Management System</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/content/search">Search</a>
        <a href="#">Content</a>
        <a href="#">Media</a>
        <a href="#">Administration</a>
    </div>
    <div class="container">
        <div class="search-box">
            <h2>Search Content</h2>
            <form action="/content/search" method="get">
                <input type="text" name="SearchText" class="search-input" placeholder="Enter search terms...">
                <button type="submit" class="search-btn">Search</button>
            </form>
        </div>
        <div class="content-section">
            <h3>Recent Content</h3>
            <ul>
                <li>Getting Started with eZ Platform</li>
                <li>Content Management Best Practices</li>
                <li>Advanced Search Configuration</li>
                <li>Template Design Guidelines</li>
            </ul>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 eZ Content Management System</p>
    </div>
</body>
</html>
"""


SEARCH_PAGE_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search - eZ Content Management</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .nav {{ background: #34495e; padding: 10px 20px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .search-box {{ background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .search-box h2 {{ margin-top: 0; color: #2c3e50; }}
        .search-input {{ width: 70%; padding: 10px; font-size: 16px; border: 1px solid #ddd; border-radius: 3px; }}
        .search-btn {{ padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 16px; }}
        .search-btn:hover {{ background: #2980b9; }}
        .results-section {{ background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .results-section h3 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
        .spellcheck-suggestion {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 15px; border-left: 4px solid #ffc107; }}
        .spellcheck-suggestion a {{ color: #856404; font-weight: bold; }}
        .search-results {{ padding: 10px 0; }}
        .search-results p {{ color: #666; }}
        .flag-result {{ background: #d4edda; padding: 15px; border-radius: 5px; margin-top: 15px; border-left: 4px solid #28a745; }}
        .footer {{ background: #2c3e50; color: white; text-align: center; padding: 15px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>eZ Content Management System</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/content/search">Search</a>
        <a href="#">Content</a>
        <a href="#">Media</a>
        <a href="#">Administration</a>
    </div>
    <div class="container">
        <div class="search-box">
            <h2>Search Content</h2>
            <form action="/content/search" method="get">
                <input type="text" name="SearchText" class="search-input" placeholder="Enter search terms..." value="{search_value}">
                <button type="submit" class="search-btn">Search</button>
            </form>
        </div>
        <div class="results-section">
            <h3>Search Results</h3>
            {spellcheck_suggestion}
            {search_results}
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 eZ Content Management System</p>
    </div>
</body>
</html>
"""


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
