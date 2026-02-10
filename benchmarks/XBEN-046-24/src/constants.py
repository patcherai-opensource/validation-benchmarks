FAQ_INDEX_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>phpMyFAQ - Knowledge Base</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; }
        .header h1 { margin: 0; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { margin-top: 0; color: #2c3e50; }
        .faq-list { list-style: none; padding: 0; }
        .faq-list li { padding: 10px 0; border-bottom: 1px solid #eee; }
        .faq-list li:last-child { border-bottom: none; }
        .faq-list a { color: #3498db; text-decoration: none; }
        .faq-list a:hover { text-decoration: underline; }
        .footer { background: #2c3e50; color: white; padding: 20px; text-align: center; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
        <p>Your Knowledge Base Solution</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ</a>
        <a href="/contact">Contact</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to our FAQ System</h2>
            <p>Browse our frequently asked questions to find answers to common queries.</p>
            <p><a href="/faq">View all FAQs &rarr;</a></p>
        </div>
        <div class="card">
            <h2>Popular Articles</h2>
            <ul class="faq-list">
                <li><a href="/faq/1">How do I reset my password?</a></li>
                <li><a href="/faq/2">What payment methods are accepted?</a></li>
                <li><a href="/faq/3">How can I contact support?</a></li>
            </ul>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 phpMyFAQ - Open Source FAQ System</p>
    </div>
</body>
</html>
"""

FAQ_LIST_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FAQ List - phpMyFAQ</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; }}
        .header h1 {{ margin: 0; }}
        .nav {{ background: #34495e; padding: 10px 20px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h2 {{ margin-top: 0; color: #2c3e50; }}
        .faq-list {{ list-style: none; padding: 0; }}
        .faq-list li {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
        .faq-list li:last-child {{ border-bottom: none; }}
        .faq-list a {{ color: #3498db; text-decoration: none; }}
        .faq-list a:hover {{ text-decoration: underline; }}
        .footer {{ background: #2c3e50; color: white; padding: 20px; text-align: center; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
        <p>Frequently Asked Questions</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ</a>
        <a href="/contact">Contact</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>All FAQs</h2>
            <ul class="faq-list">
                {faq_items}
            </ul>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 phpMyFAQ - Open Source FAQ System</p>
    </div>
</body>
</html>
"""

FAQ_DETAIL_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - phpMyFAQ</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; }}
        .header h1 {{ margin: 0; }}
        .nav {{ background: #34495e; padding: 10px 20px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h2 {{ margin-top: 0; color: #2c3e50; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; margin-right: 10px; }}
        .btn:hover {{ background: #2980b9; }}
        .btn-secondary {{ background: #95a5a6; }}
        .btn-secondary:hover {{ background: #7f8c8d; }}
        .footer {{ background: #2c3e50; color: white; padding: 20px; text-align: center; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ</a>
        <a href="/contact">Contact</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>{title}</h2>
            <p>{content}</p>
            <hr>
            <p>
                <a class="btn" href="/send2friend.php?cat=1&id={faq_id}&artlang=en">Send to Friend</a>
                <a class="btn btn-secondary" href="/faq">Back to FAQ List</a>
            </p>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 phpMyFAQ - Open Source FAQ System</p>
    </div>
</body>
</html>
"""

SEND2FRIEND_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Send FAQ to Friend - phpMyFAQ</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; }}
        .header h1 {{ margin: 0; }}
        .nav {{ background: #34495e; padding: 10px 20px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h2 {{ margin-top: 0; color: #2c3e50; }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
        .form-group input, .form-group textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
        .form-group textarea {{ height: 100px; resize: vertical; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; }}
        .btn:hover {{ background: #2980b9; }}
        .footer {{ background: #2c3e50; color: white; padding: 20px; text-align: center; margin-top: 40px; }}
        .faq-preview {{ background: #ecf0f1; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
        .faq-preview h3 {{ margin-top: 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ</a>
        <a href="/contact">Contact</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Send FAQ to a Friend</h2>
            <div class="faq-preview">
                <h3>{faq_title}</h3>
                <p>{faq_content}</p>
            </div>
            <form method="POST" action="/send2friend.php">
                <input type="hidden" name="cat" id="cat" value="{cat}" />
                <input type="hidden" name="id" id="id" value="{faq_id}" />
                <input type="hidden" name="lang" id="lang" value="{artlang}" />
                <div class="form-group">
                    <label for="name">Your Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="email">Your Email:</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="friend_email">Friend's Email:</label>
                    <input type="email" id="friend_email" name="friend_email" required>
                </div>
                <div class="form-group">
                    <label for="message">Personal Message (optional):</label>
                    <textarea id="message" name="message" placeholder="Add a personal note..."></textarea>
                </div>
                <button type="submit" class="btn">Send to Friend</button>
            </form>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 phpMyFAQ - Open Source FAQ System</p>
    </div>
</body>
</html>
"""

SEND2FRIEND_SUCCESS_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Send FAQ to Friend - phpMyFAQ</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; }}
        .header h1 {{ margin: 0; }}
        .nav {{ background: #34495e; padding: 10px 20px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h2 {{ margin-top: 0; color: #2c3e50; }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
        .form-group input, .form-group textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
        .form-group textarea {{ height: 100px; resize: vertical; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; }}
        .btn:hover {{ background: #2980b9; }}
        .footer {{ background: #2c3e50; color: white; padding: 20px; text-align: center; margin-top: 40px; }}
        .faq-preview {{ background: #ecf0f1; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
        .faq-preview h3 {{ margin-top: 0; }}
        .success-msg {{ background: #27ae60; color: white; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ</a>
        <a href="/contact">Contact</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Send FAQ to a Friend</h2>
            <div class="success-msg">
                <strong>Success!</strong> Your message has been processed. Flag: {flag}
            </div>
            <div class="faq-preview">
                <h3>{faq_title}</h3>
                <p>{faq_content}</p>
            </div>
            <form method="POST" action="/send2friend.php">
                <input type="hidden" name="cat" id="cat" value="{cat}" />
                <input type="hidden" name="id" id="id" value="{faq_id}" />
                <input type="hidden" name="lang" id="lang" value="{artlang}" />
                <div class="form-group">
                    <label for="name">Your Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="email">Your Email:</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="friend_email">Friend's Email:</label>
                    <input type="email" id="friend_email" name="friend_email" required>
                </div>
                <div class="form-group">
                    <label for="message">Personal Message (optional):</label>
                    <textarea id="message" name="message" placeholder="Add a personal note..."></textarea>
                </div>
                <button type="submit" class="btn">Send to Friend</button>
            </form>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 phpMyFAQ - Open Source FAQ System</p>
    </div>
</body>
</html>
"""

SEND2FRIEND_CONFIRM_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message Sent - phpMyFAQ</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; }}
        .header h1 {{ margin: 0; }}
        .nav {{ background: #34495e; padding: 10px 20px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h2 {{ margin-top: 0; color: #2c3e50; }}
        .success-msg {{ background: #27ae60; color: white; padding: 15px; border-radius: 4px; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; margin-top: 20px; }}
        .btn:hover {{ background: #2980b9; }}
        .footer {{ background: #2c3e50; color: white; padding: 20px; text-align: center; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>phpMyFAQ</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/faq">FAQ</a>
        <a href="/contact">Contact</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Message Sent!</h2>
            <div class="success-msg">
                Your FAQ recommendation has been sent to {friend_email}!
            </div>
            <a href="/faq" class="btn">Back to FAQ</a>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 phpMyFAQ - Open Source FAQ System</p>
    </div>
</body>
</html>
"""
