<?php $pageTitle = 'Dashboard - Asset Management System'; ?>
<?php include __DIR__ . '/layouts/header.php'; ?>

<div class="dashboard">
    <h2>Welcome, <?= htmlspecialchars($username) ?></h2>
    <p class="text-muted">Your session IP: <?= htmlspecialchars($clientIP) ?></p>

    <div class="dashboard-grid">
        <div class="stat-card">
            <h4>Total Assets</h4>
            <span class="stat-number">1,247</span>
        </div>
        <div class="stat-card">
            <h4>Active Licenses</h4>
            <span class="stat-number">342</span>
        </div>
        <div class="stat-card">
            <h4>Pending Reviews</h4>
            <span class="stat-number">18</span>
        </div>
        <div class="stat-card">
            <h4>Alerts</h4>
            <span class="stat-number">5</span>
        </div>
    </div>

    <div class="recent-activity">
        <h3>Recent Activity</h3>
        <table class="table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Action</th>
                    <th>Asset</th>
                    <th>User</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>2024-01-15</td><td>Updated</td><td>Server #A-1042</td><td>jsmith</td></tr>
                <tr><td>2024-01-15</td><td>Added</td><td>Laptop #L-2891</td><td>mwilson</td></tr>
                <tr><td>2024-01-14</td><td>Retired</td><td>Switch #N-0433</td><td>alee</td></tr>
                <tr><td>2024-01-14</td><td>Updated</td><td>License #S-0091</td><td>jsmith</td></tr>
                <tr><td>2024-01-13</td><td>Added</td><td>Monitor #D-1553</td><td>bchen</td></tr>
            </tbody>
        </table>
    </div>

    <p><a href="/logout" class="btn btn-secondary">Sign Out</a></p>
</div>

<?php include __DIR__ . '/layouts/footer.php'; ?>
