<?php
require_once __DIR__ . '/auth.php';
requireAuth();

$conn = getDbConnection();
$result = $conn->query("SELECT id, `type`, `key`, `path`, published, creationDate, modificationDate FROM documents ORDER BY id ASC");
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
    <title>Administration - Documents</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body>
    <div class="admin-layout">
        <nav class="sidebar">
            <div class="sidebar-header"><h2>CMS Admin</h2></div>
            <ul class="nav-menu">
                <li><a href="/admin/portal.php">Dashboard</a></li>
                <li class="active"><a href="/admin/documents.php">Documents</a></li>
                <li><a href="/admin/assets-manager.php">Assets</a></li>
                <li><a href="/admin/locale/data.php">Translations</a></li>
                <?php if ($_SESSION['is_admin']): ?>
                <li><a href="/admin/users.php">Users</a></li>
                <?php endif; ?>
                <li><a href="/admin/logout.php">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header"><h1>Documents</h1></div>
            <table class="data-table">
                <thead>
                    <tr><th>ID</th><th>Type</th><th>Key</th><th>Path</th><th>Published</th><th>Created</th></tr>
                </thead>
                <tbody>
                    <?php foreach ($documents as $doc): ?>
                    <tr>
                        <td><?php echo $doc['id']; ?></td>
                        <td><?php echo htmlspecialchars($doc['type']); ?></td>
                        <td><?php echo htmlspecialchars($doc['key'] ?: '/'); ?></td>
                        <td><?php echo htmlspecialchars($doc['path']); ?></td>
                        <td><?php echo $doc['published'] ? 'Yes' : 'No'; ?></td>
                        <td><?php echo $doc['creationDate'] ? date('Y-m-d H:i', $doc['creationDate']) : '-'; ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>
