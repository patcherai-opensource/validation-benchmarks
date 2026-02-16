<?php
session_start();

if (!isset($_SESSION['admin_user_id']) || !isset($_SESSION['admin_role'])) {
    header("Location: /admin/");
    exit;
}

$conn = new mysqli(getenv('MYSQL_HOST') ?: '127.0.0.1', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'cmsDB');
if ($conn->connect_error) {
    die("Service Unavailable");
}

$docs = $conn->query("SELECT d.*, u.display_name as author FROM documents d LEFT JOIN users u ON d.created_by = u.id ORDER BY d.updated_at DESC");
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
<body class="admin-body">
<div class="admin-sidebar">
    <div class="sidebar-header">
        <h2>CMS Admin</h2>
    </div>
    <nav class="sidebar-nav">
        <a href="/panel/">Dashboard</a>
        <a href="/panel/documents.php" class="active">Documents</a>
        <a href="/panel/assets.php">Assets</a>
        <?php if ($_SESSION['admin_role'] === 'admin'): ?>
        <a href="/panel/activity.php">Activity Log</a>
        <a href="/panel/settings.php">Settings</a>
        <?php endif; ?>
        <a href="/panel/logout.php">Sign Out</a>
    </nav>
</div>
<div class="admin-main">
    <div class="admin-topbar">
        <span>Welcome, <?php echo htmlspecialchars($_SESSION['admin_display_name']); ?></span>
        <span class="role-badge"><?php echo htmlspecialchars($_SESSION['admin_role']); ?></span>
    </div>
    <div class="admin-content">
        <h1>Documents</h1>
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Key</th>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Path</th>
                    <th>Published</th>
                    <th>Author</th>
                    <th>Updated</th>
                </tr>
            </thead>
            <tbody>
                <?php while ($doc = $docs->fetch_assoc()): ?>
                <tr>
                    <td><?php echo $doc['id']; ?></td>
                    <td><?php echo htmlspecialchars($doc['key']); ?></td>
                    <td><?php echo htmlspecialchars($doc['title']); ?></td>
                    <td><?php echo htmlspecialchars($doc['type']); ?></td>
                    <td><?php echo htmlspecialchars($doc['path']); ?></td>
                    <td><?php echo $doc['published'] ? 'Yes' : 'No'; ?></td>
                    <td><?php echo htmlspecialchars($doc['author']); ?></td>
                    <td><?php echo htmlspecialchars($doc['updated_at']); ?></td>
                </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
