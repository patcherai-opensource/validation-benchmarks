<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$conn = getDbConnection();

$segmentCount = $conn->query("SELECT COUNT(*) as cnt FROM customer_segments")->fetch_assoc()['cnt'];
$groupCount = $conn->query("SELECT COUNT(*) as cnt FROM customer_segment_groups")->fetch_assoc()['cnt'];
$objectCount = $conn->query("SELECT COUNT(*) as cnt FROM objects WHERE o_type = 'object'")->fetch_assoc()['cnt'];
$activityCount = $conn->query("SELECT COUNT(*) as cnt FROM activities")->fetch_assoc()['cnt'];

$recentActivities = $conn->query("SELECT a.*, o.o_key as customer_name FROM activities a LEFT JOIN objects o ON a.customerId = o.o_id ORDER BY a.activityDate DESC LIMIT 5");

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMF Admin - Dashboard</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="admin-layout">
    <?php include __DIR__ . '/sidebar.php'; ?>
    <div class="admin-content">
        <div class="admin-header">
            <h1>Dashboard</h1>
            <span class="user-info">Logged in as: <?php echo htmlspecialchars($_SESSION['admin_user']); ?> (<?php echo htmlspecialchars($_SESSION['admin_role']); ?>)</span>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number"><?php echo $objectCount; ?></div>
                <div class="stat-label">Customer Objects</div>
            </div>
            <div class="stat-card">
                <div class="stat-number"><?php echo $segmentCount; ?></div>
                <div class="stat-label">Segments</div>
            </div>
            <div class="stat-card">
                <div class="stat-number"><?php echo $groupCount; ?></div>
                <div class="stat-label">Segment Groups</div>
            </div>
            <div class="stat-card">
                <div class="stat-number"><?php echo $activityCount; ?></div>
                <div class="stat-label">Activities</div>
            </div>
        </div>

        <div class="panel">
            <h2>Recent Activity</h2>
            <table class="data-table">
                <thead>
                    <tr><th>Customer</th><th>Type</th><th>Date</th></tr>
                </thead>
                <tbody>
                <?php while ($row = $recentActivities->fetch_assoc()): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($row['customer_name'] ?? 'N/A'); ?></td>
                        <td><?php echo htmlspecialchars($row['type']); ?></td>
                        <td><?php echo htmlspecialchars($row['activityDate']); ?></td>
                    </tr>
                <?php endwhile; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>