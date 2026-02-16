<?php include __DIR__ . '/layout_header.php'; ?>
<div class="navbar">
    <div class="brand"><span>&#9670;</span> Meridian Platform</div>
    <div class="nav-links">
        <a href="/">Dashboard</a>
        <a href="/console/overview">Console</a>
        <a href="/console/network">Network</a>
        <a href="/console/sysconfig" class="active">System Config</a>
        <a href="/logout">Sign Out</a>
    </div>
    <div class="user-info"><?php echo htmlspecialchars($username); ?> (<?php echo htmlspecialchars($role); ?>)</div>
</div>
<div class="container">
    <div class="sidebar-layout">
        <div class="sidebar card">
            <a href="/console/overview">Overview</a>
            <a href="/console/network">Network</a>
            <a href="/console/sysconfig" class="active">System Config</a>
        </div>
        <div class="main-content">
            <div class="card">
                <h2>System Configuration</h2>
                <p>Internal system configuration data. Access restricted to authorized network locations.</p>
            </div>
            <div class="card">
                <h3>Access Verification</h3>
                <table>
                    <tr><th>Client Address</th><td><?php echo htmlspecialchars($clientIp); ?></td></tr>
                    <tr><th>Access Status</th><td><span class="badge badge-success">Authorized</span></td></tr>
                    <tr><th>User</th><td><?php echo htmlspecialchars($username); ?> (<?php echo htmlspecialchars($role); ?>)</td></tr>
                </table>
            </div>
            <div class="card">
                <h3>System Secrets</h3>
                <div class="config-block"><?php echo htmlspecialchars($secrets); ?></div>
            </div>
        </div>
    </div>
</div>
<?php include __DIR__ . '/layout_footer.php'; ?>
