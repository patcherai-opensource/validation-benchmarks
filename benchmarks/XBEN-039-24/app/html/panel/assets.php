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

$assets = $conn->query("SELECT a.*, u.display_name as uploader FROM assets a LEFT JOIN users u ON a.created_by = u.id ORDER BY a.updated_at DESC");
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
<body class="admin-body">
<div class="admin-sidebar">
    <div class="sidebar-header">
        <h2>CMS Admin</h2>
    </div>
    <nav class="sidebar-nav">
        <a href="/panel/">Dashboard</a>
        <a href="/panel/documents.php">Documents</a>
        <a href="/panel/assets.php" class="active">Assets</a>
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
        <h1>Assets</h1>
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Filename</th>
                    <th>Type</th>
                    <th>Path</th>
                    <th>MIME Type</th>
                    <th>Size</th>
                    <th>Uploaded By</th>
                    <th>Updated</th>
                </tr>
            </thead>
            <tbody>
                <?php while ($asset = $assets->fetch_assoc()): ?>
                <tr>
                    <td><?php echo $asset['id']; ?></td>
                    <td><?php echo htmlspecialchars($asset['filename']); ?></td>
                    <td><?php echo htmlspecialchars($asset['type']); ?></td>
                    <td><?php echo htmlspecialchars($asset['path']); ?></td>
                    <td><?php echo htmlspecialchars($asset['mimetype']); ?></td>
                    <td><?php echo number_format($asset['filesize']); ?> bytes</td>
                    <td><?php echo htmlspecialchars($asset['uploader']); ?></td>
                    <td><?php echo htmlspecialchars($asset['updated_at']); ?></td>
                </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
