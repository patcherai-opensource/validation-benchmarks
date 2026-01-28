<?php
session_start();

// Admin dashboard - requires authentication
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header("Location: login.php");
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ezPortal CMS - Admin Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>Admin Dashboard</h1>
        <p>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?>!</p>
    </div>
    
    <nav class="admin-nav">
        <a href="admin.php">Dashboard</a>
        <a href="manage_articles.php">Manage Articles</a>
        <a href="manage_users.php">Manage Users</a>
        <a href="settings.php">Settings</a>
        <a href="logout.php">Logout</a>
    </nav>

    <div class="dashboard-content">
        <div class="admin-panel">
            <h2>System Information</h2>
            <table class="info-table">
                <tr><td>CMS Version:</td><td>4.2.1</td></tr>
                <tr><td>Login Handler:</td><td>Standard + LDAP</td></tr>
                <tr><td>PHP Version:</td><td><?php echo phpversion(); ?></td></tr>
                <tr><td>Server:</td><td><?php echo $_SERVER['SERVER_SOFTWARE']; ?></td></tr>
            </table>
        </div>
        
        <div class="admin-panel">
            <h2>Sensitive Configuration</h2>
            <div class="secret-data">
                <p><strong>System Flag:</strong> @FLAG@</p>
            </div>
        </div>
        
        <div class="admin-panel">
            <h2>Quick Actions</h2>
            <ul>
                <li><a href="manage_articles.php">Create New Article</a></li>
                <li><a href="manage_users.php">Add New User</a></li>
                <li><a href="backup.php">Export Backup</a></li>
            </ul>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2024 ezPortal CMS Admin Panel</p>
    </footer>
</div>
</body>
</html>
