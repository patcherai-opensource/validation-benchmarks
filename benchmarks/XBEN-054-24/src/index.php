<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiStyle CMS - Theme Manager</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header {
            background: white;
            padding: 20px 30px;
            border-radius: 10px 10px 0 0;
            border-bottom: 3px solid #667eea;
        }
        .header h1 { color: #333; font-size: 24px; }
        .header p { color: #666; margin-top: 5px; }
        .nav {
            background: #f8f9fa;
            padding: 10px 30px;
            display: flex;
            gap: 20px;
        }
        .nav a {
            color: #667eea;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 5px;
            transition: background 0.3s;
        }
        .nav a:hover { background: #e9ecef; }
        .nav a.active { background: #667eea; color: white; }
        .content {
            background: white;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .card h3 { color: #333; margin-bottom: 15px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #555; font-weight: 500; }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .form-group textarea { min-height: 100px; resize: vertical; }
        .btn {
            background: #667eea;
            color: white;
            padding: 10px 25px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .btn:hover { background: #5a67d8; }
        .preset-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
        .preset-item {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        .preset-item .color-preview {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin: 0 auto 10px;
            border: 2px solid #eee;
        }
        .alert { padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .api-docs { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px; }
        .api-docs code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
        .footer { text-align: center; color: white; margin-top: 20px; opacity: 0.8; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>WikiStyle CMS</h1>
            <p>Theme Manager - Customize your wiki appearance</p>
        </div>
        <div class="nav">
            <a href="/" class="active">Dashboard</a>
            <a href="/themes.php">Themes</a>
            <a href="/presets.php">CSS Presets</a>
            <a href="/api-docs.php">API Docs</a>
            <a href="/about.php">About</a>
        </div>
        <div class="content">
            <div class="card">
                <h3>Welcome to WikiStyle Theme Manager</h3>
                <p>Manage your wiki's visual appearance with custom themes and CSS presets.</p>
                <br>
                <p>Features available:</p>
                <ul style="margin-left: 20px; margin-top: 10px;">
                    <li>Browse pre-built themes</li>
                    <li>Create custom CSS presets</li>
                    <li>API access for theme management</li>
                </ul>
            </div>
            
            <div class="card">
                <h3>Quick Stats</h3>
                <div class="preset-list">
                    <div class="preset-item">
                        <div class="color-preview" style="background: #667eea;"></div>
                        <strong>Default Theme</strong>
                        <p style="color: #888; font-size: 12px;">Active</p>
                    </div>
                    <div class="preset-item">
                        <div class="color-preview" style="background: #28a745;"></div>
                        <strong>Nature</strong>
                        <p style="color: #888; font-size: 12px;">Available</p>
                    </div>
                    <div class="preset-item">
                        <div class="color-preview" style="background: #dc3545;"></div>
                        <strong>Ruby</strong>
                        <p style="color: #888; font-size: 12px;">Available</p>
                    </div>
                </div>
            </div>
            
            <div class="api-docs">
                <h4>Quick API Reference</h4>
                <p style="margin-top: 10px;">
                    Save custom presets: <code>POST /api/templates/custom-presets/{filename}</code>
                </p>
                <p style="margin-top: 5px;">
                    List presets: <code>GET /api/templates/list</code>
                </p>
            </div>
        </div>
        <div class="footer">
            <p>WikiStyle CMS v4.5.3 | Theme Manager Module</p>
        </div>
    </div>
</body>
</html>

