<?php
session_start();

if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: index.php');
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Settings - Admin Panel</title>
    <link rel="stylesheet" href="../styles.css">
    <style>
        .sidebar { float: left; width: 200px; background: #f4f4f4; padding: 20px; min-height: 400px; }
        .sidebar a { display: block; padding: 10px; margin: 5px 0; text-decoration: none; color: #333; }
        .sidebar a:hover { background: #ddd; }
        .sidebar a.active { background: #333; color: white; }
        .main-content { margin-left: 240px; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select { width: 300px; padding: 8px; }
        button { padding: 10px 20px; background: #333; color: white; border: none; cursor: pointer; }
        button:hover { background: #555; }
    </style>
</head>
<body>
<div class="container">
    <h1>Admin Panel</h1>
    <p>Welcome, <?php echo htmlspecialchars($_SESSION['admin_username']); ?> | <a href="logout.php">Logout</a></p>
    
    <div class="sidebar">
        <a href="dashboard.php">Dashboard</a>
        <a href="posts.php">Posts</a>
        <a href="translations.php">Translations</a>
        <a href="settings.php" class="active">Settings</a>
    </div>
    
    <div class="main-content">
        <h2>System Settings</h2>
        
        <form method="POST" action="">
            <div class="form-group">
                <label>Site Name:</label>
                <input type="text" name="site_name" value="Content Management System">
            </div>
            <div class="form-group">
                <label>Default Language:</label>
                <select name="default_language">
                    <option value="en" selected>English</option>
                    <option value="de">German</option>
                    <option value="fr">French</option>
                    <option value="es">Spanish</option>
                </select>
            </div>
            <div class="form-group">
                <label>Maintenance Mode:</label>
                <select name="maintenance_mode">
                    <option value="0" selected>Disabled</option>
                    <option value="1">Enabled</option>
                </select>
            </div>
            <button type="submit">Save Settings</button>
        </form>
    </div>
    <div style="clear: both;"></div>
</div>
</body>
</html>
