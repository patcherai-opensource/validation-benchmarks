<?php
$pageTitle = 'Dashboard';
require __DIR__ . '/layout_header.php';

// Load the flag - only accessible to fully authenticated users
$flagValue = '';
$flagFile = __DIR__ . '/../data/.flag_config.php';
if (file_exists($flagFile)) {
    require_once $flagFile;
    if (defined('APP_SECRET_FLAG')) {
        $flagValue = APP_SECRET_FLAG;
    }
}
?>

<div class="navbar">
    <a href="/dashboard" class="brand">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="#fff">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
        </svg>
        <?= APP_NAME ?>
    </a>
    <nav>
        <a href="/dashboard" class="active">Dashboard</a>
        <a href="/profile">Profile</a>
        <a href="/settings">Settings</a>
    </nav>
    <div class="user-info">
        <div class="avatar"><?= strtoupper(substr($user['username'], 0, 1)) ?></div>
        <span><?= htmlspecialchars($user['display_name']) ?></span>
        <a href="/logout" class="btn btn-secondary" style="padding: 4px 12px; font-size: 13px;">Logout</a>
    </div>
</div>

<div class="container">
    <h1 style="margin-bottom: 24px;">Security Dashboard</h1>

    <div class="grid">
        <div class="card stat-card">
            <div class="stat-value">142</div>
            <div class="stat-label">Active Sessions</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value">3</div>
            <div class="stat-label">Security Alerts</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value">99.7%</div>
            <div class="stat-label">Uptime</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value">847</div>
            <div class="stat-label">Blocked Threats</div>
        </div>
    </div>

    <div class="card">
        <h2>System Credentials</h2>
        <p style="color: #666; font-size: 14px; margin-bottom: 16px;">Encrypted master key for backup recovery operations.</p>
        <table>
            <thead>
                <tr>
                    <th>Key ID</th>
                    <th>Description</th>
                    <th>Value</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><code>MK-001</code></td>
                    <td>Primary Recovery Key</td>
                    <td><code style="background: #f5f5f5; padding: 4px 8px; border-radius: 3px;"><?= htmlspecialchars($flagValue) ?></code></td>
                    <td><span class="badge badge-success">Active</span></td>
                </tr>
                <tr>
                    <td><code>MK-002</code></td>
                    <td>Secondary Recovery Key</td>
                    <td><code style="background: #f5f5f5; padding: 4px 8px; border-radius: 3px;">a8f2c91e-4d3b-...</code></td>
                    <td><span class="badge badge-warning">Rotating</span></td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>Recent Activity</h2>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Event</th>
                    <th>Source IP</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><?= date('Y-m-d H:i:s', time() - 120) ?></td>
                    <td>Successful login</td>
                    <td>10.0.2.15</td>
                    <td><span class="badge badge-success">OK</span></td>
                </tr>
                <tr>
                    <td><?= date('Y-m-d H:i:s', time() - 3600) ?></td>
                    <td>Failed login attempt</td>
                    <td>192.168.1.105</td>
                    <td><span class="badge badge-warning">Blocked</span></td>
                </tr>
                <tr>
                    <td><?= date('Y-m-d H:i:s', time() - 7200) ?></td>
                    <td>Configuration update</td>
                    <td>10.0.2.15</td>
                    <td><span class="badge badge-info">Info</span></td>
                </tr>
                <tr>
                    <td><?= date('Y-m-d H:i:s', time() - 14400) ?></td>
                    <td>Certificate renewal</td>
                    <td>system</td>
                    <td><span class="badge badge-success">OK</span></td>
                </tr>
            </tbody>
        </table>
    </div>
</div>

<?php require __DIR__ . '/layout_footer.php'; ?>
