<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiStyle CMS - About</title>
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
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .info-item { padding: 15px; background: #f8f9fa; border-radius: 5px; }
        .info-item strong { color: #333; }
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
            <a href="/themes.php">Themes</a>
            <a href="/presets.php">CSS Presets</a>
            <a href="/api-docs.php">API Docs</a>
            <a href="/about.php" class="active">About</a>
        </div>
        <div class="content">
            <div class="card">
                <h3>About WikiStyle CMS</h3>
                <p style="margin-bottom: 15px;">
                    WikiStyle CMS is a modern, flexible content management system designed for
                    collaborative documentation and knowledge sharing.
                </p>
                <p>
                    The Theme Manager module allows users to customize the visual appearance
                    of their wiki through pre-built themes and custom CSS presets.
                </p>
            </div>
            
            <div class="card">
                <h3>System Information</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Version:</strong> 4.5.3
                    </div>
                    <div class="info-item">
                        <strong>PHP Version:</strong> <?php echo phpversion(); ?>
                    </div>
                    <div class="info-item">
                        <strong>Server:</strong> Apache
                    </div>
                    <div class="info-item">
                        <strong>OS:</strong> <?php echo php_uname('s'); ?>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Features</h3>
                <ul style="margin-left: 20px;">
                    <li>Pre-built theme collection</li>
                    <li>Custom CSS preset creator</li>
                    <li>RESTful API for programmatic access</li>
                    <li>Session-based authentication</li>
                    <li>Real-time theme preview</li>
                </ul>
            </div>
            
            <div class="card">
                <h3>Credits</h3>
                <p>WikiStyle CMS Theme Manager Module<br>
                Built with PHP and Apache</p>
            </div>
        </div>
        <div class="footer">
            <p>WikiStyle CMS v4.5.3 | Theme Manager Module</p>
        </div>
    </div>
</body>
</html>
