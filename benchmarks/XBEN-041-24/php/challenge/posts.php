<!DOCTYPE html>
<html>
<head>
    <title>MediaFlow CMS - Blog Posts</title>
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
        .post-item { padding: 20px 0; border-bottom: 1px solid #eee; }
        .post-item:last-child { border-bottom: none; }
        .post-title { font-size: 1.2em; color: #2c3e50; margin-bottom: 8px; }
        .post-meta { font-size: 0.9em; color: #7f8c8d; margin-bottom: 10px; }
        .post-excerpt { color: #555; line-height: 1.6; }
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
            <h2>📝 Blog Posts</h2>
            <div class="post-item">
                <div class="post-title">Getting Started with MediaFlow CMS</div>
                <div class="post-meta">Posted on January 15, 2024 by admin</div>
                <div class="post-excerpt">Welcome to MediaFlow CMS! This guide will help you get started with our simple and powerful content management system...</div>
            </div>
            <div class="post-item">
                <div class="post-title">Media Management Best Practices</div>
                <div class="post-meta">Posted on January 10, 2024 by admin</div>
                <div class="post-excerpt">Learn how to effectively organize and manage your media assets with MediaFlow's built-in media manager...</div>
            </div>
            <div class="post-item">
                <div class="post-title">Security Tips for Your Website</div>
                <div class="post-meta">Posted on January 5, 2024 by admin</div>
                <div class="post-excerpt">Security is important. Here are some tips to keep your MediaFlow site secure and protected from common threats...</div>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>MediaFlow CMS v2.1.3 | &copy; 2024 MediaFlow Technologies</p>
    </div>
</body>
</html>
