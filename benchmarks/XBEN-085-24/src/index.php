<?php
/**
 * PrintControl - 3D Printer Management Interface
 * Version 1.10.0
 * 
 * Configuration loaded from config.yaml
 * autologinLocal: true (allows automatic login for local network connections)
 */

// Configuration settings (simulating config.yaml)
$config = [
    'autologinLocal' => true,  // Enable auto-login for local connections
    'trustedNetworks' => ['127.0.0.1', '::1', 'localhost'],
    'adminUser' => 'admin',
    'version' => '1.10.0'
];

// Flag stored securely - only accessible to authenticated admin
$flag = getenv('FLAG') ?: "@FLAG@";

/**
 * Get remote address from request
 * VULNERABLE: Trusts X-Forwarded-For header without verifying request comes from trusted proxy
 * This mimics CVE-2024-32977 in OctoPrint
 */
function get_remote_address() {
    // Check for X-Forwarded-For header (vulnerable - doesn't verify trusted proxy)
    if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        // Take the left-most value (client IP in proxy chain)
        $forwarded = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
        return trim($forwarded[0]);
    }
    // Fall back to actual remote address
    return $_SERVER['REMOTE_ADDR'] ?? '';
}

/**
 * Check if request is from local network
 */
function is_local_request($config) {
    $remote_ip = get_remote_address();
    return in_array($remote_ip, $config['trustedNetworks']);
}

/**
 * Authenticate user - supports autologinLocal feature
 */
function authenticate_user($config) {
    // If autologinLocal is enabled and request appears to be local, auto-authenticate
    if ($config['autologinLocal'] && is_local_request($config)) {
        return [
            'authenticated' => true,
            'user' => $config['adminUser'],
            'method' => 'autologin'
        ];
    }
    return ['authenticated' => false, 'user' => null, 'method' => null];
}

