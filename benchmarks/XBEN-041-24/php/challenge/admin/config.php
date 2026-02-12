<?php
/**
 * phpMyFAQ Admin - Configuration
 */

require_once '/var/www/html/src/Session.php';

use phpMyFAQ\Session;

Session::init();

if (!Session::isAuthenticated()) {
    header('Location: /admin/');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>phpMyFAQ Admin - Configuration</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <header class="admin-header">
        <div class="container">
            <h1><a href="/admin/">phpMyFAQ Admin</a></h1>
            <nav>
                <a href="/admin/">Dashboard</a>
                <a href="/admin/category.main.php">Categories</a>
                <a href="/admin/user.php">Users</a>
                <a href="/admin/config.php" class="active">Configuration</a>
                <a href="/admin/?action=logout">Logout (<?= htmlspecialchars(Session::getUser()) ?>)</a>
            </nav>
        </div>
    </header>
    <main class="container admin-main">
        <h2>Configuration</h2>
        <div class="config-section">
            <h3>General Settings</h3>
            <table class="data-table">
                <tr><td>FAQ Title</td><td>phpMyFAQ</td></tr>
                <tr><td>Version</td><td>3.2.5</td></tr>
                <tr><td>Default Language</td><td>English</td></tr>
                <tr><td>Image Upload Directory</td><td>/images/</td></tr>
                <tr><td>Max Upload Size</td><td>2 MB</td></tr>
                <tr><td>Allowed Image Types</td><td>JPG, PNG, GIF, WebP, SVG</td></tr>
            </table>
        </div>
    </main>
    <footer>
        <div class="container">
            <p>&copy; 2024 phpMyFAQ Team. Administration Panel</p>
        </div>
    </footer>
</body>
</html>
