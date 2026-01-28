# PrestaStore - E-commerce Platform Demo Templates

INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrestaStore - E-commerce Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .header { background: rgba(255,255,255,0.95); padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header h1 { color: #333; font-size: 28px; }
        .header .tagline { color: #666; font-size: 14px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .nav { display: flex; gap: 20px; margin-top: 20px; flex-wrap: wrap; }
        .nav a { background: #fff; padding: 20px 30px; border-radius: 10px; text-decoration: none; color: #333; font-weight: bold; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .nav a:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.2); }
        .nav a .desc { font-weight: normal; color: #666; font-size: 12px; display: block; margin-top: 5px; }
        .features { margin-top: 40px; background: rgba(255,255,255,0.95); border-radius: 10px; padding: 30px; }
        .features h2 { margin-bottom: 20px; color: #333; }
        .features ul { list-style: none; }
        .features li { padding: 10px 0; border-bottom: 1px solid #eee; color: #555; }
        .features li:last-child { border-bottom: none; }
        .footer { text-align: center; color: rgba(255,255,255,0.8); padding: 20px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>&#128722; PrestaStore</h1>
            <p class="tagline">Open Source E-commerce Platform - Demo Instance</p>
        </div>
    </div>
    <div class="container">
        <nav class="nav">
            <a href="/products">&#128230; Products<span class="desc">Browse catalog</span></a>
            <a href="/reviews">&#11088; Reviews<span class="desc">Customer feedback</span></a>
            <a href="/customize">&#127912; Customize<span class="desc">Store settings</span></a>
            <a href="/contact">&#128231; Contact<span class="desc">Get in touch</span></a>
            <a href="/newsletter">&#128236; Newsletter<span class="desc">Subscribe</span></a>
        </nav>
        
        <div class="features">
            <h2>Platform Features</h2>
            <ul>
                <li>&#10003; Product Management - Add and manage your product catalog</li>
                <li>&#10003; Customer Reviews - Collect and display customer feedback</li>
                <li>&#10003; Store Customization - Personalize your store with HTML descriptions</li>
                <li>&#10003; Newsletter System - Build your customer mailing list</li>
                <li>&#10003; Contact Forms - Easy communication with customers</li>
                <li>&#10003; HTML Content Validation - Secure content filtering (isCleanHtml)</li>
            </ul>
        </div>
    </div>
    <div class="footer">
        PrestaStore v1.7.8 | HTML content validation powered by isCleanHtml()
    </div>
</body>
</html>
"""


PRODUCTS_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Products - PrestaStore</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #667eea; color: white; padding: 20px; }
        .header h1 { font-size: 24px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .breadcrumb { margin-bottom: 20px; color: #666; }
        .breadcrumb a { color: #667eea; text-decoration: none; }
        .products { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
        .product { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .product h3 { color: #333; margin-bottom: 10px; }
        .product .price { color: #667eea; font-size: 24px; font-weight: bold; }
        .product .category { color: #999; font-size: 12px; margin-top: 10px; }
        .back-link { display: inline-block; margin-top: 20px; color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <div class="header"><div class="container"><h1>&#128722; PrestaStore</h1></div></div>
    <div class="container">
        <p class="breadcrumb"><a href="/">Home</a> / Products</p>
        <div class="products">
            <div class="product">
                <h3>Wireless Mouse</h3>
                <p class="price">$29.99</p>
                <p class="category">Electronics</p>
            </div>
            <div class="product">
                <h3>USB-C Hub</h3>
                <p class="price">$49.99</p>
                <p class="category">Electronics</p>
            </div>
            <div class="product">
                <h3>Mechanical Keyboard</h3>
                <p class="price">$89.99</p>
                <p class="category">Electronics</p>
            </div>
            <div class="product">
                <h3>Monitor Stand</h3>
                <p class="price">$39.99</p>
                <p class="category">Accessories</p>
            </div>
        </div>
        <a href="/" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""


CONTACT_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Contact - PrestaStore</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }}
        .header {{ background: #667eea; color: white; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .breadcrumb {{ margin-bottom: 20px; color: #666; }}
        .breadcrumb a {{ color: #667eea; text-decoration: none; }}
        .form-box {{ background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; margin-bottom: 5px; color: #333; font-weight: bold; }}
        input, textarea {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }}
        textarea {{ height: 150px; resize: vertical; }}
        button {{ background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        button:hover {{ background: #5a6fd6; }}
        .alert {{ padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .alert-danger {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .back-link {{ display: inline-block; margin-top: 20px; color: #667eea; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="header"><div class="container" style="max-width:1200px"><h1>&#128722; PrestaStore</h1></div></div>
    <div class="container">
        <p class="breadcrumb"><a href="/">Home</a> / Contact</p>
        <div class="form-box">
            <h2 style="margin-bottom:20px">Contact Us</h2>
            {0}
            <form method="POST">
                <div class="form-group">
                    <label>Your Name</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Message</label>
                    <textarea name="message" required></textarea>
                </div>
                <button type="submit">Send Message</button>
            </form>
        </div>
        <a href="/" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""


REVIEWS_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Reviews - PrestaStore</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }}
        .header {{ background: #667eea; color: white; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .breadcrumb {{ margin-bottom: 20px; color: #666; }}
        .breadcrumb a {{ color: #667eea; text-decoration: none; }}
        .form-box {{ background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        textarea {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; height: 100px; }}
        button {{ background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px; }}
        .alert {{ padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .alert-success {{ background: #d4edda; color: #155724; }}
        .review {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .review .author {{ font-weight: bold; color: #333; }}
        .review .date {{ color: #999; font-size: 12px; }}
        .review .text {{ margin-top: 10px; color: #555; }}
        .back-link {{ display: inline-block; margin-top: 20px; color: #667eea; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="header"><div class="container" style="max-width:1200px"><h1>&#128722; PrestaStore</h1></div></div>
    <div class="container">
        <p class="breadcrumb"><a href="/">Home</a> / Reviews</p>
        <div class="form-box">
            <h2 style="margin-bottom:20px">Write a Review</h2>
            {0}
            <form method="POST">
                <textarea name="review" placeholder="Share your experience..."></textarea>
                <button type="submit">Submit Review</button>
            </form>
            <p style="margin-top:10px;color:#999;font-size:12px">Note: HTML is not allowed in reviews for security reasons.</p>
        </div>
        <h3 style="margin-bottom:15px">Recent Reviews</h3>
        <div class="review">
            <span class="author">John D.</span> <span class="date">2 days ago</span>
            <p class="text">Great products and fast shipping! Will definitely order again.</p>
        </div>
        <div class="review">
            <span class="author">Sarah M.</span> <span class="date">1 week ago</span>
            <p class="text">The quality exceeded my expectations. Highly recommend!</p>
        </div>
        <a href="/" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""


NEWSLETTER_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Newsletter - PrestaStore</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }}
        .header {{ background: #667eea; color: white; padding: 20px; }}
        .container {{ max-width: 500px; margin: 0 auto; padding: 20px; }}
        .breadcrumb {{ margin-bottom: 20px; color: #666; }}
        .breadcrumb a {{ color: #667eea; text-decoration: none; }}
        .form-box {{ background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
        input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; margin: 15px 0; }}
        button {{ background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; }}
        .alert {{ padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .alert-success {{ background: #d4edda; color: #155724; }}
        .alert-danger {{ background: #f8d7da; color: #721c24; }}
        .back-link {{ display: inline-block; margin-top: 20px; color: #667eea; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="header"><div class="container" style="max-width:1200px"><h1>&#128722; PrestaStore</h1></div></div>
    <div class="container">
        <p class="breadcrumb"><a href="/">Home</a> / Newsletter</p>
        <div class="form-box">
            <h2>&#128236; Stay Updated</h2>
            <p style="color:#666;margin-top:10px">Subscribe to our newsletter for deals and updates!</p>
            {0}
            <form method="POST">
                <input type="email" name="email" placeholder="Enter your email address" required>
                <button type="submit">Subscribe</button>
            </form>
        </div>
        <a href="/" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""


CUSTOMIZE_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Store Customization - PrestaStore</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }}
        .header {{ background: #667eea; color: white; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .breadcrumb {{ margin-bottom: 20px; color: #666; }}
        .breadcrumb a {{ color: #667eea; text-decoration: none; }}
        .form-box {{ background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        textarea {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; height: 150px; font-family: monospace; }}
        button {{ background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px; }}
        .alert {{ padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .alert-danger {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .alert-warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }}
        .alert-info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        .alert-secondary {{ background: #e2e3e5; color: #383d41; border: 1px solid #d6d8db; }}
        .preview-box {{ background: #f8f9fa; border: 2px dashed #dee2e6; border-radius: 10px; padding: 20px; min-height: 100px; }}
        .info {{ background: #e7f3ff; border: 1px solid #b8daff; border-radius: 5px; padding: 15px; margin-top: 20px; font-size: 13px; color: #004085; }}
        .back-link {{ display: inline-block; margin-top: 20px; color: #667eea; text-decoration: none; }}
        code {{ background: #f1f1f1; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="header"><div class="container" style="max-width:1200px"><h1>&#128722; PrestaStore</h1></div></div>
    <div class="container">
        <p class="breadcrumb"><a href="/">Home</a> / Store Customization</p>
        
        <div class="form-box">
            <h2 style="margin-bottom:20px">&#127912; Customize Store Description</h2>
            <p style="color:#666;margin-bottom:20px">Enter HTML content for your store description. Content is validated using our <code>isCleanHtml()</code> security filter.</p>
            
            {1}
            
            <form method="POST">
                <label style="display:block;margin-bottom:5px;font-weight:bold">Store Description (HTML allowed):</label>
                <textarea name="description" placeholder="Enter your store description with HTML formatting...">{2}</textarea>
                <button type="submit">Preview Content</button>
            </form>
            
            <div class="info">
                <strong>Security Notice:</strong> Content is filtered to prevent XSS attacks. Blocked elements include:
                <ul style="margin-top:10px;margin-left:20px">
                    <li>Script tags and JavaScript URLs</li>
                    <li>Dangerous tags (iframe, object, embed, svg, etc.)</li>
                    <li>Event handlers (onclick, onmouseover, onerror, etc.)</li>
                </ul>
            </div>
        </div>
        
        <div class="form-box">
            <h3 style="margin-bottom:15px">Content Preview</h3>
            <div class="preview-box">
                {0}
            </div>
        </div>
        
        <a href="/" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""


CUSTOMIZE_PREVIEW = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Preview</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
    </style>
</head>
<body>
    <div class="store-description">
        {0}
    </div>
</body>
</html>
"""


ADMIN_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin - PrestaStore</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #333; color: white; padding: 20px; }
        .container { max-width: 500px; margin: 100px auto; padding: 20px; }
        .login-box { background: white; border-radius: 10px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; margin: 10px 0; }
        button { background: #333; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 10px; }
        .back-link { display: inline-block; margin-top: 20px; color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <div class="header"><div class="container" style="max-width:1200px;margin:0 auto"><h1>&#128722; PrestaStore Admin</h1></div></div>
    <div class="container">
        <div class="login-box">
            <h2>&#128274; Admin Login</h2>
            <p style="color:#666;margin:15px 0">Authentication required to access admin panel.</p>
            <form method="POST" action="/admin/login">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Sign In</button>
            </form>
            <p style="margin-top:20px;color:#999;font-size:12px">Contact system administrator for access.</p>
        </div>
        <a href="/" class="back-link">&larr; Back to Store</a>
    </div>
</body>
</html>
"""


# Image routes (kept for compatibility with check_xss function)
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
