<?php
session_start();

if (!isset($_SESSION['admin_user_id']) || !isset($_SESSION['admin_role'])) {
    header("Location: /admin/");
    exit;
}

if ($_SESSION['admin_role'] !== 'admin') {
    header("HTTP/1.1 403 Forbidden");
    echo "Access denied. Administrator privileges required.";
    exit;
}

$conn = new mysqli(getenv('MYSQL_HOST') ?: '127.0.0.1', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'cmsDB');
if ($conn->connect_error) {
    die("Service Unavailable");
}

$settings = $conn->query("SELECT * FROM settings ORDER BY `scope`, `name`");
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Administration - Settings</title>
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
        <a href="/panel/assets.php">Assets</a>
        <a href="/panel/activity.php">Activity Log</a>
        <a href="/panel/settings.php" class="active">Settings</a>
        <a href="/panel/logout.php">Sign Out</a>
    </nav>
</div>
<div class="admin-main">
    <div class="admin-topbar">
        <span>Welcome, <?php echo htmlspecialchars($_SESSION['admin_display_name']); ?></span>
        <span class="role-badge"><?php echo htmlspecialchars($_SESSION['admin_role']); ?></span>
    </div>
    <div class="admin-content">
        <h1>System Settings</h1>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Scope</th>
                    <th>Setting</th>
                    <th>Value</th>
                    <th>Updated</th>
                </tr>
            </thead>
            <tbody>
                <?php while ($s = $settings->fetch_assoc()): ?>
                <tr>
                    <td><?php echo htmlspecialchars($s['scope']); ?></td>
                    <td><?php echo htmlspecialchars($s['name']); ?></td>
                    <td><?php echo htmlspecialchars($s['value']); ?></td>
                    <td><?php echo htmlspecialchars($s['updated_at']); ?></td>
                </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
