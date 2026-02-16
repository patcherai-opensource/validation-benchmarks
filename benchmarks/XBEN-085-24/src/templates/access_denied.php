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
    <div class="user-info"><?php echo htmlspecialchars($username); ?></div>
</div>
<div class="container">
    <div class="card">
        <h2>Access Denied</h2>
        <div class="alert alert-danger">
            Your request was denied. System configuration is only accessible from authorized internal network addresses.
        </div>
        <table>
            <tr><th>Your IP Address</th><td><?php echo htmlspecialchars($clientIp); ?></td></tr>
            <tr><th>Required Network</th><td>Internal network (contact your administrator)</td></tr>
        </table>
        <p style="margin-top: 16px;">
            <a href="/console/overview" class="btn btn-primary">Back to Console</a>
        </p>
    </div>
</div>
<?php include __DIR__ . '/layout_footer.php'; ?>
