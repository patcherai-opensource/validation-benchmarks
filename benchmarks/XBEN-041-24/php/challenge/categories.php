<!DOCTYPE html>
<html>
<head>
    <title>MediaFlow CMS - Categories</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5em; }
        .header nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; }
        .header nav a:hover { text-decoration: underline; }
        .container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
        .panel { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .panel h2 { color: #2c3e50; margin-bottom: 20px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .category-list { list-style: none; }
        .category-list li { padding: 12px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
        .category-name { color: #2c3e50; font-weight: 600; }
        .category-count { color: #7f8c8d; background: #f8f9fa; padding: 3px 10px; border-radius: 12px; font-size: 0.9em; }
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
        <div class="panel">
            <h2>🏷️ Categories</h2>
            <ul class="category-list">
                <li>
                    <span class="category-name">Technology</span>
                    <span class="category-count">5 posts</span>
                </li>
                <li>
                    <span class="category-name">Tutorials</span>
                    <span class="category-count">3 posts</span>
                </li>
                <li>
                    <span class="category-name">News</span>
                    <span class="category-count">8 posts</span>
                </li>
                <li>
                    <span class="category-name">Updates</span>
                    <span class="category-count">2 posts</span>
                </li>
            </ul>
        </div>
    </div>
    <div class="footer">
        <p>MediaFlow CMS v2.1.3 | &copy; 2024 MediaFlow Technologies</p>
    </div>
</body>
</html>
