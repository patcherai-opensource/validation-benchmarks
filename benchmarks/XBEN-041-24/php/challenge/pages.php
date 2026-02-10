<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pages - Automad</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; min-height: 100vh; }
        .header { background: #1a1a2e; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5rem; font-weight: 500; }
        .nav { display: flex; gap: 2rem; }
        .nav a { color: #ccc; text-decoration: none; font-size: 0.9rem; }
        .nav a:hover { color: white; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .page-list { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .page-item { padding: 1.5rem 2rem; border-bottom: 1px solid #eee; }
        .page-item:last-child { border-bottom: none; }
        .page-item h2 { color: #333; margin-bottom: 0.5rem; }
        .page-item h2 a { color: inherit; text-decoration: none; }
        .page-item h2 a:hover { color: #4a4a8a; }
        .page-item p { color: #666; font-size: 0.9rem; }
        footer { text-align: center; padding: 2rem; color: #666; font-size: 0.8rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Automad</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/pages.php">Pages</a>
            <a href="/admin/">Dashboard</a>
        </nav>
    </div>
    <div class="container">
        <div class="page-list">
            <div class="page-item">
                <h2><a href="#">About Us</a></h2>
                <p>Learn more about our company and mission.</p>
            </div>
            <div class="page-item">
                <h2><a href="#">Services</a></h2>
                <p>Explore the services we offer to our clients.</p>
            </div>
            <div class="page-item">
                <h2><a href="#">Blog</a></h2>
                <p>Read our latest news and articles.</p>
            </div>
            <div class="page-item">
                <h2><a href="#">Contact</a></h2>
                <p>Get in touch with our team.</p>
            </div>
        </div>
    </div>
    <footer>
        Automad CMS &copy; 2024
    </footer>
</body>
</html>
