<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$conn = getDbConnection();

$activities = $conn->query("SELECT a.*, o.o_key as customer_name FROM activities a LEFT JOIN objects o ON a.customerId = o.o_id ORDER BY a.activityDate DESC LIMIT 50");

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMF Admin - Activities</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="admin-layout">
    <?php include __DIR__ . '/sidebar.php'; ?>
    <div class="admin-content">
        <div class="admin-header">
            <h1>Activity Log</h1>
        </div>
        <div class="panel">
            <table class="data-table">
                <thead>
                    <tr><th>ID</th><th>Customer</th><th>Type</th><th>Date</th><th>Details</th></tr>
                </thead>
                <tbody>
                <?php while ($row = $activities->fetch_assoc()): ?>
                    <tr>
                        <td><?php echo intval($row['id']); ?></td>
                        <td><?php echo htmlspecialchars($row['customer_name'] ?? 'N/A'); ?></td>
                        <td><?php echo htmlspecialchars($row['type']); ?></td>
                        <td><?php echo htmlspecialchars($row['activityDate']); ?></td>
                        <td><?php echo htmlspecialchars(substr($row['attributes'] ?? '', 0, 80)); ?></td>
                    </tr>
                <?php endwhile; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>