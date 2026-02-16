<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$conn = getDbConnection();
$docCount = $conn->query("SELECT COUNT(*) as cnt FROM documents")->fetch_assoc()['cnt'];
$assetCount = $conn->query("SELECT COUNT(*) as cnt FROM assets")->fetch_assoc()['cnt'];
$objCount = $conn->query("SELECT COUNT(*) as cnt FROM objects")->fetch_assoc()['cnt'];
$segCount = $conn->query("SELECT COUNT(*) as cnt FROM customer_segments")->fetch_assoc()['cnt'];
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Administration</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>CMS Admin</h2>
                <span class="user-badge"><?php echo htmlspecialchars($_SESSION['cms_username']); ?> (<?php echo htmlspecialchars($_SESSION['cms_role']); ?>)</span>
            </div>
            <ul class="nav-menu">
                <li><a href="/admin/dashboard.php" class="active">Dashboard</a></li>
                <li><a href="/admin/elements.php">Elements</a></li>
                <li><a href="/admin/segments.php">Segments</a></li>
                <li><a href="/admin/segment-manager.php">Segment Manager</a></li>
                <?php if ($_SESSION['cms_role'] === 'admin'): ?>
                <li><a href="/admin/users.php">Users</a></li>
                <?php endif; ?>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <h1>Dashboard</h1>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Documents</h3>
                    <span class="stat-number"><?php echo $docCount; ?></span>
                </div>
                <div class="stat-card">
                    <h3>Assets</h3>
                    <span class="stat-number"><?php echo $assetCount; ?></span>
                </div>
                <div class="stat-card">
                    <h3>Objects</h3>
                    <span class="stat-number"><?php echo $objCount; ?></span>
                </div>
                <div class="stat-card">
                    <h3>Segments</h3>
                    <span class="stat-number"><?php echo $segCount; ?></span>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
