<?php
require_once __DIR__ . '/../includes/auth.php';
$user = requireAdminAuth();
$conn = getDbConnection();

$stmt = $conn->prepare("SELECT id, parentId, type, `key`, path, published FROM documents ORDER BY `key`");
$stmt->execute();
$result = $stmt->get_result();
$documents = [];
while ($row = $result->fetch_assoc()) {
    $documents[] = $row;
}
$stmt->close();
$conn->close();

$accept = $_SERVER['HTTP_ACCEPT'] ?? '';
if (strpos($accept, 'application/json') !== false) {
    header('Content-Type: application/json');
    echo json_encode(['success' => true, 'data' => $documents]);
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Documents - pimcore Admin</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header"><h2>pimcore</h2></div>
            <ul class="nav-menu">
                <li><a href="/admin/index.php">Dashboard</a></li>
                <li><a href="/admin/objects.php">Data Objects</a></li>
                <li class="active"><a href="/admin/documents.php">Documents</a></li>
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
            <div class="content-header"><h1>Documents</h1></div>
            <table class="data-table">
                <thead><tr><th>ID</th><th>Key</th><th>Type</th><th>Path</th><th>Published</th></tr></thead>
                <tbody>
                <?php foreach ($documents as $doc): ?>
                    <tr>
                        <td><?php echo $doc['id']; ?></td>
                        <td><?php echo htmlspecialchars($doc['key']); ?></td>
                        <td><?php echo htmlspecialchars($doc['type']); ?></td>
                        <td><?php echo htmlspecialchars($doc['path']); ?></td>
                        <td><?php echo $doc['published'] ? 'Yes' : 'No'; ?></td>
                    </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>
