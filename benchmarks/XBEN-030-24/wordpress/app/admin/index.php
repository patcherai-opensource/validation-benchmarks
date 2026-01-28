<?php
/**
 * ModuLink - Admin Panel
 */

session_start();

if (!isset($_SESSION['user_id'])) {
    header('Location: /login.php?msg=unauthorized');
    exit;
}

if ($_SESSION['role'] !== 'admin') {
    header('Location: /login.php?msg=admin_required');
    exit;
}

$username = $_SESSION['username'];
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - ModuLink</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { background: #1e293b; padding: 15px 0; border-bottom: 1px solid #334155; }
        nav { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .logo { font-size: 1.5rem; font-weight: bold; color: #38bdf8; }
        .nav-links { display: flex; gap: 20px; }
        .nav-links a { color: #94a3b8; text-decoration: none; }
        .nav-links a:hover { color: #f8fafc; }
        .card { background: #1e293b; border-radius: 8px; padding: 20px; margin: 20px 0; border: 1px solid #334155; }
        .card h2 { color: #f8fafc; margin-bottom: 15px; }
        .admin-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }
        .admin-card { background: #1e293b; border-radius: 8px; padding: 25px; border: 1px solid #334155; transition: transform 0.2s, border-color 0.2s; }
        .admin-card:hover { transform: translateY(-2px); border-color: #3b82f6; }
        .admin-card h3 { color: #f8fafc; margin-bottom: 10px; }
        .admin-card p { color: #94a3b8; margin-bottom: 15px; }
        .btn { display: inline-block; padding: 10px 20px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; }
        .btn:hover { background: #2563eb; }
        .admin-header { background: linear-gradient(135deg, #3b82f6, #7c3aed); padding: 30px; border-radius: 8px; margin-bottom: 30px; }
        .admin-header h1 { font-size: 2rem; margin-bottom: 10px; }
        .admin-header p { opacity: 0.9; }
        footer { text-align: center; padding: 20px; color: #64748b; margin-top: 40px; }
    </style>
</head>
<body>
    <header>
        <nav>
            <div class="logo">ModuLink Admin</div>
            <div class="nav-links">
                <a href="/">Home</a>
                <a href="/dashboard.php">Dashboard</a>
                <a href="/admin/">Admin</a>
                <a href="/logout.php">Logout (<?php echo htmlspecialchars($username); ?>)</a>
            </div>
        </nav>
    </header>

    <div class="container">
        <div class="admin-header">
            <h1>Administration Panel</h1>
            <p>Manage plugins, users, and system settings</p>
        </div>

        <div class="admin-grid">
            <div class="admin-card">
                <h3>🔌 Plugin Management</h3>
                <p>Install, update, and configure plugins from various sources including Git repositories and npm packages.</p>
                <a href="/admin/plugins.php" class="btn">Manage Plugins</a>
            </div>

            <div class="admin-card">
                <h3>👥 User Management</h3>
                <p>Manage user accounts, roles, and permissions for your organization.</p>
                <a href="/admin/users.php" class="btn">Manage Users</a>
            </div>

            <div class="admin-card">
                <h3>⚙️ System Settings</h3>
                <p>Configure system-wide settings, integrations, and security options.</p>
                <a href="/admin/settings.php" class="btn">Settings</a>
            </div>

            <div class="admin-card">
                <h3>📊 System Logs</h3>
                <p>View application logs, error reports, and audit trails.</p>
                <a href="/admin/logs.php" class="btn">View Logs</a>
            </div>

            <div class="admin-card">
                <h3>🔄 Backup & Restore</h3>
                <p>Create backups and restore your system configuration.</p>
                <a href="/admin/backup.php" class="btn">Backup</a>
            </div>

            <div class="admin-card">
                <h3>🌐 API Management</h3>
                <p>Manage API keys, rate limits, and external integrations.</p>
                <a href="/admin/api.php" class="btn">API Settings</a>
            </div>
        </div>
    </div>

    <footer>
        <p>&copy; 2024 ModuLink v3.2.1. All rights reserved.</p>
    </footer>
</body>
</html>
