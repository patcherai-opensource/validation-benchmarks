<?php
require_once __DIR__ . '/auth.php';
requireAdmin();

$conn = getDbConnection();
$result = $conn->query("SELECT * FROM plugin_cmf_customer_segments ORDER BY `group`, name");
$segments = [];
while ($row = $result->fetch_assoc()) {
    $segments[] = $row;
}
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore Admin - Segments</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header"><h2>pimcore</h2></div>
            <ul class="nav-menu">
                <li><a href="/admin/dashboard.php">Dashboard</a></li>
                <li><a href="/admin/customers.php">Customers</a></li>
                <li class="active"><a href="/admin/segments.php">Segments</a></li>
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
                <h1>Customer Segments</h1>
                <span class="user-info">Logged in as: <?php echo htmlspecialchars($_SESSION['pimcore_user']); ?></span>
            </div>
            <div class="data-table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Reference</th>
                            <th>Group</th>
                            <th>Calculated</th>
                            <th>Target Group</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($segments as $s): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($s['id']); ?></td>
                            <td><?php echo htmlspecialchars($s['name']); ?></td>
                            <td><?php echo htmlspecialchars($s['reference']); ?></td>
                            <td><?php echo htmlspecialchars($s['group']); ?></td>
                            <td><?php echo $s['calculated'] ? 'Yes' : 'No'; ?></td>
                            <td><?php echo $s['useAsTargetGroup'] ? 'Yes' : 'No'; ?></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </main>
    </div>
</body>
</html>
