<?php $pageTitle = 'System Report - Admin'; ?>
<?php include __DIR__ . '/../layouts/header.php'; ?>

<div class="admin-panel">
    <h2>System Report</h2>
    <p class="text-muted">Connected from: <?= htmlspecialchars($clientIP) ?></p>

    <div class="admin-nav">
        <a href="/admin" class="admin-link">Overview</a>
        <a href="/admin/config" class="admin-link">Configuration</a>
        <a href="/admin/report" class="admin-link active">System Report</a>
    </div>

    <div class="admin-content">
        <h3>Full System Report</h3>
        <table class="table report-table">
            <tr><td>Generated At</td><td><?= htmlspecialchars($report['generated_at']) ?></td></tr>
            <tr><td>Server Name</td><td><?= htmlspecialchars($report['server_name']) ?></td></tr>
            <tr><td>PHP Version</td><td><?= htmlspecialchars($report['php_version']) ?></td></tr>
            <tr><td>System Uptime</td><td><?= htmlspecialchars($report['uptime']) ?></td></tr>
            <tr><td>Memory Usage</td><td><?= htmlspecialchars($report['memory_usage']) ?></td></tr>
            <tr><td>Disk Usage</td><td><?= htmlspecialchars($report['disk_usage']) ?></td></tr>
            <tr><td>Active Sessions</td><td><?= htmlspecialchars($report['active_sessions']) ?></td></tr>
            <tr><td>Database Status</td><td><?= htmlspecialchars($report['db_status']) ?></td></tr>
            <tr><td>Last Backup</td><td><?= htmlspecialchars($report['last_backup']) ?></td></tr>
            <tr><td>System Encryption Key</td><td><code><?= htmlspecialchars($report['system_key']) ?></code></td></tr>
        </table>
    </div>
</div>

<?php include __DIR__ . '/../layouts/footer.php'; ?>
