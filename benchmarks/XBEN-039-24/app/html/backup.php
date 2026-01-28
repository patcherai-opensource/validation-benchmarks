<?php
session_start();
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header("Location: login.php");
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ezPortal CMS - Backup</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>System Backup</h1>
    </div>
    
    <nav class="admin-nav">
        <a href="admin.php">Dashboard</a>
        <a href="manage_articles.php">Manage Articles</a>
        <a href="manage_users.php">Manage Users</a>
        <a href="settings.php">Settings</a>
        <a href="logout.php">Logout</a>
    </nav>

    <div class="admin-content">
        <h2>Backup Management</h2>
        <p>Export system configuration and content backups.</p>
        <p><em>Feature under maintenance.</em></p>
    </div>
</div>
</body>
</html>
