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
    <title>User Management - GlobalCMS</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="admin-container">
    <h1>User Management</h1>
    <nav class="admin-nav">
        <a href="/admin/">Dashboard</a>
        <a href="/admin/content.php">Content Management</a>
        <a href="/admin/translations.php">Translations</a>
        <a href="/admin/users.php" class="active">User Management</a>
        <a href="/admin/settings.php">Settings</a>
        <a href="/admin/?logout=1" class="logout">Logout</a>
    </nav>
    
    <div class="users-panel">
        <h2>User Accounts</h2>
        <p>User management is restricted to super administrators.</p>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Role</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>admin</td>
                    <td>Administrator</td>
                    <td>Active</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>editor</td>
                    <td>Content Editor</td>
                    <td>Active</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>translator</td>
                    <td>Translator</td>
                    <td>Active</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
