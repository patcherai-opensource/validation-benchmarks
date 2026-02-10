# E-commerce shop templates (PrestaShop-like)
SHOP_INDEX = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>TechShop - Quality Electronics</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5rem; }
        .nav a { color: white; text-decoration: none; margin-left: 2rem; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 4rem 2rem; text-align: center; margin-bottom: 2rem; border-radius: 8px; }
        .hero h2 { font-size: 2.5rem; margin-bottom: 1rem; }
        .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 2rem; }
        .product-card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .product-card:hover { transform: translateY(-5px); }
        .product-image { width: 100%; height: 200px; background: #eee; display: flex; align-items: center; justify-content: center; font-size: 4rem; color: #999; }
        .product-info { padding: 1.5rem; }
        .product-title { font-size: 1.2rem; margin-bottom: 0.5rem; }
        .product-price { color: #e74c3c; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem; }
        .btn { display: inline-block; padding: 0.75rem 1.5rem; background: #3498db; color: white; text-decoration: none; border-radius: 4px; }
        .btn:hover { background: #2980b9; }
        .footer { background: #2c3e50; color: white; text-align: center; padding: 2rem; margin-top: 3rem; }
    </style>
</head>
<body>
    <header class="header">
        <h1>TechShop</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/products">Products</a>
            <a href="/admin">Admin</a>
        </nav>
    </header>
    
    <div class="container">
        <div class="hero">
            <h2>Welcome to TechShop</h2>
            <p>Your trusted source for quality electronics and tech accessories</p>
        </div>
        
        <h3 style="margin-bottom: 1.5rem;">Featured Products</h3>
        <div class="products-grid">
            <div class="product-card">
                <div class="product-image">&#128241;</div>
                <div class="product-info">
                    <h4 class="product-title">Smartphone Pro X</h4>
                    <p class="product-price">$999.00</p>
                    <a href="/product/1" class="btn">View Details</a>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#128187;</div>
                <div class="product-info">
                    <h4 class="product-title">Laptop Ultra 15</h4>
                    <p class="product-price">$1,499.00</p>
                    <a href="/product/2" class="btn">View Details</a>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#127911;</div>
                <div class="product-info">
                    <h4 class="product-title">Wireless Headphones</h4>
                    <p class="product-price">$299.00</p>
                    <a href="/product/3" class="btn">View Details</a>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 TechShop. All rights reserved.</p>
    </footer>
</body>
</html>
"""

PRODUCTS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Products - TechShop</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5rem; }
        .nav a { color: white; text-decoration: none; margin-left: 2rem; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 2rem; }
        .product-card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .product-image { width: 100%; height: 200px; background: #eee; display: flex; align-items: center; justify-content: center; font-size: 4rem; color: #999; }
        .product-info { padding: 1.5rem; }
        .product-title { font-size: 1.2rem; margin-bottom: 0.5rem; }
        .product-price { color: #e74c3c; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem; }
        .btn { display: inline-block; padding: 0.75rem 1.5rem; background: #3498db; color: white; text-decoration: none; border-radius: 4px; }
    </style>
</head>
<body>
    <header class="header">
        <h1>TechShop</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/products">Products</a>
            <a href="/admin">Admin</a>
        </nav>
    </header>
    
    <div class="container">
        <h2 style="margin-bottom: 2rem;">All Products</h2>
        <div class="products-grid">
            <div class="product-card">
                <div class="product-image">&#128241;</div>
                <div class="product-info">
                    <h4 class="product-title">Smartphone Pro X</h4>
                    <p class="product-price">$999.00</p>
                    <a href="/product/1" class="btn">View Details</a>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#128187;</div>
                <div class="product-info">
                    <h4 class="product-title">Laptop Ultra 15</h4>
                    <p class="product-price">$1,499.00</p>
                    <a href="/product/2" class="btn">View Details</a>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#127911;</div>
                <div class="product-info">
                    <h4 class="product-title">Wireless Headphones</h4>
                    <p class="product-price">$299.00</p>
                    <a href="/product/3" class="btn">View Details</a>
                </div>
            </div>
            <div class="product-card">
                <div class="product-image">&#8986;</div>
                <div class="product-info">
                    <h4 class="product-title">Smart Watch Elite</h4>
                    <p class="product-price">$449.00</p>
                    <a href="/product/4" class="btn">View Details</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

PRODUCT_DETAIL = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Product Details - TechShop</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ font-size: 1.5rem; }}
        .nav a {{ color: white; text-decoration: none; margin-left: 2rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .product-detail {{ background: white; border-radius: 8px; padding: 2rem; margin-bottom: 2rem; }}
        .product-image {{ width: 100%; height: 300px; background: #eee; display: flex; align-items: center; justify-content: center; font-size: 6rem; color: #999; margin-bottom: 1.5rem; }}
        .reviews {{ background: white; border-radius: 8px; padding: 2rem; }}
        .review-item {{ border-bottom: 1px solid #eee; padding: 1rem 0; }}
        .review-item:last-child {{ border-bottom: none; }}
        .review-content {{ margin-top: 0.5rem; color: #666; }}
        h2 {{ margin-bottom: 1rem; }}
    </style>
</head>
<body>
    <header class="header">
        <h1>TechShop</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/products">Products</a>
            <a href="/admin">Admin</a>
        </nav>
    </header>
    
    <div class="container">
        <div class="product-detail">
            <div class="product-image">&#128241;</div>
            <h2>Product #{0}</h2>
            <p>High-quality electronics with premium features.</p>
        </div>
        
        <div class="reviews">
            <h2>Customer Reviews</h2>
            {1}
        </div>
    </div>
</body>
</html>
"""

ADMIN_LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Admin Login - TechShop</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-box { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 20px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        .login-box h2 { text-align: center; margin-bottom: 1.5rem; color: #2c3e50; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; color: #666; }
        .form-group input { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; }
        .btn { width: 100%; padding: 0.75rem; background: #3498db; color: white; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .back-link { text-align: center; margin-top: 1rem; }
        .back-link a { color: #3498db; text-decoration: none; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Admin Panel</h2>
        <form action="/admin/login" method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
        <div class="back-link">
            <a href="/">Back to Store</a>
        </div>
    </div>
</body>
</html>
"""

ADMIN_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Admin Dashboard - TechShop</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ font-size: 1.5rem; }}
        .nav a {{ color: white; text-decoration: none; margin-left: 2rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .card {{ background: white; border-radius: 8px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .form-group {{ margin-bottom: 1rem; }}
        .form-group label {{ display: block; margin-bottom: 0.5rem; font-weight: bold; }}
        .form-group input, .form-group select, .form-group textarea {{ width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; }}
        .form-group textarea {{ min-height: 150px; font-family: monospace; }}
        .btn {{ padding: 0.75rem 1.5rem; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 0.5rem; }}
        .btn:hover {{ background: #2980b9; }}
        .btn-secondary {{ background: #95a5a6; }}
        .btn-secondary:hover {{ background: #7f8c8d; }}
        .alert {{ padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }}
        .alert-success {{ background: #d4edda; color: #155724; }}
        .alert-danger {{ background: #f8d7da; color: #721c24; }}
        .preview-area {{ border: 1px solid #ddd; padding: 1rem; min-height: 100px; margin-top: 1rem; background: #fafafa; }}
        .help-text {{ font-size: 0.85rem; color: #666; margin-top: 0.5rem; }}
    </style>
</head>
<body>
    <header class="header">
        <h1>TechShop Admin</h1>
        <nav class="nav">
            <a href="/">View Store</a>
            <a href="/admin/dashboard">Dashboard</a>
        </nav>
    </header>
    
    <div class="container">
        <h2 style="margin-bottom: 1.5rem;">Product Content Manager</h2>
        
        {0}
        
        <div class="card">
            <h3 style="margin-bottom: 1rem;">Add Product Description / Review</h3>
            <form action="/admin/dashboard" method="POST" id="contentForm">
                <div class="form-group">
                    <label>Product</label>
                    <select name="product_id">
                        <option value="1">Smartphone Pro X</option>
                        <option value="2">Laptop Ultra 15</option>
                        <option value="3">Wireless Headphones</option>
                        <option value="4">Smart Watch Elite</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Author Name</label>
                    <input type="text" name="author" value="Admin" required>
                </div>
                <div class="form-group">
                    <label>Content (HTML allowed)</label>
                    <textarea name="content" id="contentInput" placeholder="Enter product description or review..."></textarea>
                    <p class="help-text">You can use basic HTML tags for formatting. Dangerous scripts and event handlers are filtered for security.</p>
                </div>
                <button type="submit" class="btn">Save Content</button>
                <button type="button" class="btn btn-secondary" onclick="previewContent()">Preview</button>
            </form>
            
            <div id="previewArea" class="preview-area" style="display: none;">
                <strong>Preview:</strong>
                <div id="previewContent"></div>
            </div>
        </div>
    </div>
    
    <script>
        function previewContent() {{
            var content = document.getElementById('contentInput').value;
            var formData = new FormData();
            formData.append('content', content);
            
            fetch('/admin/preview', {{
                method: 'POST',
                body: formData
            }})
            .then(response => response.text())
            .then(html => {{
                document.getElementById('previewArea').style.display = 'block';
                document.getElementById('previewContent').innerHTML = html;
            }});
        }}
    </script>
</body>
</html>
"""

PREVIEW_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Preview</title>
    <style>
        body {{ font-family: sans-serif; padding: 20px; }}
    </style>
</head>
<body>
    <div class="preview-content">
        {0}
    </div>
</body>
</html>
"""

# Image routes for XSS detection feedback
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
