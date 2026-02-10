INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>phpMyFAQ - Open Source FAQ System</title>
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .header h1 { margin: 0; }
        .container { max-width: 1000px; margin: 20px auto; padding: 20px; }
        .nav { background: #34495e; padding: 10px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; padding: 5px 10px; }
        .nav a:hover { background: #2c3e50; }
        .content { background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .welcome { font-size: 18px; line-height: 1.6; }
        .features { margin-top: 20px; }
        .feature-item { background: #ecf0f1; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
        <p>Open Source FAQ System</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ</a>
    </div>
    <div class="container">
        <div class="content">
            <div class="welcome">
                <h2>Welcome to phpMyFAQ</h2>
                <p>phpMyFAQ is a multilingual, completely database-driven FAQ-system. It supports various databases and PHP 7+.</p>
            </div>
            <div class="features">
                <div class="feature-item">
                    <strong>Browse FAQs</strong><br>
                    Visit our <a href="/faq">FAQ section</a> to find answers to common questions.
                </div>
                <div class="feature-item">
                    <strong>Share with Friends</strong><br>
                    Found a useful article? Use the "Send to Friend" feature to share it.
                </div>
            </div>
        </div>
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
    <title>FAQ Categories - phpMyFAQ</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .header h1 {{ margin: 0; }}
        .nav {{ background: #34495e; padding: 10px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; padding: 5px 10px; }}
        .nav a:hover {{ background: #2c3e50; }}
        .container {{ max-width: 1000px; margin: 20px auto; padding: 20px; }}
        .content {{ background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .category-item {{ background: #ecf0f1; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }}
        .category-item a {{ color: #2980b9; text-decoration: none; }}
        .category-item a:hover {{ text-decoration: underline; }}
        .desc {{ color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
        <p>Open Source FAQ System</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ</a>
    </div>
    <div class="container">
        <div class="content">
            <h2>FAQ Categories</h2>
            {0}
        </div>
    </div>
</body>
</html>
"""

FAQ_CATEGORY_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{0} - phpMyFAQ</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .header h1 {{ margin: 0; }}
        .nav {{ background: #34495e; padding: 10px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; padding: 5px 10px; }}
        .nav a:hover {{ background: #2c3e50; }}
        .container {{ max-width: 1000px; margin: 20px auto; padding: 20px; }}
        .content {{ background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .article-item {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
        .article-item a {{ color: #2980b9; text-decoration: none; }}
        .article-item a:hover {{ text-decoration: underline; }}
        .breadcrumb {{ margin-bottom: 20px; color: #666; }}
        .breadcrumb a {{ color: #2980b9; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
        <p>Open Source FAQ System</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ</a>
    </div>
    <div class="container">
        <div class="content">
            <div class="breadcrumb"><a href="/faq">FAQ</a> &gt; {0}</div>
            <h2>{0}</h2>
            {1}
        </div>
    </div>
</body>
</html>
"""

FAQ_ARTICLE_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{0} - phpMyFAQ</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .header h1 {{ margin: 0; }}
        .nav {{ background: #34495e; padding: 10px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; padding: 5px 10px; }}
        .nav a:hover {{ background: #2c3e50; }}
        .container {{ max-width: 1000px; margin: 20px auto; padding: 20px; }}
        .content {{ background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .article-content {{ line-height: 1.6; margin: 20px 0; }}
        .actions {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
        .actions a {{ color: #2980b9; margin-right: 20px; }}
        .breadcrumb {{ margin-bottom: 20px; color: #666; }}
        .breadcrumb a {{ color: #2980b9; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
        <p>Open Source FAQ System</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ</a>
    </div>
    <div class="container">
        <div class="content">
            <div class="breadcrumb"><a href="/faq">FAQ</a> &gt; Article</div>
            <h2>{0}</h2>
            <div class="article-content">
                {1}
            </div>
            <div class="actions">
                <a href="/send2friend?cat={3}&id={2}&artlang={4}">Send to Friend</a>
                <a href="/faq">Back to FAQ</a>
            </div>
        </div>
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
    <title>Send to Friend - phpMyFAQ</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .header h1 {{ margin: 0; }}
        .nav {{ background: #34495e; padding: 10px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; padding: 5px 10px; }}
        .nav a:hover {{ background: #2c3e50; }}
        .container {{ max-width: 1000px; margin: 20px auto; padding: 20px; }}
        .content {{ background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
        .form-group input, .form-group textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
        .form-group textarea {{ height: 100px; }}
        .btn {{ background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
        .btn:hover {{ background: #2980b9; }}
        .alert {{ padding: 15px; margin-bottom: 20px; border-radius: 4px; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .alert-info {{ background: #cce5ff; color: #004085; border: 1px solid #b8daff; }}
        .breadcrumb {{ margin-bottom: 20px; color: #666; }}
        .breadcrumb a {{ color: #2980b9; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
        <p>Open Source FAQ System</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ</a>
    </div>
    <div class="container">
        <div class="content">
            <div class="breadcrumb"><a href="/faq">FAQ</a> &gt; Send to Friend</div>
            <h2>Send "{0}" to a Friend</h2>
            {7}
            <form method="POST">
                <input type="hidden" name="id" id="id" value="{1}" />
                <input type="hidden" name="cat" id="cat" value="{2}" />
                <input type="hidden" name="lang" id="lang" value="{3}" />
                <div class="form-group">
                    <label for="email">Friend's Email Address:</label>
                    <input type="email" name="email" id="email" value="{4}" required />
                </div>
                <div class="form-group">
                    <label for="name">Your Name:</label>
                    <input type="text" name="name" id="name" value="{5}" required />
                </div>
                <div class="form-group">
                    <label for="message">Personal Message (optional):</label>
                    <textarea name="message" id="message">{6}</textarea>
                </div>
                <button type="submit" class="btn">Send to Friend</button>
            </form>
        </div>
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
