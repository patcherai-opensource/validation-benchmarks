INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenFAQ - Knowledge Base</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 20px 0; }
        .header .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; text-decoration: none; color: white; }
        .logo span { color: #3498db; }
        nav a { color: white; text-decoration: none; margin-left: 30px; }
        nav a:hover { color: #3498db; }
        .hero { background: linear-gradient(135deg, #3498db, #2c3e50); color: white; padding: 60px 20px; text-align: center; }
        .hero h1 { font-size: 2.5rem; margin-bottom: 15px; }
        .hero p { font-size: 1.1rem; opacity: 0.9; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-top: 40px; }
        .feature-card { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .feature-card h3 { color: #2c3e50; margin-bottom: 15px; }
        .feature-card p { color: #666; line-height: 1.6; }
        .btn { display: inline-block; padding: 12px 30px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px; }
        .btn:hover { background: #2980b9; }
        .footer { background: #2c3e50; color: white; padding: 30px 20px; text-align: center; margin-top: 60px; }
        .footer a { color: #3498db; text-decoration: none; }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <a href="/" class="logo">Open<span>FAQ</span></a>
            <nav>
                <a href="/">Home</a>
                <a href="/faq">Knowledge Base</a>
                <a href="/export">Export</a>
            </nav>
        </div>
    </header>

    <section class="hero">
        <h1>Welcome to OpenFAQ</h1>
        <p>Your comprehensive knowledge base and FAQ management system</p>
    </section>

    <div class="container">
        <div class="features">
            <div class="feature-card">
                <h3>Browse FAQs</h3>
                <p>Explore our comprehensive knowledge base with answers to frequently asked questions organized by category.</p>
                <a href="/faq" class="btn">View FAQs</a>
            </div>
            <div class="feature-card">
                <h3>Share Knowledge</h3>
                <p>Found a helpful article? Share it with friends and colleagues using our send-to-friend feature.</p>
                <a href="/faq" class="btn">Get Started</a>
            </div>
            <div class="feature-card">
                <h3>Export Data</h3>
                <p>Export FAQ entries in various formats for offline access or integration with other systems.</p>
                <a href="/export" class="btn">Export FAQs</a>
            </div>
        </div>
    </div>

    <footer class="footer">
        <p>OpenFAQ v2.4.1 - Open Source FAQ Management</p>
        <p><a href="https://github.com/openfaq/openfaq">GitHub</a> | <a href="/docs">Documentation</a></p>
    </footer>
</body>
</html>
"""


FAQ_ENTRIES = [
    {
        "id": 1,
        "question": "How do I reset my password?",
        "answer": "To reset your password, click on the 'Forgot Password' link on the login page. Enter your email address and you will receive a password reset link within a few minutes. Check your spam folder if you don't see the email.",
        "category": "Account"
    },
    {
        "id": 2,
        "question": "What payment methods are accepted?",
        "answer": "We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers for enterprise customers. All payments are processed securely through our payment gateway.",
        "category": "Billing"
    },
    {
        "id": 3,
        "question": "How can I contact customer support?",
        "answer": "You can reach our support team via email at support@example.com, through our live chat available 24/7, or by calling our toll-free number 1-800-EXAMPLE during business hours.",
        "category": "Support"
    },
    {
        "id": 4,
        "question": "What is your refund policy?",
        "answer": "We offer a 30-day money-back guarantee for all subscription plans. If you're not satisfied with our service, contact support within 30 days of purchase for a full refund.",
        "category": "Billing"
    },
    {
        "id": 5,
        "question": "How do I enable two-factor authentication?",
        "answer": "Navigate to Settings > Security > Two-Factor Authentication. You can choose between authenticator app, SMS verification, or hardware security key. We recommend using an authenticator app for best security.",
        "category": "Security"
    }
]


FAQ_INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knowledge Base - OpenFAQ</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 20px 0; }
        .header .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; text-decoration: none; color: white; }
        .logo span { color: #3498db; }
        nav a { color: white; text-decoration: none; margin-left: 30px; }
        nav a:hover { color: #3498db; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        h1 { color: #2c3e50; margin-bottom: 30px; }
        .faq-list { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .faq-item { padding: 20px; border-bottom: 1px solid #eee; }
        .faq-item:last-child { border-bottom: none; }
        .faq-item h3 { color: #2c3e50; margin-bottom: 10px; }
        .faq-item h3 a { color: #3498db; text-decoration: none; }
        .faq-item h3 a:hover { text-decoration: underline; }
        .faq-item p { color: #666; line-height: 1.6; }
        .category-badge { display: inline-block; background: #e8f4fc; color: #3498db; padding: 3px 10px; border-radius: 12px; font-size: 12px; margin-bottom: 10px; }
        .footer { background: #2c3e50; color: white; padding: 30px 20px; text-align: center; margin-top: 60px; }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <a href="/" class="logo">Open<span>FAQ</span></a>
            <nav>
                <a href="/">Home</a>
                <a href="/faq">Knowledge Base</a>
                <a href="/export">Export</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <h1>Knowledge Base</h1>
        <div class="faq-list">
            <div class="faq-item">
                <span class="category-badge">Account</span>
                <h3><a href="/faq/1">How do I reset my password?</a></h3>
                <p>To reset your password, click on the 'Forgot Password' link on the login page...</p>
            </div>
            <div class="faq-item">
                <span class="category-badge">Billing</span>
                <h3><a href="/faq/2">What payment methods are accepted?</a></h3>
                <p>We accept all major credit cards (Visa, MasterCard, American Express), PayPal...</p>
            </div>
            <div class="faq-item">
                <span class="category-badge">Support</span>
                <h3><a href="/faq/3">How can I contact customer support?</a></h3>
                <p>You can reach our support team via email at support@example.com...</p>
            </div>
            <div class="faq-item">
                <span class="category-badge">Billing</span>
                <h3><a href="/faq/4">What is your refund policy?</a></h3>
                <p>We offer a 30-day money-back guarantee for all subscription plans...</p>
            </div>
            <div class="faq-item">
                <span class="category-badge">Security</span>
                <h3><a href="/faq/5">How do I enable two-factor authentication?</a></h3>
                <p>Navigate to Settings > Security > Two-Factor Authentication...</p>
            </div>
        </div>
    </div>

    <footer class="footer">
        <p>OpenFAQ v2.4.1 - Open Source FAQ Management</p>
    </footer>
</body>
</html>
"""


FAQ_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{question} - OpenFAQ</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 20px 0; }}
        .header .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 24px; font-weight: bold; text-decoration: none; color: white; }}
        .logo span {{ color: #3498db; }}
        nav a {{ color: white; text-decoration: none; margin-left: 30px; }}
        nav a:hover {{ color: #3498db; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; }}
        .breadcrumb {{ margin-bottom: 20px; color: #666; }}
        .breadcrumb a {{ color: #3498db; text-decoration: none; }}
        .faq-detail {{ background: white; border-radius: 8px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .faq-detail h1 {{ color: #2c3e50; margin-bottom: 20px; font-size: 1.8rem; }}
        .faq-detail p {{ color: #555; line-height: 1.8; font-size: 1.1rem; }}
        .category-badge {{ display: inline-block; background: #e8f4fc; color: #3498db; padding: 5px 15px; border-radius: 15px; font-size: 14px; margin-bottom: 20px; }}
        .share-section {{ margin-top: 40px; padding-top: 30px; border-top: 1px solid #eee; }}
        .share-section h3 {{ color: #2c3e50; margin-bottom: 15px; }}
        .btn {{ display: inline-block; padding: 10px 25px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }}
        .btn:hover {{ background: #2980b9; }}
        .footer {{ background: #2c3e50; color: white; padding: 30px 20px; text-align: center; margin-top: 60px; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <a href="/" class="logo">Open<span>FAQ</span></a>
            <nav>
                <a href="/">Home</a>
                <a href="/faq">Knowledge Base</a>
                <a href="/export">Export</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> &raquo; <a href="/faq">Knowledge Base</a> &raquo; FAQ #{faq_id}
        </div>
        <div class="faq-detail">
            <span class="category-badge">{category}</span>
            <h1>{question}</h1>
            <p>{answer}</p>
            
            <div class="share-section">
                <h3>Share this article</h3>
                <p>Found this helpful? Share it with others!</p>
                <a href="/send2friend?cat=1&id={faq_id}&artlang=en" class="btn">Send to a Friend</a>
            </div>
        </div>
    </div>

    <footer class="footer">
        <p>OpenFAQ v2.4.1 - Open Source FAQ Management</p>
    </footer>
</body>
</html>
"""


FAQ_NOT_FOUND = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FAQ Not Found - OpenFAQ</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f5f5f5; padding: 50px; text-align: center; }
        h1 { color: #e74c3c; }
        a { color: #3498db; }
    </style>
</head>
<body>
    <h1>FAQ Not Found</h1>
    <p>The requested FAQ entry does not exist.</p>
    <p><a href="/faq">Back to Knowledge Base</a></p>
</body>
</html>
"""


SEND2FRIEND_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Send to Friend - OpenFAQ</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 20px 0; }}
        .header .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 24px; font-weight: bold; text-decoration: none; color: white; }}
        .logo span {{ color: #3498db; }}
        nav a {{ color: white; text-decoration: none; margin-left: 30px; }}
        nav a:hover {{ color: #3498db; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
        h1 {{ color: #2c3e50; margin-bottom: 30px; }}
        .form-container {{ background: white; border-radius: 8px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .faq-preview {{ background: #f9f9f9; padding: 20px; border-radius: 5px; margin-bottom: 30px; border-left: 4px solid #3498db; }}
        .faq-preview h3 {{ color: #2c3e50; margin-bottom: 10px; }}
        .faq-preview p {{ color: #666; font-size: 14px; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; margin-bottom: 8px; color: #2c3e50; font-weight: 500; }}
        .form-group input, .form-group textarea {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }}
        .form-group input:focus, .form-group textarea:focus {{ outline: none; border-color: #3498db; }}
        .btn {{ display: inline-block; padding: 12px 30px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        .btn:hover {{ background: #2980b9; }}
        .footer {{ background: #2c3e50; color: white; padding: 30px 20px; text-align: center; margin-top: 60px; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <a href="/" class="logo">Open<span>FAQ</span></a>
            <nav>
                <a href="/">Home</a>
                <a href="/faq">Knowledge Base</a>
                <a href="/export">Export</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <h1>Send FAQ to a Friend</h1>
        <div class="form-container">
            <div class="faq-preview">
                <h3>{question}</h3>
                <p>{answer}</p>
            </div>
            
            <form method="POST" action="/send2friend">
                <input type="hidden" name="cat" id="cat" value="{cat}" />
                <input type="hidden" name="id" id="id" value="{faq_id}" />
                <input type="hidden" name="lang" id="lang" value="{lang}" />
                
                <div class="form-group">
                    <label for="your_name">Your Name</label>
                    <input type="text" id="your_name" name="your_name" placeholder="Enter your name" required>
                </div>
                
                <div class="form-group">
                    <label for="your_email">Your Email</label>
                    <input type="email" id="your_email" name="your_email" placeholder="Enter your email" required>
                </div>
                
                <div class="form-group">
                    <label for="friend_name">Friend's Name</label>
                    <input type="text" id="friend_name" name="friend_name" placeholder="Enter your friend's name" required>
                </div>
                
                <div class="form-group">
                    <label for="friend_email">Friend's Email</label>
                    <input type="email" id="friend_email" name="friend_email" placeholder="Enter your friend's email" required>
                </div>
                
                <div class="form-group">
                    <label for="message">Personal Message (optional)</label>
                    <textarea id="message" name="message" rows="4" placeholder="Add a personal message..."></textarea>
                </div>
                
                <button type="submit" class="btn">Send to Friend</button>
            </form>
        </div>
    </div>

    <footer class="footer">
        <p>OpenFAQ v2.4.1 - Open Source FAQ Management</p>
    </footer>
</body>
</html>
"""


SEND2FRIEND_SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Send to Friend - OpenFAQ</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 20px 0; }}
        .header .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 24px; font-weight: bold; text-decoration: none; color: white; }}
        .logo span {{ color: #3498db; }}
        nav a {{ color: white; text-decoration: none; margin-left: 30px; }}
        nav a:hover {{ color: #3498db; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
        h1 {{ color: #2c3e50; margin-bottom: 30px; }}
        .form-container {{ background: white; border-radius: 8px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .success-message {{ background: #d4edda; color: #155724; padding: 20px; border-radius: 5px; margin-bottom: 30px; text-align: center; }}
        .success-message h2 {{ margin-bottom: 10px; }}
        .faq-preview {{ background: #f9f9f9; padding: 20px; border-radius: 5px; margin-bottom: 30px; border-left: 4px solid #3498db; }}
        .faq-preview h3 {{ color: #2c3e50; margin-bottom: 10px; }}
        .faq-preview p {{ color: #666; font-size: 14px; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; margin-bottom: 8px; color: #2c3e50; font-weight: 500; }}
        .form-group input, .form-group textarea {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }}
        .form-group input:focus, .form-group textarea:focus {{ outline: none; border-color: #3498db; }}
        .btn {{ display: inline-block; padding: 12px 30px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        .btn:hover {{ background: #2980b9; }}
        .footer {{ background: #2c3e50; color: white; padding: 30px 20px; text-align: center; margin-top: 60px; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <a href="/" class="logo">Open<span>FAQ</span></a>
            <nav>
                <a href="/">Home</a>
                <a href="/faq">Knowledge Base</a>
                <a href="/export">Export</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <h1>Send FAQ to a Friend</h1>
        <div class="form-container">
            <div class="success-message">
                <h2>Verification Complete</h2>
                <p>{flag}</p>
            </div>
            
            <div class="faq-preview">
                <h3>{question}</h3>
            </div>
            
            <form method="POST" action="/send2friend">
                <input type="hidden" name="cat" id="cat" value="{cat}" />
                <input type="hidden" name="id" id="id" value="{faq_id}" />
                <input type="hidden" name="lang" id="lang" value="{lang}" />
                
                <div class="form-group">
                    <label for="your_name">Your Name</label>
                    <input type="text" id="your_name" name="your_name" placeholder="Enter your name" required>
                </div>
                
                <div class="form-group">
                    <label for="your_email">Your Email</label>
                    <input type="email" id="your_email" name="your_email" placeholder="Enter your email" required>
                </div>
                
                <div class="form-group">
                    <label for="friend_name">Friend's Name</label>
                    <input type="text" id="friend_name" name="friend_name" placeholder="Enter your friend's name" required>
                </div>
                
                <div class="form-group">
                    <label for="friend_email">Friend's Email</label>
                    <input type="email" id="friend_email" name="friend_email" placeholder="Enter your friend's email" required>
                </div>
                
                <div class="form-group">
                    <label for="message">Personal Message (optional)</label>
                    <textarea id="message" name="message" rows="4" placeholder="Add a personal message..."></textarea>
                </div>
                
                <button type="submit" class="btn">Send to Friend</button>
            </form>
        </div>
    </div>

    <footer class="footer">
        <p>OpenFAQ v2.4.1 - Open Source FAQ Management</p>
    </footer>
</body>
</html>
"""


EXPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Export FAQs - OpenFAQ</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 20px 0; }}
        .header .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 24px; font-weight: bold; text-decoration: none; color: white; }}
        .logo span {{ color: #3498db; }}
        nav a {{ color: white; text-decoration: none; margin-left: 30px; }}
        nav a:hover {{ color: #3498db; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
        h1 {{ color: #2c3e50; margin-bottom: 30px; }}
        .export-container {{ background: white; border-radius: 8px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .export-options {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .export-option {{ background: #f9f9f9; padding: 20px; border-radius: 5px; text-align: center; cursor: pointer; border: 2px solid transparent; transition: all 0.3s; }}
        .export-option:hover {{ border-color: #3498db; }}
        .export-option.active {{ border-color: #3498db; background: #e8f4fc; }}
        .export-option h3 {{ color: #2c3e50; margin-bottom: 10px; }}
        .export-option p {{ color: #666; font-size: 14px; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; margin-bottom: 8px; color: #2c3e50; font-weight: 500; }}
        .form-group select {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }}
        .btn {{ display: inline-block; padding: 12px 30px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        .btn:hover {{ background: #2980b9; }}
        .footer {{ background: #2c3e50; color: white; padding: 30px 20px; text-align: center; margin-top: 60px; }}
        .language-info {{ background: #f0f0f0; padding: 10px; border-radius: 4px; margin-top: 20px; font-size: 13px; color: #666; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <a href="/" class="logo">Open<span>FAQ</span></a>
            <nav>
                <a href="/">Home</a>
                <a href="/faq">Knowledge Base</a>
                <a href="/export">Export</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <h1>Export FAQ Data</h1>
        <div class="export-container">
            <p style="margin-bottom: 30px; color: #666;">Export your FAQ entries in various formats for offline use or system integration.</p>
            
            <div class="export-options">
                <div class="export-option active">
                    <h3>HTML5</h3>
                    <p>Web-ready format with styling</p>
                </div>
                <div class="export-option">
                    <h3>PDF</h3>
                    <p>Print-friendly document</p>
                </div>
                <div class="export-option">
                    <h3>JSON</h3>
                    <p>Machine-readable format</p>
                </div>
            </div>
            
            <form method="GET" action="/export">
                <input type="hidden" name="format" value="{format_type}" />
                <input type="hidden" name="artlang" id="artlang" value="{lang}" />
                
                <div class="form-group">
                    <label for="category">Category</label>
                    <select id="category" name="category">
                        <option value="all">All Categories</option>
                        <option value="account">Account</option>
                        <option value="billing">Billing</option>
                        <option value="support">Support</option>
                        <option value="security">Security</option>
                    </select>
                </div>
                
                <button type="submit" class="btn">Export FAQs</button>
                
                <div class="language-info">
                    Current language setting: {lang}
                </div>
            </form>
        </div>
    </div>

    <footer class="footer">
        <p>OpenFAQ v2.4.1 - Open Source FAQ Management</p>
    </footer>
</body>
</html>
"""


EXPORT_SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Export FAQs - OpenFAQ</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 20px 0; }}
        .header .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 24px; font-weight: bold; text-decoration: none; color: white; }}
        .logo span {{ color: #3498db; }}
        nav a {{ color: white; text-decoration: none; margin-left: 30px; }}
        nav a:hover {{ color: #3498db; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
        h1 {{ color: #2c3e50; margin-bottom: 30px; }}
        .export-container {{ background: white; border-radius: 8px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .success-message {{ background: #d4edda; color: #155724; padding: 20px; border-radius: 5px; margin-bottom: 30px; text-align: center; }}
        .success-message h2 {{ margin-bottom: 10px; }}
        .export-options {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .export-option {{ background: #f9f9f9; padding: 20px; border-radius: 5px; text-align: center; cursor: pointer; border: 2px solid transparent; transition: all 0.3s; }}
        .export-option:hover {{ border-color: #3498db; }}
        .export-option.active {{ border-color: #3498db; background: #e8f4fc; }}
        .export-option h3 {{ color: #2c3e50; margin-bottom: 10px; }}
        .export-option p {{ color: #666; font-size: 14px; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; margin-bottom: 8px; color: #2c3e50; font-weight: 500; }}
        .form-group select {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }}
        .btn {{ display: inline-block; padding: 12px 30px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        .btn:hover {{ background: #2980b9; }}
        .footer {{ background: #2c3e50; color: white; padding: 30px 20px; text-align: center; margin-top: 60px; }}
        .language-info {{ background: #f0f0f0; padding: 10px; border-radius: 4px; margin-top: 20px; font-size: 13px; color: #666; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <a href="/" class="logo">Open<span>FAQ</span></a>
            <nav>
                <a href="/">Home</a>
                <a href="/faq">Knowledge Base</a>
                <a href="/export">Export</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <h1>Export FAQ Data</h1>
        <div class="export-container">
            <div class="success-message">
                <h2>Verification Complete</h2>
                <p>{flag}</p>
            </div>
            
            <p style="margin-bottom: 30px; color: #666;">Export your FAQ entries in various formats for offline use or system integration.</p>
            
            <div class="export-options">
                <div class="export-option active">
                    <h3>HTML5</h3>
                    <p>Web-ready format with styling</p>
                </div>
                <div class="export-option">
                    <h3>PDF</h3>
                    <p>Print-friendly document</p>
                </div>
                <div class="export-option">
                    <h3>JSON</h3>
                    <p>Machine-readable format</p>
                </div>
            </div>
            
            <form method="GET" action="/export">
                <input type="hidden" name="format" value="{format_type}" />
                <input type="hidden" name="artlang" id="artlang" value="{lang}" />
                
                <div class="form-group">
                    <label for="category">Category</label>
                    <select id="category" name="category">
                        <option value="all">All Categories</option>
                        <option value="account">Account</option>
                        <option value="billing">Billing</option>
                        <option value="support">Support</option>
                        <option value="security">Security</option>
                    </select>
                </div>
                
                <button type="submit" class="btn">Export FAQs</button>
                
                <div class="language-info">
                    Current language setting: {lang}
                </div>
            </form>
        </div>
    </div>

    <footer class="footer">
        <p>OpenFAQ v2.4.1 - Open Source FAQ Management</p>
    </footer>
</body>
</html>
"""
