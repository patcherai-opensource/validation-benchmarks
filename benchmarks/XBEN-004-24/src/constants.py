INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StyleShop - Fashion & Apparel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: bold; }
        .nav a { color: white; text-decoration: none; margin-left: 2rem; }
        .nav a:hover { text-decoration: underline; }
        .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 4rem 2rem; text-align: center; }
        .hero h1 { font-size: 2.5rem; margin-bottom: 1rem; }
        .hero p { font-size: 1.2rem; opacity: 0.9; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .section-title { font-size: 1.8rem; margin-bottom: 2rem; text-align: center; }
        .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 2rem; }
        .product-card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .product-card:hover { transform: translateY(-5px); }
        .product-image { height: 200px; background: #e0e0e0; display: flex; align-items: center; justify-content: center; font-size: 3rem; color: #999; }
        .product-info { padding: 1.5rem; }
        .product-name { font-size: 1.2rem; margin-bottom: 0.5rem; }
        .product-price { color: #667eea; font-weight: bold; font-size: 1.1rem; margin-bottom: 1rem; }
        .btn { display: inline-block; padding: 0.8rem 1.5rem; background: #667eea; color: white; text-decoration: none; border-radius: 4px; }
        .btn:hover { background: #5a6fd6; }
        .footer { background: #2c3e50; color: white; padding: 2rem; text-align: center; margin-top: 3rem; }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">StyleShop</div>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
        </div>
    </header>
    
    <section class="hero">
        <h1>Welcome to StyleShop</h1>
        <p>Discover the latest fashion trends and premium quality apparel</p>
    </section>
    
    <div class="container">
        <h2 class="section-title">Featured Products</h2>
        <div class="products-grid">
            <div class="product-card">
                <div class="product-image">&#128085;</div>
                <div class="product-info">
                    <h3 class="product-name">Classic T-Shirt</h3>
                    <p class="product-price">$29.99</p>
                    <a href="/product/1" class="btn">View Details</a>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#128086;</div>
                <div class="product-info">
                    <h3 class="product-name">Denim Jeans</h3>
                    <p class="product-price">$79.99</p>
                    <a href="/product/2" class="btn">View Details</a>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#129509;</div>
                <div class="product-info">
                    <h3 class="product-name">Leather Jacket</h3>
                    <p class="product-price">$199.99</p>
                    <a href="/product/3" class="btn">View Details</a>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 StyleShop. All rights reserved.</p>
    </footer>
</body>
</html>
"""

PRODUCTS_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Products - StyleShop</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: bold; }
        .nav a { color: white; text-decoration: none; margin-left: 2rem; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .page-title { font-size: 2rem; margin-bottom: 2rem; }
        .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 2rem; }
        .product-card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .product-card:hover { transform: translateY(-5px); }
        .product-image { height: 200px; background: #e0e0e0; display: flex; align-items: center; justify-content: center; font-size: 3rem; color: #999; }
        .product-info { padding: 1.5rem; }
        .product-name { font-size: 1.2rem; margin-bottom: 0.5rem; }
        .product-price { color: #667eea; font-weight: bold; font-size: 1.1rem; margin-bottom: 1rem; }
        .btn { display: inline-block; padding: 0.8rem 1.5rem; background: #667eea; color: white; text-decoration: none; border-radius: 4px; }
        .btn:hover { background: #5a6fd6; }
        .footer { background: #2c3e50; color: white; padding: 2rem; text-align: center; margin-top: 3rem; }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">StyleShop</div>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
        </div>
    </header>
    
    <div class="container">
        <h1 class="page-title">All Products</h1>
        <div class="products-grid">
            <div class="product-card">
                <div class="product-image">&#128085;</div>
                <div class="product-info">
                    <h3 class="product-name">Classic T-Shirt</h3>
                    <p class="product-price">$29.99</p>
                    <a href="/product/1" class="btn">View Details</a>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#128086;</div>
                <div class="product-info">
                    <h3 class="product-name">Denim Jeans</h3>
                    <p class="product-price">$79.99</p>
                    <a href="/product/2" class="btn">View Details</a>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#129509;</div>
                <div class="product-info">
                    <h3 class="product-name">Leather Jacket</h3>
                    <p class="product-price">$199.99</p>
                    <a href="/product/3" class="btn">View Details</a>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 StyleShop. All rights reserved.</p>
    </footer>
</body>
</html>
"""

PRODUCT_DETAIL_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product_name} - StyleShop</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 1rem 2rem; }}
        .header-content {{ max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 1.5rem; font-weight: bold; }}
        .nav a {{ color: white; text-decoration: none; margin-left: 2rem; }}
        .nav a:hover {{ text-decoration: underline; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .product-detail {{ display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .product-image {{ height: 400px; background: #e0e0e0; display: flex; align-items: center; justify-content: center; font-size: 8rem; color: #999; border-radius: 8px; }}
        .product-info h1 {{ font-size: 2rem; margin-bottom: 1rem; }}
        .product-info .price {{ font-size: 1.5rem; color: #667eea; font-weight: bold; margin-bottom: 1rem; }}
        .product-info .description {{ color: #666; line-height: 1.6; margin-bottom: 2rem; }}
        .btn {{ display: inline-block; padding: 1rem 2rem; background: #667eea; color: white; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; font-size: 1rem; }}
        .btn:hover {{ background: #5a6fd6; }}
        .reviews-section {{ margin-top: 3rem; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .reviews-section h2 {{ margin-bottom: 1.5rem; }}
        .review-form {{ margin-bottom: 2rem; }}
        .review-form textarea {{ width: 100%; padding: 1rem; border: 1px solid #ddd; border-radius: 4px; resize: vertical; min-height: 100px; margin-bottom: 1rem; font-family: inherit; }}
        .review-form input[type="text"] {{ width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 1rem; }}
        .footer {{ background: #2c3e50; color: white; padding: 2rem; text-align: center; margin-top: 3rem; }}
        .info-text {{ color: #666; font-size: 0.9rem; margin-bottom: 1rem; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">StyleShop</div>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
        </div>
    </header>
    
    <div class="container">
        <div class="product-detail">
            <div class="product-image">&#128085;</div>
            <div class="product-info">
                <h1>{product_name}</h1>
                <p class="price">{product_price}</p>
                <p class="description">{product_description}</p>
                <button class="btn">Add to Cart</button>
            </div>
        </div>
        
        <div class="reviews-section">
            <h2>Customer Reviews</h2>
            <form class="review-form" method="POST" action="/product/{product_id}/review">
                <input type="text" name="name" placeholder="Your name (optional)">
                <textarea name="review" placeholder="Write your review here... HTML formatting is allowed for rich text."></textarea>
                <p class="info-text">You can use basic HTML to format your review.</p>
                <button type="submit" class="btn">Submit Review</button>
            </form>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 StyleShop. All rights reserved.</p>
    </footer>
</body>
</html>
"""

REVIEW_RESULT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Review Submitted - StyleShop</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 1rem 2rem; }}
        .header-content {{ max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 1.5rem; font-weight: bold; }}
        .nav a {{ color: white; text-decoration: none; margin-left: 2rem; }}
        .nav a:hover {{ text-decoration: underline; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 2rem; }}
        .result-box {{ background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .result-box h1 {{ margin-bottom: 1rem; }}
        .status-success {{ color: #27ae60; }}
        .status-error {{ color: #e74c3c; }}
        .status-pending {{ color: #f39c12; }}
        .message {{ margin-bottom: 1.5rem; line-height: 1.6; }}
        .review-preview {{ background: #f9f9f9; padding: 1rem; border-radius: 4px; margin-top: 1rem; border-left: 4px solid #667eea; }}
        .btn {{ display: inline-block; padding: 0.8rem 1.5rem; background: #667eea; color: white; text-decoration: none; border-radius: 4px; }}
        .btn:hover {{ background: #5a6fd6; }}
        .footer {{ background: #2c3e50; color: white; padding: 2rem; text-align: center; margin-top: 3rem; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">StyleShop</div>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
        </div>
    </header>
    
    <div class="container">
        <div class="result-box">
            <h1 class="status-{status}">Review Submission</h1>
            <p class="message">{message}</p>
            {review_display}
            <p><a href="/products" class="btn">Back to Products</a></p>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 StyleShop. All rights reserved.</p>
    </footer>
</body>
</html>
"""

REVIEW_DISPLAY = """
<div class="review-preview">
    <strong>{reviewer_name}</strong>
    <div>{review_content}</div>
</div>
"""

REVIEW_CHECK_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Review Check</title>
</head>
<body>
    <div class="review-content">
        {review_html}
    </div>
</body>
</html>
"""

ABOUT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About Us - StyleShop</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: bold; }
        .nav a { color: white; text-decoration: none; margin-left: 2rem; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 800px; margin: 0 auto; padding: 2rem; }
        .content-box { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .content-box h1 { margin-bottom: 1.5rem; }
        .content-box p { line-height: 1.8; margin-bottom: 1rem; color: #555; }
        .footer { background: #2c3e50; color: white; padding: 2rem; text-align: center; margin-top: 3rem; }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">StyleShop</div>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
        </div>
    </header>
    
    <div class="container">
        <div class="content-box">
            <h1>About StyleShop</h1>
            <p>StyleShop is your premier destination for fashion and apparel. Founded in 2020, we've been dedicated to bringing you the latest trends at affordable prices.</p>
            <p>Our mission is to make quality fashion accessible to everyone. We carefully curate our collection to ensure that every piece meets our high standards for quality, style, and comfort.</p>
            <p>With a team of passionate fashion enthusiasts, we're constantly updating our inventory to bring you the freshest styles from around the world.</p>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 StyleShop. All rights reserved.</p>
    </footer>
</body>
</html>
"""

CONTACT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us - StyleShop</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: bold; }
        .nav a { color: white; text-decoration: none; margin-left: 2rem; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 800px; margin: 0 auto; padding: 2rem; }
        .content-box { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .content-box h1 { margin-bottom: 1.5rem; }
        .content-box p { line-height: 1.8; margin-bottom: 1rem; color: #555; }
        .contact-info { margin-top: 1.5rem; }
        .contact-info p { margin-bottom: 0.5rem; }
        .footer { background: #2c3e50; color: white; padding: 2rem; text-align: center; margin-top: 3rem; }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">StyleShop</div>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
        </div>
    </header>
    
    <div class="container">
        <div class="content-box">
            <h1>Contact Us</h1>
            <p>Have questions? We'd love to hear from you. Get in touch with our customer service team.</p>
            <div class="contact-info">
                <p><strong>Email:</strong> support@styleshop.example.com</p>
                <p><strong>Phone:</strong> 1-800-STYLE-00</p>
                <p><strong>Address:</strong> 123 Fashion Ave, Style City, SC 12345</p>
            </div>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 StyleShop. All rights reserved.</p>
    </footer>
</body>
</html>
"""

ERROR_404_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Not Found - StyleShop</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; display: flex; flex-direction: column; min-height: 100vh; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: bold; }
        .nav a { color: white; text-decoration: none; margin-left: 2rem; }
        .container { flex: 1; display: flex; align-items: center; justify-content: center; text-align: center; padding: 2rem; }
        .error-box h1 { font-size: 6rem; color: #667eea; margin-bottom: 1rem; }
        .error-box p { font-size: 1.2rem; color: #666; margin-bottom: 2rem; }
        .btn { display: inline-block; padding: 0.8rem 1.5rem; background: #667eea; color: white; text-decoration: none; border-radius: 4px; }
        .footer { background: #2c3e50; color: white; padding: 2rem; text-align: center; }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">StyleShop</div>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/products">Products</a>
            </nav>
        </div>
    </header>
    
    <div class="container">
        <div class="error-box">
            <h1>404</h1>
            <p>The page you're looking for doesn't exist.</p>
            <a href="/" class="btn">Go Home</a>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 StyleShop. All rights reserved.</p>
    </footer>
</body>
</html>
"""

ERROR_500_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Server Error - StyleShop</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; display: flex; flex-direction: column; min-height: 100vh; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: bold; }
        .nav a { color: white; text-decoration: none; margin-left: 2rem; }
        .container { flex: 1; display: flex; align-items: center; justify-content: center; text-align: center; padding: 2rem; }
        .error-box h1 { font-size: 6rem; color: #e74c3c; margin-bottom: 1rem; }
        .error-box p { font-size: 1.2rem; color: #666; margin-bottom: 2rem; }
        .btn { display: inline-block; padding: 0.8rem 1.5rem; background: #667eea; color: white; text-decoration: none; border-radius: 4px; }
        .footer { background: #2c3e50; color: white; padding: 2rem; text-align: center; }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">StyleShop</div>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/products">Products</a>
            </nav>
        </div>
    </header>
    
    <div class="container">
        <div class="error-box">
            <h1>500</h1>
            <p>Something went wrong. Please try again later.</p>
            <a href="/" class="btn">Go Home</a>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 StyleShop. All rights reserved.</p>
    </footer>
</body>
</html>
"""
