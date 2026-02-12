<?php $pageTitle = 'Admin Panel - Asset Management System'; ?>
<?php include __DIR__ . '/../layouts/header.php'; ?>

<div class="admin-panel">
    <h2>Administration Panel</h2>
    <p class="text-muted">Connected from: <?= htmlspecialchars($clientIP) ?></p>

    <div class="admin-nav">
        <a href="/admin" class="admin-link active">Overview</a>
        <a href="/admin/config" class="admin-link">Configuration</a>
        <a href="/admin/report" class="admin-link">System Report</a>
    </div>

    <div class="admin-content">
        <h3>System Overview</h3>
        <div class="dashboard-grid">
            <div class="stat-card">
                <h4>Registered Users</h4>
                <span class="stat-number">48</span>
            </div>
            <div class="stat-card">
                <h4>Active Sessions</h4>
                <span class="stat-number">12</span>
            </div>
            <div class="stat-card">
                <h4>Total Assets</h4>
                <span class="stat-number">1,247</span>
            </div>
            <div class="stat-card">
                <h4>System Alerts</h4>
                <span class="stat-number">3</span>
            </div>
        </div>
    </div>
</div>

<?php include __DIR__ . '/../layouts/footer.php'; ?>
