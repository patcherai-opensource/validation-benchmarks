<?php
session_start();
require_once __DIR__ . '/classes/Database.php';

if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header('Location: /');
    exit;
}

$user = $_SESSION['user'];
if ($user['admin'] != 1) {
    header('HTTP/1.1 403 Forbidden');
    echo 'Access denied.';
    exit;
}

$config = include __DIR__ . '/config/localconf.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContentFlow CMS - Settings</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div class="cms-wrapper">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>ContentFlow</h2>
                <span class="version-tag">v8.7.16</span>
            </div>
            <ul class="nav-menu">
                <li><a href="/dashboard.php">Dashboard</a></li>
                <li><a href="/pages.php">Pages</a></li>
                <li><a href="/content.php">Content</a></li>
                <li class="active"><a href="/settings.php">Settings</a></li>
                <li><a href="/users.php">Backend Users</a></li>
            </ul>
            <div class="sidebar-footer">
                <span class="user-info"><?php echo htmlspecialchars($user['realName'] ?: $user['username']); ?></span>
                <a href="/?action=logout" class="logout-link">Logout</a>
            </div>
        </nav>
        <main class="content-area">
            <div class="content-header">
                <h1>System Settings</h1>
            </div>
            <div class="card">
                <h3>Extension Configuration</h3>
                <table class="data-table">
                    <tbody>
                        <tr>
                            <td><strong>Site Name</strong></td>
                            <td><?php echo htmlspecialchars($config['siteName']); ?></td>
                        </tr>
                        <tr>
                            <td><strong>Default Language</strong></td>
                            <td><?php echo htmlspecialchars($config['defaultLanguage']); ?></td>
                        </tr>
                        <tr>
                            <td><strong>Session Timeout</strong></td>
                            <td><?php echo (int)$config['sessionTimeout']; ?>s</td>
                        </tr>
                        <tr>
                            <td><strong>Max Login Attempts</strong></td>
                            <td><?php echo (int)$config['maxLoginAttempts']; ?></td>
                        </tr>
                        <tr>
                            <td><strong>Lockout Duration</strong></td>
                            <td><?php echo (int)$config['lockoutDuration']; ?>s</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="card">
                <h3>Password Hashing Configuration</h3>
                <table class="data-table">
                    <tbody>
                        <tr>
                            <td><strong>Configured Method</strong></td>
                            <td><?php echo htmlspecialchars($config['saltedPWHashingMethod']); ?></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </main>
    </div>
</body>
</html>