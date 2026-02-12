<?php
require_once __DIR__ . '/includes/config.php';
require_once __DIR__ . '/includes/plugin_manager.php';

$pm = new PluginManager();
$plugins = $pm->loadPlugins();
$sysInfo = get_system_info();

$totalPlugins = count($plugins);
$activePlugins = count(array_filter($plugins, function($p) { return $p['status'] === 'STARTED'; }));
$disabledPlugins = $totalPlugins - $activePlugins;

require_once __DIR__ . '/includes/header.php';
?>
    <div class="container">
        <div class="page-header">
            <h1>Dashboard</h1>
            <a href="/upload.php" class="btn btn-primary">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                Install Plugin
            </a>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value"><?php echo $totalPlugins; ?></div>
                <div class="stat-label">Total Plugins</div>
            </div>
            <div class="stat-card">
                <div class="stat-value"><?php echo $activePlugins; ?></div>
                <div class="stat-label">Active</div>
            </div>
            <div class="stat-card">
                <div class="stat-value"><?php echo $disabledPlugins; ?></div>
                <div class="stat-label">Disabled</div>
            </div>
            <div class="stat-card">
                <div class="stat-value"><?php echo APP_VERSION; ?></div>
                <div class="stat-label">Runtime Version</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span>Installed Plugins</span>
                <a href="/plugins.php" class="btn btn-secondary btn-sm">View All</a>
            </div>
            <div class="card-body">
                <?php if (empty($plugins)): ?>
                    <p style="text-align:center; color:var(--text-light); padding: 32px;">
                        No plugins installed. <a href="/upload.php" style="color:var(--primary);">Install your first plugin</a>.
                    </p>
                <?php else: ?>
                    <table>
                        <thead>
                            <tr>
                                <th>Plugin ID</th>
                                <th>Version</th>
                                <th>Provider</th>
                                <th>Status</th>
                                <th>Installed</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($plugins as $plugin): ?>
                            <tr>
                                <td><strong><?php echo htmlspecialchars($plugin['name']); ?></strong></td>
                                <td><?php echo htmlspecialchars($plugin['version']); ?></td>
                                <td><?php echo htmlspecialchars($plugin['provider']); ?></td>
                                <td><span class="badge badge-success"><?php echo htmlspecialchars($plugin['status']); ?></span></td>
                                <td><?php echo htmlspecialchars($plugin['installed_at']); ?></td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                <?php endif; ?>
            </div>
        </div>
    </div>
<?php require_once __DIR__ . '/includes/footer.php'; ?>
