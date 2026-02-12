<?php
require_once __DIR__ . '/includes/config.php';
$sysInfo = get_system_info();

require_once __DIR__ . '/includes/header.php';
?>
    <div class="container">
        <div class="page-header">
            <h1>System Information</h1>
        </div>

        <div class="card" style="margin-bottom: 16px;">
            <div class="card-header">Runtime Environment</div>
            <div class="card-body">
                <table>
                    <tr><td style="font-weight:500; width:200px;">Runtime Version</td><td><?php echo htmlspecialchars($sysInfo['runtime_version']); ?></td></tr>
                    <tr><td style="font-weight:500;">PHP Version</td><td><?php echo htmlspecialchars($sysInfo['php_version']); ?></td></tr>
                    <tr><td style="font-weight:500;">Operating System</td><td><?php echo htmlspecialchars($sysInfo['os']); ?></td></tr>
                    <tr><td style="font-weight:500;">Plugins Directory</td><td><?php echo htmlspecialchars($sysInfo['plugins_directory']); ?></td></tr>
                    <tr><td style="font-weight:500;">Max Upload Size</td><td><?php echo htmlspecialchars($sysInfo['upload_max']); ?></td></tr>
                </table>
            </div>
        </div>

        <div class="card" style="margin-bottom: 16px;">
            <div class="card-header">Extensions</div>
            <div class="card-body">
                <table>
                    <thead>
                        <tr><th>Extension Point</th><th>Type</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>org.pf4j.ExtensionPoint</td><td>Interface</td><td><span class="badge badge-success">Available</span></td></tr>
                        <tr><td>org.pf4j.Plugin</td><td>Abstract Class</td><td><span class="badge badge-success">Available</span></td></tr>
                        <tr><td>org.pf4j.PluginWrapper</td><td>Class</td><td><span class="badge badge-success">Available</span></td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <div class="card-header">Plugin Repositories</div>
            <div class="card-body">
                <table>
                    <thead>
                        <tr><th>Repository</th><th>Path</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>DefaultPluginRepository</td><td><?php echo htmlspecialchars(PLUGINS_DIR); ?></td><td><span class="badge badge-success">Active</span></td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
<?php require_once __DIR__ . '/includes/footer.php'; ?>
