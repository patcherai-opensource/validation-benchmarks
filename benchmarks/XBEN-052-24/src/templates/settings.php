<?php $pageTitle = 'Settings'; ?>
<?php require __DIR__ . '/layout_header.php'; ?>

<div class="navbar">
    <a href="/dashboard" class="brand">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="#fff">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
        </svg>
        <?= APP_NAME ?>
    </a>
    <nav>
        <a href="/dashboard">Dashboard</a>
        <a href="/profile">Profile</a>
        <a href="/settings" class="active">Settings</a>
    </nav>
    <div class="user-info">
        <div class="avatar"><?= strtoupper(substr($user['username'], 0, 1)) ?></div>
        <span><?= htmlspecialchars($user['display_name']) ?></span>
        <a href="/logout" class="btn btn-secondary" style="padding: 4px 12px; font-size: 13px;">Logout</a>
    </div>
</div>

<div class="container">
    <h1 style="margin-bottom: 24px;">Application Settings</h1>

    <div class="card">
        <h2>Security Configuration</h2>
        <table>
            <tr><th style="width: 250px;">Session Timeout</th><td>30 minutes</td></tr>
            <tr><th>Max Login Attempts</th><td>5</td></tr>
            <tr><th>Password Policy</th><td>Minimum 12 characters, mixed case, special characters</td></tr>
            <tr><th>Two-Factor Enforcement</th><td><span class="badge badge-success">Required for admin & analyst roles</span></td></tr>
            <tr><th>Remember Me Duration</th><td>7 days</td></tr>
            <tr><th>IP Whitelist</th><td>Disabled</td></tr>
        </table>
    </div>

    <div class="card">
        <h2>Notification Preferences</h2>
        <table>
            <tr><th style="width: 250px;">Login Alerts</th><td><span class="badge badge-success">Enabled</span></td></tr>
            <tr><th>Security Event Digest</th><td><span class="badge badge-success">Daily</span></td></tr>
            <tr><th>Threat Intelligence Feed</th><td><span class="badge badge-warning">Weekly</span></td></tr>
        </table>
    </div>
</div>

<?php require __DIR__ . '/layout_footer.php'; ?>
