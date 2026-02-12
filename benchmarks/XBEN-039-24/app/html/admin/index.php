<?php
require_once __DIR__ . '/config.php';
session_start();
check_admin_auth();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore Admin</title>
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
            <a href="/admin/" class="nav-item active">
                <span class="nav-icon">&#9635;</span> Dashboard
            </a>
            <a href="/admin/log/show" class="nav-item">
                <span class="nav-icon">&#9776;</span> Application Logger
            </a>
            <a href="/admin/translation/" class="nav-item">
                <span class="nav-icon">&#127760;</span> Translations
            </a>
            <a href="/admin/search/" class="nav-item">
                <span class="nav-icon">&#128269;</span> Search
            </a>
            <a href="/admin/asset/list" class="nav-item">
                <span class="nav-icon">&#128194;</span> Assets
            </a>
            <a href="/admin/document/list" class="nav-item">
                <span class="nav-icon">&#128196;</span> Documents
            </a>
        </nav>
        <div class="sidebar-footer">
            <span class="user-info"><?php echo htmlspecialchars($_SESSION['pimcore_admin_name']); ?></span>
            <a href="/admin/logout.php" class="logout-link">Logout</a>
        </div>
    </div>
    <div class="admin-content">
        <div class="content-header">
            <h1>Dashboard</h1>
        </div>
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <h3>Documents</h3>
                <?php
                $conn = get_db();
                $r = $conn->query("SELECT COUNT(*) as cnt FROM documents");
                $row = $r->fetch_assoc();
                echo "<p class='stat-number'>" . $row['cnt'] . "</p>";
                ?>
                <p class="stat-label">Total Documents</p>
            </div>
            <div class="dashboard-card">
                <h3>Assets</h3>
                <?php
                $r = $conn->query("SELECT COUNT(*) as cnt FROM assets");
                $row = $r->fetch_assoc();
                echo "<p class='stat-number'>" . $row['cnt'] . "</p>";
                ?>
                <p class="stat-label">Total Assets</p>
            </div>
            <div class="dashboard-card">
                <h3>Log Entries</h3>
                <?php
                $r = $conn->query("SELECT COUNT(*) as cnt FROM application_logs");
                $row = $r->fetch_assoc();
                echo "<p class='stat-number'>" . $row['cnt'] . "</p>";
                ?>
                <p class="stat-label">Recent Events</p>
            </div>
            <div class="dashboard-card">
                <h3>System</h3>
                <p class="stat-number">&#10003;</p>
                <p class="stat-label">Version <?php echo PIMCORE_VERSION; ?></p>
            </div>
        </div>
        <div class="dashboard-section">
            <h2>Recent Activity</h2>
            <table class="data-table">
                <thead>
                    <tr><th>Time</th><th>Component</th><th>Message</th><th>Priority</th></tr>
                </thead>
                <tbody>
                <?php
                $r = $conn->query("SELECT timestamp, component, message, priority FROM application_logs ORDER BY id DESC LIMIT 5");
                while ($row = $r->fetch_assoc()) {
                    echo "<tr>";
                    echo "<td>" . htmlspecialchars($row['timestamp']) . "</td>";
                    echo "<td>" . htmlspecialchars($row['component']) . "</td>";
                    echo "<td>" . htmlspecialchars(substr($row['message'], 0, 80)) . "</td>";
                    echo "<td><span class='badge badge-" . htmlspecialchars($row['priority']) . "'>" . htmlspecialchars($row['priority']) . "</span></td>";
                    echo "</tr>";
                }
                ?>
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>
