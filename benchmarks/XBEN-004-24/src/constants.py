INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>ContentShare - Share Your Ideas</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; margin: 0; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: rgba(255,255,255,0.95); padding: 15px 30px; border-radius: 8px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; color: #667eea; }
        .nav a { margin-left: 20px; color: #333; text-decoration: none; }
        .nav a:hover { color: #667eea; }
        .hero { background: rgba(255,255,255,0.95); border-radius: 12px; padding: 60px; text-align: center; margin-bottom: 30px; }
        .hero h1 { color: #333; margin-bottom: 20px; }
        .hero p { color: #666; font-size: 18px; max-width: 600px; margin: 0 auto 30px; }
        .btn-primary { background: #667eea; color: white; padding: 15px 40px; border-radius: 25px; text-decoration: none; font-size: 16px; display: inline-block; }
        .btn-primary:hover { background: #5a6fd6; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .feature-card { background: rgba(255,255,255,0.95); border-radius: 8px; padding: 30px; text-align: center; }
        .feature-card h3 { color: #333; margin-top: 15px; }
        .feature-card p { color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="logo">ContentShare</div>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/content/submit">Submit Content</a>
                <a href="/about">About</a>
            </nav>
        </header>
        
        <section class="hero">
            <h1>Share Your Ideas with the World</h1>
            <p>ContentShare is a platform for creators to submit and share rich content with our community. Express yourself with custom HTML formatting!</p>
            <a href="/content/submit" class="btn-primary">Start Creating</a>
        </section>
        
        <section class="features">
            <div class="feature-card">
                <h3>Rich Content</h3>
                <p>Submit content with custom HTML formatting to make your posts stand out.</p>
            </div>
            <div class="feature-card">
                <h3>Community Review</h3>
                <p>All content is reviewed by our admin team before publication.</p>
            </div>
            <div class="feature-card">
                <h3>Safe Platform</h3>
                <p>Advanced content validation ensures a safe environment for everyone.</p>
            </div>
        </section>
    </div>
</body>
</html>
"""


CONTENT_SUBMIT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>ContentShare - Submit Content</title>
    <style>
        @keyframes contentAnimation {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes fadeIn {{
            0%   {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
        @keyframes pulse {{
            0%   {{ transform: scale(1); }}
            50%  {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        @keyframes slideIn {{
            from {{ transform: translateX(-20px); opacity: 0; }}
            to   {{ transform: translateX(0); opacity: 1; }}
        }}
        @keyframes x {{
            from {{ opacity: 1; }}
            to   {{ opacity: 0.99; }}
        }}
        body {{ font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; margin: 0; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: rgba(255,255,255,0.95); padding: 15px 30px; border-radius: 8px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        .nav a {{ margin-left: 20px; color: #333; text-decoration: none; }}
        .nav a:hover {{ color: #667eea; }}
        .content-box {{ background: rgba(255,255,255,0.95); border-radius: 12px; padding: 40px; }}
        .content-box h2 {{ color: #333; margin-bottom: 10px; }}
        .content-box p {{ color: #666; margin-bottom: 20px; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; color: #333; margin-bottom: 8px; font-weight: bold; }}
        .form-group textarea {{ width: 100%; min-height: 200px; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; resize: vertical; box-sizing: border-box; }}
        .form-group textarea:focus {{ border-color: #667eea; outline: none; }}
        .btn-submit {{ background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 25px; font-size: 16px; cursor: pointer; }}
        .btn-submit:hover {{ background: #5a6fd6; }}
        .preview-section {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; }}
        .preview-section h3 {{ color: #333; margin-bottom: 15px; }}
        .preview-content {{ background: #f8f9fa; padding: 20px; border-radius: 8px; min-height: 50px; }}
        .solution-text {{ text-align: center; padding: 20px; }}
        .solution-text img {{ margin-bottom: 15px; }}
        .info-box {{ background: #e8f4fd; border-left: 4px solid #667eea; padding: 15px; margin-bottom: 20px; border-radius: 0 8px 8px 0; }}
        .info-box p {{ margin: 0; color: #333; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="logo">ContentShare</div>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/content/submit">Submit Content</a>
                <a href="/about">About</a>
            </nav>
        </header>
        
        <div class="content-box">
            <h2>Submit Your Content</h2>
            <p>Share your ideas with our community. HTML formatting is supported for rich content presentation.</p>
            
            <div class="info-box">
                <p>Your content will be reviewed by our admin team. For security, certain HTML elements and attributes are filtered.</p>
            </div>
            
            {2}
            
            <form method="post" action="/content/submit">
                <div class="form-group">
                    <label for="content">Content (HTML supported)</label>
                    <textarea name="content" id="content" placeholder="Enter your content here... HTML tags are allowed for formatting.">{0}</textarea>
                </div>
                <button type="submit" class="btn-submit">Submit for Review</button>
            </form>
            
            <div class="preview-section">
                <h3>Preview</h3>
                <div class="preview-content">
                    {1}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""


PRODUCTS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>ContentShare - Products</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; margin: 0; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: rgba(255,255,255,0.95); padding: 15px 30px; border-radius: 8px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; color: #667eea; }
        .nav a { margin-left: 20px; color: #333; text-decoration: none; }
        .nav a:hover { color: #667eea; }
        .content { background: rgba(255,255,255,0.95); border-radius: 12px; padding: 40px; }
        .content h1 { color: #333; }
        .products-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
        .product-card { border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; text-align: center; }
        .product-card h3 { color: #333; }
        .product-card p { color: #666; }
        .product-card .price { color: #667eea; font-size: 24px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="logo">ContentShare</div>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/content/submit">Submit Content</a>
                <a href="/about">About</a>
            </nav>
        </header>
        <div class="content">
            <h1>Our Products</h1>
            <p>Explore our premium content creation tools and services.</p>
            <div class="products-grid">
                <div class="product-card">
                    <h3>Basic Plan</h3>
                    <p>Perfect for getting started</p>
                    <div class="price">Free</div>
                </div>
                <div class="product-card">
                    <h3>Pro Plan</h3>
                    <p>For serious content creators</p>
                    <div class="price">$9.99/mo</div>
                </div>
                <div class="product-card">
                    <h3>Enterprise</h3>
                    <p>Full-featured solution</p>
                    <div class="price">Contact Us</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""


ABOUT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>ContentShare - About</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; margin: 0; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background: rgba(255,255,255,0.95); padding: 15px 30px; border-radius: 8px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; color: #667eea; }
        .nav a { margin-left: 20px; color: #333; text-decoration: none; }
        .nav a:hover { color: #667eea; }
        .content { background: rgba(255,255,255,0.95); border-radius: 12px; padding: 40px; }
        .content h1 { color: #333; }
        .content p { color: #666; line-height: 1.8; }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="logo">ContentShare</div>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/products">Products</a>
                <a href="/content/submit">Submit Content</a>
                <a href="/about">About</a>
            </nav>
        </header>
        <div class="content">
            <h1>About ContentShare</h1>
            <p>ContentShare is a platform dedicated to helping creators share their ideas with the world. Founded in 2023, we've built a community of thousands of content creators who use our platform daily.</p>
            <p>Our mission is to provide a safe, easy-to-use platform for content sharing. We believe in the power of expression and work hard to maintain a secure environment for all our users.</p>
            <p>Our content moderation team reviews all submissions to ensure they meet our community guidelines while preserving creative freedom.</p>
        </div>
    </div>
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
