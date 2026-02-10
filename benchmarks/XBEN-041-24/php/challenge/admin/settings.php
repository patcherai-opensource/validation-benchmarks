<?php
session_start();
if (!isset($_SESSION['admin_authenticated']) || $_SESSION['admin_authenticated'] !== true) {
    header('Location: /admin/login.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Settings - Automad</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #1a1a2e; color: white; padding: 1rem 2rem; }
        .header h1 { font-size: 1.5rem; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card h2 { margin-bottom: 1rem; }
        .setting { margin: 1rem 0; padding: 1rem; background: #f8f8f8; border-radius: 4px; }
        .setting h3 { font-size: 0.9rem; margin-bottom: 0.5rem; }
        .setting p { color: #666; font-size: 0.85rem; }
        a { color: #4a4a8a; }
    </style>
</head>
<body>
    <div class="header"><h1>Automad Dashboard</h1></div>
    <div class="container">
        <div class="card">
            <h2>System Settings</h2>
            <div class="setting">
                <h3>Site Title</h3>
                <p>Automad CMS</p>
            </div>
            <div class="setting">
                <h3>Timezone</h3>
                <p>UTC</p>
            </div>
            <div class="setting">
                <h3>Debug Mode</h3>
                <p>Disabled</p>
            </div>
            <p style="margin-top: 1rem;"><a href="/admin/">← Back to Dashboard</a></p>
        </div>
    </div>
</body>
</html>
