<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$conn = getDbConnection();
$result = $conn->query("SELECT id, `type`, filename, `path`, mimetype, creationDate FROM assets ORDER BY id ASC");
$assets = [];
while ($row = $result->fetch_assoc()) {
    $assets[] = $row;
}
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Administration - Assets</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header"><h2>CMS Admin</h2></div>
            <ul class="nav-menu">
                <li><a href="/admin/portal.php">Dashboard</a></li>
                <li><a href="/admin/documents.php">Documents</a></li>
                <li class="active"><a href="/admin/assets-manager.php">Assets</a></li>
                <li><a href="/admin/locale/data.php">Translations</a></li>
                <?php if ($_SESSION['is_admin']): ?>
                <li><a href="/admin/users.php">Users</a></li>
                <?php endif; ?>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header"><h1>Assets</h1></div>
            <table class="data-table">
                <thead>
                    <tr><th>ID</th><th>Type</th><th>Filename</th><th>Path</th><th>MIME Type</th><th>Created</th></tr>
                </thead>
                <tbody>
                    <?php foreach ($assets as $asset): ?>
                    <tr>
                        <td><?php echo $asset['id']; ?></td>
                        <td><?php echo htmlspecialchars($asset['type']); ?></td>
                        <td><?php echo htmlspecialchars($asset['filename'] ?: '/'); ?></td>
                        <td><?php echo htmlspecialchars($asset['path']); ?></td>
                        <td><?php echo htmlspecialchars($asset['mimetype'] ?? '-'); ?></td>
                        <td><?php echo $asset['creationDate'] ? date('Y-m-d H:i', $asset['creationDate']) : '-'; ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>
