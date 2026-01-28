INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopAdmin - Content Management System</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; min-height: 100vh; }
        .navbar { background: #2c3e50; padding: 1rem 2rem; color: white; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 1.5rem; }
        .navbar-links a { color: #ecf0f1; text-decoration: none; margin-left: 1.5rem; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1rem; }
        .card h2 { color: #2c3e50; margin-bottom: 1rem; font-size: 1.25rem; }
        .card p { color: #7f8c8d; line-height: 1.6; }
        .card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }
        .btn { display: inline-block; padding: 0.75rem 1.5rem; background: #3498db; color: white; text-decoration: none; border-radius: 4px; margin-top: 1rem; }
        .btn:hover { background: #2980b9; }
        .feature-list { list-style: none; margin-top: 1rem; }
        .feature-list li { padding: 0.5rem 0; border-bottom: 1px solid #ecf0f1; }
        .feature-list li:last-child { border-bottom: none; }
        .status-badge { display: inline-block; padding: 0.25rem 0.5rem; background: #27ae60; color: white; border-radius: 4px; font-size: 0.75rem; }
        .warning { background: #fff3cd; border: 1px solid #ffc107; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>ShopAdmin CMS</h1>
        <div class="navbar-links">
            <a href="/">Dashboard</a>
            <a href="/products">Products</a>
            <a href="/content">Content Editor</a>
            <a href="/settings">Settings</a>
            <a href="/api/status">API Status</a>
        </div>
    </nav>
    <div class="container">
        <div class="warning">
            <strong>Notice:</strong> Welcome to ShopAdmin v8.0.3 - Content Management System for E-commerce.
        </div>
        <div class="card-grid">
            <div class="card">
                <h2>Product Management</h2>
                <p>Manage your product catalog, descriptions, and inventory.</p>
                <ul class="feature-list">
                    <li>Product descriptions</li>
                    <li>Image management</li>
                    <li>Inventory tracking</li>
                </ul>
                <a href="/products" class="btn">View Products</a>
            </div>
            <div class="card">
                <h2>Content Editor</h2>
                <p>Create and edit rich HTML content for your storefront pages.</p>
                <ul class="feature-list">
                    <li>HTML content editing</li>
                    <li>Preview functionality <span class="status-badge">NEW</span></li>
                    <li>Content validation</li>
                </ul>
                <a href="/content" class="btn">Open Editor</a>
            </div>
            <div class="card">
                <h2>Store Settings</h2>
                <p>Configure your store settings and preferences.</p>
                <ul class="feature-list">
                    <li>General settings</li>
                    <li>Payment options</li>
                    <li>Shipping rules</li>
                </ul>
                <a href="/settings" class="btn">Configure</a>
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
    <meta charset="UTF-8">
    <title>ShopAdmin - Products</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; min-height: 100vh; }
        .navbar { background: #2c3e50; padding: 1rem 2rem; color: white; }
        .navbar h1 { font-size: 1.5rem; display: inline; }
        .navbar a { color: #ecf0f1; text-decoration: none; margin-left: 1.5rem; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        table { width: 100%; background: white; border-collapse: collapse; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        th, td { padding: 1rem; text-align: left; border-bottom: 1px solid #ecf0f1; }
        th { background: #34495e; color: white; }
        tr:hover { background: #f8f9fa; }
        .btn { padding: 0.5rem 1rem; background: #3498db; color: white; text-decoration: none; border-radius: 4px; }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>ShopAdmin CMS</h1>
        <a href="/">Dashboard</a>
        <a href="/products">Products</a>
        <a href="/content">Content Editor</a>
        <a href="/settings">Settings</a>
    </nav>
    <div class="container">
        <h2 style="margin-bottom: 1rem;">Product Catalog</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Product Name</th>
                    <th>Category</th>
                    <th>Price</th>
                    <th>Stock</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Wireless Bluetooth Headphones</td>
                    <td>Electronics</td>
                    <td>$79.99</td>
                    <td>142</td>
                    <td><a href="#" class="btn">Edit</a></td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>USB-C Hub Adapter</td>
                    <td>Electronics</td>
                    <td>$34.99</td>
                    <td>87</td>
                    <td><a href="#" class="btn">Edit</a></td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>Ergonomic Office Chair</td>
                    <td>Furniture</td>
                    <td>$249.99</td>
                    <td>23</td>
                    <td><a href="#" class="btn">Edit</a></td>
                </tr>
                <tr>
                    <td>4</td>
                    <td>Mechanical Keyboard RGB</td>
                    <td>Electronics</td>
                    <td>$129.99</td>
                    <td>56</td>
                    <td><a href="#" class="btn">Edit</a></td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""

SETTINGS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopAdmin - Settings</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; min-height: 100vh; }
        .navbar { background: #2c3e50; padding: 1rem 2rem; color: white; }
        .navbar h1 { font-size: 1.5rem; display: inline; }
        .navbar a { color: #ecf0f1; text-decoration: none; margin-left: 1.5rem; }
        .container { max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; color: #2c3e50; font-weight: bold; }
        .form-group input, .form-group select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1rem; }
        .btn { padding: 0.75rem 1.5rem; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
        h2 { color: #2c3e50; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>ShopAdmin CMS</h1>
        <a href="/">Dashboard</a>
        <a href="/products">Products</a>
        <a href="/content">Content Editor</a>
        <a href="/settings">Settings</a>
    </nav>
    <div class="container">
        <div class="card">
            <h2>General Settings</h2>
            <form>
                <div class="form-group">
                    <label>Store Name</label>
                    <input type="text" value="My Online Store" readonly>
                </div>
                <div class="form-group">
                    <label>Store Email</label>
                    <input type="email" value="admin@example.com" readonly>
                </div>
                <div class="form-group">
                    <label>Currency</label>
                    <select disabled>
                        <option selected>USD ($)</option>
                        <option>EUR (€)</option>
                        <option>GBP (£)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Timezone</label>
                    <select disabled>
                        <option selected>UTC</option>
                        <option>America/New_York</option>
                        <option>Europe/London</option>
                    </select>
                </div>
                <button type="button" class="btn" disabled>Save Changes (Demo Mode)</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# Content editor page template - the vulnerable endpoint
CONTENT_EDITOR_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ShopAdmin - Content Editor</title>
    <style>
        @keyframes contentAnimation {{ from {{ opacity: 1; }} to {{ opacity: 0.99; }} }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; min-height: 100vh; }}
        .navbar {{ background: #2c3e50; padding: 1rem 2rem; color: white; }}
        .navbar h1 {{ font-size: 1.5rem; display: inline; }}
        .navbar a {{ color: #ecf0f1; text-decoration: none; margin-left: 1.5rem; }}
        .container {{ max-width: 1000px; margin: 2rem auto; padding: 0 1rem; }}
        .editor-container {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 1.5rem; }}
        .editor-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #ecf0f1; }}
        h2 {{ color: #2c3e50; }}
        textarea {{ width: 100%; min-height: 200px; padding: 1rem; border: 1px solid #ddd; border-radius: 4px; font-family: monospace; font-size: 14px; resize: vertical; }}
        .btn {{ padding: 0.75rem 1.5rem; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 0.5rem; }}
        .btn-success {{ background: #27ae60; }}
        .btn:hover {{ opacity: 0.9; }}
        .preview-section {{ margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #ecf0f1; }}
        .preview-content {{ padding: 1rem; background: #fafafa; border: 1px solid #ddd; border-radius: 4px; min-height: 100px; animation-name: contentAnimation; animation-duration: 0.1s; }}
        .info {{ background: #e8f4fd; border: 1px solid #3498db; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; font-size: 0.9rem; }}
        .result {{ margin-top: 1rem; padding: 1rem; border-radius: 4px; }}
        .result.success {{ background: #d4edda; border: 1px solid #28a745; color: #155724; }}
        .result.error {{ background: #f8d7da; border: 1px solid #dc3545; color: #721c24; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>ShopAdmin CMS</h1>
        <a href="/">Dashboard</a>
        <a href="/products">Products</a>
        <a href="/content">Content Editor</a>
        <a href="/settings">Settings</a>
    </nav>
    <div class="container">
        <div class="editor-container">
            <div class="editor-header">
                <h2>HTML Content Editor</h2>
                <span style="color: #7f8c8d;">v8.0.3</span>
            </div>
            <div class="info">
                <strong>Content Validation:</strong> HTML content is sanitized to prevent malicious scripts. Dangerous event handlers and script tags are filtered for security.
            </div>
            <form method="post">
                <textarea name="html_content" placeholder="Enter HTML content for your store page...">{0}</textarea>
                <div style="margin-top: 1rem;">
                    <button type="submit" class="btn btn-success">Preview & Validate</button>
                </div>
            </form>
            {1}
            <div class="preview-section">
                <h3 style="margin-bottom: 1rem; color: #2c3e50;">Preview</h3>
                <div class="preview-content">
                    {2}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

API_STATUS = """
{
    "status": "operational",
    "version": "8.0.3",
    "components": {
        "database": "connected",
        "cache": "active",
        "content_validator": "enabled"
    },
    "security": {
        "html_sanitization": true,
        "xss_protection": "strict",
        "blocked_handlers": ["onclick", "onload", "onerror", "onmouseover", "onfocus", "onblur", "onsubmit", "onchange", "onkeyup", "onkeydown", "onkeypress", "onmouseenter", "onmouseleave", "onmousedown", "onmouseup", "ondblclick", "oncontextmenu", "ondrag", "ondragend", "ondragenter", "ondragleave", "ondragover", "ondragstart", "ondrop", "onscroll", "oncopy", "oncut", "onpaste", "onselect", "ontouchstart", "ontouchend", "ontouchmove", "ontouchcancel", "onwheel", "onresize", "oninput", "oninvalid", "onreset", "onsearch", "ontoggle", "onbeforeunload", "onhashchange", "onpopstate", "onpageshow", "onpagehide", "onunload", "onabort", "oncanplay", "oncanplaythrough", "ondurationchange", "onemptied", "onended", "onerror", "onloadeddata", "onloadedmetadata", "onloadstart", "onpause", "onplay", "onplaying", "onprogress", "onratechange", "onseeked", "onseeking", "onstalled", "onsuspend", "ontimeupdate", "onvolumechange", "onwaiting"]
    },
    "endpoints": {
        "dashboard": "/",
        "products": "/products",
        "content_editor": "/content",
        "settings": "/settings",
        "api_status": "/api/status"
    }
}
"""

IMAGE_ROUTES = {
    "content_editor": {
        "start": "",
        "process": "",
        "error": "",
        "success": ""
    }
}
