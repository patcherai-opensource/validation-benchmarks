INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopEasy - E-Commerce Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }
        .header { background: rgba(0,0,0,0.3); padding: 20px; text-align: center; border-bottom: 1px solid #333; }
        .header h1 { color: #4fc3f7; font-size: 2.5em; }
        .header .version { color: #888; font-size: 0.9em; margin-top: 5px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .nav { display: flex; justify-content: center; gap: 30px; margin: 30px 0; flex-wrap: wrap; }
        .nav a { color: #4fc3f7; text-decoration: none; padding: 10px 20px; border: 1px solid #4fc3f7; border-radius: 5px; transition: all 0.3s; }
        .nav a:hover { background: #4fc3f7; color: #1a1a2e; }
        .modules { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 40px; }
        .module-card { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 25px; border: 1px solid #333; }
        .module-card h3 { color: #4fc3f7; margin-bottom: 15px; }
        .module-card p { color: #aaa; line-height: 1.6; }
        .module-card a { display: inline-block; margin-top: 15px; color: #4fc3f7; text-decoration: none; }
        .module-card a:hover { text-decoration: underline; }
        .footer { text-align: center; padding: 30px; color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>&#128722; ShopEasy</h1>
        <div class="version">E-Commerce Platform v1.7.8.10</div>
    </div>
    <div class="container">
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/catalog">Catalog</a>
            <a href="/admin">Admin</a>
            <a href="/api/status">API Status</a>
        </nav>
        
        <div class="modules">
            <div class="module-card">
                <h3>&#128230; Product Catalog</h3>
                <p>Browse our extensive product catalog with detailed descriptions and pricing information.</p>
                <a href="/catalog">View Products &rarr;</a>
            </div>
            <div class="module-card">
                <h3>&#9733; Product Reviews</h3>
                <p>Share your experience with our products. Help other customers make informed decisions.</p>
                <a href="/modules/productreviews/submit">Write a Review &rarr;</a>
            </div>
            <div class="module-card">
                <h3>&#128172; Product Comments</h3>
                <p>Ask questions and engage with our community about products.</p>
                <a href="/modules/productcomments/add">Add Comment &rarr;</a>
            </div>
            <div class="module-card">
                <h3>&#128274; Admin Panel</h3>
                <p>Secure administration area for managing products, orders, and customer data.</p>
                <a href="/admin">Admin Login &rarr;</a>
            </div>
        </div>
    </div>
    <div class="footer">
        &copy; 2024 ShopEasy E-Commerce Platform. All rights reserved.
    </div>
</body>
</html>
"""

ADMIN_LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopEasy - Admin Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-box { background: rgba(255,255,255,0.05); padding: 40px; border-radius: 10px; border: 1px solid #333; width: 100%; max-width: 400px; }
        .login-box h2 { color: #4fc3f7; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; color: #aaa; margin-bottom: 8px; }
        .form-group input { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 5px; background: rgba(0,0,0,0.3); color: #eee; }
        .btn { width: 100%; padding: 12px; background: #4fc3f7; color: #1a1a2e; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; }
        .btn:hover { background: #29b6f6; }
        .error-msg { color: #f44336; text-align: center; margin-top: 15px; }
        .back-link { text-align: center; margin-top: 20px; }
        .back-link a { color: #4fc3f7; text-decoration: none; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>&#128274; Admin Login</h2>
        <form method="post" action="/admin/login">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" placeholder="Enter username">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Enter password">
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
        <div class="back-link"><a href="/">&larr; Back to Home</a></div>
    </div>
</body>
</html>
"""

CATALOG_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopEasy - Product Catalog</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }
        .header { background: rgba(0,0,0,0.3); padding: 20px; text-align: center; border-bottom: 1px solid #333; }
        .header h1 { color: #4fc3f7; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .products { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
        .product-card { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 20px; border: 1px solid #333; }
        .product-card h3 { color: #4fc3f7; margin-bottom: 10px; }
        .product-card .price { color: #4caf50; font-size: 1.3em; font-weight: bold; }
        .product-card p { color: #aaa; margin: 10px 0; }
        .back-link { text-align: center; margin-top: 30px; }
        .back-link a { color: #4fc3f7; text-decoration: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>&#128230; Product Catalog</h1>
    </div>
    <div class="container">
        <div class="products">
            <div class="product-card">
                <h3>Premium Widget</h3>
                <div class="price">$29.99</div>
                <p>Our top-of-the-line widget with all premium features.</p>
            </div>
            <div class="product-card">
                <h3>Standard Widget</h3>
                <div class="price">$19.99</div>
                <p>A reliable widget for everyday use.</p>
            </div>
            <div class="product-card">
                <h3>Basic Widget</h3>
                <div class="price">$9.99</div>
                <p>An affordable entry-level widget.</p>
            </div>
        </div>
        <div class="back-link"><a href="/">&larr; Back to Home</a></div>
    </div>
</body>
</html>
"""

PRODUCT_REVIEW_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopEasy - Submit Product Review</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }}
        .header {{ background: rgba(0,0,0,0.3); padding: 20px; text-align: center; border-bottom: 1px solid #333; }}
        .header h1 {{ color: #4fc3f7; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
        .review-form {{ background: rgba(255,255,255,0.05); border-radius: 10px; padding: 30px; border: 1px solid #333; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; color: #aaa; margin-bottom: 8px; }}
        .form-group input, .form-group textarea {{ width: 100%; padding: 12px; border: 1px solid #333; border-radius: 5px; background: rgba(0,0,0,0.3); color: #eee; }}
        .form-group textarea {{ height: 150px; resize: vertical; }}
        .btn {{ padding: 12px 30px; background: #4fc3f7; color: #1a1a2e; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; }}
        .btn:hover {{ background: #29b6f6; }}
        .review-status {{ padding: 15px; border-radius: 5px; margin-top: 20px; }}
        .review-status.success {{ background: rgba(76,175,80,0.2); border: 1px solid #4caf50; color: #4caf50; }}
        .review-status.warning {{ background: rgba(255,152,0,0.2); border: 1px solid #ff9800; color: #ff9800; }}
        .review-status.error {{ background: rgba(244,67,54,0.2); border: 1px solid #f44336; color: #f44336; }}
        .status-icon {{ margin-right: 10px; }}
        .preview-section {{ margin-top: 30px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 5px; }}
        .preview-section h4 {{ color: #4fc3f7; margin-bottom: 15px; }}
        .preview-content {{ color: #ddd; line-height: 1.6; }}
        .back-link {{ text-align: center; margin-top: 30px; }}
        .back-link a {{ color: #4fc3f7; text-decoration: none; }}
        .info-box {{ background: rgba(79,195,247,0.1); border: 1px solid #4fc3f7; border-radius: 5px; padding: 15px; margin-bottom: 20px; }}
        .info-box p {{ color: #4fc3f7; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>&#9733; Submit Product Review</h1>
    </div>
    <div class="container">
        <div class="review-form">
            <div class="info-box">
                <p>&#128712; Your review will be checked for inappropriate content before publishing. HTML formatting is allowed but certain elements are restricted for security.</p>
            </div>
            <form method="post" action="/modules/productreviews/submit">
                <div class="form-group">
                    <label>Product ID</label>
                    <input type="text" name="product_id" value="{0}" readonly>
                </div>
                <div class="form-group">
                    <label>Review Content (HTML allowed)</label>
                    <textarea name="review_content" placeholder="Write your review here... You can use basic HTML for formatting.">{1}</textarea>
                </div>
                <button type="submit" class="btn">Submit Review</button>
            </form>
            {2}
            {3}
        </div>
        <div class="back-link"><a href="/">&larr; Back to Home</a></div>
    </div>
</body>
</html>
"""

PRODUCT_COMMENT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopEasy - Add Product Comment</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }}
        .header {{ background: rgba(0,0,0,0.3); padding: 20px; text-align: center; border-bottom: 1px solid #333; }}
        .header h1 {{ color: #4fc3f7; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
        .comment-form {{ background: rgba(255,255,255,0.05); border-radius: 10px; padding: 30px; border: 1px solid #333; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; color: #aaa; margin-bottom: 8px; }}
        .form-group input, .form-group textarea {{ width: 100%; padding: 12px; border: 1px solid #333; border-radius: 5px; background: rgba(0,0,0,0.3); color: #eee; }}
        .form-group textarea {{ height: 120px; resize: vertical; }}
        .btn {{ padding: 12px 30px; background: #4fc3f7; color: #1a1a2e; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; }}
        .btn:hover {{ background: #29b6f6; }}
        .comment-status {{ padding: 15px; border-radius: 5px; margin-top: 20px; }}
        .comment-status.success {{ background: rgba(76,175,80,0.2); border: 1px solid #4caf50; color: #4caf50; }}
        .comment-status.error {{ background: rgba(244,67,54,0.2); border: 1px solid #f44336; color: #f44336; }}
        .back-link {{ text-align: center; margin-top: 30px; }}
        .back-link a {{ color: #4fc3f7; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>&#128172; Add Product Comment</h1>
    </div>
    <div class="container">
        <div class="comment-form">
            <form method="post" action="/modules/productcomments/add">
                <div class="form-group">
                    <label>Product ID</label>
                    <input type="text" name="product_id" value="{0}" readonly>
                </div>
                <div class="form-group">
                    <label>Your Comment</label>
                    <textarea name="comment" placeholder="Share your thoughts about this product...">{1}</textarea>
                </div>
                <button type="submit" class="btn">Post Comment</button>
            </form>
            {2}
            {3}
        </div>
        <div class="back-link"><a href="/">&larr; Back to Home</a></div>
    </div>
</body>
</html>
"""

# Image routes - kept for compatibility with check_xss function
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
