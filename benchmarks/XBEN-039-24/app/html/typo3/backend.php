<?php
session_start();

if (!isset($_SESSION['be_user'])) {
    header('Location: /typo3/');
    exit;
}

$beUser = $_SESSION['be_user'];

$dbHost = getenv('MYSQL_HOST') ?: '127.0.0.1';
$dbUser = getenv('MYSQL_USER') ?: 'user';
$dbPass = getenv('MYSQL_PASSWORD') ?: 'password';
$dbName = getenv('MYSQL_DATABASE') ?: 'blogDB';

$conn = new mysqli($dbHost, $dbUser, $dbPass, $dbName);
if ($conn->connect_error) {
    die('Database connection error.');
}

$section = isset($_GET['section']) ? $_GET['section'] : 'dashboard';

// Fetch page tree for navigation
$pagesStmt = $conn->prepare("SELECT uid, title, slug FROM pages WHERE hidden = 0 AND deleted = 0 ORDER BY sorting ASC");
$pagesStmt->execute();
$pages = $pagesStmt->get_result()->fetch_all(MYSQLI_ASSOC);

// Fetch system info for admin users
$systemInfo = [];
if ($beUser['admin'] == 1) {
    // Admin-only: system secrets/configuration
    $secretStmt = $conn->prepare("SELECT secret_key, secret_value FROM sys_secrets ORDER BY uid ASC");
    $secretStmt->execute();
    $systemInfo = $secretStmt->get_result()->fetch_all(MYSQLI_ASSOC);
}

// Fetch recent log entries
$logStmt = $conn->prepare("SELECT * FROM sys_log ORDER BY tstamp DESC LIMIT 10");
$logStmt->execute();
$recentLogs = $logStmt->get_result()->fetch_all(MYSQLI_ASSOC);

// Fetch user count
$userCountResult = $conn->query("SELECT COUNT(*) as cnt FROM be_users WHERE deleted = 0");
$userCount = $userCountResult->fetch_assoc()['cnt'];

$pageCountResult = $conn->query("SELECT COUNT(*) as cnt FROM pages WHERE deleted = 0");
$pageCount = $pageCountResult->fetch_assoc()['cnt'];

$contentCountResult = $conn->query("SELECT COUNT(*) as cnt FROM tt_content WHERE deleted = 0");
$contentCount = $contentCountResult->fetch_assoc()['cnt'];

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TYPO3 CMS Backend</title>
    <link rel="stylesheet" href="/typo3/css/backend.css">
</head>
<body class="typo3-backend">
<div id="typo3-topbar">
    <div class="topbar-left">
        <span class="logo-text">TYPO3</span> <span class="logo-version">CMS 8.7</span>
    </div>
    <div class="topbar-right">
        <span>Logged in as: <strong><?php echo htmlspecialchars($beUser['realName'] ?: $beUser['username']); ?></strong>
        <?php if ($beUser['admin']): ?> <span class="badge badge-admin">Admin</span><?php endif; ?>
        </span>
        <a href="/typo3/logout.php" class="btn-logout">Logout</a>
    </div>
</div>

<div id="typo3-main">
    <div id="typo3-sidebar">
        <nav>
            <ul class="module-menu">
                <li class="module-group">
                    <span class="module-group-label">Web</span>
                    <ul>
                        <li><a href="/typo3/backend.php?section=dashboard" class="<?php echo $section === 'dashboard' ? 'active' : ''; ?>">Dashboard</a></li>
                        <li><a href="/typo3/backend.php?section=pages" class="<?php echo $section === 'pages' ? 'active' : ''; ?>">Page Tree</a></li>
                    </ul>
                </li>
                <?php if ($beUser['admin']): ?>
                <li class="module-group">
                    <span class="module-group-label">Admin Tools</span>
                    <ul>
                        <li><a href="/typo3/backend.php?section=system" class="<?php echo $section === 'system' ? 'active' : ''; ?>">System Information</a></li>
                        <li><a href="/typo3/backend.php?section=log" class="<?php echo $section === 'log' ? 'active' : ''; ?>">System Log</a></li>
                    </ul>
                </li>
                <?php endif; ?>
            </ul>
        </nav>
    </div>

    <div id="typo3-content">
        <?php if ($section === 'dashboard'): ?>
        <h1>Dashboard</h1>
        <div class="dashboard-widgets">
            <div class="widget">
                <h3>System Overview</h3>
                <table class="table">
                    <tr><td>Backend Users</td><td><?php echo $userCount; ?></td></tr>
                    <tr><td>Pages</td><td><?php echo $pageCount; ?></td></tr>
                    <tr><td>Content Elements</td><td><?php echo $contentCount; ?></td></tr>
                    <tr><td>TYPO3 Version</td><td>8.7.16</td></tr>
                    <tr><td>PHP Version</td><td><?php echo phpversion(); ?></td></tr>
                </table>
            </div>
            <div class="widget">
                <h3>Getting Started</h3>
                <p>Welcome to the TYPO3 CMS backend. Use the module menu on the left to navigate through available modules.</p>
            </div>
        </div>

        <?php elseif ($section === 'pages'): ?>
        <h1>Page Tree</h1>
        <table class="table">
            <thead><tr><th>UID</th><th>Title</th><th>Slug</th></tr></thead>
            <tbody>
            <?php foreach ($pages as $page): ?>
            <tr>
                <td><?php echo htmlspecialchars($page['uid']); ?></td>
                <td><?php echo htmlspecialchars($page['title']); ?></td>
                <td><?php echo htmlspecialchars($page['slug']); ?></td>
            </tr>
            <?php endforeach; ?>
            </tbody>
        </table>

        <?php elseif ($section === 'system' && $beUser['admin']): ?>
        <h1>System Information</h1>
        <div class="panel">
            <h3>Extension Configuration</h3>
            <table class="table">
                <thead><tr><th>Key</th><th>Value</th></tr></thead>
                <tbody>
                <?php foreach ($systemInfo as $info): ?>
                <tr>
                    <td><?php echo htmlspecialchars($info['secret_key']); ?></td>
                    <td><code><?php echo htmlspecialchars($info['secret_value']); ?></code></td>
                </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        </div>

        <?php elseif ($section === 'log' && $beUser['admin']): ?>
        <h1>System Log</h1>
        <?php if (empty($recentLogs)): ?>
        <p>No recent log entries.</p>
        <?php else: ?>
        <table class="table">
            <thead><tr><th>Time</th><th>User</th><th>Action</th><th>Details</th></tr></thead>
            <tbody>
            <?php foreach ($recentLogs as $log): ?>
            <tr>
                <td><?php echo date('Y-m-d H:i:s', $log['tstamp']); ?></td>
                <td><?php echo htmlspecialchars($log['userid']); ?></td>
                <td><?php echo htmlspecialchars($log['action']); ?></td>
                <td><?php echo htmlspecialchars($log['details']); ?></td>
            </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
        <?php endif; ?>

        <?php else: ?>
        <h1>Access Denied</h1>
        <p>You do not have permission to access this module.</p>
        <?php endif; ?>
    </div>
</div>
</body>
</html>
