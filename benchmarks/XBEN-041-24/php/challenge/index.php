<!doctype html>
<html>
<head>
    <title>MediaFlow CMS - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5em; }
        .header nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; }
        .header nav a:hover { text-decoration: underline; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .welcome { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; border-radius: 8px; padding: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .card h3 { color: #2c3e50; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .card a { display: block; color: #3498db; text-decoration: none; padding: 8px 0; }
        .card a:hover { color: #2980b9; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📁 MediaFlow CMS</h1>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/pages.php">Pages</a>
            <a href="/admin/media.php">Media</a>
            <a href="/settings.php">Settings</a>
            <a href="/docs.php">Documentation</a>
        </nav>
    </div>
    <div class="container">
        <div class="welcome">
            <h2>Welcome to MediaFlow CMS</h2>
            <p>MediaFlow is a lightweight content management system designed for simplicity and ease of use. Manage your media assets, pages, and site settings all from one place.</p>
        </div>
        <div class="grid">
            <div class="card">
                <h3>📄 Content Management</h3>
                <a href="/pages.php">Manage Pages</a>
                <a href="/posts.php">Blog Posts</a>
                <a href="/categories.php">Categories</a>
            </div>
            <div class="card">
                <h3>🖼️ Media Library</h3>
                <a href="/admin/media.php">Upload Media</a>
                <a href="/gallery.php">View Gallery</a>
                <a href="/admin/media.php?action=browse">Browse Files</a>
            </div>
            <div class="card">
                <h3>⚙️ Administration</h3>
                <a href="/settings.php">Site Settings</a>
                <a href="/users.php">User Management</a>
                <a href="/backup.php">Backup & Restore</a>
            </div>
            <div class="card">
                <h3>📊 Statistics</h3>
                <p>Total Pages: <strong>12</strong></p>
                <p>Media Files: <strong>47</strong></p>
                <p>Active Users: <strong>3</strong></p>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>MediaFlow CMS v2.1.3 | &copy; 2024 MediaFlow Technologies</p>
    </div>
</body>
</html>
