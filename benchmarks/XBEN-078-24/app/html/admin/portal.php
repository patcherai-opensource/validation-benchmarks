<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$conn = getDbConnection();

$docResult = $conn->query("SELECT COUNT(*) as cnt FROM documents");
$docCount = $docResult->fetch_assoc()['cnt'];

$assetResult = $conn->query("SELECT COUNT(*) as cnt FROM assets");
$assetCount = $assetResult->fetch_assoc()['cnt'];

$transResult = $conn->query("SELECT COUNT(DISTINCT `key`) as cnt FROM translations_messages");
$transCount = $transResult->fetch_assoc()['cnt'];

$userResult = $conn->query("SELECT COUNT(*) as cnt FROM users WHERE active = 1");
$userCount = $userResult->fetch_assoc()['cnt'];

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Administration - Dashboard</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>CMS Admin</h2>
            </div>
            <ul class="nav-menu">
                <li class="active"><a href="/admin/portal.php">Dashboard</a></li>
                <li><a href="/admin/documents.php">Documents</a></li>
                <li><a href="/admin/assets-manager.php">Assets</a></li>
                <li><a href="/admin/locale/data.php">Translations</a></li>
                <?php if ($_SESSION['is_admin']): ?>
                <li><a href="/admin/users.php">Users</a></li>
                <?php endif; ?>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header">
                <h1>Dashboard</h1>
                <span class="user-info">Logged in as: <?php echo htmlspecialchars($_SESSION['username']); ?></span>
            </div>
            <div class="dashboard-stats">
                <div class="stat-card">
                    <h3><?php echo $docCount; ?></h3>
                    <p>Documents</p>
                </div>
                <div class="stat-card">
                    <h3><?php echo $assetCount; ?></h3>
                    <p>Assets</p>
                </div>
                <div class="stat-card">
                    <h3><?php echo $transCount; ?></h3>
                    <p>Translation Keys</p>
                </div>
                <div class="stat-card">
                    <h3><?php echo $userCount; ?></h3>
                    <p>Active Users</p>
                </div>
            </div>
            <div class="recent-activity">
                <h2>Quick Actions</h2>
                <div class="action-links">
                    <a href="/admin/locale/data.php" class="action-btn">Manage Translations</a>
                    <a href="/admin/locale/download.php?domain=messages" class="action-btn">Export Website Translations</a>
                    <a href="/admin/documents.php" class="action-btn">Manage Documents</a>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
