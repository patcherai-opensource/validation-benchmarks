<?php
require_once __DIR__ . '/includes/config.php';
require_once __DIR__ . '/includes/plugin_manager.php';

$pm = new PluginManager();

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    header('Content-Type: application/json');
    if ($_POST['action'] === 'uninstall' && isset($_POST['plugin_id'])) {
        $result = $pm->uninstallPlugin($_POST['plugin_id']);
        echo json_encode($result);
        exit;
    }
}

$plugins = $pm->loadPlugins();

require_once __DIR__ . '/includes/header.php';
?>
    <div class="container">
        <div class="page-header">
            <h1>Installed Plugins</h1>
            <a href="/upload.php" class="btn btn-primary">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                Install Plugin
            </a>
        </div>

        <?php if (empty($plugins)): ?>
            <div class="card">
                <div class="card-body" style="text-align:center; padding: 48px;">
                    <svg width="64" height="64" viewBox="0 0 64 64" fill="none" style="margin-bottom:16px; color:var(--text-light);">
                        <rect x="8" y="8" width="48" height="48" rx="8" stroke="currentColor" stroke-width="2"/>
                        <path d="M24 32h16M32 24v16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <h3 style="margin-bottom: 8px; color: var(--text-light);">No plugins installed</h3>
                    <p style="color: var(--text-light); margin-bottom: 16px;">Get started by installing your first plugin package.</p>
                    <a href="/upload.php" class="btn btn-primary">Install Plugin</a>
                </div>
            </div>
        <?php else: ?>
            <div class="plugin-grid">
                <?php foreach ($plugins as $plugin): ?>
                <div class="plugin-card">
                    <div class="plugin-header">
                        <h3><?php echo htmlspecialchars($plugin['name']); ?></h3>
                        <span class="version">v<?php echo htmlspecialchars($plugin['version']); ?></span>
                    </div>
                    <p class="description"><?php echo htmlspecialchars($plugin['description']); ?></p>
                    <div class="plugin-meta">
                        <span>Provider: <?php echo htmlspecialchars($plugin['provider']); ?></span>
                        <span>License: <?php echo htmlspecialchars($plugin['license']); ?></span>
                        <span class="badge badge-success"><?php echo htmlspecialchars($plugin['status']); ?></span>
                    </div>
                    <div style="margin-top: 12px; display: flex; gap: 8px;">
                        <a href="/plugin-detail.php?id=<?php echo urlencode($plugin['id']); ?>" class="btn btn-secondary btn-sm">Details</a>
                        <form method="POST" style="display:inline;" onsubmit="return confirm('Uninstall this plugin?');">
                            <input type="hidden" name="action" value="uninstall">
                            <input type="hidden" name="plugin_id" value="<?php echo htmlspecialchars($plugin['id']); ?>">
                            <button type="submit" class="btn btn-danger btn-sm">Uninstall</button>
                        </form>
                    </div>
                </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </div>
<?php require_once __DIR__ . '/includes/footer.php'; ?>
