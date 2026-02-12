<?php $pageTitle = 'System Configuration - Admin'; ?>
<?php include __DIR__ . '/../layouts/header.php'; ?>

<div class="admin-panel">
    <h2>System Configuration</h2>
    <p class="text-muted">Connected from: <?= htmlspecialchars($clientIP) ?></p>

    <div class="admin-nav">
        <a href="/admin" class="admin-link">Overview</a>
        <a href="/admin/config" class="admin-link active">Configuration</a>
        <a href="/admin/report" class="admin-link">System Report</a>
    </div>

    <div class="admin-content">
        <h3>Application Settings</h3>
        <table class="table">
            <tr><td>Application Name</td><td>Asset Management System</td></tr>
            <tr><td>Version</td><td>4.2.10</td></tr>
            <tr><td>Environment</td><td>production</td></tr>
            <tr><td>Debug Mode</td><td>Disabled</td></tr>
            <tr><td>Session Lifetime</td><td>7200 seconds</td></tr>
            <tr><td>CSRF Protection</td><td>Disabled</td></tr>
        </table>

        <h3>Network Settings</h3>
        <table class="table">
            <tr><td>Trusted Proxies</td><td>10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16</td></tr>
            <tr><td>Admin IP Whitelist</td><td>127.0.0.1, 10.0.0.1, 192.168.1.1, 172.16.0.1</td></tr>
        </table>
    </div>
</div>

<?php include __DIR__ . '/../layouts/footer.php'; ?>
