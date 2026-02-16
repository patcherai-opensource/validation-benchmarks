<?php
require_once __DIR__ . '/includes/bootstrap.php';

session_start();

if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header('Location: /');
    exit;
}

$config = require __DIR__ . '/includes/config.php';
$username = htmlspecialchars($_SESSION['username'] ?? '');
$role = $_SESSION['role'] ?? 'editor';

$flagContent = '';
if ($role === 'admin') {
    $flagFile = '/var/www/private/admin_token.txt';
    if (file_exists($flagFile)) {
        $flagContent = trim(file_get_contents($flagFile));
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContentForge CMS - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; min-height: 100vh; }
        .header { background: #2d3748; color: #fff; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
        .header .logo { font-size: 18px; font-weight: 600; }
        .header .logo span { color: #63b3ed; }
        .header .user-info { display: flex; align-items: center; gap: 16px; }
        .header .user-info span { font-size: 14px; color: #cbd5e0; }
        .header .user-info a { color: #fc8181; text-decoration: none; font-size: 13px; }
        .container { max-width: 1000px; margin: 32px auto; padding: 0 20px; }
        .card { background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); padding: 24px; margin-bottom: 20px; }
        .card h3 { color: #2d3748; margin-bottom: 12px; font-size: 18px; }
        .card p { color: #4a5568; font-size: 14px; line-height: 1.6; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
        .badge-admin { background: #fed7d7; color: #c53030; }
        .badge-editor { background: #c6f6d5; color: #276749; }
        .admin-section { border-left: 3px solid #e53e3e; padding-left: 16px; }
        .token-display { background: #1a202c; color: #68d391; padding: 12px 16px; border-radius: 6px; font-family: monospace; font-size: 14px; margin-top: 8px; word-break: break-all; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
        .stat-card { text-align: center; padding: 16px; }
        .stat-card .number { font-size: 32px; font-weight: 700; color: #3182ce; }
        .stat-card .label { font-size: 13px; color: #718096; margin-top: 4px; }
        .footer { text-align: center; padding: 16px; color: #a0aec0; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Content<span>Forge</span> CMS</div>
        <div class="user-info">
            <span><?php echo $username; ?> <span class="badge badge-<?php echo $role; ?>"><?php echo $role; ?></span></span>
            <a href="/?logout=1">Logout</a>
        </div>
    </div>
    <div class="container">
        <div class="card">
            <h3>Dashboard</h3>
            <p>Welcome back, <strong><?php echo $username; ?></strong>. You are logged in as <strong><?php echo $role; ?></strong>.</p>
        </div>

        <div class="card">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="number">47</div>
                    <div class="label">Published Pages</div>
                </div>
                <div class="stat-card">
                    <div class="number">12</div>
                    <div class="label">Draft Articles</div>
                </div>
                <div class="stat-card">
                    <div class="number">3</div>
                    <div class="label">Active Users</div>
                </div>
                <div class="stat-card">
                    <div class="number">128</div>
                    <div class="label">Media Files</div>
                </div>
            </div>
        </div>

        <?php if ($role === 'admin'): ?>
        <div class="card admin-section">
            <h3>Administration</h3>
            <p>System administration tools and configuration access.</p>
            <?php if ($flagContent): ?>
            <div style="margin-top: 16px;">
                <p><strong>System Authorization Token:</strong></p>
                <div class="token-display"><?php echo htmlspecialchars($flagContent); ?></div>
            </div>
            <?php endif; ?>
        </div>
        <?php endif; ?>

        <div class="card">
            <h3>Recent Activity</h3>
            <p style="color: #a0aec0; font-style: italic;">No recent activity to display.</p>
        </div>
    </div>
    <div class="footer">
        &copy; 2024 ContentForge CMS v4.2.1
    </div>
</body>
</html>