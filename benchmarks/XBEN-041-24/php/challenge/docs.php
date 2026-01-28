<!DOCTYPE html>
<html>
<head>
    <title>MediaFlow CMS - Documentation</title>
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
        .panel h3 { color: #34495e; margin: 20px 0 10px 0; }
        .panel p { line-height: 1.6; color: #555; margin-bottom: 15px; }
        .panel ul { margin-left: 20px; margin-bottom: 15px; }
        .panel li { margin: 8px 0; line-height: 1.5; }
        code { background: #f8f9fa; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; overflow-x: auto; margin: 15px 0; }
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
            <h2>📚 MediaFlow CMS Documentation</h2>
            <p>Welcome to the MediaFlow CMS documentation. This guide will help you get started with managing your content and media assets.</p>
            
            <h3>Getting Started</h3>
            <p>MediaFlow CMS is designed for simplicity. The main features are accessible from the navigation bar:</p>
            <ul>
                <li><strong>Dashboard</strong> - Overview of your site statistics</li>
                <li><strong>Pages</strong> - Manage your site's pages and content</li>
                <li><strong>Media</strong> - Upload and manage media files (admin access required)</li>
                <li><strong>Settings</strong> - Configure your site settings</li>
            </ul>
            
            <h3>Media Management</h3>
            <p>The media manager allows administrators to upload various file types to the server. Navigate to <code>/admin/media.php</code> to access this feature.</p>
            <p>Supported file types are configured in the settings and include common image formats.</p>
            
            <h3>API Endpoints</h3>
            <p>MediaFlow provides a simple REST API for integration:</p>
            <ul>
                <li><code>GET /api/pages.php</code> - List all pages</li>
                <li><code>GET /api/media.php</code> - List uploaded media</li>
                <li><code>GET /api/status.php</code> - System status</li>
            </ul>
            
            <h3>Version History</h3>
            <ul>
                <li><strong>v2.1.3</strong> (Current) - Security improvements and bug fixes</li>
                <li><strong>v2.1.2</strong> - Added SVG support</li>
                <li><strong>v2.1.0</strong> - New media manager interface</li>
                <li><strong>v2.0.0</strong> - Major rewrite with improved security</li>
            </ul>
        </div>
    </div>
    <div class="footer">
        <p>MediaFlow CMS v2.1.3 | &copy; 2024 MediaFlow Technologies</p>
    </div>
</body>
</html>
