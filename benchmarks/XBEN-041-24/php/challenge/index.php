<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Automad CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f5f5; min-height: 100vh; }
        .header { background: #1a1a2e; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5rem; font-weight: 500; }
        .nav { display: flex; gap: 2rem; }
        .nav a { color: #ccc; text-decoration: none; font-size: 0.9rem; }
        .nav a:hover { color: white; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .welcome { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .welcome h2 { color: #333; margin-bottom: 1rem; }
        .welcome p { color: #666; line-height: 1.6; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
        .feature-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .feature-card h3 { color: #333; margin-bottom: 0.5rem; }
        .feature-card p { color: #666; font-size: 0.9rem; }
        .btn { display: inline-block; background: #4a4a8a; color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none; margin-top: 1rem; font-size: 0.9rem; }
        .btn:hover { background: #3a3a7a; }
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
        <div class="welcome">
            <h2>Welcome to Automad</h2>
            <p>A flat-file content management system and template engine. Create beautiful websites with ease using our intuitive dashboard and flexible templating system.</p>
        </div>
        <div class="features">
            <div class="feature-card">
                <h3>Flat-File Storage</h3>
                <p>No database required. All content is stored in simple text files, making backups and version control straightforward.</p>
            </div>
            <div class="feature-card">
                <h3>Template Engine</h3>
                <p>Powerful template system with variables, loops, and includes. Build any layout you can imagine.</p>
            </div>
            <div class="feature-card">
                <h3>Admin Dashboard</h3>
                <p>Intuitive web-based dashboard for content management, media uploads, and site configuration.</p>
                <a href="/admin/" class="btn">Access Dashboard</a>
            </div>
        </div>
    </div>
    <footer>
        Automad CMS &copy; 2024
    </footer>
</body>
</html>
