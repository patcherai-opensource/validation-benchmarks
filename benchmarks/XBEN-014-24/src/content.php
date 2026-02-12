<?php
session_start();
require_once __DIR__ . '/classes/Database.php';

if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header('Location: /');
    exit;
}

$user = $_SESSION['user'];
$content = [];

try {
    $db = Database::getInstance();
    $content = $db->fetchAll('SELECT c.uid, c.header, c.bodytext, c.CType, c.tstamp, p.title as page_title FROM tt_content c LEFT JOIN pages p ON c.pid = p.uid ORDER BY c.tstamp DESC');
} catch (Exception $e) {
    error_log('Content error: ' . $e->getMessage());
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContentFlow CMS - Content</title>
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
                <li class="active"><a href="/content.php">Content</a></li>
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
                <h1>Content Elements</h1>
            </div>
            <div class="card">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>UID</th>
                            <th>Header</th>
                            <th>Type</th>
                            <th>Page</th>
                            <th>Modified</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($content as $item): ?>
                        <tr>
                            <td><?php echo (int)$item['uid']; ?></td>
                            <td><?php echo htmlspecialchars($item['header']); ?></td>
                            <td><span class="badge"><?php echo htmlspecialchars($item['CType']); ?></span></td>
                            <td><?php echo htmlspecialchars($item['page_title'] ?? ''); ?></td>
                            <td><?php echo date('Y-m-d H:i', $item['tstamp']); ?></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </main>
    </div>
</body>
</html>