<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation - Aimeos CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }
        .navbar { background: #2c3e50; padding: 15px 30px; color: white; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 1.5em; }
        .navbar nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; }
        .container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
        .card h2 { color: #2c3e50; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .card h3 { color: #34495e; margin: 20px 0 10px 0; }
        .card p { color: #555; line-height: 1.6; margin-bottom: 15px; }
        .card ul { margin-left: 20px; color: #555; }
        .card li { margin-bottom: 8px; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; margin: 15px 0; }
        .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; }
        .info { background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🎨 Aimeos CMS - Documentation</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Admin Panel</a>
            <a href="/docs/">Documentation</a>
        </nav>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>📖 Getting Started</h2>
            <p>Welcome to Aimeos CMS, your all-in-one e-commerce content management solution. This documentation will help you get started with the platform.</p>
            
            <h3>Quick Links</h3>
            <ul>
                <li><a href="/admin/">Admin Panel</a> - Manage your store</li>
                <li><a href="/api/media">Media API</a> - REST API for media management</li>
                <li><a href="/docs/api.php">API Documentation</a> - Full API reference</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>🔧 Installation</h2>
            <p>Aimeos CMS can be installed via Composer or Docker:</p>
            
            <h3>Composer Installation</h3>
            <pre>composer create-project aimeos/aimeos-cms myshop
cd myshop
php artisan aimeos:setup</pre>
            
            <h3>Docker Installation</h3>
            <pre>docker pull aimeos/aimeos-cms
docker run -p 8080:80 aimeos/aimeos-cms</pre>
        </div>
        
        <div class="card">
            <h2>🔑 Authentication</h2>
            <p>The admin panel uses session-based authentication. The API uses API key authentication.</p>
            
            <h3>Default Credentials</h3>
            <div class="info">
                <p>For development environments, default credentials are:</p>
                <ul>
                    <li>Admin Panel: <code>admin</code> / <code>aimeos2024</code></li>
                    <li>API Key: <code>aimeos_dev_key</code></li>
                </ul>
            </div>
            
            <div class="warning">
                <strong>⚠️ Security Notice:</strong> Always change default credentials in production environments!
            </div>
        </div>
        
        <div class="card">
            <h2>📁 Media Management</h2>
            <p>Aimeos CMS provides powerful media management capabilities through both the web interface and REST API.</p>
            
            <h3>Web Interface</h3>
            <p>Access the Media Manager from the admin dashboard to upload and organize files.</p>
            
            <h3>REST API</h3>
            <p>Use the Media API for programmatic file management. See the <a href="/docs/api.php">API documentation</a> for details.</p>
            
            <pre>curl -X POST \
  -H "X-API-Key: your-api-key" \
  -F "file=@image.jpg" \
  http://localhost/api/media/upload</pre>
        </div>
        
        <div class="card">
            <h2>📋 Version History</h2>
            <ul>
                <li><strong>2024.04.5</strong> - Security fixes for media upload</li>
                <li><strong>2024.04.4</strong> - Current version (you are here)</li>
                <li><strong>2024.04.3</strong> - Performance improvements</li>
                <li><strong>2024.04.2</strong> - Bug fixes</li>
                <li><strong>2024.04.1</strong> - Initial release</li>
            </ul>
        </div>
    </div>
</body>
</html>
