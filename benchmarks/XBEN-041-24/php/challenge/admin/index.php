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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Automad</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f5f5; }
        .header { background: #1a1a2e; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5rem; font-weight: 500; }
        .nav { display: flex; gap: 2rem; align-items: center; }
        .nav a { color: #ccc; text-decoration: none; font-size: 0.9rem; }
        .nav a:hover { color: white; }
        .user-info { color: #aaa; font-size: 0.85rem; }
        .layout { display: flex; min-height: calc(100vh - 60px); }
        .sidebar { width: 250px; background: #fff; border-right: 1px solid #e0e0e0; padding: 1.5rem; }
        .sidebar h3 { font-size: 0.75rem; text-transform: uppercase; color: #999; margin-bottom: 1rem; letter-spacing: 0.5px; }
        .sidebar ul { list-style: none; }
        .sidebar li { margin-bottom: 0.5rem; }
        .sidebar a { color: #333; text-decoration: none; font-size: 0.9rem; padding: 0.5rem; display: block; border-radius: 4px; }
        .sidebar a:hover, .sidebar a.active { background: #f0f0f0; }
        .main { flex: 1; padding: 2rem; }
        .card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem; }
        .card h2 { margin-bottom: 1rem; color: #333; font-size: 1.2rem; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .stat-card h3 { font-size: 0.8rem; text-transform: uppercase; color: #999; margin-bottom: 0.5rem; }
        .stat-card .value { font-size: 2rem; font-weight: 600; color: #333; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Automad Dashboard</h1>
        <nav class="nav">
            <a href="/">View Site</a>
            <span class="user-info">Logged in as: admin</span>
            <a href="/admin/logout.php">Logout</a>
        </nav>
    </div>
    <div class="layout">
        <div class="sidebar">
            <h3>Content</h3>
            <ul>
                <li><a href="/admin/" class="active">Dashboard</a></li>
                <li><a href="/admin/pages.php">Pages</a></li>
                <li><a href="/admin/shared.php">Shared</a></li>
            </ul>
            <h3>Media</h3>
            <ul>
                <li><a href="/admin/images.php">Images</a></li>
                <li><a href="/admin/files.php">Files</a></li>
            </ul>
            <h3>System</h3>
            <ul>
                <li><a href="/admin/settings.php">Settings</a></li>
                <li><a href="/admin/users.php">Users</a></li>
                <li><a href="/admin/update.php">Update</a></li>
            </ul>
        </div>
        <div class="main">
            <div class="stats">
                <div class="stat-card">
                    <h3>Pages</h3>
                    <div class="value">12</div>
                </div>
                <div class="stat-card">
                    <h3>Images</h3>
                    <div class="value">47</div>
                </div>
                <div class="stat-card">
                    <h3>Files</h3>
                    <div class="value">8</div>
                </div>
                <div class="stat-card">
                    <h3>Users</h3>
                    <div class="value">1</div>
                </div>
            </div>
            <div class="card">
                <h2>Quick Actions</h2>
                <p style="color: #666; line-height: 1.6;">Welcome to the Automad dashboard. Use the sidebar to navigate between different sections. Upload new images via the <a href="/admin/images.php">Images</a> section or manage your site pages through the <a href="/admin/pages.php">Pages</a> menu.</p>
            </div>
            <div class="card">
                <h2>Recent Activity</h2>
                <ul style="color: #666; font-size: 0.9rem; line-height: 2;">
                    <li>Page "About Us" updated - 2 hours ago</li>
                    <li>Image "hero-banner.jpg" uploaded - Yesterday</li>
                    <li>Settings changed - 3 days ago</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
