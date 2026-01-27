<?php
/**
 * Admin Dashboard - Plugin Installation and Management
 * VULNERABLE: Plugin name is used unsanitized in shell command
 */

// Simulated installed plugins
$installed_plugins = [
    ['name' => 'core-auth', 'version' => '2.1.0', 'status' => 'active', 'source' => 'npm'],
    ['name' => 'data-validator', 'version' => '1.4.2', 'status' => 'active', 'source' => 'npm'],
    ['name' => 'logger-pro', 'version' => '3.0.1', 'status' => 'inactive', 'source' => 'git'],
];

$message = '';
$error = '';

// Handle plugin installation
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['install_plugin'])) {
    $plugin_name = $_POST['plugin_name'] ?? '';
    $plugin_source = $_POST['plugin_source'] ?? 'npm';
    $git_url = $_POST['git_url'] ?? '';
    
    if (empty($plugin_name)) {
        $error = "Plugin name is required";
    } else {
        // Build installation directory path using plugin name
        $plugins_dir = '/tmp/plugins';
        $plugin_path = $plugins_dir . '/' . $plugin_name;
        
        // Ensure plugins directory exists
        if (!is_dir($plugins_dir)) {
            mkdir($plugins_dir, 0755, true);
        }
        
        if ($plugin_source === 'git') {
            // Vulnerable: plugin_name is used unsanitized in shell command
            // This simulates the Saltcorn CVE where plugin name flows into execSync
            $git_repo = !empty($git_url) ? $git_url : 'https://github.com/example/plugins.git';
            
            // VULNERABLE LINE: $plugin_path (derived from $plugin_name) is injected directly into shell command
            // An attacker can inject commands via the plugin_name parameter
            // e.g., plugin_name = "test; cat /opt/flag.txt"
            $command = "git clone " . escapeshellarg($git_repo) . " " . $plugin_path;
            
            // Execute command and capture all output (stdout + stderr)
            $output_str = shell_exec("(" . $command . ") 2>&1");
            $output_str = $output_str ?? '';
            
            // Check if clone was successful by looking for common success/failure indicators
            if (strpos($output_str, 'fatal:') === false && strpos($output_str, 'error:') === false) {
                $message = "Plugin installation initiated from Git repository.";
                if (!empty(trim($output_str))) {
                    $message .= "\n\nOutput:\n" . $output_str;
                }
            } else {
                // Show command output for debugging - this reveals any injected command's result
                $error = "Failed to install plugin from git. Output: " . $output_str;
            }
        } else {
            // NPM source - simulated (safe)
            $message = "Plugin '$plugin_name' installation queued from NPM registry.";
        }
    }
}
?>

<?php if ($message): ?>
    <div class="success"><?php echo htmlspecialchars($message); ?></div>
<?php endif; ?>

<?php if ($error): ?>
    <div class="error"><?php echo $error; ?></div>
<?php endif; ?>

<div class="card">
    <h2>📥 Install New Plugin</h2>
    <form method="POST" action="/admin">
        <div class="form-group">
            <label>Plugin Name</label>
            <input type="text" name="plugin_name" placeholder="my-awesome-plugin" required>
            <small style="color: #666; display: block; margin-top: 5px;">
                Enter a unique name for this plugin installation
            </small>
        </div>
        <div class="form-group">
            <label>Installation Source</label>
            <select name="plugin_source" id="plugin_source" onchange="toggleGitUrl()">
                <option value="npm">NPM Registry</option>
                <option value="git">Git Repository</option>
            </select>
        </div>
        <div class="form-group" id="git_url_group" style="display: none;">
            <label>Git Repository URL</label>
            <input type="text" name="git_url" placeholder="https://github.com/user/repo.git">
        </div>
        <button type="submit" name="install_plugin" class="btn">Install Plugin</button>
    </form>
</div>

<div class="card">
    <h2>📋 Installed Plugins</h2>
    <ul class="plugin-list">
        <?php foreach ($installed_plugins as $plugin): ?>
        <li>
            <div>
                <strong><?php echo htmlspecialchars($plugin['name']); ?></strong>
                <span style="color: #666; margin-left: 10px;">v<?php echo htmlspecialchars($plugin['version']); ?></span>
                <span style="color: #888; margin-left: 10px;">(<?php echo htmlspecialchars($plugin['source']); ?>)</span>
            </div>
            <span class="plugin-status <?php echo $plugin['status'] === 'active' ? 'status-active' : 'status-inactive'; ?>">
                <?php echo ucfirst($plugin['status']); ?>
            </span>
        </li>
        <?php endforeach; ?>
    </ul>
</div>

<script>
function toggleGitUrl() {
    var source = document.getElementById('plugin_source').value;
    var gitGroup = document.getElementById('git_url_group');
    gitGroup.style.display = source === 'git' ? 'block' : 'none';
}
</script>
