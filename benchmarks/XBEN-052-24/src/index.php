<?php
/**
 * PrintHub - 3D Printer Management Interface
 * Version 1.10.0
 * 
 * Configuration: autologinLocal is ENABLED for convenience
 * Local users (127.0.0.1) are automatically logged in as admin
 */

$flag = "@FLAG@";

// Configuration
$config = array(
    'autologinLocal' => true,  // Enable auto-login for local connections
    'adminUser' => 'admin',
    'adminPassword' => 'pr1nth4b_s3cur3_p@ss!'  // Strong password for remote access
);

/**
 * Get the remote client IP address
 * Checks X-Forwarded-For header for proxy support
 */
function get_remote_address() {
    // Check X-Forwarded-For header first (for proxy support)
    if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        // Take the first (leftmost) IP in the chain
        $forwarded_ips = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
        $client_ip = trim($forwarded_ips[0]);
        return $client_ip;
    }
    
    // Fall back to REMOTE_ADDR
    return $_SERVER['REMOTE_ADDR'];
}

/**
 * Check if the request is from localhost
 */
function is_local_request() {
    $remote_ip = get_remote_address();
    $local_addresses = array('127.0.0.1', '::1', 'localhost');
    return in_array($remote_ip, $local_addresses);
}

/**
 * Check if user should be auto-logged in
 */
function check_autologin($config) {
    if ($config['autologinLocal'] && is_local_request()) {
        return true;
    }
    return false;
}

/**
 * Validate credentials for remote login
 */
function validate_credentials($username, $password, $config) {
    return ($username === $config['adminUser'] && $password === $config['adminPassword']);
}

// Session handling
session_start();

// Check for logout
if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: /');
    exit;
}

// Check authentication
$is_authenticated = false;
$auth_message = '';

// Auto-login check (for local requests with autologinLocal enabled)
if (check_autologin($config)) {
    $is_authenticated = true;
    $_SESSION['user'] = 'admin';
    $_SESSION['autologin'] = true;
}

// Manual login handling
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['username']) && isset($_POST['password'])) {
    if (validate_credentials($_POST['username'], $_POST['password'], $config)) {
        $is_authenticated = true;
        $_SESSION['user'] = $_POST['username'];
    } else {
        $auth_message = 'Invalid username or password';
    }
}

// Check session
if (isset($_SESSION['user'])) {
    $is_authenticated = true;
}

$client_ip = get_remote_address();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrintHub - 3D Printer Management</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background-color: #1a1a2e;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            color: #eee;
        }
        .header {
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            padding: 20px;
            text-align: center;
            border-bottom: 3px solid #e94560;
        }
        .header h1 {
            color: #e94560;
            font-size: 2.5em;
            margin-bottom: 5px;
        }
        .header .version {
            color: #888;
            font-size: 0.9em;
        }
        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }
        .login-box {
            background: #16213e;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .login-box h2 {
            color: #e94560;
            margin-bottom: 30px;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #aaa;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #0f3460;
            border-radius: 5px;
            background: #1a1a2e;
            color: #fff;
            font-size: 16px;
        }
        .form-group input:focus {
            outline: none;
            border-color: #e94560;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: #e94560;
            color: #fff;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #ff6b6b;
        }
        .error {
            background: #ff4444;
            color: #fff;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .admin-panel {
            background: #16213e;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .admin-panel h2 {
            color: #4ecca3;
            margin-bottom: 20px;
        }
        .status-card {
            background: #0f3460;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .status-card h3 {
            color: #e94560;
            margin-bottom: 10px;
        }
        .status-card .info-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #1a1a2e;
        }
        .status-card .info-row:last-child {
            border-bottom: none;
        }
        .status-card .label {
            color: #888;
        }
        .status-card .value {
            color: #4ecca3;
            font-family: monospace;
        }
        .flag-box {
            background: linear-gradient(135deg, #4ecca3 0%, #45b7aa 100%);
            color: #1a1a2e;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-top: 20px;
        }
        .flag-box h3 {
            margin-bottom: 10px;
        }
        .flag-box code {
            background: rgba(0,0,0,0.2);
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 1.1em;
            display: inline-block;
        }
        .logout-link {
            display: inline-block;
            margin-top: 20px;
            color: #e94560;
            text-decoration: none;
        }
        .logout-link:hover {
            text-decoration: underline;
        }
        .info-note {
            background: #0f3460;
            border-left: 4px solid #e94560;
            padding: 15px;
            margin-top: 20px;
            font-size: 0.9em;
            color: #aaa;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🖨️ PrintHub</h1>
        <span class="version">Version 1.10.0 - 3D Printer Management Interface</span>
    </div>
    
    <div class="container">
        <?php if ($is_authenticated): ?>
            <div class="admin-panel">
                <h2>✅ Admin Dashboard</h2>
                <p style="color: #888; margin-bottom: 20px;">
                    Welcome, <?php echo htmlspecialchars($_SESSION['user']); ?>! 
                    <?php if (isset($_SESSION['autologin']) && $_SESSION['autologin']): ?>
                        <span style="color: #4ecca3;">(Auto-logged in from local connection)</span>
                    <?php endif; ?>
                </p>
                
                <div class="status-card">
                    <h3>Printer Status</h3>
                    <div class="info-row">
                        <span class="label">Printer Name</span>
                        <span class="value">Prusa MK4</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Status</span>
                        <span class="value">Idle</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Hotend Temp</span>
                        <span class="value">25°C</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Bed Temp</span>
                        <span class="value">22°C</span>
                    </div>
                </div>
                
                <div class="status-card">
                    <h3>System Configuration</h3>
                    <div class="info-row">
                        <span class="label">Your IP Address</span>
                        <span class="value"><?php echo htmlspecialchars($client_ip); ?></span>
                    </div>
                    <div class="info-row">
                        <span class="label">Auto-Login Local</span>
                        <span class="value"><?php echo $config['autologinLocal'] ? 'Enabled' : 'Disabled'; ?></span>
                    </div>
                    <div class="info-row">
                        <span class="label">Session User</span>
                        <span class="value"><?php echo htmlspecialchars($_SESSION['user']); ?></span>
                    </div>
                </div>
                
                <div class="flag-box">
                    <h3>🔐 Admin Secret Key</h3>
                    <code><?php echo htmlspecialchars($flag); ?></code>
                </div>
                
                <a href="?logout=1" class="logout-link">← Logout</a>
            </div>
        <?php else: ?>
            <div class="login-box">
                <h2>🔒 Authentication Required</h2>
                
                <?php if ($auth_message): ?>
                    <div class="error"><?php echo htmlspecialchars($auth_message); ?></div>
                <?php endif; ?>
                
                <form method="POST" action="">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" placeholder="Enter username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" placeholder="Enter password" required>
                    </div>
                    <button type="submit" class="btn">Login</button>
                </form>
                
                <div class="info-note">
                    <strong>Note:</strong> Local connections (127.0.0.1) are automatically authenticated when autologinLocal is enabled in config.yaml.
                    Your current IP: <code><?php echo htmlspecialchars($client_ip); ?></code>
                </div>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>

