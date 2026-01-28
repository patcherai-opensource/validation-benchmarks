<?php
session_start();
$is_admin = isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;
?>
<!DOCTYPE html>
<html>
<head>
    <title>MediaFlow CMS - Settings</title>
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
        .setting-item { padding: 15px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
        .setting-item:last-child { border-bottom: none; }
        .setting-label { font-weight: 600; color: #2c3e50; }
        .setting-value { color: #7f8c8d; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.9em; }
        .alert { padding: 15px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; margin-bottom: 20px; color: #856404; }
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
        <?php if (!$is_admin): ?>
            <div class="alert">⚠️ You are viewing settings in read-only mode. <a href="/admin/media.php">Login as admin</a> to modify settings.</div>
        <?php endif; ?>
        
        <div class="panel">
            <h2>⚙️ General Settings</h2>
            <div class="setting-item">
                <span class="setting-label">Site Title</span>
                <span class="setting-value">MediaFlow Demo Site</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Site URL</span>
                <span class="setting-value">http://localhost:8080</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Timezone</span>
                <span class="setting-value">UTC</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Language</span>
                <span class="setting-value">English (US)</span>
            </div>
        </div>
        
        <div class="panel">
            <h2>🔒 Security Settings</h2>
            <div class="setting-item">
                <span class="setting-label">Session Timeout</span>
                <span class="setting-value">30 minutes</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Max Login Attempts</span>
                <span class="setting-value">5</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Two-Factor Auth</span>
                <span class="setting-value">Disabled</span>
            </div>
        </div>
        
        <div class="panel">
            <h2>📁 Media Settings</h2>
            <div class="setting-item">
                <span class="setting-label">Upload Directory</span>
                <span class="setting-value">/upload/</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Max File Size</span>
                <span class="setting-value">10 MB</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Allowed Extensions</span>
                <span class="setting-value">See configuration file for details</span>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>MediaFlow CMS v2.1.3 | &copy; 2024 MediaFlow Technologies</p>
    </div>
</body>
</html>
