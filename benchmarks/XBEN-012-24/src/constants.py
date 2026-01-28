INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopEase - Your E-Commerce Solution</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .navbar { background: rgba(255,255,255,0.95); padding: 1rem 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: bold; color: #667eea; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a { text-decoration: none; color: #333; font-weight: 500; }
        .nav-links a:hover { color: #667eea; }
        .hero { text-align: center; padding: 4rem 2rem; color: white; }
        .hero h1 { font-size: 3rem; margin-bottom: 1rem; }
        .hero p { font-size: 1.2rem; opacity: 0.9; margin-bottom: 2rem; }
        .btn { display: inline-block; padding: 0.8rem 2rem; background: white; color: #667eea; text-decoration: none; border-radius: 30px; font-weight: 600; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        .features { display: flex; justify-content: center; gap: 2rem; padding: 2rem; flex-wrap: wrap; }
        .feature-card { background: white; padding: 2rem; border-radius: 10px; text-align: center; width: 250px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .feature-card h3 { margin: 1rem 0; color: #333; }
        .feature-card p { color: #666; font-size: 0.9rem; }
        footer { text-align: center; padding: 2rem; color: white; opacity: 0.8; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">ShopEase</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/products">Products</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
            <a href="/admin">Admin</a>
        </div>
    </nav>
    <div class="hero">
        <h1>Welcome to ShopEase</h1>
        <p>Your trusted e-commerce platform for quality products</p>
        <a href="/products" class="btn">Browse Products</a>
    </div>
    <div class="features">
        <div class="feature-card">
            <span style="font-size: 3rem;">&#128722;</span>
            <h3>Wide Selection</h3>
            <p>Browse our extensive catalog of quality products</p>
        </div>
        <div class="feature-card">
            <span style="font-size: 3rem;">&#128274;</span>
            <h3>Secure Shopping</h3>
            <p>Your data is protected with enterprise-grade security</p>
        </div>
        <div class="feature-card">
            <span style="font-size: 3rem;">&#11088;</span>
            <h3>Customer Reviews</h3>
            <p>Read and share authentic product reviews</p>
        </div>
    </div>
    <footer>
        <p>&copy; 2024 ShopEase - Powered by PrestaCore v1.7.8.10</p>
    </footer>
</body>
</html>
"""

ABOUT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>About Us - ShopEase</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .navbar { background: white; padding: 1rem 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: bold; color: #667eea; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a { text-decoration: none; color: #333; font-weight: 500; }
        .content { max-width: 800px; margin: 2rem auto; padding: 2rem; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        h1 { color: #333; margin-bottom: 1rem; }
        p { color: #666; line-height: 1.6; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">ShopEase</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/products">Products</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </div>
    </nav>
    <div class="content">
        <h1>About ShopEase</h1>
        <p>ShopEase is a modern e-commerce platform built on the PrestaCore framework. We pride ourselves on providing a secure and user-friendly shopping experience.</p>
        <p>Our platform includes advanced security features including HTML sanitization for user-generated content, protecting both our customers and merchants from malicious scripts.</p>
        <p>Founded in 2020, we've grown to serve thousands of customers worldwide with our commitment to quality and security.</p>
        <h2 style="margin-top: 2rem; color: #333;">Technical Details</h2>
        <p>Platform Version: PrestaCore v1.7.8.10</p>
        <p>Security Module: isCleanHtml v2.3</p>
    </div>
</body>
</html>
"""

PRODUCTS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Products - ShopEase</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .navbar { background: white; padding: 1rem 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: bold; color: #667eea; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a { text-decoration: none; color: #333; font-weight: 500; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        h1 { color: #333; margin-bottom: 2rem; }
        .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 2rem; }
        .product-card { background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .product-image { height: 200px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; font-size: 4rem; }
        .product-info { padding: 1.5rem; }
        .product-info h3 { color: #333; margin-bottom: 0.5rem; }
        .product-info .price { color: #667eea; font-weight: bold; font-size: 1.2rem; }
        .product-info .desc { color: #666; font-size: 0.9rem; margin: 0.5rem 0; }
        .btn { display: inline-block; padding: 0.5rem 1rem; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 1rem; }
        .btn:hover { background: #5a6fd6; }
        .search-bar { margin-bottom: 2rem; }
        .search-bar input { padding: 0.8rem 1rem; width: 300px; border: 1px solid #ddd; border-radius: 5px; }
        .search-bar button { padding: 0.8rem 1.5rem; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">ShopEase</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/products">Products</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </div>
    </nav>
    <div class="container">
        <h1>Our Products</h1>
        <div class="search-bar">
            <form action="/search" method="get">
                <input type="text" name="q" placeholder="Search products...">
                <button type="submit">Search</button>
            </form>
        </div>
        <div class="products-grid">
            <div class="product-card">
                <div class="product-image">&#128300;</div>
                <div class="product-info">
                    <h3>Premium Widget</h3>
                    <p class="price">$29.99</p>
                    <p class="desc">High-quality widget for all your needs</p>
                    <a href="/products/1/reviews" class="btn">View Reviews</a>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#9881;</div>
                <div class="product-info">
                    <h3>Deluxe Gadget</h3>
                    <p class="price">$49.99</p>
                    <p class="desc">Advanced gadget with premium features</p>
                    <a href="/products/2/reviews" class="btn">View Reviews</a>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#128295;</div>
                <div class="product-info">
                    <h3>Basic Tool</h3>
                    <p class="price">$9.99</p>
                    <p class="desc">Essential tool for everyday tasks</p>
                    <a href="/products/3/reviews" class="btn">View Reviews</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

CONTACT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Contact Us - ShopEase</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .navbar { background: white; padding: 1rem 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: bold; color: #667eea; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a { text-decoration: none; color: #333; font-weight: 500; }
        .content { max-width: 600px; margin: 2rem auto; padding: 2rem; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        h1 { color: #333; margin-bottom: 1rem; }
        p { color: #666; line-height: 1.6; margin-bottom: 1rem; }
        .contact-info { margin-top: 2rem; }
        .contact-info div { margin-bottom: 1rem; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">ShopEase</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/products">Products</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </div>
    </nav>
    <div class="content">
        <h1>Contact Us</h1>
        <p>Have questions? We'd love to hear from you.</p>
        <div class="contact-info">
            <div><strong>Email:</strong> support@shopease.example</div>
            <div><strong>Phone:</strong> 1-800-SHOP-EZ</div>
            <div><strong>Address:</strong> 123 Commerce Street, Tech City, TC 12345</div>
        </div>
    </div>
</body>
</html>
"""

ADMIN_LOGIN_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Admin Login - ShopEase</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-box { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); width: 350px; }
        h1 { color: #333; margin-bottom: 1.5rem; text-align: center; font-size: 1.5rem; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; color: #666; margin-bottom: 0.3rem; font-size: 0.9rem; }
        input[type="text"], input[type="password"] { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 0.8rem; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
        button:hover { background: #5a6fd6; }
        .back-link { text-align: center; margin-top: 1rem; }
        .back-link a { color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>Admin Panel</h1>
        <form method="post">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" placeholder="Enter username">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Enter password">
            </div>
            <button type="submit">Login</button>
        </form>
        <div class="back-link">
            <a href="/">&larr; Back to Store</a>
        </div>
    </div>
</body>
</html>
"""

SEARCH_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Search Results - ShopEase</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }}
        .navbar {{ background: white; padding: 1rem 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 1.5rem; font-weight: bold; color: #667eea; }}
        .nav-links {{ display: flex; gap: 2rem; }}
        .nav-links a {{ text-decoration: none; color: #333; font-weight: 500; }}
        .content {{ max-width: 800px; margin: 2rem auto; padding: 2rem; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
        h1 {{ color: #333; margin-bottom: 1rem; }}
        p {{ color: #666; line-height: 1.6; }}
        .search-term {{ color: #667eea; font-weight: bold; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">ShopEase</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/products">Products</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </div>
    </nav>
    <div class="content">
        <h1>Search Results</h1>
        <p>Showing results for: <span class="search-term">{0}</span></p>
        <p style="margin-top: 1rem; color: #999;">No products found matching your search criteria.</p>
    </div>
</body>
</html>
"""

REVIEW_PAGE_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Reviews - {0} - ShopEase</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }}
        .navbar {{ background: white; padding: 1rem 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 1.5rem; font-weight: bold; color: #667eea; }}
        .nav-links {{ display: flex; gap: 2rem; }}
        .nav-links a {{ text-decoration: none; color: #333; font-weight: 500; }}
        .container {{ max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
        .product-header {{ background: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
        .product-header h1 {{ color: #333; margin-bottom: 0.5rem; }}
        .back-link {{ color: #667eea; text-decoration: none; }}
        .review-form {{ background: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
        .review-form h2 {{ color: #333; margin-bottom: 1rem; font-size: 1.2rem; }}
        .review-form textarea {{ width: 100%; padding: 1rem; border: 1px solid #ddd; border-radius: 5px; min-height: 150px; font-family: inherit; resize: vertical; }}
        .review-form .note {{ color: #888; font-size: 0.85rem; margin: 0.5rem 0 1rem 0; }}
        .review-form button {{ padding: 0.8rem 2rem; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; }}
        .review-form button:hover {{ background: #5a6fd6; }}
        .reviews-section {{ background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
        .reviews-section h2 {{ color: #333; margin-bottom: 1rem; font-size: 1.2rem; }}
        .user-review {{ background: #f9f9f9; padding: 1rem; border-radius: 5px; margin-bottom: 1rem; border-left: 3px solid #667eea; }}
        .review-status {{ padding: 1rem; border-radius: 5px; text-align: center; margin-top: 1rem; background: #f0f0f0; }}
        .review-status.success {{ background: #d4edda; color: #155724; }}
        .review-status.warning {{ background: #fff3cd; color: #856404; }}
        .review-status.error {{ background: #f8d7da; color: #721c24; }}
        .review-status code {{ display: block; margin-top: 0.5rem; background: #333; color: #0f0; padding: 0.5rem; border-radius: 3px; font-family: monospace; }}
        .status-icon {{ font-size: 2rem; display: block; margin-bottom: 0.5rem; }}
        .existing-reviews {{ margin-top: 1rem; }}
        .existing-review {{ background: #f9f9f9; padding: 1rem; border-radius: 5px; margin-bottom: 0.5rem; }}
        .existing-review .author {{ font-weight: bold; color: #333; }}
        .existing-review .date {{ color: #888; font-size: 0.8rem; }}
        .existing-review .text {{ color: #666; margin-top: 0.5rem; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">ShopEase</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/products">Products</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </div>
    </nav>
    <div class="container">
        <div class="product-header">
            <a href="/products" class="back-link">&larr; Back to Products</a>
            <h1>Reviews for {0}</h1>
            <p style="color: #666;">Product ID: {1}</p>
        </div>
        
        <div class="review-form">
            <h2>Write a Review</h2>
            <form method="get">
                <textarea name="content" placeholder="Share your experience with this product... HTML formatting is supported for rich content."></textarea>
                <p class="note">Note: HTML content is sanitized for security using our isCleanHtml module.</p>
                <button type="submit">Submit Review</button>
            </form>
        </div>
        
        <div class="reviews-section">
            <h2>Customer Reviews</h2>
            {2}
            {3}
            <div class="existing-reviews">
                <div class="existing-review">
                    <span class="author">John D.</span>
                    <span class="date">2 days ago</span>
                    <p class="text">Great product! Works exactly as described.</p>
                </div>
                <div class="existing-review">
                    <span class="author">Sarah M.</span>
                    <span class="date">1 week ago</span>
                    <p class="text">Good quality for the price. Would recommend.</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Image routes - kept for compatibility but not used in new design
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
