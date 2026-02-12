<?php
require_once __DIR__ . '/../includes/auth.php';
$user = requireAdminAuth();
$conn = getDbConnection();

$stmt = $conn->prepare("SELECT id, name, description, active FROM plugin_cmf_action_trigger_rules ORDER BY name");
$stmt->execute();
$result = $stmt->get_result();
$rules = [];
while ($row = $result->fetch_assoc()) {
    $rules[] = $row;
}
$stmt->close();
$conn->close();

$accept = $_SERVER['HTTP_ACCEPT'] ?? '';
if (strpos($accept, 'application/json') !== false) {
    header('Content-Type: application/json');
    echo json_encode(['success' => true, 'data' => $rules]);
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Action Triggers - pimcore Admin</title>
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
                <li><a href="/admin/segments.php">Customer Segments</a></li>
                <li><a href="/admin/activities.php">Activities</a></li>
                <li class="active"><a href="/admin/action-triggers.php">Action Triggers</a></li>
                <li class="nav-divider"></li>
                <li><a href="/admin/settings.php">Settings</a></li>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header"><h1>Action Trigger Rules</h1></div>
            <table class="data-table">
                <thead><tr><th>ID</th><th>Name</th><th>Description</th><th>Active</th></tr></thead>
                <tbody>
                <?php foreach ($rules as $rule): ?>
                    <tr>
                        <td><?php echo $rule['id']; ?></td>
                        <td><?php echo htmlspecialchars($rule['name']); ?></td>
                        <td><?php echo htmlspecialchars($rule['description'] ?? ''); ?></td>
                        <td><?php echo $rule['active'] ? 'Yes' : 'No'; ?></td>
                    </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>
