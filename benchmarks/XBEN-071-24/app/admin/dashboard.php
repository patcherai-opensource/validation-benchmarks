<?php
session_start();
if (!isset($_SESSION['admin_authenticated'])) {
    header('Location: /admin/login.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore - Admin Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #1d2332; color: #fff; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 20px; font-weight: 300; letter-spacing: 2px; color: #b388ff; }
        .header .user { color: #aaa; font-size: 13px; }
        .sidebar { position: fixed; left: 0; top: 48px; bottom: 0; width: 220px; background: #263238; color: #cfd8dc; padding: 16px 0; }
        .sidebar a { display: block; padding: 10px 24px; color: #cfd8dc; text-decoration: none; font-size: 13px; transition: background 0.2s; }
        .sidebar a:hover, .sidebar a.active { background: #37474f; color: #fff; }
        .main { margin-left: 220px; padding: 24px; margin-top: 48px; }
        .card { background: #fff; border-radius: 4px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card h3 { font-size: 16px; margin-bottom: 12px; color: #333; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
        .stat { text-align: center; }
        .stat .number { font-size: 32px; font-weight: 700; color: #4a148c; }
        .stat .label { font-size: 12px; color: #999; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>pimcore</h1>
        <span class="user">Logged in as: <?= htmlspecialchars($_SESSION['admin_user'] ?? 'admin') ?></span>
    </div>
    <div class="sidebar">
        <a href="/admin/dashboard.php" class="active">Dashboard</a>
        <a href="/admin/api/documents.php?action=list">Documents</a>
        <a href="/admin/api/assets.php?action=list">Assets</a>
        <a href="/admin/api/uuid.php?action=list">UUID Registry</a>
        <a href="/admin/login.php?logout=1">Logout</a>
    </div>
    <div class="main">
        <div class="stats">
            <div class="card stat">
                <div class="number">12</div>
                <div class="label">Documents</div>
            </div>
            <div class="card stat">
                <div class="number">8</div>
                <div class="label">Assets</div>
            </div>
            <div class="card stat">
                <div class="number">15</div>
                <div class="label">UUID Records</div>
            </div>
        </div>
        <div class="card">
            <h3>Quick Actions</h3>
            <p style="color: #666; font-size: 14px; line-height: 1.6;">
                Welcome to the pimcore administration panel. Use the sidebar navigation to manage your content, 
                assets, and system settings.
            </p>
        </div>
    </div>
</body>
</html>
