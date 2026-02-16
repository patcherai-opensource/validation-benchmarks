<?php
require_once __DIR__ . '/auth.php';
requireAdmin();

$conn = getDbConnection();

$elementType = isset($_GET['element_type']) ? $_GET['element_type'] : 'document';
$allowedTypes = ['document', 'asset', 'object'];
if (!in_array($elementType, $allowedTypes)) {
    $elementType = 'document';
}

if ($elementType === 'object') {
    $query = "SELECT o_id as id, o_key as `key`, o_path as `path` FROM objects ORDER BY o_path, o_key";
} else {
    $table = $conn->real_escape_string($elementType . 's');
    $query = "SELECT id, `key`, path FROM $table ORDER BY path, `key`";
}

$result = $conn->query($query);
$elements = [];
while ($row = $result->fetch_assoc()) {
    $elements[] = $row;
}

$assignments = $conn->query("SELECT * FROM element_segment_assignments WHERE elementType = '" . $conn->real_escape_string($elementType) . "'")->fetch_all(MYSQLI_ASSOC);
$assignMap = [];
foreach ($assignments as $a) {
    $assignMap[$a['elementId']] = $a;
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Segment Manager - Administration</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
    <script src="/assets/js/segment-manager.js" defer></script>
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
                <li><a href="/admin/elements.php">Elements</a></li>
                <li><a href="/admin/segments.php">Segments</a></li>
                <li><a href="/admin/segment-manager.php" class="active">Segment Manager</a></li>
                <?php if ($_SESSION['cms_role'] === 'admin'): ?>
                <li><a href="/admin/users.php">Users</a></li>
                <?php endif; ?>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <h1>Segment Assignment Manager</h1>
            <p>Manage segment assignments for elements. Segments can be inherited from parent elements in the tree hierarchy.</p>
            
            <div class="tab-bar">
                <a href="?element_type=document" class="tab <?php echo $elementType === 'document' ? 'active' : ''; ?>">Documents</a>
                <a href="?element_type=asset" class="tab <?php echo $elementType === 'asset' ? 'active' : ''; ?>">Assets</a>
                <a href="?element_type=object" class="tab <?php echo $elementType === 'object' ? 'active' : ''; ?>">Objects</a>
            </div>

            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Path</th>
                        <th>Assigned Segments</th>
                        <th>Breaks Inheritance</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($elements as $el): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($el['id']); ?></td>
                        <td><?php echo htmlspecialchars($el['path'] . $el['key']); ?></td>
                        <td><?php echo isset($assignMap[$el['id']]) ? htmlspecialchars($assignMap[$el['id']]['segments']) : '-'; ?></td>
                        <td><?php echo isset($assignMap[$el['id']]) ? ($assignMap[$el['id']]['breaksInheritance'] ? 'Yes' : 'No') : '-'; ?></td>
                        <td>
                            <button class="btn btn-sm" onclick="loadInheritedSegments(<?php echo $el['id']; ?>, '<?php echo $elementType; ?>')">View Inherited</button>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>

            <div id="inherited-panel" class="panel" style="display:none;">
                <h3>Inherited Segments</h3>
                <div id="inherited-content"></div>
            </div>
        </main>
    </div>
</body>
</html>
