<?php
/**
 * phpMyFAQ Admin - User Management
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
    <title>phpMyFAQ Admin - Users</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <header class="admin-header">
        <div class="container">
            <h1><a href="/admin/">phpMyFAQ Admin</a></h1>
            <nav>
                <a href="/admin/">Dashboard</a>
                <a href="/admin/category.main.php">Categories</a>
                <a href="/admin/user.php" class="active">Users</a>
                <a href="/admin/config.php">Configuration</a>
                <a href="/admin/?action=logout">Logout (<?= htmlspecialchars(Session::getUser()) ?>)</a>
            </nav>
        </div>
    </header>
    <main class="container admin-main">
        <h2>User Management</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Last Login</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>admin</td>
                    <td>Administrator</td>
                    <td><span class="status-active">Active</span></td>
                    <td><?= date('Y-m-d H:i:s') ?></td>
                </tr>
            </tbody>
        </table>
    </main>
    <footer>
        <div class="container">
            <p>&copy; 2024 phpMyFAQ Team. Administration Panel</p>
        </div>
    </footer>
</body>
</html>