// Perform authentication check
$auth = authenticate_user($config);
$client_ip = get_remote_address();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrintControl - 3D Printer Management</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .navbar {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #333;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #00d4aa;
        }
        .logo span {
            color: #ffffff;
        }
        .version {
            color: #888;
            font-size: 12px;
        }
        .nav-links {
            display: flex;
            gap: 20px;
        }
        .nav-links a {
            color: #aaa;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 5px;
            transition: all 0.3s;
        }
        .nav-links a:hover {
            background: rgba(0, 212, 170, 0.2);
            color: #00d4aa;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .status-banner {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #00d4aa;
        }
        .status-banner.warning {
            border-left-color: #ffa500;
        }
        .status-banner.error {
            border-left-color: #ff4444;
        }
        .status-banner h3 {
            color: #00d4aa;
            margin-bottom: 10px;
        }
        .status-banner.warning h3 {
            color: #ffa500;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .card h2 {
            color: #00d4aa;
            margin-bottom: 20px;
            font-size: 20px;
        }
        .login-form {
            max-width: 400px;
            margin: 50px auto;
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
            padding: 12px 15px;
            border: 1px solid #333;
            border-radius: 5px;
            background: rgba(0, 0, 0, 0.3);
            color: #fff;
            font-size: 14px;
        }
        .form-group input:focus {
            outline: none;
            border-color: #00d4aa;
        }
        .btn {
            background: #00d4aa;
            color: #1a1a2e;
            border: none;
            padding: 12px 25px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            width: 100%;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #00b894;
        }
        .admin-panel {
            background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(0, 184, 148, 0.1));
            border: 1px solid #00d4aa;
        }
        .flag-display {
            background: rgba(0, 212, 170, 0.2);
            padding: 15px 20px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 16px;
            color: #00d4aa;
            word-break: break-all;
            margin-top: 15px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .info-item {
            background: rgba(0, 0, 0, 0.2);
            padding: 15px;
            border-radius: 5px;
        }
        .info-item label {
            color: #888;
            font-size: 12px;
            display: block;
            margin-bottom: 5px;
        }
        .info-item value {
            color: #fff;
            font-size: 14px;
        }
        .printer-status {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #00d4aa;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .debug-info {
            margin-top: 30px;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div>
            <span class="logo">Print<span>Control</span></span>
            <span class="version">v<?php echo htmlspecialchars($config['version']); ?></span>
        </div>
        <div class="nav-links">
            <a href="#">Dashboard</a>
            <a href="#">Printers</a>
            <a href="#">Files</a>
            <a href="#">Settings</a>
        </div>
    </nav>

    <div class="container">
        <?php if ($auth['authenticated']): ?>
            <!-- Admin Panel - User is authenticated via autologinLocal -->
            <div class="status-banner">
                <h3>Welcome, <?php echo htmlspecialchars($auth['user']); ?>!</h3>
                <p>You have been automatically logged in via local network access (autologinLocal enabled).</p>
            </div>

            <div class="card admin-panel">
                <h2>🔐 Admin Control Panel</h2>
                <p>Full administrative access granted. You can manage all printers and system settings.</p>
                
                <div class="info-grid">
                    <div class="info-item">
                        <label>Authentication Method</label>
                        <value><?php echo htmlspecialchars($auth['method']); ?></value>
                    </div>
                    <div class="info-item">
                        <label>Client IP (Detected)</label>
                        <value><?php echo htmlspecialchars($client_ip); ?></value>
                    </div>
                    <div class="info-item">
                        <label>AutoLogin Local</label>
                        <value><?php echo $config['autologinLocal'] ? 'Enabled' : 'Disabled'; ?></value>
                    </div>
                    <div class="info-item">
                        <label>Access Level</label>
                        <value>Administrator</value>
                    </div>
                </div>

                <h3 style="margin-top: 30px; color: #00d4aa;">System Credentials</h3>
                <p style="margin-top: 10px; color: #aaa;">Sensitive administrative credentials:</p>
                <div class="flag-display">
                    <?php echo htmlspecialchars($flag); ?>
                </div>
            </div>

            <div class="card">
                <h2>🖨️ Connected Printers</h2>
                <div class="printer-status">
                    <div class="status-indicator"></div>
                    <span>Prusa i3 MK3S+ - Operational (Idle)</span>
                </div>
            </div>

        <?php else: ?>
            <!-- Login Required - User is not from local network -->
            <div class="status-banner warning">
                <h3>Authentication Required</h3>
                <p>You are accessing PrintControl from an external network. Please log in to continue.</p>
                <p style="margin-top: 10px; font-size: 12px; color: #888;">
                    Note: Local network users with autologinLocal enabled are automatically authenticated.
                </p>
            </div>

            <div class="card login-form">
                <h2>Sign In to PrintControl</h2>
                <form action="index.php" method="POST">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" placeholder="Enter your username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" placeholder="Enter your password" required>
                    </div>
                    <button type="submit" class="btn">Sign In</button>
                </form>
                
                <?php if (isset($_POST['username'])): ?>
                    <p style="color: #ff4444; margin-top: 15px; text-align: center;">
                        Invalid credentials. Access denied.
                    </p>
                <?php endif; ?>
            </div>

            <div class="card">
                <h2>ℹ️ Access Information</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <label>Your Detected IP</label>
                        <value><?php echo htmlspecialchars($client_ip); ?></value>
                    </div>
                    <div class="info-item">
                        <label>AutoLogin Local</label>
                        <value><?php echo $config['autologinLocal'] ? 'Enabled' : 'Disabled'; ?></value>
                    </div>
                    <div class="info-item">
                        <label>Trusted Networks</label>
                        <value><?php echo htmlspecialchars(implode(', ', $config['trustedNetworks'])); ?></value>
                    </div>
                    <div class="info-item">
                        <label>Version</label>
                        <value><?php echo htmlspecialchars($config['version']); ?></value>
                    </div>
                </div>
            </div>
        <?php endif; ?>

        <div class="debug-info">
            <!-- Debug: Request processed at <?php echo date('Y-m-d H:i:s'); ?> -->
            <!-- Config: autologinLocal=<?php echo $config['autologinLocal'] ? 'true' : 'false'; ?> -->
        </div>
    </div>
</body>
</html>

