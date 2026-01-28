<?php
/**
 * ModuLink - Enterprise Plugin Management System
 * Version 3.2.1
 */

session_start();

// Configuration
define('APP_NAME', 'ModuLink');
define('APP_VERSION', '3.2.1');
define('PLUGINS_DIR', __DIR__ . '/plugins');
define('LOGS_DIR', __DIR__ . '/logs');

// Check if logged in
$is_logged_in = isset($_SESSION['user_id']) && isset($_SESSION['role']);
$is_admin = $is_logged_in && $_SESSION['role'] === 'admin';

// Route handling
$page = $_GET['page'] ?? 'home';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo APP_NAME; ?> - Plugin Manager</title>
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
        .btn { display: inline-block; padding: 10px 20px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; border: none; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #2563eb; }
        .btn-danger { background: #ef4444; }
        .btn-danger:hover { background: #dc2626; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #94a3b8; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #334155; border-radius: 5px; color: #e2e8f0; }
        .alert { padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .alert-success { background: #166534; border: 1px solid #22c55e; }
        .alert-error { background: #991b1b; border: 1px solid #ef4444; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; }
        th { background: #0f172a; }
        .status-active { color: #22c55e; }
        .status-inactive { color: #ef4444; }
        footer { text-align: center; padding: 20px; color: #64748b; margin-top: 40px; }
    </style>
</head>
<body>
    <header>
        <nav>
            <div class="logo"><?php echo APP_NAME; ?></div>
            <div class="nav-links">
                <a href="/">Home</a>
                <a href="/docs.php">Documentation</a>
                <a href="/api/status.php">API Status</a>
                <?php if ($is_logged_in): ?>
                    <a href="/dashboard.php">Dashboard</a>
                    <?php if ($is_admin): ?>
                        <a href="/admin/">Admin</a>
                    <?php endif; ?>
                    <a href="/logout.php">Logout (<?php echo htmlspecialchars($_SESSION['username']); ?>)</a>
                <?php else: ?>
                    <a href="/login.php">Login</a>
                <?php endif; ?>
            </div>
        </nav>
    </header>

    <div class="container">
        <div class="card">
            <h2>Welcome to <?php echo APP_NAME; ?></h2>
            <p style="color: #94a3b8; margin-bottom: 20px;">
                ModuLink is an enterprise-grade plugin management system for managing your application extensions.
                Install, update, and configure plugins from various sources including npm, GitHub, and custom repositories.
            </p>
            <a href="/login.php" class="btn">Get Started</a>
        </div>

        <div class="card">
            <h2>Features</h2>
            <ul style="color: #94a3b8; margin-left: 20px;">
                <li>Install plugins from Git repositories</li>
                <li>Support for npm packages</li>
                <li>Custom plugin marketplace</li>
                <li>Automated dependency resolution</li>
                <li>Plugin health monitoring</li>
                <li>Role-based access control</li>
            </ul>
        </div>

        <div class="card">
            <h2>Quick Stats</h2>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 10px;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; color: #38bdf8;">1,247</div>
                    <div style="color: #64748b;">Available Plugins</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; color: #22c55e;">89</div>
                    <div style="color: #64748b;">Active Installations</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; color: #f59e0b;">5</div>
                    <div style="color: #64748b;">Pending Updates</div>
                </div>
            </div>
        </div>
    </div>

    <footer>
        <p>&copy; 2024 <?php echo APP_NAME; ?> v<?php echo APP_VERSION; ?>. All rights reserved.</p>
    </footer>
</body>
</html>
