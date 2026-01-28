<?php
session_start();

if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: /admin/');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Settings - GlobalCMS</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="admin-container">
    <h1>System Settings</h1>
    <nav class="admin-nav">
        <a href="/admin/">Dashboard</a>
        <a href="/admin/content.php">Content Management</a>
        <a href="/admin/translations.php">Translations</a>
        <a href="/admin/users.php">User Management</a>
        <a href="/admin/settings.php" class="active">Settings</a>
        <a href="/admin/?logout=1" class="logout">Logout</a>
    </nav>
    
    <div class="settings-panel">
        <h2>Configuration</h2>
        <form method="POST">
            <div class="form-group">
                <label>Site Name:</label>
                <input type="text" value="GlobalCMS" disabled>
            </div>
            <div class="form-group">
                <label>Default Language:</label>
                <select disabled>
                    <option>English (en_US)</option>
                    <option>German (de_DE)</option>
                    <option>French (fr_FR)</option>
                </select>
            </div>
            <div class="form-group">
                <label>Cache TTL (seconds):</label>
                <input type="number" value="3600" disabled>
            </div>
            <p class="info">Settings are managed via configuration files. Contact system administrator for changes.</p>
        </form>
    </div>
</div>
</body>
</html>
