<?php
/**
 * ModuLink - Plugin Management
 * Install plugins from various sources
 */

session_start();

if (!isset($_SESSION['user_id'])) {
    header('Location: /login.php?msg=unauthorized');
    exit;
}

if ($_SESSION['role'] !== 'admin') {
    header('Location: /login.php?msg=admin_required');
    exit;
}

$username = $_SESSION['username'];
$message = '';
$error = '';
$output = '';

// Plugin installation directory
$plugins_dir = '/var/www/html/plugins';
if (!is_dir($plugins_dir)) {
    mkdir($plugins_dir, 0755, true);
}

// Handle plugin installation
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    $action = $_POST['action'];
    
    if ($action === 'install_git') {
        $plugin_name = $_POST['plugin_name'] ?? '';
        $git_url = $_POST['git_url'] ?? '';
        
        if (empty($plugin_name) || empty($git_url)) {
            $error = 'Plugin name and Git URL are required.';
        } else {
            // Validate git URL format (basic check)
            if (!preg_match('/^https?:\/\//', $git_url)) {
                $error = 'Invalid Git URL format. Must start with http:// or https://';
            } else {
                // Create plugin directory path using plugin name
                // VULNERABLE: Plugin name is not properly sanitized before shell execution
                $plugin_dir = $plugins_dir . '/' . $plugin_name;
                
                // Log the installation attempt
                $log_file = '/var/www/html/logs/plugin_install.log';
                file_put_contents($log_file, date('Y-m-d H:i:s') . " - Installing plugin: $plugin_name from $git_url\n", FILE_APPEND);
                
                // Execute git clone command
                // VULNERABILITY: Command injection via plugin_name parameter
                $command = "cd " . $plugins_dir . " && git clone " . escapeshellarg($git_url) . " " . $plugin_name . " 2>&1";
                
                $result = shell_exec($command);
                
                if ($result !== null) {
                    $output = $result;
                    if (strpos($result, 'fatal:') !== false || strpos($result, 'error:') !== false) {
                        $error = 'Git clone failed. See output below.';
                    } else {
                        $message = "Plugin '$plugin_name' installation initiated successfully.";
                    }
                } else {
                    $error = 'Failed to execute installation command.';
                }
            }
        }
    } elseif ($action === 'install_npm') {
        $package_name = $_POST['package_name'] ?? '';
        
        if (empty($package_name)) {
            $error = 'Package name is required.';
        } else {
            // Sanitize npm package name properly
            $safe_package = preg_replace('/[^a-zA-Z0-9@\/_-]/', '', $package_name);
            $message = "NPM package '$safe_package' would be installed (demo mode).";
        }
    } elseif ($action === 'delete') {
        $plugin_to_delete = $_POST['plugin_name'] ?? '';
        if (!empty($plugin_to_delete)) {
            // Safely delete - only allow alphanumeric and dashes
            $safe_name = preg_replace('/[^a-zA-Z0-9_-]/', '', $plugin_to_delete);
            $target_path = $plugins_dir . '/' . $safe_name;
            if (is_dir($target_path) && strpos(realpath($target_path), realpath($plugins_dir)) === 0) {
                // In a real app, we would actually delete
                $message = "Plugin '$safe_name' would be deleted (demo mode).";
            } else {
                $error = 'Invalid plugin path.';
            }
        }
    }
}

// List installed plugins (mock data + real dirs)
$installed_plugins = [
    ['name' => 'analytics-core', 'version' => '2.1.0', 'source' => 'npm', 'status' => 'active'],
    ['name' => 'form-builder', 'version' => '1.8.3', 'source' => 'git', 'status' => 'active'],
];

