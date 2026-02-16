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

$docCount = $conn->query("SELECT COUNT(*) as cnt FROM documents")->fetch_assoc()['cnt'];
$assetCount = $conn->query("SELECT COUNT(*) as cnt FROM assets")->fetch_assoc()['cnt'];
$userCount = $conn->query("SELECT COUNT(*) as cnt FROM users")->fetch_assoc()['cnt'];
$recentLogs = $conn->query("SELECT * FROM application_logs ORDER BY timestamp DESC LIMIT 5");

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Administration - Dashboard</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body class="admin-body">
<div class="admin-sidebar">
    <div class="sidebar-header">
        <h2>CMS Admin</h2>
    </div>
    <nav class="sidebar-nav">
        <a href="/panel/" class="active">Dashboard</a>
        <a href="/panel/documents.php">Documents</a>
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
        <h1>Dashboard</h1>
        <div class="stats-grid">
            <div class="stat-card">
                <h3><?php echo $docCount; ?></h3>
                <p>Documents</p>
            </div>
            <div class="stat-card">
                <h3><?php echo $assetCount; ?></h3>
                <p>Assets</p>
            </div>
            <div class="stat-card">
                <h3><?php echo $userCount; ?></h3>
                <p>Users</p>
            </div>
        </div>
        <h2>Recent Activity</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Severity</th>
                    <th>Component</th>
                    <th>Message</th>
                </tr>
            </thead>
            <tbody>
                <?php while ($log = $recentLogs->fetch_assoc()): ?>
                <tr>
                    <td><?php echo htmlspecialchars($log['timestamp']); ?></td>
                    <td><span class="severity-<?php echo strtolower($log['severity']); ?>"><?php echo htmlspecialchars($log['severity']); ?></span></td>
                    <td><?php echo htmlspecialchars($log['component']); ?></td>
                    <td><?php echo htmlspecialchars($log['message']); ?></td>
                </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
        <p><a href="/panel/activity.php">View all activity &rarr;</a></p>
    </div>
</div>
</body>
</html>
