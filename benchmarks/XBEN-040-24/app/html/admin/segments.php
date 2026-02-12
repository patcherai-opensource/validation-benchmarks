<?php
require_once __DIR__ . '/../includes/auth.php';
$user = requireAdminAuth();
$conn = getDbConnection();

$stmt = $conn->prepare("SELECT id, name, `group`, reference, calculated FROM plugin_cmf_customer_segments ORDER BY name");
$stmt->execute();
$result = $stmt->get_result();
$segments = [];
while ($row = $result->fetch_assoc()) {
    $segments[] = $row;
}
$stmt->close();
$conn->close();

$accept = $_SERVER['HTTP_ACCEPT'] ?? '';
if (strpos($accept, 'application/json') !== false) {
    header('Content-Type: application/json');
    echo json_encode(['success' => true, 'data' => $segments]);
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Customer Segments - pimcore Admin</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header"><h2>pimcore</h2></div>
            <ul class="nav-menu">
                <li><a href="/admin/index.php">Dashboard</a></li>
                <li><a href="/admin/objects.php">Data Objects</a></li>
                <li><a href="/admin/documents.php">Documents</a></li>
                <li><a href="/admin/assets.php">Assets</a></li>
                <li class="nav-divider"></li>
                <li class="nav-section">Customer Management</li>
                <li><a href="/admin/customers.php">Customers</a></li>
                <li class="active"><a href="/admin/segments.php">Customer Segments</a></li>
                <li><a href="/admin/activities.php">Activities</a></li>
                <li><a href="/admin/action-triggers.php">Action Triggers</a></li>
                <li class="nav-divider"></li>
                <li><a href="/admin/settings.php">Settings</a></li>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header"><h1>Customer Segments</h1></div>
            <table class="data-table">
                <thead><tr><th>ID</th><th>Name</th><th>Group</th><th>Reference</th><th>Calculated</th></tr></thead>
                <tbody>
                <?php foreach ($segments as $seg): ?>
                    <tr>
                        <td><?php echo $seg['id']; ?></td>
                        <td><?php echo htmlspecialchars($seg['name']); ?></td>
                        <td><?php echo htmlspecialchars($seg['group'] ?? '-'); ?></td>
                        <td><?php echo htmlspecialchars($seg['reference'] ?? '-'); ?></td>
                        <td><?php echo $seg['calculated'] ? 'Yes' : 'No'; ?></td>
                    </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>