// Check for actual plugin directories
if (is_dir($plugins_dir)) {
    $dirs = scandir($plugins_dir);
    foreach ($dirs as $dir) {
        if ($dir !== '.' && $dir !== '..' && is_dir($plugins_dir . '/' . $dir)) {
            $installed_plugins[] = [
                'name' => $dir,
                'version' => 'unknown',
                'source' => 'git',
                'status' => 'installed'
            ];
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plugin Management - ModuLink</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { background: #1e293b; padding: 15px 0; border-bottom: 1px solid #334155; }
        nav { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .logo { font-size: 1.5rem; font-weight: bold; color: #38bdf8; }
        .nav-links { display: flex; gap: 20px; }
        .nav-links a { color: #94a3b8; text-decoration: none; }
        .nav-links a:hover { color: #f8fafc; }
        .card { background: #1e293b; border-radius: 8px; padding: 20px; margin: 20px 0; border: 1px solid #334155; }
        .card h2 { color: #f8fafc; margin-bottom: 15px; }
        .btn { display: inline-block; padding: 10px 20px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; border: none; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #2563eb; }
        .btn-danger { background: #ef4444; }
        .btn-danger:hover { background: #dc2626; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #94a3b8; }
        .form-group input, .form-group select { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #334155; border-radius: 5px; color: #e2e8f0; }
        .form-group input:focus { outline: none; border-color: #3b82f6; }
        .alert { padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .alert-success { background: #166534; border: 1px solid #22c55e; }
        .alert-error { background: #991b1b; border: 1px solid #ef4444; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; }
        th { background: #0f172a; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab { padding: 10px 20px; background: #0f172a; border: 1px solid #334155; border-radius: 5px; cursor: pointer; color: #94a3b8; }
        .tab.active { background: #3b82f6; color: white; border-color: #3b82f6; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .output { background: #0f172a; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; color: #94a3b8; margin-top: 15px; max-height: 300px; overflow-y: auto; }
        .help-text { font-size: 12px; color: #64748b; margin-top: 5px; }
        footer { text-align: center; padding: 20px; color: #64748b; margin-top: 40px; }
    </style>
</head>
<body>
    <header>
        <nav>
            <div class="logo">ModuLink Admin</div>
            <div class="nav-links">
                <a href="/">Home</a>
                <a href="/dashboard.php">Dashboard</a>
                <a href="/admin/">Admin</a>
                <a href="/logout.php">Logout (<?php echo htmlspecialchars($username); ?>)</a>
            </div>
        </nav>
    </header>

    <div class="container">
        <h1 style="margin-bottom: 20px;">Plugin Management</h1>

        <?php if ($message): ?>
            <div class="alert alert-success"><?php echo htmlspecialchars($message); ?></div>
        <?php endif; ?>

        <?php if ($error): ?>
            <div class="alert alert-error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>

        <div class="card">
            <h2>Install New Plugin</h2>
            
            <div class="tabs">
                <div class="tab active" onclick="showTab('git')">From Git Repository</div>
                <div class="tab" onclick="showTab('npm')">From NPM</div>
                <div class="tab" onclick="showTab('marketplace')">Marketplace</div>
            </div>

            <div id="tab-git" class="tab-content active">
                <form method="POST">
                    <input type="hidden" name="action" value="install_git">
                    <div class="form-group">
                        <label for="plugin_name">Plugin Name</label>
                        <input type="text" id="plugin_name" name="plugin_name" placeholder="my-awesome-plugin" required>
                        <div class="help-text">Name for the plugin directory. Use only letters, numbers, and hyphens.</div>
                    </div>
                    <div class="form-group">
                        <label for="git_url">Git Repository URL</label>
                        <input type="text" id="git_url" name="git_url" placeholder="https://github.com/user/repo.git" required>
                        <div class="help-text">HTTPS URL to the Git repository.</div>
                    </div>
                    <button type="submit" class="btn">Install from Git</button>
                </form>
            </div>

            <div id="tab-npm" class="tab-content">
                <form method="POST">
                    <input type="hidden" name="action" value="install_npm">
                    <div class="form-group">
                        <label for="package_name">NPM Package Name</label>
                        <input type="text" id="package_name" name="package_name" placeholder="@scope/package-name" required>
                        <div class="help-text">Full npm package name including scope if applicable.</div>
                    </div>
                    <button type="submit" class="btn">Install from NPM</button>
                </form>
            </div>

            <div id="tab-marketplace" class="tab-content">
                <p style="color: #94a3b8;">Browse and install plugins from the ModuLink marketplace.</p>
                <div style="margin-top: 15px;">
                    <input type="text" placeholder="Search marketplace..." style="width: 100%; padding: 10px; background: #0f172a; border: 1px solid #334155; border-radius: 5px; color: #e2e8f0;">
                </div>
                <p style="color: #64748b; margin-top: 15px;">Marketplace integration coming soon...</p>
            </div>

            <?php if ($output): ?>
                <div class="output"><?php echo htmlspecialchars($output); ?></div>
            <?php endif; ?>
        </div>

        <div class="card">
            <h2>Installed Plugins</h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Version</th>
                        <th>Source</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($installed_plugins as $plugin): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($plugin['name']); ?></td>
                        <td><?php echo htmlspecialchars($plugin['version']); ?></td>
                        <td><?php echo strtoupper(htmlspecialchars($plugin['source'])); ?></td>
                        <td style="color: #22c55e;"><?php echo ucfirst(htmlspecialchars($plugin['status'])); ?></td>
                        <td>
                            <form method="POST" style="display: inline;">
                                <input type="hidden" name="action" value="delete">
                                <input type="hidden" name="plugin_name" value="<?php echo htmlspecialchars($plugin['name']); ?>">
                                <button type="submit" class="btn btn-danger" style="padding: 5px 10px; font-size: 12px;">Remove</button>
                            </form>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>

    <footer>
        <p>&copy; 2024 ModuLink v3.2.1. All rights reserved.</p>
    </footer>

    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
