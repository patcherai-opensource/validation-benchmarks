<?php
require_once __DIR__ . '/../includes/auth.php';
$user = requireAdminAuth();
$conn = getDbConnection();

$parentId = isset($_GET['parentId']) ? intval($_GET['parentId']) : 0;
$stmt = $conn->prepare("SELECT o_id, o_parentId, o_type, o_key, o_path, o_classId, o_className FROM objects WHERE o_parentId = ? ORDER BY o_key");
$stmt->bind_param('i', $parentId);
$stmt->execute();
$result = $stmt->get_result();
$objects = [];
while ($row = $result->fetch_assoc()) {
    $objects[] = $row;
}
$stmt->close();
$conn->close();

// If JSON request
$accept = $_SERVER['HTTP_ACCEPT'] ?? '';
if (strpos($accept, 'application/json') !== false) {
    header('Content-Type: application/json');
    echo json_encode(['success' => true, 'data' => $objects]);
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Data Objects - pimcore Admin</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header"><h2>pimcore</h2></div>
            <ul class="nav-menu">
                <li><a href="/admin/index.php">Dashboard</a></li>
                <li class="active"><a href="/admin/objects.php">Data Objects</a></li>
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
                <h1>Data Objects</h1>
            </div>
            <table class="data-table">
                <thead>
                    <tr><th>ID</th><th>Key</th><th>Type</th><th>Class</th><th>Path</th></tr>
                </thead>
                <tbody>
                <?php foreach ($objects as $obj): ?>
                    <tr>
                        <td><?php echo $obj['o_id']; ?></td>
                        <td>
                            <?php if ($obj['o_type'] === 'folder'): ?>
                                <a href="?parentId=<?php echo $obj['o_id']; ?>"><?php echo htmlspecialchars($obj['o_key']); ?></a>
                            <?php else: ?>
                                <?php echo htmlspecialchars($obj['o_key']); ?>
                            <?php endif; ?>
                        </td>
                        <td><?php echo htmlspecialchars($obj['o_type']); ?></td>
                        <td><?php echo htmlspecialchars($obj['o_className'] ?? '-'); ?></td>
                        <td><?php echo htmlspecialchars($obj['o_path']); ?></td>
                    </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>
