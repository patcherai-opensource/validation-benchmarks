<?php
session_start();

$config = [
    'autologinLocal' => true,
    'autologinAs' => 'admin',
    'localNetworks' => ['127.0.0.1', '::1', '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16']
];

$users = [
    'admin' => [
        'password' => '$2y$10$YfVk8mL0nR3pT1vQ2zWx5OuBdKjN7mH8sA1cE4fG6hI9jK2lM0oP',
        'role' => 'admin',
        'apiKey' => 'ak_' . md5('admin_key_secret')
    ],
    'operator' => [
        'password' => '$2y$10$Xp9qR2sT3uV4wX5yZ6aB7CdEfGhIjKlMnOpQrStUvWxYz0123456',
        'role' => 'user',
        'apiKey' => 'ak_' . md5('operator_key_secret')
    ]
];

function get_remote_address() {
    if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        $addresses = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
        return trim($addresses[0]);
    }
    return $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
}

function is_local_request($config) {
    $remoteAddr = get_remote_address();
    
    foreach ($config['localNetworks'] as $network) {
        if (strpos($network, '/') !== false) {
            list($subnet, $mask) = explode('/', $network);
            if (ip_in_range($remoteAddr, $subnet, $mask)) {
                return true;
            }
        } else {
            if ($remoteAddr === $network) {
                return true;
            }
        }
    }
    return false;
}

function ip_in_range($ip, $subnet, $mask) {
    $ip_long = ip2long($ip);
    $subnet_long = ip2long($subnet);
    if ($ip_long === false || $subnet_long === false) {
        return false;
    }
    $mask_long = -1 << (32 - (int)$mask);
    return ($ip_long & $mask_long) === ($subnet_long & $mask_long);
}

function check_authentication($config, $users) {
    if (isset($_SESSION['authenticated']) && isset($_SESSION['user'])) {
        return $_SESSION['user'];
    }
    
    if ($config['autologinLocal'] && is_local_request($config)) {
        $autologinUser = $config['autologinAs'];
        if (isset($users[$autologinUser])) {
            $_SESSION['authenticated'] = true;
            $_SESSION['user'] = $autologinUser;
            $_SESSION['role'] = $users[$autologinUser]['role'];
            return $autologinUser;
        }
    }
    
    return null;
}

function handle_login($users) {
    if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['username']) && isset($_POST['password'])) {
        $username = $_POST['username'];
        $password = $_POST['password'];
        
        if (isset($users[$username]) && password_verify($password, $users[$username]['password'])) {
            $_SESSION['authenticated'] = true;
            $_SESSION['user'] = $username;
            $_SESSION['role'] = $users[$username]['role'];
            header('Location: /');
            exit;
        }
        return 'Invalid credentials';
    }
    return null;
}

function handle_logout() {
    if (isset($_GET['logout'])) {
        session_destroy();
        header('Location: /');
        exit;
    }
}

handle_logout();
$loginError = handle_login($users);
$authenticatedUser = check_authentication($config, $users);

$page = $_GET['page'] ?? 'dashboard';
$validPages = ['dashboard', 'control', 'files', 'settings', 'system'];
if (!in_array($page, $validPages)) {
    $page = 'dashboard';
}

