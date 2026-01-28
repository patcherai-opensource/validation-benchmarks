<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aimeos CMS - Media Manager</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }
        .navbar { background: #2c3e50; padding: 15px 30px; color: white; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 1.5em; }
        .navbar nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; }
        .navbar nav a:hover { color: #3498db; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .welcome-card { background: white; border-radius: 8px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .welcome-card h2 { color: #2c3e50; margin-bottom: 20px; }
        .welcome-card p { color: #7f8c8d; margin-bottom: 30px; }
        .btn { display: inline-block; padding: 12px 30px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
        .btn:hover { background: #2980b9; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 40px; }
        .feature-card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .feature-card h3 { color: #2c3e50; margin-bottom: 10px; }
        .feature-card p { color: #7f8c8d; font-size: 0.9em; }
        .footer { text-align: center; padding: 30px; color: #95a5a6; margin-top: 50px; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🎨 Aimeos CMS</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Admin Panel</a>
            <a href="/docs/">Documentation</a>
            <a href="/about.php">About</a>
        </nav>
    </div>
    
    <div class="container">
        <div class="welcome-card">
            <h2>Welcome to Aimeos Content Management System</h2>
            <p>A powerful and flexible e-commerce platform for managing your online store, products, and media assets.</p>
            <a href="/admin/" class="btn">Access Admin Panel</a>
            <a href="/docs/" class="btn">View Documentation</a>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <h3>📦 Product Management</h3>
                <p>Easily manage your product catalog with our intuitive interface. Add descriptions, prices, and variants.</p>
            </div>
            <div class="feature-card">
                <h3>🖼️ Media Manager</h3>
                <p>Upload and organize images, videos, and documents. Our media manager handles all your digital assets.</p>
            </div>
            <div class="feature-card">
                <h3>🛒 Order Processing</h3>
                <p>Track orders from placement to delivery. Manage inventory and customer communications.</p>
            </div>
            <div class="feature-card">
                <h3>👥 Customer Management</h3>
                <p>Build relationships with your customers. View order history and manage accounts.</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Aimeos CMS v2024.04.4 | &copy; 2024 Aimeos GmbH</p>
    </div>
</body>
</html>
