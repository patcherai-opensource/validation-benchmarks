<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$conn = getDbConnection();
$result = $conn->query("SELECT * FROM customer_segments ORDER BY segmentGroup, name");
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
    <title>Segments - Administration</title>
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
                <li><a href="/admin/elements.php">Elements</a></li>
                <li><a href="/admin/segments.php" class="active">Segments</a></li>
                <li><a href="/admin/segment-manager.php">Segment Manager</a></li>
                <?php if ($_SESSION['cms_role'] === 'admin'): ?>
                <li><a href="/admin/users.php">Users</a></li>
                <?php endif; ?>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <h1>Customer Segments</h1>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Group</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($segments as $seg): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($seg['id']); ?></td>
                        <td><?php echo htmlspecialchars($seg['name']); ?></td>
                        <td><?php echo htmlspecialchars($seg['type']); ?></td>
                        <td><?php echo htmlspecialchars($seg['segmentGroup']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>
