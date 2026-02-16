<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$conn = getDbConnection();

$elementType = isset($_GET['type']) ? $_GET['type'] : 'document';
$allowedTypes = ['document', 'asset', 'object'];
if (!in_array($elementType, $allowedTypes)) {
    $elementType = 'document';
}

if ($elementType === 'object') {
    $query = "SELECT o_id as id, o_parentId as parentId, o_key as `key`, o_path as `path`, o_type as `type` FROM objects ORDER BY o_path, o_key";
} else {
    $tableName = $elementType . 's';
    $query = "SELECT id, parentId, `key`, path, type FROM " . $conn->real_escape_string($tableName) . " ORDER BY path, `key`";
}

$result = $conn->query($query);
$elements = [];
while ($row = $result->fetch_assoc()) {
    $elements[] = $row;
}
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elements - Administration</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>CMS Admin</h2>
                <span class="user-badge"><?php echo htmlspecialchars($_SESSION['cms_username']); ?></span>
            </div>
            <ul class="nav-menu">
                <li><a href="/admin/dashboard.php">Dashboard</a></li>
                <li><a href="/admin/elements.php" class="active">Elements</a></li>
                <li><a href="/admin/segments.php">Segments</a></li>
                <li><a href="/admin/segment-manager.php">Segment Manager</a></li>
                <?php if ($_SESSION['cms_role'] === 'admin'): ?>
                <li><a href="/admin/users.php">Users</a></li>
                <?php endif; ?>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <h1>Elements Browser</h1>
            <div class="tab-bar">
                <a href="?type=document" class="tab <?php echo $elementType === 'document' ? 'active' : ''; ?>">Documents</a>
                <a href="?type=asset" class="tab <?php echo $elementType === 'asset' ? 'active' : ''; ?>">Assets</a>
                <a href="?type=object" class="tab <?php echo $elementType === 'object' ? 'active' : ''; ?>">Objects</a>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Key</th>
                        <th>Path</th>
                        <th>Type</th>
                        <th>Parent ID</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($elements as $el): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($el['id']); ?></td>
                        <td><?php echo htmlspecialchars($el['key']); ?></td>
                        <td><?php echo htmlspecialchars($el['path']); ?></td>
                        <td><?php echo htmlspecialchars($el['type']); ?></td>
                        <td><?php echo htmlspecialchars($el['parentId']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>
