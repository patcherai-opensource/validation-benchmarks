<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediaShare Pro - Enterprise Asset Management</title>
    <script src="/js/app.js" defer></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .navbar {
            background: rgba(0,0,0,0.3);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: #00d4ff;
        }
        .nav-links a {
            color: #e0e0e0;
            text-decoration: none;
            margin-left: 2rem;
            transition: color 0.3s;
        }
        .nav-links a:hover { color: #00d4ff; }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        .hero {
            text-align: center;
            padding: 4rem 2rem;
        }
        .hero h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: #fff;
        }
        .hero p {
            font-size: 1.2rem;
            color: #a0a0a0;
            margin-bottom: 2rem;
        }
        .btn {
            display: inline-block;
            padding: 0.8rem 2rem;
            background: #00d4ff;
            color: #1a1a2e;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background 0.3s;
        }
        .btn:hover { background: #00b8e0; }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }
        .feature-card {
            background: rgba(255,255,255,0.05);
            padding: 2rem;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .feature-card h3 {
            color: #00d4ff;
            margin-bottom: 1rem;
        }
        .footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 3rem;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">MediaShare Pro</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/gallery.php">Gallery</a>
            <a href="/upload.php">Upload</a>
            <a href="/login.php">Login</a>
            <a href="/api/status.php">API</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="hero">
            <h1>Enterprise Media Asset Management</h1>
            <p>Securely upload, manage, and share your digital assets with our enterprise-grade platform.</p>
            <a href="/login.php" class="btn">Get Started</a>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <h3>Secure Storage</h3>
                <p>All uploads are processed through our secure pipeline with enterprise-grade encryption.</p>
            </div>
            <div class="feature-card">
                <h3>Easy Sharing</h3>
                <p>Share assets with your team via secure links with granular permission controls.</p>
            </div>
            <div class="feature-card">
                <h3>API Access</h3>
                <p>Integrate with your existing workflow using our comprehensive REST API.</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>&copy; 2024 MediaShare Pro. All rights reserved. | Version 2.4.1</p>
    </div>
</body>
</html>

