<?php
session_start();
require_once __DIR__ . '/classes/Database.php';

if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header('Location: /');
    exit;
}

$user = $_SESSION['user'];
$pages = [];

try {
    $db = Database::getInstance();
    $pages = $db->fetchAll('SELECT uid, title, slug, tstamp, hidden, sorting FROM pages ORDER BY sorting');
} catch (Exception $e) {
    error_log('Pages error: ' . $e->getMessage());
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContentFlow CMS - Pages</title>
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
                <li class="active"><a href="/pages.php">Pages</a></li>
                <li><a href="/content.php">Content</a></li>
                <?php if ($user['admin'] == 1): ?>
                <li><a href="/settings.php">Settings</a></li>
                <li><a href="/users.php">Backend Users</a></li>
                <?php endif; ?>
            </ul>
            <div class="sidebar-footer">
                <span class="user-info"><?php echo htmlspecialchars($user['realName'] ?: $user['username']); ?></span>
                <a href="/?action=logout" class="logout-link">Logout</a>
            </div>
        </nav>
        <main class="content-area">
            <div class="content-header">
                <h1>Page Tree</h1>
            </div>
            <div class="card">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>UID</th>
                            <th>Title</th>
                            <th>Slug</th>
                            <th>Status</th>
                            <th>Last Modified</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($pages as $page): ?>
                        <tr>
                            <td><?php echo (int)$page['uid']; ?></td>
                            <td><?php echo htmlspecialchars($page['title']); ?></td>
                            <td><?php echo htmlspecialchars($page['slug']); ?></td>
                            <td><?php echo $page['hidden'] ? '<span class="badge badge-hidden">Hidden</span>' : '<span class="badge badge-visible">Visible</span>'; ?></td>
                            <td><?php echo date('Y-m-d H:i', $page['tstamp']); ?></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </main>
    </div>
</body>
</html>