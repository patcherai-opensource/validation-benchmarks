<?php
require_once __DIR__ . '/includes/bootstrap.php';
$config = require __DIR__ . '/includes/config.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContentForge CMS - About</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; min-height: 100vh; display: flex; flex-direction: column; }
        .header { background: #2d3748; color: #fff; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
        .header .logo { font-size: 18px; font-weight: 600; }
        .header .logo span { color: #63b3ed; }
        .header nav a { color: #cbd5e0; text-decoration: none; margin-left: 20px; font-size: 14px; }
        .header nav a:hover { color: #fff; }
        .content { flex: 1; max-width: 800px; margin: 32px auto; padding: 0 20px; }
        .card { background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); padding: 32px; margin-bottom: 20px; }
        .card h2 { color: #2d3748; margin-bottom: 16px; }
        .card p { color: #4a5568; font-size: 14px; line-height: 1.8; margin-bottom: 12px; }
        .card ul { padding-left: 20px; margin-bottom: 12px; }
        .card li { color: #4a5568; font-size: 14px; line-height: 1.8; }
        .footer { text-align: center; padding: 16px; color: #a0aec0; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Content<span>Forge</span> CMS</div>
        <nav>
            <a href="/">Home</a>
            <a href="/about.php">About</a>
        </nav>
    </div>
    <div class="content">
        <div class="card">
            <h2>About ContentForge CMS</h2>
            <p>ContentForge is an enterprise-grade content management system designed for teams that need reliable, secure content workflows.</p>
            <p>Version: <?php echo htmlspecialchars($config['site']['version']); ?></p>
            <p>Key features:</p>
            <ul>
                <li>Multi-user role-based access control</li>
                <li>Flexible content modeling and page management</li>
                <li>Extensible authentication service with pluggable hash methods</li>
                <li>Built-in media asset management</li>
                <li>RESTful API for headless deployments</li>
            </ul>
            <p>The authentication subsystem supports multiple password hashing strategies including standard MD5-based crypt hashing and enhanced bcrypt-based hashing, with automatic hash migration for upgraded installations.</p>
        </div>
    </div>
    <div class="footer">
        &copy; 2024 ContentForge CMS v<?php echo htmlspecialchars($config['site']['version']); ?>
    </div>
</body>
</html>