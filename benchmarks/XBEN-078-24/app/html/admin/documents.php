<?php
require_once __DIR__ . '/auth.php';
requireAdmin();

$conn = getDbConnection();
$result = $conn->query("SELECT * FROM documents ORDER BY path, `key`");
$documents = [];
while ($row = $result->fetch_assoc()) {
    $documents[] = $row;
}
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore Admin - Documents</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header"><h2>pimcore</h2></div>
            <ul class="nav-menu">
                <li><a href="/admin/dashboard.php">Dashboard</a></li>
                <li><a href="/admin/customers.php">Customers</a></li>
                <li><a href="/admin/segments.php">Segments</a></li>
                <li><a href="/admin/segment-assignment.php">Segment Assignments</a></li>
                <li><a href="/admin/objects.php">Data Objects</a></li>
                <li class="active"><a href="/admin/documents.php">Documents</a></li>
                <li><a href="/admin/assets.php">Assets</a></li>
                <li class="nav-divider"></li>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header">
                <h1>Documents</h1>
                <span class="user-info">Logged in as: <?php echo htmlspecialchars($_SESSION['pimcore_user']); ?></span>
            </div>
            <div class="data-table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Key</th>
                            <th>Path</th>
                            <th>Type</th>
                            <th>Published</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($documents as $d): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($d['id']); ?></td>
                            <td><?php echo htmlspecialchars($d['key']); ?></td>
                            <td><?php echo htmlspecialchars($d['path']); ?></td>
                            <td><?php echo htmlspecialchars($d['type']); ?></td>
                            <td><?php echo $d['published'] ? 'Yes' : 'No'; ?></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </main>
    </div>
</body>
</html>
