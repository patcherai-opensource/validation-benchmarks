# phpMyFAQ-like FAQ application templates

INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenFAQ - Knowledge Base</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px 0; }
        .header h1 { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .nav { background: #34495e; padding: 10px 0; }
        .nav ul { max-width: 1200px; margin: 0 auto; padding: 0 20px; list-style: none; display: flex; gap: 20px; }
        .nav a { color: white; text-decoration: none; }
        .nav a:hover { text-decoration: underline; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { margin-bottom: 15px; color: #2c3e50; }
        .card p { color: #666; line-height: 1.6; }
        .btn { display: inline-block; background: #3498db; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; }
        .btn:hover { background: #2980b9; }
        .categories { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .footer { background: #2c3e50; color: white; padding: 20px 0; margin-top: 40px; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ</h1>
    </div>
    <nav class="nav">
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/faq">Browse FAQs</a></li>
            <li><a href="/search">Search</a></li>
            <li><a href="/contact">Contact</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="card">
            <h2>Welcome to OpenFAQ Knowledge Base</h2>
            <p>Find answers to frequently asked questions about our products and services.</p>
        </div>
        <h2 style="margin-bottom: 20px;">Categories</h2>
        <div class="categories">
            <div class="card">
                <h2>Account & Security</h2>
                <p>Password resets, account settings, and security questions.</p>
                <a href="/faq?cat=1" class="btn">Browse</a>
            </div>
            <div class="card">
                <h2>Billing & Payments</h2>
                <p>Payment methods, refunds, and billing inquiries.</p>
                <a href="/faq?cat=2" class="btn">Browse</a>
            </div>
            <div class="card">
                <h2>Support</h2>
                <p>Get help from our support team.</p>
                <a href="/faq?cat=3" class="btn">Browse</a>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 OpenFAQ - Powered by open source</p>
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
    <title>FAQs - OpenFAQ</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px 0; }
        .header h1 { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .nav { background: #34495e; padding: 10px 0; }
        .nav ul { max-width: 1200px; margin: 0 auto; padding: 0 20px; list-style: none; display: flex; gap: 20px; }
        .nav a { color: white; text-decoration: none; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .faq-item { border-bottom: 1px solid #eee; padding: 15px 0; }
        .faq-item:last-child { border-bottom: none; }
        .faq-item h3 { color: #2c3e50; margin-bottom: 10px; }
        .faq-item a { color: #3498db; text-decoration: none; }
        .faq-item a:hover { text-decoration: underline; }
        .actions { margin-top: 10px; }
        .actions a { margin-right: 15px; font-size: 0.9em; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ</h1>
    </div>
    <nav class="nav">
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/faq">Browse FAQs</a></li>
            <li><a href="/search">Search</a></li>
            <li><a href="/contact">Contact</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="card">
            <h2>Frequently Asked Questions</h2>
            <div class="faq-item">
                <h3><a href="/faq/view?id=1&cat=1">How do I reset my password?</a></h3>
                <p>Go to Settings > Security > Reset Password.</p>
                <div class="actions">
                    <a href="/faq/view?id=1&cat=1">View</a>
                    <a href="/send2friend?id=1&cat=1&artlang=en">Send to friend</a>
                </div>
            </div>
            <div class="faq-item">
                <h3><a href="/faq/view?id=2&cat=1">How do I change my email?</a></h3>
                <p>Navigate to Account Settings and update your email address.</p>
                <div class="actions">
                    <a href="/faq/view?id=2&cat=1">View</a>
                    <a href="/send2friend?id=2&cat=1&artlang=en">Send to friend</a>
                </div>
            </div>
            <div class="faq-item">
                <h3><a href="/faq/view?id=3&cat=2">What payment methods are accepted?</a></h3>
                <p>We accept Visa, Mastercard, and PayPal.</p>
                <div class="actions">
                    <a href="/faq/view?id=3&cat=2">View</a>
                    <a href="/send2friend?id=3&cat=2&artlang=en">Send to friend</a>
                </div>
            </div>
            <div class="faq-item">
                <h3><a href="/faq/view?id=4&cat=2">Is there a refund policy?</a></h3>
                <p>Yes, we offer 30-day money back guarantee.</p>
                <div class="actions">
                    <a href="/faq/view?id=4&cat=2">View</a>
                    <a href="/send2friend?id=4&cat=2&artlang=en">Send to friend</a>
                </div>
            </div>
            <div class="faq-item">
                <h3><a href="/faq/view?id=5&cat=3">How do I contact support?</a></h3>
                <p>Use the contact form or email support@example.com.</p>
                <div class="actions">
                    <a href="/faq/view?id=5&cat=3">View</a>
                    <a href="/send2friend?id=5&cat=3&artlang=en">Send to friend</a>
                </div>
            </div>
        </div>
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
    <title>{title} - OpenFAQ</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px 0; }}
        .header h1 {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .nav {{ background: #34495e; padding: 10px 0; }}
        .nav ul {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; list-style: none; display: flex; gap: 20px; }}
        .nav a {{ color: white; text-decoration: none; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .btn {{ display: inline-block; background: #3498db; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-right: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ</h1>
    </div>
    <nav class="nav">
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/faq">Browse FAQs</a></li>
            <li><a href="/search">Search</a></li>
            <li><a href="/contact">Contact</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="card">
            <h2>{title}</h2>
            <p style="margin: 20px 0; line-height: 1.8;">{content}</p>
            <div style="margin-top: 20px;">
                <a href="/faq" class="btn">Back to FAQs</a>
                <a href="/send2friend?id={faq_id}&cat={cat}&artlang=en" class="btn">Send to Friend</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

CONTACT_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us - OpenFAQ</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px 0; }
        .header h1 { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .nav { background: #34495e; padding: 10px 0; }
        .nav ul { max-width: 1200px; margin: 0 auto; padding: 0 20px; list-style: none; display: flex; gap: 20px; }
        .nav a { color: white; text-decoration: none; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        input, textarea { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        label { display: block; margin-top: 15px; color: #333; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ</h1>
    </div>
    <nav class="nav">
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/faq">Browse FAQs</a></li>
            <li><a href="/search">Search</a></li>
            <li><a href="/contact">Contact</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="card">
            <h2>Contact Us</h2>
            <form method="POST" action="/contact">
                <label>Name</label>
                <input type="text" name="name" required>
                <label>Email</label>
                <input type="email" name="email" required>
                <label>Message</label>
                <textarea name="message" rows="5" required></textarea>
                <button type="submit">Send Message</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

CONTACT_SUCCESS_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message Sent - OpenFAQ</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px 0; }}
        .header h1 {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .alert {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ</h1>
    </div>
    <div class="container">
        <div class="card">
            <div class="alert">
                Thank you {name}! Your message has been sent successfully.
            </div>
            <p style="margin-top: 20px;"><a href="/">Return to Home</a></p>
        </div>
    </div>
</body>
</html>
"""

# This is the vulnerable page template - the {lang} parameter is NOT escaped
# Similar to CVE-2023-1880 where artlang was inserted without htmlentities()
SEND2FRIEND_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Send to Friend - OpenFAQ</title>
</head>
<body>
    <div class="container">
        <h2>Share: {title}</h2>
        <p>{content}</p>
        <form method="POST" action="/send2friend">
            <input type="hidden" name="cat" id="cat" value="{cat}" />
            <input type="hidden" name="id" id="id" value="{faq_id}" />
            <input type="hidden" name="lang" id="lang" value="{lang}" />
            <label>Your Name</label>
            <input type="text" name="name" required>
            <label>Friend's Email</label>
            <input type="email" name="email" required>
            <label>Message</label>
            <textarea name="message" rows="3"></textarea>
            <button type="submit">Send</button>
        </form>
    </div>
</body>
</html>
"""

SEND2FRIEND_RESPONSE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Send to Friend - OpenFAQ</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px 0; }}
        .header h1 {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .nav {{ background: #34495e; padding: 10px 0; }}
        .nav ul {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; list-style: none; display: flex; gap: 20px; }}
        .nav a {{ color: white; text-decoration: none; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        input, textarea {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }}
        button {{ background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
        label {{ display: block; margin-top: 15px; color: #333; }}
        .alert-success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ</h1>
    </div>
    <nav class="nav">
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/faq">Browse FAQs</a></li>
            <li><a href="/search">Search</a></li>
            <li><a href="/contact">Contact</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="card">
            <h2>Share this FAQ with a Friend</h2>
            {result}
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <h3>{title}</h3>
                <p>{content}</p>
            </div>
            <form method="POST" action="/send2friend">
                <input type="hidden" name="cat" id="cat" value="{cat}" />
                <input type="hidden" name="id" id="id" value="{faq_id}" />
                <input type="hidden" name="lang" id="lang" value="{lang}" />
                <label>Your Name</label>
                <input type="text" name="name" required>
                <label>Friend's Email</label>
                <input type="email" name="email" required>
                <label>Personal Message (optional)</label>
                <textarea name="message" rows="3" placeholder="Add a personal note..."></textarea>
                <button type="submit">Send to Friend</button>
            </form>
            <p style="margin-top: 20px;"><a href="/faq">Back to FAQs</a></p>
        </div>
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
    <title>Search - OpenFAQ</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px 0; }}
        .header h1 {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .nav {{ background: #34495e; padding: 10px 0; }}
        .nav ul {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; list-style: none; display: flex; gap: 20px; }}
        .nav a {{ color: white; text-decoration: none; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        input {{ width: 70%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        button {{ background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
        ul {{ margin-left: 20px; margin-top: 15px; }}
        li {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ</h1>
    </div>
    <nav class="nav">
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/faq">Browse FAQs</a></li>
            <li><a href="/search">Search</a></li>
            <li><a href="/contact">Contact</a></li>
        </ul>
    </nav>
    <div class="container">
        <div class="card">
            <h2>Search FAQs</h2>
            <form method="GET" action="/search" style="margin: 20px 0;">
                <input type="text" name="q" placeholder="Search..." value="{query}">
                <button type="submit">Search</button>
            </form>
            <h3>Results:</h3>
            <ul>
                {results_html}
            </ul>
        </div>
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
    <title>Admin - OpenFAQ</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #c0392b; color: white; padding: 20px 0; }
        .header h1 { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .alert { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenFAQ Admin</h1>
    </div>
    <div class="container">
        <div class="card">
            <div class="alert">
                <strong>Access Denied</strong><br>
                You must be logged in as an administrator to access this area.
            </div>
            <p style="margin-top: 20px;"><a href="/">Return to Home</a></p>
        </div>
    </div>
</body>
</html>
"""

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
