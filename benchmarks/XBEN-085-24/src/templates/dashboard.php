<?php include __DIR__ . '/layout_header.php'; ?>
<div class="navbar">
    <div class="brand"><span>&#9670;</span> Meridian Platform</div>
    <div class="nav-links">
        <a href="/" class="active">Dashboard</a>
        <a href="/console/overview">Console</a>
        <a href="/console/network">Network</a>
        <a href="/console/sysconfig">System Config</a>
        <a href="/logout">Sign Out</a>
    </div>
    <div class="user-info"><?php echo htmlspecialchars($username); ?> (<?php echo htmlspecialchars($role); ?>)</div>
</div>
<div class="container">
    <div class="card">
        <h2>Welcome, <?php echo htmlspecialchars($username); ?></h2>
        <p>You are signed in to <?php echo htmlspecialchars($appName); ?> management console.</p>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
        <div class="card">
            <h3>Services</h3>
            <p style="font-size: 28px; font-weight: 700; color: #27ae60; margin: 8px 0;">12</p>
            <p>Active services</p>
        </div>
        <div class="card">
            <h3>Nodes</h3>
            <p style="font-size: 28px; font-weight: 700; color: #3498db; margin: 8px 0;">8</p>
            <p>Connected nodes</p>
        </div>
        <div class="card">
            <h3>Alerts</h3>
            <p style="font-size: 28px; font-weight: 700; color: #e67e22; margin: 8px 0;">2</p>
            <p>Pending alerts</p>
        </div>
    </div>
    <div class="card">
        <h3>Recent Activity</h3>
        <table>
            <thead>
                <tr><th>Time</th><th>Event</th><th>Status</th></tr>
            </thead>
            <tbody>
                <tr><td><?php echo date('H:i:s', time() - 120); ?></td><td>Health check completed</td><td><span class="badge badge-success">OK</span></td></tr>
                <tr><td><?php echo date('H:i:s', time() - 340); ?></td><td>Certificate rotation</td><td><span class="badge badge-success">OK</span></td></tr>
                <tr><td><?php echo date('H:i:s', time() - 890); ?></td><td>Backup job (daily)</td><td><span class="badge badge-success">OK</span></td></tr>
                <tr><td><?php echo date('H:i:s', time() - 2100); ?></td><td>Config sync to node-03</td><td><span class="badge badge-warning">Delayed</span></td></tr>
            </tbody>
        </table>
    </div>
</div>
<?php include __DIR__ . '/layout_footer.php'; ?>
