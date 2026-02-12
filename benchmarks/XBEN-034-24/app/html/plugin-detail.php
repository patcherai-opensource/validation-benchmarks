<?php
require_once __DIR__ . '/includes/config.php';
require_once __DIR__ . '/includes/plugin_manager.php';

$pm = new PluginManager();
$pluginId = isset($_GET['id']) ? $_GET['id'] : '';
$plugin = $pm->getPluginInfo($pluginId);

if (!$plugin) {
    header('HTTP/1.1 404 Not Found');
    require_once __DIR__ . '/includes/header.php';
    echo '<div class="container"><div class="alert alert-error">Plugin not found.</div></div>';
    require_once __DIR__ . '/includes/footer.php';
    exit;
}

require_once __DIR__ . '/includes/header.php';
?>
    <div class="container">
        <div class="page-header">
            <h1><?php echo htmlspecialchars($plugin['name']); ?></h1>
            <span class="badge badge-success"><?php echo htmlspecialchars($plugin['status']); ?></span>
        </div>

        <div class="card" style="margin-bottom: 16px;">
            <div class="card-header">Plugin Details</div>
            <div class="card-body">
                <table>
                    <tr><td style="font-weight:500; width:180px;">Plugin ID</td><td><?php echo htmlspecialchars($plugin['name']); ?></td></tr>
                    <tr><td style="font-weight:500;">Version</td><td><?php echo htmlspecialchars($plugin['version']); ?></td></tr>
                    <tr><td style="font-weight:500;">Provider</td><td><?php echo htmlspecialchars($plugin['provider']); ?></td></tr>
                    <tr><td style="font-weight:500;">Description</td><td><?php echo htmlspecialchars($plugin['description']); ?></td></tr>
                    <tr><td style="font-weight:500;">Class</td><td><?php echo htmlspecialchars($plugin['class']); ?></td></tr>
                    <tr><td style="font-weight:500;">Requires</td><td><?php echo htmlspecialchars($plugin['requires']); ?></td></tr>
                    <tr><td style="font-weight:500;">License</td><td><?php echo htmlspecialchars($plugin['license']); ?></td></tr>
                </table>
            </div>
        </div>

        <div class="card">
            <div class="card-header">Plugin Files</div>
            <div class="card-body">
                <?php if (empty($plugin['files'])): ?>
                    <p style="color: var(--text-light);">No files found.</p>
                <?php else: ?>
                    <div class="log-output"><?php
                        foreach ($plugin['files'] as $f) {
                            echo htmlspecialchars($f) . "\n";
                        }
                    ?></div>
                <?php endif; ?>
            </div>
        </div>

        <div style="margin-top: 16px;">
            <a href="/plugins.php" class="btn btn-secondary">Back to Plugins</a>
        </div>
    </div>
<?php require_once __DIR__ . '/includes/footer.php'; ?>
