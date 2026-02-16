<?php include __DIR__ . '/layout_header.php'; ?>
<div class="navbar">
    <div class="brand"><span>&#9670;</span> Meridian Platform</div>
    <div class="nav-links">
        <a href="/">Dashboard</a>
        <a href="/console/overview">Console</a>
        <a href="/console/network" class="active">Network</a>
        <a href="/console/sysconfig">System Config</a>
        <a href="/logout">Sign Out</a>
    </div>
    <div class="user-info"><?php echo htmlspecialchars($username); ?> (<?php echo htmlspecialchars($role); ?>)</div>
</div>
<div class="container">
    <div class="sidebar-layout">
        <div class="sidebar card">
            <a href="/console/overview">Overview</a>
            <a href="/console/network" class="active">Network</a>
            <a href="/console/sysconfig">System Config</a>
        </div>
        <div class="main-content">
            <div class="card">
                <h2>Network Diagnostics</h2>
                <p>View network connectivity information and routing details.</p>
            </div>
            <div class="card">
                <h3>Connection Details</h3>
                <table>
                    <tr><th>Your IP Address</th><td><?php echo htmlspecialchars($clientIp); ?></td></tr>
                    <tr><th>Server Address</th><td><?php echo htmlspecialchars($_SERVER['SERVER_ADDR'] ?? 'N/A'); ?></td></tr>
                    <tr><th>Server Port</th><td><?php echo htmlspecialchars($_SERVER['SERVER_PORT'] ?? 'N/A'); ?></td></tr>
                    <tr><th>Protocol</th><td><?php echo htmlspecialchars($_SERVER['SERVER_PROTOCOL'] ?? 'N/A'); ?></td></tr>
                </table>
            </div>
            <div class="card">
                <h3>Active Interfaces</h3>
                <table>
                    <thead><tr><th>Interface</th><th>Address</th><th>Status</th></tr></thead>
                    <tbody>
                        <tr><td>eth0</td><td>10.20.30.50</td><td><span class="badge badge-success">UP</span></td></tr>
                        <tr><td>lo</td><td>127.0.0.1</td><td><span class="badge badge-success">UP</span></td></tr>
                    </tbody>
                </table>
            </div>
            <div class="alert alert-info">
                Access to System Configuration requires a connection from an authorized internal network address.
                Your current address is <strong><?php echo htmlspecialchars($clientIp); ?></strong>.
            </div>
        </div>
    </div>
</div>
<?php include __DIR__ . '/layout_footer.php'; ?>
