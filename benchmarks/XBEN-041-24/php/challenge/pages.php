<!DOCTYPE html>
<html>
<head>
    <title>MediaFlow CMS - Pages</title>
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
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; color: #2c3e50; }
        .status-published { color: #27ae60; font-weight: 600; }
        .status-draft { color: #f39c12; font-weight: 600; }
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
            <h2>📄 Site Pages</h2>
            <table>
                <tr>
                    <th>Title</th>
                    <th>Slug</th>
                    <th>Status</th>
                    <th>Last Modified</th>
                </tr>
                <tr>
                    <td>Home</td>
                    <td>/</td>
                    <td class="status-published">Published</td>
                    <td>2024-01-15</td>
                </tr>
                <tr>
                    <td>About Us</td>
                    <td>/about</td>
                    <td class="status-published">Published</td>
                    <td>2024-01-10</td>
                </tr>
                <tr>
                    <td>Contact</td>
                    <td>/contact</td>
                    <td class="status-published">Published</td>
                    <td>2024-01-08</td>
                </tr>
                <tr>
                    <td>Services</td>
                    <td>/services</td>
                    <td class="status-draft">Draft</td>
                    <td>2024-01-20</td>
                </tr>
                <tr>
                    <td>Blog</td>
                    <td>/blog</td>
                    <td class="status-published">Published</td>
                    <td>2024-01-18</td>
                </tr>
            </table>
        </div>
    </div>
    <div class="footer">
        <p>MediaFlow CMS v2.1.3 | &copy; 2024 MediaFlow Technologies</p>
    </div>
</body>
</html>
