<?php
session_start();

require_once __DIR__ . '/classes/Database.php';

// Require authentication
if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header('Location: /');
    exit;
}

$user = $_SESSION['user'];
$config = include __DIR__ . '/config/localconf.php';

// Load dashboard data
$pages = [];
$recentContent = [];
$systemNotes = [];

try {
    $db = Database::getInstance();
    $pages = $db->fetchAll('SELECT uid, title, slug, tstamp, hidden FROM pages ORDER BY sorting LIMIT 10');
    $recentContent = $db->fetchAll('SELECT uid, header, bodytext, tstamp FROM tt_content ORDER BY tstamp DESC LIMIT 5');

    // Admin-only: load system configuration notes
    if ($user['admin'] == 1) {
        $systemNotes = $db->fetchAll('SELECT uid, subject, message, crdate FROM sys_note ORDER BY crdate DESC');
    }
} catch (Exception $e) {
    error_log('Dashboard error: ' . $e->getMessage());
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContentFlow CMS - Dashboard</title>
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
                <li class="active"><a href="/dashboard.php">Dashboard</a></li>
                <li><a href="/pages.php">Pages</a></li>
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
                <h1>Dashboard</h1>
                <p>Welcome back, <?php echo htmlspecialchars($user['realName'] ?: $user['username']); ?>.</p>
            </div>

            <div class="dashboard-grid">
                <div class="card">
                    <h3>Pages</h3>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Slug</th>
                                <th>Status</th>
                                <th>Modified</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($pages as $page): ?>
                            <tr>
                                <td><?php echo htmlspecialchars($page['title']); ?></td>
                                <td><?php echo htmlspecialchars($page['slug']); ?></td>
                                <td><?php echo $page['hidden'] ? '<span class="badge badge-hidden">Hidden</span>' : '<span class="badge badge-visible">Visible</span>'; ?></td>
                                <td><?php echo date('Y-m-d H:i', $page['tstamp']); ?></td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>

                <div class="card">
                    <h3>Recent Content</h3>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Header</th>
                                <th>Modified</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($recentContent as $content): ?>
                            <tr>
                                <td><?php echo htmlspecialchars($content['header']); ?></td>
                                <td><?php echo date('Y-m-d H:i', $content['tstamp']); ?></td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>

                <?php if ($user['admin'] == 1 && !empty($systemNotes)): ?>
                <div class="card card-admin">
                    <h3>System Notes</h3>
                    <?php foreach ($systemNotes as $note): ?>
                    <div class="note-item">
                        <strong><?php echo htmlspecialchars($note['subject']); ?></strong>
                        <p><?php echo htmlspecialchars($note['message']); ?></p>
                        <small><?php echo date('Y-m-d H:i', $note['crdate']); ?></small>
                    </div>
                    <?php endforeach; ?>
                </div>
                <?php endif; ?>
            </div>
        </main>
    </div>
</body>
</html>