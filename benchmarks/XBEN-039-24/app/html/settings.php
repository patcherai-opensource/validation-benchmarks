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
    <title>ezPortal CMS - Settings</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>System Settings</h1>
    </div>
    
    <nav class="admin-nav">
        <a href="admin.php">Dashboard</a>
        <a href="manage_articles.php">Manage Articles</a>
        <a href="manage_users.php">Manage Users</a>
        <a href="settings.php">Settings</a>
        <a href="logout.php">Logout</a>
    </nav>

    <div class="admin-content">
        <h2>Authentication Settings</h2>
        <div class="settings-section">
            <h3>Active Login Handlers</h3>
            <ul>
                <li>✓ Standard (Database)</li>
                <li>✓ LDAP (Directory Service)</li>
                <li>✗ TextFile (Disabled)</li>
            </ul>
        </div>
        
        <div class="settings-section">
            <h3>Security Configuration</h3>
            <table class="info-table">
                <tr><td>Password Hashing:</td><td>MD5</td></tr>
                <tr><td>Session Timeout:</td><td>30 minutes</td></tr>
                <tr><td>Max Login Attempts:</td><td>5</td></tr>
            </table>
        </div>
    </div>
</div>
</body>
</html>
