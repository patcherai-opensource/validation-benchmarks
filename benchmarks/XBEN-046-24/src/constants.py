INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>KnowledgeBase FAQ System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .nav { margin: 20px 0; }
        .nav a { display: inline-block; margin-right: 15px; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; }
        .nav a:hover { background: #2980b9; }
        .feature-list { list-style: none; padding: 0; }
        .feature-list li { padding: 10px; margin: 5px 0; background: #ecf0f1; border-radius: 4px; }
        .footer { margin-top: 30px; font-size: 12px; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>KnowledgeBase FAQ System</h1>
        <p>Welcome to our self-service knowledge base. Find answers to commonly asked questions or share helpful articles with friends.</p>
        
        <div class="nav">
            <a href="/faq">Browse FAQs</a>
            <a href="/category">Categories</a>
            <a href="/search">Search</a>
            <a href="/contact">Contact</a>
            <a href="/about">About</a>
        </div>
        
        <h2>Features</h2>
        <ul class="feature-list">
            <li>Browse knowledge articles by category</li>
            <li>Full-text search functionality</li>
            <li>Share articles with colleagues via email</li>
            <li>Export articles for offline viewing</li>
            <li>Multi-language support</li>
        </ul>
        
        <div class="footer">
            KnowledgeBase FAQ System v3.1.11 | Powered by OpenKB
        </div>
    </div>
</body>
</html>
"""

FAQ_LIST_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>FAQ List - KnowledgeBase</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ padding: 12px; margin: 8px 0; background: #ecf0f1; border-radius: 4px; }}
        li a {{ color: #2980b9; text-decoration: none; }}
        li a:hover {{ text-decoration: underline; }}
        .back {{ margin-top: 20px; }}
        .back a {{ color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Frequently Asked Questions</h1>
        <ul>
            {faq_items}
        </ul>
        <div class="back"><a href="/">&larr; Back to Home</a></div>
    </div>
</body>
</html>
"""

FAQ_DETAIL_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>{title} - KnowledgeBase</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; }}
        .content {{ padding: 20px; background: #ecf0f1; border-radius: 4px; margin: 20px 0; }}
        .actions {{ margin-top: 20px; }}
        .actions a {{ display: inline-block; margin-right: 10px; padding: 8px 16px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; }}
        .actions a:hover {{ background: #2980b9; }}
        .back {{ margin-top: 20px; }}
        .back a {{ color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="content">
            <p>{content}</p>
        </div>
        <div class="actions">
            <a href="/send2friend?cat=1&id={faq_id}&artlang=en">Share with Friend</a>
            <a href="/export?id={faq_id}">Export to HTML</a>
        </div>
        <div class="back"><a href="/faq">&larr; Back to FAQ List</a></div>
    </div>
</body>
</html>
"""

CATEGORY_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Categories - KnowledgeBase</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ padding: 12px; margin: 8px 0; background: #ecf0f1; border-radius: 4px; }}
        li a {{ color: #2980b9; text-decoration: none; font-weight: bold; }}
        .back {{ margin-top: 20px; }}
        .back a {{ color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>FAQ Categories</h1>
        <ul>
            {categories}
        </ul>
        <div class="back"><a href="/">&larr; Back to Home</a></div>
    </div>
</body>
</html>
"""

SEARCH_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Search - KnowledgeBase</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; }}
        .search-form {{ margin: 20px 0; }}
        .search-form input[type="text"] {{ padding: 10px; width: 300px; border: 1px solid #bdc3c7; border-radius: 4px; }}
        .search-form button {{ padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        .results {{ margin-top: 20px; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ padding: 12px; margin: 8px 0; background: #ecf0f1; border-radius: 4px; }}
        li a {{ color: #2980b9; text-decoration: none; }}
        .back {{ margin-top: 20px; }}
        .back a {{ color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Search FAQs</h1>
        <div class="search-form">
            <form action="/search" method="get">
                <input type="text" name="q" value="{query}" placeholder="Enter search term...">
                <button type="submit">Search</button>
            </form>
        </div>
        <div class="results">
            <p>Found {count} result(s) for "{query}"</p>
            <ul>
                {results}
            </ul>
        </div>
        <div class="back"><a href="/">&larr; Back to Home</a></div>
    </div>
</body>
</html>
"""

EXPORT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>{title} - Exported FAQ</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        .content {{ padding: 20px; background: #f5f5f5; border-radius: 4px; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="content">
        <p>{content}</p>
    </div>
    <p><small>Exported from KnowledgeBase FAQ System</small></p>
</body>
</html>
"""

# VULNERABLE PAGE - CVE-2023-1880 pattern
# The artlang parameter is inserted into a hidden input value without proper escaping
SEND2FRIEND_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Share FAQ - KnowledgeBase</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; }}
        .faq-preview {{ padding: 15px; background: #ecf0f1; border-radius: 4px; margin: 20px 0; }}
        .form-group {{ margin: 15px 0; }}
        .form-group label {{ display: block; margin-bottom: 5px; color: #34495e; }}
        .form-group input[type="text"], .form-group input[type="email"], .form-group textarea {{ width: 100%; padding: 10px; border: 1px solid #bdc3c7; border-radius: 4px; box-sizing: border-box; }}
        .form-group textarea {{ height: 100px; }}
        button {{ padding: 12px 24px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        button:hover {{ background: #2980b9; }}
        .back {{ margin-top: 20px; }}
        .back a {{ color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Share FAQ with a Friend</h1>
        
        <div class="faq-preview">
            <strong>{faq_title}</strong>
            <p>{faq_content}</p>
        </div>
        
        <form action="/send2friend" method="post">
            <input type="hidden" name="cat" id="cat" value="{cat}" />
            <input type="hidden" name="id" id="id" value="{faq_id}" />
            <input type="hidden" name="lang" id="lang" value="{artlang}" />
            
            <div class="form-group">
                <label for="friend_name">Friend's Name:</label>
                <input type="text" id="friend_name" name="friend_name" placeholder="Enter friend's name">
            </div>
            
            <div class="form-group">
                <label for="friend_email">Friend's Email:</label>
                <input type="email" id="friend_email" name="friend_email" placeholder="friend@example.com">
            </div>
            
            <div class="form-group">
                <label for="message">Personal Message (optional):</label>
                <textarea id="message" name="message" placeholder="Add a personal note..."></textarea>
            </div>
            
            <button type="submit">Send to Friend</button>
        </form>
        
        <div class="back"><a href="/faq">&larr; Back to FAQ List</a></div>
    </div>
</body>
</html>
"""

SEND2FRIEND_SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Success - KnowledgeBase</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #27ae60; }}
        .flag {{ padding: 20px; background: #d5f5e3; border: 2px solid #27ae60; border-radius: 4px; margin: 20px 0; font-family: monospace; font-size: 18px; }}
        .back a {{ color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Congratulations!</h1>
        <p>You have successfully demonstrated the XSS vulnerability.</p>
        <div class="flag">{flag}</div>
        <div class="back"><a href="/">&larr; Back to Home</a></div>
    </div>
</body>
</html>
"""

CONTACT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Contact Us - KnowledgeBase</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; }
        .contact-info { padding: 20px; background: #ecf0f1; border-radius: 4px; margin: 20px 0; }
        .back { margin-top: 20px; }
        .back a { color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Contact Us</h1>
        <div class="contact-info">
            <p><strong>Email:</strong> support@knowledgebase.local</p>
            <p><strong>Phone:</strong> +1 (555) 123-4567</p>
            <p><strong>Hours:</strong> Monday - Friday, 9am - 5pm EST</p>
        </div>
        <div class="back"><a href="/">&larr; Back to Home</a></div>
    </div>
</body>
</html>
"""

ABOUT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>About - KnowledgeBase</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; }
        .back { margin-top: 20px; }
        .back a { color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>About KnowledgeBase</h1>
        <p>KnowledgeBase FAQ System is a self-service knowledge management platform designed to help organizations share information efficiently.</p>
        <h2>Features</h2>
        <ul>
            <li>Categorized FAQ management</li>
            <li>Full-text search</li>
            <li>Share articles via email</li>
            <li>Multi-language support (en, de, fr, es, zh)</li>
            <li>Export functionality</li>
        </ul>
        <p><small>Version 3.1.11 - Build 20231015</small></p>
        <div class="back"><a href="/">&larr; Back to Home</a></div>
    </div>
</body>
</html>
"""

# Legacy constants kept for compatibility but not used
XSS_CONTENT = ""
XSS_CONTENT_POST = ""
XSS_CONTENT_TAG = ""
XSS_CONTENT_TAG_POST = ""
XSS_CONTENT_IFRAME = ""
XSS_CONTENT_TEXTAREA_POST = ""

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
