<?php
require_once __DIR__ . '/../config.php';
session_start();
check_admin_auth();

$conn = get_db();
$result = $conn->query("SELECT id, `key`, type, path, published, creationDate FROM documents ORDER BY id ASC");
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore Admin - Documents</title>
    <link rel="stylesheet" href="/admin/static/pimcore.css">
</head>
<body>
<div class="admin-layout">
    <div class="admin-sidebar">
        <div class="sidebar-logo">
            <svg width="100" height="32" viewBox="0 0 100 32">
                <text x="0" y="24" font-family="Arial, sans-serif" font-size="22" font-weight="bold" fill="#fff">pimcore</text>
            </svg>
        </div>
        <nav class="sidebar-nav">
            <a href="/admin/" class="nav-item"><span class="nav-icon">&#9635;</span> Dashboard</a>
            <a href="/admin/log/show" class="nav-item"><span class="nav-icon">&#9776;</span> Application Logger</a>
            <a href="/admin/translation/" class="nav-item"><span class="nav-icon">&#127760;</span> Translations</a>
            <a href="/admin/search/" class="nav-item"><span class="nav-icon">&#128269;</span> Search</a>
            <a href="/admin/asset/list" class="nav-item"><span class="nav-icon">&#128194;</span> Assets</a>
            <a href="/admin/document/list" class="nav-item active"><span class="nav-icon">&#128196;</span> Documents</a>
        </nav>
        <div class="sidebar-footer">
            <span class="user-info"><?php echo htmlspecialchars($_SESSION['pimcore_admin_name']); ?></span>
            <a href="/admin/logout.php" class="logout-link">Logout</a>
        </div>
    </div>
    <div class="admin-content">
        <div class="content-header"><h1>Documents</h1></div>
        <table class="data-table">
            <thead><tr><th>ID</th><th>Key</th><th>Type</th><th>Path</th><th>Published</th></tr></thead>
            <tbody>
            <?php while ($row = $result->fetch_assoc()): ?>
            <tr>
                <td><?php echo htmlspecialchars($row['id']); ?></td>
                <td><?php echo htmlspecialchars($row['key']); ?></td>
                <td><?php echo htmlspecialchars($row['type']); ?></td>
                <td><?php echo htmlspecialchars($row['path']); ?></td>
                <td><?php echo $row['published'] ? '&#10003;' : '&#10007;'; ?></td>
            </tr>
            <?php endwhile; ?>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