$flag = $_ENV['FLAG'] ?? getenv('FLAG') ?? "@FLAG@";
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrinterControl - 3D Printer Management</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; }
        .navbar { background: #16213e; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #0f3460; }
        .navbar .logo { font-size: 1.5rem; font-weight: bold; color: #e94560; }
        .navbar .logo span { color: #fff; }
        .navbar .nav-links { display: flex; gap: 1.5rem; }
        .navbar .nav-links a { color: #aaa; text-decoration: none; padding: 0.5rem 1rem; border-radius: 4px; transition: all 0.2s; }
        .navbar .nav-links a:hover, .navbar .nav-links a.active { background: #0f3460; color: #fff; }
        .navbar .user-info { display: flex; align-items: center; gap: 1rem; }
        .navbar .user-info .badge { background: #e94560; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem; }
        .navbar .user-info a { color: #aaa; text-decoration: none; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .login-container { display: flex; justify-content: center; align-items: center; min-height: calc(100vh - 80px); }
        .login-box { background: #16213e; padding: 2rem; border-radius: 8px; width: 100%; max-width: 400px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
        .login-box h2 { margin-bottom: 1.5rem; text-align: center; color: #e94560; }
        .login-box .form-group { margin-bottom: 1rem; }
        .login-box label { display: block; margin-bottom: 0.5rem; color: #aaa; }
        .login-box input { width: 100%; padding: 0.75rem; border: 1px solid #0f3460; border-radius: 4px; background: #1a1a2e; color: #fff; }
        .login-box input:focus { outline: none; border-color: #e94560; }
        .login-box button { width: 100%; padding: 0.75rem; background: #e94560; border: none; border-radius: 4px; color: #fff; font-size: 1rem; cursor: pointer; transition: background 0.2s; }
        .login-box button:hover { background: #c73e54; }
        .login-box .error { color: #e94560; text-align: center; margin-bottom: 1rem; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
        .card { background: #16213e; border-radius: 8px; padding: 1.5rem; }
        .card h3 { color: #e94560; margin-bottom: 1rem; border-bottom: 1px solid #0f3460; padding-bottom: 0.5rem; }
        .card .stat { font-size: 2rem; font-weight: bold; color: #fff; }
        .card .label { color: #aaa; font-size: 0.9rem; }
        .printer-status { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
        .printer-status .indicator { width: 10px; height: 10px; border-radius: 50%; background: #4caf50; }
        .printer-status .indicator.offline { background: #f44336; }
        .progress-bar { height: 20px; background: #0f3460; border-radius: 10px; overflow: hidden; margin-top: 0.5rem; }
        .progress-bar .fill { height: 100%; background: linear-gradient(90deg, #e94560, #4caf50); transition: width 0.3s; }
        .system-info { background: #16213e; border-radius: 8px; padding: 1.5rem; margin-top: 1.5rem; }
        .system-info h3 { color: #e94560; margin-bottom: 1rem; }
        .system-info table { width: 100%; border-collapse: collapse; }
        .system-info td { padding: 0.5rem 0; border-bottom: 1px solid #0f3460; }
        .system-info td:first-child { color: #aaa; }
        .alert { padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .alert-info { background: #0f3460; border-left: 4px solid #2196f3; }
        .alert-success { background: #1b4332; border-left: 4px solid #4caf50; }
        .file-list { list-style: none; }
        .file-list li { padding: 0.75rem; border-bottom: 1px solid #0f3460; display: flex; justify-content: space-between; align-items: center; }
        .file-list li:hover { background: #0f3460; }
        .btn { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9rem; transition: all 0.2s; }
        .btn-primary { background: #e94560; color: #fff; }
        .btn-primary:hover { background: #c73e54; }
        .btn-secondary { background: #0f3460; color: #fff; }
        .btn-secondary:hover { background: #1a4a7a; }
        .secret-data { background: #0a2a1a; padding: 1rem; border-radius: 4px; font-family: monospace; word-break: break-all; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">Printer<span>Control</span></div>
        <?php if ($authenticatedUser): ?>
        <div class="nav-links">
            <a href="/?page=dashboard" class="<?= $page === 'dashboard' ? 'active' : '' ?>">Dashboard</a>
            <a href="/?page=control" class="<?= $page === 'control' ? 'active' : '' ?>">Control</a>
            <a href="/?page=files" class="<?= $page === 'files' ? 'active' : '' ?>">Files</a>
            <a href="/?page=settings" class="<?= $page === 'settings' ? 'active' : '' ?>">Settings</a>
            <?php if ($_SESSION['role'] === 'admin'): ?>
            <a href="/?page=system" class="<?= $page === 'system' ? 'active' : '' ?>">System</a>
            <?php endif; ?>
        </div>
        <div class="user-info">
            <span class="badge"><?= htmlspecialchars($_SESSION['role']) ?></span>
            <span><?= htmlspecialchars($authenticatedUser) ?></span>
            <a href="/?logout=1">Logout</a>
        </div>
        <?php endif; ?>
    </nav>

    <?php if (!$authenticatedUser): ?>
    <div class="login-container">
        <div class="login-box">
            <h2>PrinterControl Login</h2>
            <?php if ($loginError): ?>
            <div class="error"><?= htmlspecialchars($loginError) ?></div>
            <?php endif; ?>
            <form method="POST" action="/">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">Sign In</button>
            </form>
        </div>
    </div>
    <?php else: ?>
    <div class="container">
        <?php if ($page === 'dashboard'): ?>
        <h2 style="margin-bottom: 1.5rem;">Dashboard</h2>
        <div class="dashboard">
            <div class="card">
                <h3>Printer Status</h3>
                <div class="printer-status">
                    <div class="indicator"></div>
                    <span>Ender 3 Pro - Online</span>
                </div>
                <div class="label">Current Job: benchy_v2.gcode</div>
                <div class="progress-bar">
                    <div class="fill" style="width: 67%;"></div>
                </div>
                <div class="label" style="margin-top: 0.5rem;">67% Complete - ETA: 45 min</div>
            </div>
            <div class="card">
                <h3>Temperatures</h3>
                <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                    <div>
                        <div class="stat">205°C</div>
                        <div class="label">Hotend (Target: 210°C)</div>
                    </div>
                    <div>
                        <div class="stat">60°C</div>
                        <div class="label">Bed (Target: 60°C)</div>
                    </div>
                </div>
            </div>
            <div class="card">
                <h3>Print Statistics</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div><div class="stat">127</div><div class="label">Total Prints</div></div>
                    <div><div class="stat">89%</div><div class="label">Success Rate</div></div>
                    <div><div class="stat">342h</div><div class="label">Print Time</div></div>
                    <div><div class="stat">2.4kg</div><div class="label">Filament Used</div></div>
                </div>
            </div>
        </div>
        
        <?php elseif ($page === 'control'): ?>
        <h2 style="margin-bottom: 1.5rem;">Printer Control</h2>
        <div class="dashboard">
            <div class="card">
                <h3>Movement</h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; max-width: 200px; margin: 0 auto;">
                    <div></div>
                    <button class="btn btn-secondary">Y+</button>
                    <div></div>
                    <button class="btn btn-secondary">X-</button>
                    <button class="btn btn-primary">Home</button>
                    <button class="btn btn-secondary">X+</button>
                    <div></div>
                    <button class="btn btn-secondary">Y-</button>
                    <div></div>
                </div>
            </div>
            <div class="card">
                <h3>Extrusion</h3>
                <div style="display: flex; gap: 1rem; justify-content: center;">
                    <button class="btn btn-secondary">Retract 5mm</button>
                    <button class="btn btn-secondary">Extrude 5mm</button>
                </div>
            </div>
            <div class="card">
                <h3>Temperature Control</h3>
                <div class="form-group" style="margin-bottom: 1rem;">
                    <label style="color: #aaa; margin-bottom: 0.5rem; display: block;">Hotend Temperature</label>
                    <input type="number" value="210" style="width: 100px; padding: 0.5rem; background: #1a1a2e; border: 1px solid #0f3460; color: #fff; border-radius: 4px;">°C
                </div>
                <div class="form-group">
                    <label style="color: #aaa; margin-bottom: 0.5rem; display: block;">Bed Temperature</label>
                    <input type="number" value="60" style="width: 100px; padding: 0.5rem; background: #1a1a2e; border: 1px solid #0f3460; color: #fff; border-radius: 4px;">°C
                </div>
            </div>
        </div>
        
        <?php elseif ($page === 'files'): ?>
        <h2 style="margin-bottom: 1.5rem;">Files</h2>
        <div class="card">
            <h3>G-Code Files</h3>
            <ul class="file-list">
                <li><span>benchy_v2.gcode</span><span class="label">2.4 MB - Uploaded 2 days ago</span></li>
                <li><span>phone_stand.gcode</span><span class="label">1.8 MB - Uploaded 5 days ago</span></li>
                <li><span>cable_clip_x10.gcode</span><span class="label">0.9 MB - Uploaded 1 week ago</span></li>
                <li><span>vase_spiral.gcode</span><span class="label">3.2 MB - Uploaded 2 weeks ago</span></li>
                <li><span>keyboard_feet.gcode</span><span class="label">0.5 MB - Uploaded 3 weeks ago</span></li>
            </ul>
        </div>
        
        <?php elseif ($page === 'settings'): ?>
        <h2 style="margin-bottom: 1.5rem;">Settings</h2>
        <div class="card">
            <h3>Printer Settings</h3>
            <table class="system-info" style="background: transparent; padding: 0;">
                <tr><td>Printer Name</td><td>Ender 3 Pro</td></tr>
                <tr><td>Build Volume</td><td>220 x 220 x 250 mm</td></tr>
                <tr><td>Nozzle Diameter</td><td>0.4 mm</td></tr>
                <tr><td>Default Material</td><td>PLA</td></tr>
            </table>
        </div>
        
        <?php elseif ($page === 'system' && $_SESSION['role'] === 'admin'): ?>
        <h2 style="margin-bottom: 1.5rem;">System Administration</h2>
        <div class="alert alert-info">
            <strong>Admin Access</strong> - You have full system privileges.
        </div>
        <div class="dashboard">
            <div class="card">
                <h3>System Information</h3>
                <table style="width: 100%;">
                    <tr><td style="color: #aaa; padding: 0.5rem 0;">Version</td><td>PrinterControl v1.10.0</td></tr>
                    <tr><td style="color: #aaa; padding: 0.5rem 0;">Server</td><td><?= php_uname('s') . ' ' . php_uname('r') ?></td></tr>
                    <tr><td style="color: #aaa; padding: 0.5rem 0;">PHP Version</td><td><?= phpversion() ?></td></tr>
                    <tr><td style="color: #aaa; padding: 0.5rem 0;">Uptime</td><td>14 days, 7 hours</td></tr>
                </table>
            </div>
            <div class="card">
                <h3>API Configuration</h3>
                <table style="width: 100%;">
                    <tr><td style="color: #aaa; padding: 0.5rem 0;">API Enabled</td><td>Yes</td></tr>
                    <tr><td style="color: #aaa; padding: 0.5rem 0;">CORS Allowed</td><td>localhost</td></tr>
                    <tr><td style="color: #aaa; padding: 0.5rem 0;">Rate Limit</td><td>100 req/min</td></tr>
                </table>
            </div>
        </div>
        <div class="system-info" style="margin-top: 1.5rem;">
            <h3>System Secret Key</h3>
            <p style="color: #aaa; margin-bottom: 1rem;">This key is used for internal system authentication and API signing.</p>
            <div class="secret-data"><?= htmlspecialchars($flag) ?></div>
        </div>
        <?php endif; ?>
    </div>
    <?php endif; ?>
</body>
</html>

