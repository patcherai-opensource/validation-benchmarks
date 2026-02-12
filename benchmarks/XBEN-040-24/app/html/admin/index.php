<?php
require_once __DIR__ . '/../includes/auth.php';
$user = requireAdminAuth();
$conn = getDbConnection();

// Fetch dashboard stats
$objectCount = $conn->query("SELECT COUNT(*) as cnt FROM objects")->fetch_assoc()['cnt'];
$documentCount = $conn->query("SELECT COUNT(*) as cnt FROM documents")->fetch_assoc()['cnt'];
$assetCount = $conn->query("SELECT COUNT(*) as cnt FROM assets")->fetch_assoc()['cnt'];
$segmentCount = $conn->query("SELECT COUNT(*) as cnt FROM plugin_cmf_customer_segments")->fetch_assoc()['cnt'];
$activityCount = $conn->query("SELECT COUNT(*) as cnt FROM plugin_cmf_activities")->fetch_assoc()['cnt'];

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore Admin</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>pimcore</h2>
            </div>
            <ul class="nav-menu">
                <li class="active"><a href="/admin/index.php">Dashboard</a></li>
                <li><a href="/admin/objects.php">Data Objects</a></li>
                <li><a href="/admin/documents.php">Documents</a></li>
                <li><a href="/admin/assets.php">Assets</a></li>
                <li class="nav-divider"></li>
                <li class="nav-section">Customer Management</li>
                <li><a href="/admin/customers.php">Customers</a></li>
                <li><a href="/admin/segments.php">Customer Segments</a></li>
                <li><a href="/admin/activities.php">Activities</a></li>
                <li><a href="/admin/action-triggers.php">Action Triggers</a></li>
                <li class="nav-divider"></li>
                <li><a href="/admin/settings.php">Settings</a></li>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header">
                <h1>Dashboard</h1>
                <span class="user-info">Welcome, <?php echo htmlspecialchars($user['username']); ?></span>
            </div>
            <div class="dashboard-grid">
                <div class="stat-card">
                    <h3>Data Objects</h3>
                    <span class="stat-value"><?php echo $objectCount; ?></span>
                </div>
                <div class="stat-card">
                    <h3>Documents</h3>
                    <span class="stat-value"><?php echo $documentCount; ?></span>
                </div>
                <div class="stat-card">
                    <h3>Assets</h3>
                    <span class="stat-value"><?php echo $assetCount; ?></span>
                </div>
                <div class="stat-card">
                    <h3>Customer Segments</h3>
                    <span class="stat-value"><?php echo $segmentCount; ?></span>
                </div>
                <div class="stat-card">
                    <h3>Activities</h3>
                    <span class="stat-value"><?php echo $activityCount; ?></span>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
