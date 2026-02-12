<?php $pageTitle = 'Settings'; include __DIR__ . '/header.php'; ?>
<div class="admin-wrapper">
    <?php include __DIR__ . '/admin_sidebar.php'; ?>
    <div class="admin-main">
        <h1>Site Settings</h1>
        <div class="card">
            <h3>General Configuration</h3>
            <table>
                <tr><th>Setting</th><th>Value</th></tr>
                <tr><td>Site Title</td><td><?php echo htmlspecialchars($config['Title']); ?></td></tr>
                <tr><td>Tagline</td><td><?php echo htmlspecialchars($config['Tagline']); ?></td></tr>
                <tr><td>Theme</td><td><?php echo htmlspecialchars($config['Theme']); ?></td></tr>
                <tr><td>PHP Version</td><td><?php echo phpversion(); ?></td></tr>
                <tr><td>CMS Version</td><td>SilverStripe 3.1.13</td></tr>
            </table>
        </div>
    </div>
</div>
<?php include __DIR__ . '/footer.php'; ?>