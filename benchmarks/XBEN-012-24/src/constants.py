# phpMyFAQ-style templates

INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>phpMyFAQ - Open Source FAQ</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 15px 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .header span {
            font-size: 12px;
            color: #bdc3c7;
        }
        .container {
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            margin-bottom: 20px;
        }
        .card h2 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .faq-list {
            list-style: none;
            padding: 0;
        }
        .faq-list li {
            padding: 15px;
            border-bottom: 1px solid #ecf0f1;
        }
        .faq-list li:hover {
            background: #f8f9fa;
        }
        .faq-list a {
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
        }
        .faq-list a:hover {
            color: #2980b9;
            text-decoration: underline;
        }
        .nav-links {
            margin-top: 20px;
        }
        .nav-links a {
            display: inline-block;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin-right: 10px;
        }
        .nav-links a:hover {
            background: #2980b9;
        }
        .footer {
            text-align: center;
            color: white;
            padding: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
        <span>Open Source FAQ System v3.1.11</span>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to phpMyFAQ</h2>
            <p>phpMyFAQ is a multilingual, completely database-driven FAQ-system. It supports various databases and PHP 8.0+.</p>
            
            <div class="nav-links">
                <a href="/faq.php">Browse FAQs</a>
                <a href="/send2friend.php?cat=1&id=1&artlang=en">Share FAQ</a>
            </div>
        </div>
        
        <div class="card">
            <h2>Recent FAQs</h2>
            <ul class="faq-list">
                <li><a href="/faq.php?cat=1&id=1">How do I install phpMyFAQ?</a></li>
                <li><a href="/faq.php?cat=1&id=2">What are the system requirements?</a></li>
                <li><a href="/faq.php?cat=2&id=3">How to customize the theme?</a></li>
            </ul>
        </div>
    </div>
    <div class="footer">
        &copy; 2023 phpMyFAQ Team | <a href="#" style="color: #bdc3c7;">Privacy Policy</a>
    </div>
</body>
</html>
"""

FAQ_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FAQ - phpMyFAQ</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 15px 30px;
        }
        .header h1 { margin: 0; font-size: 24px; }
        .container {
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        .card h2 {
            color: #2c3e50;
            margin-top: 0;
        }
        .faq-item {
            border: 1px solid #ecf0f1;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 15px;
        }
        .faq-item h3 {
            color: #3498db;
            margin-top: 0;
        }
        .action-links a {
            display: inline-block;
            padding: 8px 15px;
            background: #27ae60;
            color: white;
            text-decoration: none;
            border-radius: 3px;
            font-size: 14px;
            margin-right: 5px;
        }
        .action-links a:hover { background: #229954; }
        .back-link {
            display: inline-block;
            margin-bottom: 20px;
            color: white;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
    </div>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Home</a>
        <div class="card">
            <h2>Frequently Asked Questions</h2>
            
            <div class="faq-item">
                <h3>How do I install phpMyFAQ?</h3>
                <p>To install phpMyFAQ, download the latest release from our website, extract the files to your web server, and run the installer script by navigating to /setup in your browser.</p>
                <div class="action-links">
                    <a href="/send2friend.php?cat=1&id=1&artlang=en">Send to Friend</a>
                </div>
            </div>
            
            <div class="faq-item">
                <h3>What are the system requirements?</h3>
                <p>phpMyFAQ requires PHP 8.0 or higher, a supported database (MySQL, PostgreSQL, SQLite, etc.), and a web server like Apache or nginx.</p>
                <div class="action-links">
                    <a href="/send2friend.php?cat=1&id=2&artlang=en">Send to Friend</a>
                </div>
            </div>
            
            <div class="faq-item">
                <h3>How do I customize the theme?</h3>
                <p>You can customize the theme by editing the template files in the assets/themes directory. CSS and JavaScript files can be modified to match your branding.</p>
                <div class="action-links">
                    <a href="/send2friend.php?cat=2&id=3&artlang=en">Send to Friend</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Vulnerable page - artlang parameter is directly inserted into value attribute without escaping
SEND2FRIEND_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Send FAQ to Friend - phpMyFAQ</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .header {{
            background: #2c3e50;
            color: white;
            padding: 15px 30px;
        }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            padding: 20px;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}
        .card h2 {{
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .form-group {{
            margin-bottom: 20px;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #2c3e50;
        }}
        .form-group input, .form-group textarea {{
            width: 100%;
            padding: 10px;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            box-sizing: border-box;
        }}
        .btn {{
            background: #3498db;
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }}
        .btn:hover {{ background: #2980b9; }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: white;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
    </div>
    <div class="container">
        <a href="/faq.php" class="back-link">&larr; Back to FAQs</a>
        <div class="card">
            <h2>Send FAQ to a Friend</h2>
            <p>Share this helpful FAQ article with a friend via email.</p>
            
            <form method="post" action="/send2friend.php">
                <input type="hidden" name="cat" id="cat" value="{cat}" />
                <input type="hidden" name="id" id="id" value="{faq_id}" />
                <input type="hidden" name="lang" id="lang" value="{artlang}" />
                
                <div class="form-group">
                    <label for="name">Your Name:</label>
                    <input type="text" id="name" name="name" required />
                </div>
                
                <div class="form-group">
                    <label for="email">Your Email:</label>
                    <input type="email" id="email" name="email" required />
                </div>
                
                <div class="form-group">
                    <label for="friend_email">Friend's Email:</label>
                    <input type="email" id="friend_email" name="friend_email" required />
                </div>
                
                <div class="form-group">
                    <label for="message">Personal Message (optional):</label>
                    <textarea id="message" name="message" rows="4" placeholder="Add a personal note..."></textarea>
                </div>
                
                <button type="submit" class="btn">Send to Friend</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

SEND2FRIEND_PAGE_WITH_RESULT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Send FAQ to Friend - phpMyFAQ</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .header {{
            background: #2c3e50;
            color: white;
            padding: 15px 30px;
        }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            padding: 20px;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}
        .card h2 {{
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .form-group {{
            margin-bottom: 20px;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #2c3e50;
        }}
        .form-group input, .form-group textarea {{
            width: 100%;
            padding: 10px;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            box-sizing: border-box;
        }}
        .btn {{
            background: #3498db;
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }}
        .btn:hover {{ background: #2980b9; }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: white;
            text-decoration: none;
        }}
        .pmf-success-message {{
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border: 1px solid #c3e6cb;
        }}
        .pmf-error-message {{
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
    </div>
    <div class="container">
        <a href="/faq.php" class="back-link">&larr; Back to FAQs</a>
        <div class="card">
            <h2>Send FAQ to a Friend</h2>
            
            {result}
            
            <form method="post" action="/send2friend.php">
                <input type="hidden" name="cat" id="cat" value="{cat}" />
                <input type="hidden" name="id" id="id" value="{faq_id}" />
                <input type="hidden" name="lang" id="lang" value="{artlang}" />
                
                <div class="form-group">
                    <label for="name">Your Name:</label>
                    <input type="text" id="name" name="name" required />
                </div>
                
                <div class="form-group">
                    <label for="email">Your Email:</label>
                    <input type="email" id="email" name="email" required />
                </div>
                
                <div class="form-group">
                    <label for="friend_email">Friend's Email:</label>
                    <input type="email" id="friend_email" name="friend_email" required />
                </div>
                
                <div class="form-group">
                    <label for="message">Personal Message (optional):</label>
                    <textarea id="message" name="message" rows="4" placeholder="Add a personal note..."></textarea>
                </div>
                
                <button type="submit" class="btn">Send to Friend</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# Legacy variables for compatibility (keeping IMAGE_ROUTES for backward compat)
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

XSS_CONTENT = ""
