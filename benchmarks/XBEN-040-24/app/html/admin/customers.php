<?php
require_once __DIR__ . '/../includes/auth.php';
$user = requireAdminAuth();
$conn = getDbConnection();

$stmt = $conn->prepare("SELECT o_id, o_key, o_path FROM objects WHERE o_classId = 'CU' ORDER BY o_key");
$stmt->execute();
$result = $stmt->get_result();
$customers = [];
while ($row = $result->fetch_assoc()) {
    $customers[] = $row;
}
$stmt->close();

// Get segment counts for each customer
foreach ($customers as &$customer) {
    $segStmt = $conn->prepare("SELECT COUNT(*) as cnt FROM plugin_cmf_segment_assignment WHERE elementId = ? AND elementType = 'object'");
    $segStmt->bind_param('i', $customer['o_id']);
    $segStmt->execute();
    $customer['segment_count'] = $segStmt->get_result()->fetch_assoc()['cnt'];
    $segStmt->close();
}

$conn->close();

$accept = $_SERVER['HTTP_ACCEPT'] ?? '';
if (strpos($accept, 'application/json') !== false) {
    header('Content-Type: application/json');
    echo json_encode(['success' => true, 'data' => $customers]);
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Customers - pimcore Admin</title>
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
                <li class="active"><a href="/admin/customers.php">Customers</a></li>
                <li><a href="/admin/segments.php">Customer Segments</a></li>
                <li><a href="/admin/activities.php">Activities</a></li>
                <li><a href="/admin/action-triggers.php">Action Triggers</a></li>
                <li class="nav-divider"></li>
                <li><a href="/admin/settings.php">Settings</a></li>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header"><h1>Customers</h1></div>
            <table class="data-table">
                <thead><tr><th>ID</th><th>Name</th><th>Path</th><th>Segments</th></tr></thead>
                <tbody>
                <?php foreach ($customers as $cust): ?>
                    <tr>
                        <td><?php echo $cust['o_id']; ?></td>
                        <td><?php echo htmlspecialchars($cust['o_key']); ?></td>
                        <td><?php echo htmlspecialchars($cust['o_path']); ?></td>
                        <td><?php echo $cust['segment_count']; ?></td>
                    </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>
