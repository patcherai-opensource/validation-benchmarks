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

$users = [];
try {
    $db = Database::getInstance();
    $users = $db->fetchAll('SELECT uid, username, realName, email, admin, lastlogin, disabled FROM be_users WHERE deleted = 0 ORDER BY uid');
} catch (Exception $e) {
    error_log('Users page error: ' . $e->getMessage());
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContentFlow CMS - Backend Users</title>
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
                <li><a href="/settings.php">Settings</a></li>
                <li class="active"><a href="/users.php">Backend Users</a></li>
            </ul>
            <div class="sidebar-footer">
                <span class="user-info"><?php echo htmlspecialchars($user['realName'] ?: $user['username']); ?></span>
                <a href="/?action=logout" class="logout-link">Logout</a>
            </div>
        </nav>
        <main class="content-area">
            <div class="content-header">
                <h1>Backend Users</h1>
            </div>
            <div class="card">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>UID</th>
                            <th>Username</th>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Admin</th>
                            <th>Status</th>
                            <th>Last Login</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($users as $u): ?>
                        <tr>
                            <td><?php echo (int)$u['uid']; ?></td>
                            <td><?php echo htmlspecialchars($u['username']); ?></td>
                            <td><?php echo htmlspecialchars($u['realName']); ?></td>
                            <td><?php echo htmlspecialchars($u['email']); ?></td>
                            <td><?php echo $u['admin'] ? 'Yes' : 'No'; ?></td>
                            <td><?php echo $u['disabled'] ? '<span class="badge badge-hidden">Disabled</span>' : '<span class="badge badge-visible">Active</span>'; ?></td>
                            <td><?php echo $u['lastlogin'] ? date('Y-m-d H:i', $u['lastlogin']) : 'Never'; ?></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </main>
    </div>
</body>
</html>