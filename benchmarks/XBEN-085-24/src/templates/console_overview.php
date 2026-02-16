<?php include __DIR__ . '/layout_header.php'; ?>
<div class="navbar">
    <div class="brand"><span>&#9670;</span> Meridian Platform</div>
    <div class="nav-links">
        <a href="/">Dashboard</a>
        <a href="/console/overview" class="active">Console</a>
        <a href="/console/network">Network</a>
        <a href="/console/sysconfig">System Config</a>
        <a href="/logout">Sign Out</a>
    </div>
    <div class="user-info"><?php echo htmlspecialchars($username); ?> (<?php echo htmlspecialchars($role); ?>)</div>
</div>
<div class="container">
    <div class="sidebar-layout">
        <div class="sidebar card">
            <a href="/console/overview" class="active">Overview</a>
            <a href="/console/network">Network</a>
            <a href="/console/sysconfig">System Config</a>
        </div>
        <div class="main-content">
            <div class="card">
                <h2>Console Overview</h2>
                <p>System management console for <?php echo htmlspecialchars($appName); ?>.</p>
            </div>
            <div class="card">
                <h3>Session Information</h3>
                <table>
                    <tr><th>Authenticated User</th><td><?php echo htmlspecialchars($username); ?></td></tr>
                    <tr><th>Role</th><td><?php echo htmlspecialchars($role); ?></td></tr>
                    <tr><th>Client IP</th><td><?php echo htmlspecialchars($clientIp); ?></td></tr>
                    <tr><th>Server Time</th><td><?php echo date('Y-m-d H:i:s T'); ?></td></tr>
                </table>
            </div>
            <div class="card">
                <h3>System Resources</h3>
                <table>
                    <tr><th>CPU Usage</th><td>23%</td></tr>
                    <tr><th>Memory</th><td>412 MB / 2048 MB</td></tr>
                    <tr><th>Disk</th><td>14.2 GB / 50 GB</td></tr>
                    <tr><th>Load Average</th><td>0.42, 0.38, 0.31</td></tr>
                </table>
            </div>
        </div>
    </div>
</div>
<?php include __DIR__ . '/layout_footer.php'; ?>
