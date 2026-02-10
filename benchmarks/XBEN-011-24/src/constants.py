# Templates simulating phpMyFAQ's vulnerable pages for CVE-2023-1880

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>phpMyFAQ - Knowledge Base</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        .nav-links {
            margin: 20px 0;
        }
        .nav-links a {
            display: inline-block;
            padding: 10px 20px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 3px;
            margin-right: 10px;
        }
        .nav-links a:hover {
            background: #0056b3;
        }
        .faq-list {
            margin-top: 20px;
        }
        .faq-item {
            padding: 15px;
            border: 1px solid #ddd;
            margin-bottom: 10px;
            border-radius: 3px;
        }
        .faq-item h3 {
            margin: 0 0 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>phpMyFAQ - Open Source FAQ System</h1>
        <div class="nav-links">
            <a href="/faq.php">FAQ Articles</a>
            <a href="/send2friend.php?cat=1&id=1&artlang=en">Send to Friend</a>
        </div>
        <div class="faq-list">
            <div class="faq-item">
                <h3>Welcome to phpMyFAQ</h3>
                <p>This is a simulated phpMyFAQ installation for security testing.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

FAQ_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>phpMyFAQ - FAQ Articles</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        .faq-item {
            padding: 15px;
            border: 1px solid #ddd;
            margin-bottom: 10px;
            border-radius: 3px;
        }
        .faq-item h3 {
            margin: 0 0 10px 0;
        }
        .faq-item a {
            color: #007bff;
            margin-right: 15px;
        }
        .breadcrumb {
            margin-bottom: 20px;
            color: #666;
        }
        .breadcrumb a {
            color: #007bff;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> &gt; FAQ Articles
        </div>
        <h1>Frequently Asked Questions</h1>
        
        <div class="faq-item">
            <h3>1. How do I use phpMyFAQ?</h3>
            <p>phpMyFAQ is an open source FAQ application for PHP.</p>
            <a href="/send2friend.php?cat=1&id=1&artlang=en">Send to Friend</a>
        </div>
        
        <div class="faq-item">
            <h3>2. What is the send to friend feature?</h3>
            <p>The send to friend feature allows you to share FAQ articles with others via email.</p>
            <a href="/send2friend.php?cat=1&id=2&artlang=en">Send to Friend</a>
        </div>
        
        <div class="faq-item">
            <h3>3. Is phpMyFAQ secure?</h3>
            <p>Security depends on keeping your installation up to date. Always check for the latest patches.</p>
            <a href="/send2friend.php?cat=1&id=3&artlang=en">Send to Friend</a>
        </div>
    </div>
</body>
</html>
"""

# This template simulates the vulnerable send2friend page from phpMyFAQ
# The artlang parameter is injected directly into value="" without HTML encoding
# Vulnerable pattern: <input type="hidden" name="lang" id="lang" value="{{ lang }}" />
SEND2FRIEND_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Send FAQ to Friend</title>
</head>
<body>
    <div class="container">
        <h1>Send FAQ to a Friend</h1>
        <form action="/send2friend.php" method="post">
            <input type="hidden" name="cat" value="{cat}" />
            <input type="hidden" name="id" value="{faq_id}" />
            <!-- VULNERABLE: artlang is injected directly without HTML encoding -->
            <!-- This mimics: <input type="hidden" name="lang" id="lang" value="{{ lang }}" /> -->
            <input type="hidden" name="lang" id="lang" value="{artlang}" />
            
            <div class="form-group">
                <label for="email">Friend's Email:</label>
                <input type="email" name="email" id="email" />
            </div>
            
            <div class="form-group">
                <label for="message">Message:</label>
                <textarea name="message" id="message"></textarea>
            </div>
            
            <button type="submit">Send</button>
        </form>
    </div>
</body>
</html>
"""

# Response template for the send2friend page
SEND2FRIEND_RESPONSE = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>phpMyFAQ - Send to Friend</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        .form-group {{
            margin-bottom: 15px;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }}
        .form-group input, .form-group textarea {{
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 3px;
            box-sizing: border-box;
        }}
        .form-group textarea {{
            height: 100px;
        }}
        button {{
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }}
        button:hover {{
            background: #0056b3;
        }}
        .breadcrumb {{
            margin-bottom: 20px;
            color: #666;
        }}
        .breadcrumb a {{
            color: #007bff;
        }}
        .info-box {{
            padding: 15px;
            margin: 20px 0;
            border-radius: 3px;
        }}
        .info-box.success {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }}
        .info-box.error {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> &gt; <a href="/faq.php">FAQ</a> &gt; Send to Friend
        </div>
        <h1>Send this FAQ to a Friend</h1>
        
        {result}
        
        <form action="/send2friend.php" method="post">
            <input type="hidden" name="cat" value="{cat}" />
            <input type="hidden" name="id" value="{faq_id}" />
            <!-- VULNERABLE: artlang is injected directly without HTML encoding -->
            <input type="hidden" name="lang" id="lang" value="{artlang}" />
            
            <div class="form-group">
                <label for="name">Your Name:</label>
                <input type="text" name="name" id="name" required />
            </div>
            
            <div class="form-group">
                <label for="email">Your Email:</label>
                <input type="email" name="email" id="email" required />
            </div>
            
            <div class="form-group">
                <label for="friend_email">Friend's Email:</label>
                <input type="email" name="friend_email" id="friend_email" required />
            </div>
            
            <div class="form-group">
                <label for="message">Personal Message (optional):</label>
                <textarea name="message" id="message" placeholder="Check out this FAQ article!"></textarea>
            </div>
            
            <button type="submit">Send to Friend</button>
        </form>
        
        <p style="margin-top: 20px; font-size: 12px; color: #666;">
            FAQ ID: {faq_id} | Category: {cat} | Language: {artlang}
        </p>
    </div>
</body>
</html>
"""

# Keep old templates for potential backward compatibility (unused)
IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    },
    "xss_medium": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    }
}
