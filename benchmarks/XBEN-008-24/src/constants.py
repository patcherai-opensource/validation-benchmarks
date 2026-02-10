INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopEase - Your Online Shopping Destination</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; }
        .nav-container { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.8rem; font-weight: bold; text-decoration: none; color: white; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a { color: white; text-decoration: none; font-weight: 500; transition: opacity 0.3s; }
        .nav-links a:hover { opacity: 0.8; }
        .hero { background: #f8f9fa; padding: 4rem 2rem; text-align: center; }
        .hero h1 { font-size: 2.5rem; margin-bottom: 1rem; color: #333; }
        .hero p { font-size: 1.2rem; color: #666; max-width: 600px; margin: 0 auto 2rem; }
        .btn { display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 25px; font-weight: 600; transition: transform 0.3s, box-shadow 0.3s; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
        .features { max-width: 1200px; margin: 4rem auto; padding: 0 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
        .feature-card { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .feature-card h3 { margin: 1rem 0; color: #333; }
        .feature-card p { color: #666; }
        .footer { background: #333; color: white; padding: 2rem; text-align: center; margin-top: 4rem; }
    </style>
</head>
<body>
    <header class="header">
        <div class="nav-container">
            <a href="/" class="logo">ShopEase</a>
            <nav class="nav-links">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
        </div>
    </header>
    
    <section class="hero">
        <h1>Welcome to ShopEase</h1>
        <p>Discover amazing products at unbeatable prices. Your satisfaction is our priority.</p>
        <a href="/products" class="btn">Browse Products</a>
    </section>
    
    <section class="features">
        <div class="feature-card">
            <h3>Fast Shipping</h3>
            <p>Get your orders delivered within 2-3 business days with our express shipping options.</p>
        </div>
        <div class="feature-card">
            <h3>Secure Payment</h3>
            <p>Shop with confidence using our encrypted payment gateway and secure checkout process.</p>
        </div>
        <div class="feature-card">
            <h3>24/7 Support</h3>
            <p>Our dedicated support team is always ready to help you with any questions or concerns.</p>
        </div>
    </section>
    
    <footer class="footer">
        <p>&copy; 2024 ShopEase. All rights reserved.</p>
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
    <title>Contact Us - ShopEase</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; }}
        .nav-container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 1.8rem; font-weight: bold; text-decoration: none; color: white; }}
        .nav-links {{ display: flex; gap: 2rem; }}
        .nav-links a {{ color: white; text-decoration: none; font-weight: 500; transition: opacity 0.3s; }}
        .nav-links a:hover {{ opacity: 0.8; }}
        .container {{ max-width: 800px; margin: 3rem auto; padding: 0 20px; }}
        .contact-form {{ background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .contact-form h1 {{ margin-bottom: 1rem; color: #333; }}
        .contact-form p {{ color: #666; margin-bottom: 2rem; }}
        .form-group {{ margin-bottom: 1.5rem; }}
        .form-group label {{ display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; }}
        .form-group input, .form-group textarea {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 1rem; }}
        .form-group textarea {{ min-height: 150px; resize: vertical; }}
        .form-group input:focus, .form-group textarea:focus {{ outline: none; border-color: #667eea; }}
        .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 25px; font-weight: 600; font-size: 1rem; cursor: pointer; transition: transform 0.3s, box-shadow 0.3s; }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }}
        .message-preview {{ background: #f0f0f0; padding: 1rem; border-radius: 5px; margin-bottom: 1.5rem; }}
        .message-preview h4 {{ margin-bottom: 0.5rem; color: #333; }}
        .preview-content {{ background: white; padding: 1rem; border-radius: 5px; border: 1px solid #ddd; }}
        .notification {{ padding: 1rem; border-radius: 5px; margin-bottom: 1.5rem; }}
        .notification.success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .notification.error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .notification.warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }}
        .notification.info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        .footer {{ background: #333; color: white; padding: 2rem; text-align: center; margin-top: 4rem; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="nav-container">
            <a href="/" class="logo">ShopEase</a>
            <nav class="nav-links">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
        </div>
    </header>
    
    <div class="container">
        <div class="contact-form">
            <h1>Contact Us</h1>
            <p>Have a question or feedback? We'd love to hear from you. Fill out the form below and our team will get back to you within 24 hours.</p>
            
            {result_html}
            {message_preview}
            
            <form method="GET" action="/contact">
                <div class="form-group">
                    <label for="name">Your Name</label>
                    <input type="text" id="name" name="name" placeholder="John Doe">
                </div>
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" placeholder="john@example.com">
                </div>
                <div class="form-group">
                    <label for="message">Your Message</label>
                    <textarea id="message" name="message" placeholder="Tell us how we can help you..."></textarea>
                </div>
                <button type="submit" class="btn">Send Message</button>
            </form>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 ShopEase. All rights reserved.</p>
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
    <title>Products - ShopEase</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; }
        .nav-container { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.8rem; font-weight: bold; text-decoration: none; color: white; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a { color: white; text-decoration: none; font-weight: 500; transition: opacity 0.3s; }
        .nav-links a:hover { opacity: 0.8; }
        .container { max-width: 1200px; margin: 3rem auto; padding: 0 20px; }
        h1 { margin-bottom: 2rem; color: #333; }
        .products-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; }
        .product-card { background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; transition: transform 0.3s; }
        .product-card:hover { transform: translateY(-5px); }
        .product-image { height: 200px; background: linear-gradient(45deg, #667eea, #764ba2); display: flex; align-items: center; justify-content: center; color: white; font-size: 3rem; }
        .product-info { padding: 1.5rem; }
        .product-info h3 { margin-bottom: 0.5rem; color: #333; }
        .product-info p { color: #666; margin-bottom: 1rem; }
        .product-price { font-size: 1.5rem; font-weight: bold; color: #667eea; }
        .footer { background: #333; color: white; padding: 2rem; text-align: center; margin-top: 4rem; }
    </style>
</head>
<body>
    <header class="header">
        <div class="nav-container">
            <a href="/" class="logo">ShopEase</a>
            <nav class="nav-links">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
        </div>
    </header>
    
    <div class="container">
        <h1>Our Products</h1>
        <div class="products-grid">
            <div class="product-card">
                <div class="product-image">&#128187;</div>
                <div class="product-info">
                    <h3>Premium Laptop</h3>
                    <p>High-performance laptop for professionals and gamers alike.</p>
                    <span class="product-price">$1,299.99</span>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#128241;</div>
                <div class="product-info">
                    <h3>Smartphone Pro</h3>
                    <p>Latest smartphone with cutting-edge camera technology.</p>
                    <span class="product-price">$899.99</span>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#127911;</div>
                <div class="product-info">
                    <h3>Wireless Headphones</h3>
                    <p>Premium noise-cancelling headphones with 30hr battery.</p>
                    <span class="product-price">$349.99</span>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#9000;</div>
                <div class="product-info">
                    <h3>Smart Watch</h3>
                    <p>Track your fitness and stay connected on the go.</p>
                    <span class="product-price">$299.99</span>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 ShopEase. All rights reserved.</p>
    </footer>
</body>
</html>
"""

ABOUT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About Us - ShopEase</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; }
        .nav-container { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.8rem; font-weight: bold; text-decoration: none; color: white; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a { color: white; text-decoration: none; font-weight: 500; transition: opacity 0.3s; }
        .nav-links a:hover { opacity: 0.8; }
        .container { max-width: 800px; margin: 3rem auto; padding: 0 20px; }
        .about-content { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .about-content h1 { margin-bottom: 1rem; color: #333; }
        .about-content p { color: #666; margin-bottom: 1rem; }
        .team-section { margin-top: 2rem; }
        .team-section h2 { margin-bottom: 1rem; color: #333; }
        .footer { background: #333; color: white; padding: 2rem; text-align: center; margin-top: 4rem; }
    </style>
</head>
<body>
    <header class="header">
        <div class="nav-container">
            <a href="/" class="logo">ShopEase</a>
            <nav class="nav-links">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
        </div>
    </header>
    
    <div class="container">
        <div class="about-content">
            <h1>About ShopEase</h1>
            <p>Founded in 2020, ShopEase has quickly become one of the most trusted online shopping destinations. Our mission is to provide customers with high-quality products at competitive prices while delivering exceptional customer service.</p>
            <p>We believe in making online shopping simple, secure, and enjoyable. With our curated selection of products and user-friendly platform, finding what you need has never been easier.</p>
            
            <div class="team-section">
                <h2>Our Values</h2>
                <p><strong>Quality First:</strong> We carefully select every product in our catalog to ensure it meets our high standards.</p>
                <p><strong>Customer Focus:</strong> Your satisfaction is our top priority. We're here to help every step of the way.</p>
                <p><strong>Innovation:</strong> We continuously improve our platform to provide the best shopping experience possible.</p>
            </div>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 ShopEase. All rights reserved.</p>
    </footer>
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
