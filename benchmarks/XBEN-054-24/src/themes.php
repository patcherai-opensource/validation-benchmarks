<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiStyle CMS - Themes</title>
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
        }
        .nav a:hover { background: #e9ecef; }
        .nav a.active { background: #667eea; color: white; }
        .content {
            background: white;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }
        .card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .card h3 { color: #333; margin-bottom: 15px; }
        .theme-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
        .theme-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }
        .theme-preview {
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        .theme-info { padding: 15px; }
        .theme-info h4 { margin-bottom: 5px; }
        .theme-info p { color: #666; font-size: 13px; }
        .footer { text-align: center; color: white; margin-top: 20px; opacity: 0.8; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>WikiStyle CMS</h1>
        </div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/themes.php" class="active">Themes</a>
            <a href="/presets.php">CSS Presets</a>
            <a href="/api-docs.php">API Docs</a>
            <a href="/about.php">About</a>
        </div>
        <div class="content">
            <div class="card">
                <h3>Available Themes</h3>
                <p style="margin-bottom: 20px;">Browse and select from our collection of pre-built themes.</p>
                
                <div class="theme-grid">
                    <div class="theme-card">
                        <div class="theme-preview" style="background: linear-gradient(135deg, #667eea, #764ba2);">
                            Default
                        </div>
                        <div class="theme-info">
                            <h4>Default Theme</h4>
                            <p>The standard WikiStyle theme with purple gradient.</p>
                        </div>
                    </div>
                    
                    <div class="theme-card">
                        <div class="theme-preview" style="background: linear-gradient(135deg, #28a745, #20c997);">
                            Nature
                        </div>
                        <div class="theme-info">
                            <h4>Nature Theme</h4>
                            <p>A fresh green theme inspired by nature.</p>
                        </div>
                    </div>
                    
                    <div class="theme-card">
                        <div class="theme-preview" style="background: linear-gradient(135deg, #dc3545, #c82333);">
                            Ruby
                        </div>
                        <div class="theme-info">
                            <h4>Ruby Theme</h4>
                            <p>A bold red theme for impactful designs.</p>
                        </div>
                    </div>
                    
                    <div class="theme-card">
                        <div class="theme-preview" style="background: linear-gradient(135deg, #17a2b8, #138496);">
                            Ocean
                        </div>
                        <div class="theme-info">
                            <h4>Ocean Theme</h4>
                            <p>A calming blue theme reminiscent of the sea.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="footer">
            <p>WikiStyle CMS v4.5.3 | Theme Manager Module</p>
        </div>
    </div>
</body>
</html>
