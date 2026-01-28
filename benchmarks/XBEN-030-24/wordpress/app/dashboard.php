<?php
/**
 * ModuLink - User Dashboard
 */

session_start();

if (!isset($_SESSION['user_id'])) {
    header('Location: /login.php?msg=unauthorized');
    exit;
}

$username = $_SESSION['username'];
$role = $_SESSION['role'];
$is_admin = $role === 'admin';

// Sample plugins data
$installed_plugins = [
    ['name' => 'analytics-core', 'version' => '2.1.0', 'status' => 'active', 'source' => 'npm'],
    ['name' => 'form-builder', 'version' => '1.8.3', 'status' => 'active', 'source' => 'git'],
    ['name' => 'auth-ldap', 'version' => '3.0.1', 'status' => 'inactive', 'source' => 'npm'],
    ['name' => 'cache-redis', 'version' => '1.2.0', 'status' => 'active', 'source' => 'marketplace'],
    ['name' => 'export-tools', 'version' => '2.4.5', 'status' => 'active', 'source' => 'git'],
];
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - ModuLink</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { background: #1e293b; padding: 15px 0; border-bottom: 1px solid #334155; }
        nav { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .logo { font-size: 1.5rem; font-weight: bold; color: #38bdf8; }
        .nav-links { display: flex; gap: 20px; }
        .nav-links a { color: #94a3b8; text-decoration: none; transition: color 0.2s; }
        .nav-links a:hover { color: #f8fafc; }
        .card { background: #1e293b; border-radius: 8px; padding: 20px; margin: 20px 0; border: 1px solid #334155; }
        .card h2 { color: #f8fafc; margin-bottom: 15px; }
        .btn { display: inline-block; padding: 8px 16px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; border: none; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #2563eb; }
        .btn-sm { padding: 5px 10px; font-size: 12px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; }
        th { background: #0f172a; }
        .status-active { color: #22c55e; }
        .status-inactive { color: #ef4444; }
        .badge { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
        .badge-npm { background: #c41e3a; }
        .badge-git { background: #f14e32; }
        .badge-marketplace { background: #3b82f6; }
        .user-info { background: #334155; padding: 10px 15px; border-radius: 5px; margin-bottom: 20px; }
        footer { text-align: center; padding: 20px; color: #64748b; margin-top: 40px; }
    </style>
</head>
<body>
    <header>
        <nav>
            <div class="logo">ModuLink</div>
            <div class="nav-links">
                <a href="/">Home</a>
                <a href="/docs.php">Documentation</a>
                <a href="/api/status.php">API Status</a>
                <a href="/dashboard.php">Dashboard</a>
                <?php if ($is_admin): ?>
                    <a href="/admin/">Admin Panel</a>
                <?php endif; ?>
                <a href="/logout.php">Logout (<?php echo htmlspecialchars($username); ?>)</a>
            </div>
        </nav>
    </header>

    <div class="container">
        <div class="user-info">
            <strong>Logged in as:</strong> <?php echo htmlspecialchars($username); ?> 
            <span style="color: #94a3b8;">(<?php echo ucfirst($role); ?>)</span>
            <?php if ($is_admin): ?>
                <span style="color: #22c55e; margin-left: 10px;">✓ Administrator</span>
            <?php endif; ?>
        </div>

        <div class="card">
            <h2>Installed Plugins</h2>
            <table>
                <thead>
                    <tr>
                        <th>Plugin Name</th>
                        <th>Version</th>
                        <th>Source</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($installed_plugins as $plugin): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($plugin['name']); ?></td>
                        <td><?php echo htmlspecialchars($plugin['version']); ?></td>
                        <td>
                            <span class="badge badge-<?php echo $plugin['source']; ?>">
                                <?php echo strtoupper($plugin['source']); ?>
                            </span>
                        </td>
                        <td class="status-<?php echo $plugin['status']; ?>">
                            <?php echo ucfirst($plugin['status']); ?>
                        </td>
                        <td>
                            <a href="#" class="btn btn-sm">View</a>
                            <?php if ($is_admin): ?>
                            <a href="#" class="btn btn-sm" style="background: #6b7280;">Configure</a>
                            <?php endif; ?>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>Quick Actions</h2>
            <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                <?php if ($is_admin): ?>
                    <a href="/admin/plugins.php" class="btn">Install New Plugin</a>
                    <a href="/admin/settings.php" class="btn" style="background: #6b7280;">System Settings</a>
                <?php endif; ?>
                <a href="/api/plugins/list" class="btn" style="background: #059669;">View Plugin API</a>
                <a href="/docs.php" class="btn" style="background: #7c3aed;">Documentation</a>
            </div>
        </div>

        <div class="card">
            <h2>Recent Activity</h2>
            <div style="color: #94a3b8;">
                <p style="padding: 8px 0; border-bottom: 1px solid #334155;">
                    <span style="color: #64748b;">2024-01-15 14:32</span> - Plugin <strong>analytics-core</strong> updated to v2.1.0
                </p>
                <p style="padding: 8px 0; border-bottom: 1px solid #334155;">
                    <span style="color: #64748b;">2024-01-14 09:15</span> - Plugin <strong>form-builder</strong> installed from git
                </p>
                <p style="padding: 8px 0; border-bottom: 1px solid #334155;">
                    <span style="color: #64748b;">2024-01-13 16:45</span> - Plugin <strong>auth-ldap</strong> deactivated
                </p>
                <p style="padding: 8px 0;">
                    <span style="color: #64748b;">2024-01-12 11:20</span> - System configuration updated
                </p>
            </div>
        </div>
    </div>

    <footer>
        <p>&copy; 2024 ModuLink v3.2.1. All rights reserved.</p>
    </footer>
</body>
</html>
