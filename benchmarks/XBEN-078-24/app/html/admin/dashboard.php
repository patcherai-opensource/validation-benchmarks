<?php
require_once __DIR__ . '/auth.php';
requireAdmin();

$conn = getDbConnection();

$customerCount = $conn->query("SELECT COUNT(*) as cnt FROM plugin_cmf_customers")->fetch_assoc()['cnt'];
$segmentCount = $conn->query("SELECT COUNT(*) as cnt FROM plugin_cmf_customer_segments")->fetch_assoc()['cnt'];
$activityCount = $conn->query("SELECT COUNT(*) as cnt FROM plugin_cmf_activities")->fetch_assoc()['cnt'];
$objectCount = $conn->query("SELECT COUNT(*) as cnt FROM objects")->fetch_assoc()['cnt'];
$documentCount = $conn->query("SELECT COUNT(*) as cnt FROM documents")->fetch_assoc()['cnt'];

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore Admin - Dashboard</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>pimcore</h2>
            </div>
            <ul class="nav-menu">
                <li class="active"><a href="/admin/dashboard.php">Dashboard</a></li>
                <li><a href="/admin/customers.php">Customers</a></li>
                <li><a href="/admin/segments.php">Segments</a></li>
                <li><a href="/admin/segment-assignment.php">Segment Assignments</a></li>
                <li><a href="/admin/objects.php">Data Objects</a></li>
                <li><a href="/admin/documents.php">Documents</a></li>
                <li><a href="/admin/assets.php">Assets</a></li>
                <li class="nav-divider"></li>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header">
                <h1>Dashboard</h1>
                <span class="user-info">Logged in as: <?php echo htmlspecialchars($_SESSION['pimcore_user']); ?></span>
            </div>
            <div class="dashboard-grid">
                <div class="stat-card">
                    <h3>Customers</h3>
                    <span class="stat-number"><?php echo $customerCount; ?></span>
                </div>
                <div class="stat-card">
                    <h3>Segments</h3>
                    <span class="stat-number"><?php echo $segmentCount; ?></span>
                </div>
                <div class="stat-card">
                    <h3>Activities</h3>
                    <span class="stat-number"><?php echo $activityCount; ?></span>
                </div>
                <div class="stat-card">
                    <h3>Data Objects</h3>
                    <span class="stat-number"><?php echo $objectCount; ?></span>
                </div>
                <div class="stat-card">
                    <h3>Documents</h3>
                    <span class="stat-number"><?php echo $documentCount; ?></span>
                </div>
            </div>
            <div class="recent-activity">
                <h2>Recent Customer Activity</h2>
                <p>Use the navigation to manage customer segments and assignments.</p>
            </div>
        </main>
    </div>
</body>
</html>
