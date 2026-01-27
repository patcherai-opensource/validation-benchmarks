<?php
    // PrintHub 3D Printer Management System v1.8.2
    // Configuration
    $config = [
        'autologinLocal' => true,  // Enable auto-login for local network users
        'trustedProxies' => [],    // Empty - we trust X-Forwarded-For from any source
        'localNetworks' => ['127.0.0.1', '::1', 'localhost']
    ];
    
    $flag = $_ENV['FLAG'] ?? getenv('FLAG') ?? "@FLAG@";
    
    // Get client IP address - checks X-Forwarded-For header first
    function getClientIp() {
        if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
            // Trust the leftmost IP in X-Forwarded-For chain
            $ips = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
            return trim($ips[0]);
        }
        return $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    }
    
    // Check if request is from local network
    function isLocalRequest($config) {
        $clientIp = getClientIp();
        return in_array($clientIp, $config['localNetworks']);
    }
    
    // Check if user should be auto-logged in
    function checkAutoLogin($config) {
        if ($config['autologinLocal'] && isLocalRequest($config)) {
            return true;
        }
        return false;
    }
    
    $isAuthenticated = checkAutoLogin($config);
    $clientIp = getClientIp();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrintHub - 3D Printer Control Panel</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e4e4e4;
        }
        .navbar {
            background: rgba(0,0,0,0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #333;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #00d4ff;
        }
        .logo span {
            color: #ff6b6b;
        }
        .nav-info {
            font-size: 12px;
            color: #888;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h2 {
            color: #00d4ff;
            margin-bottom: 20px;
            font-size: 22px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .status-item {
            background: rgba(0,0,0,0.2);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .status-item .value {
            font-size: 28px;
            font-weight: bold;
            color: #00d4ff;
        }
        .status-item .label {
            color: #888;
            margin-top: 5px;
        }
        .admin-panel {
            background: linear-gradient(135deg, #2d5016 0%, #1a3d0c 100%);
            border: 2px solid #4CAF50;
        }
        .flag-display {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            word-break: break-all;
            color: #4CAF50;
            margin-top: 15px;
        }
        .login-required {
            text-align: center;
            padding: 60px 20px;
        }
        .login-required h2 {
            color: #ff6b6b;
            margin-bottom: 15px;
        }
        .login-required p {
            color: #888;
            margin-bottom: 20px;
        }
        .btn {
            background: #00d4ff;
            color: #000;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            background: #00a8cc;
        }
        .info-box {
            background: rgba(0,212,255,0.1);
            border: 1px solid #00d4ff;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            font-size: 13px;
        }
        .info-box code {
            background: rgba(0,0,0,0.3);
            padding: 2px 6px;
            border-radius: 4px;
            color: #ff6b6b;
        }
        footer {
            text-align: center;
            padding: 20px;
            color: #555;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">Print<span>Hub</span></div>
        <div class="nav-info">
            Client IP: <?php echo htmlspecialchars($clientIp); ?> |
            Status: <?php echo $isAuthenticated ? '<span style="color:#4CAF50">Authenticated</span>' : '<span style="color:#ff6b6b">Guest</span>'; ?>
        </div>
    </nav>
    
    <div class="container">
        <?php if ($isAuthenticated): ?>
            <!-- Authenticated Admin View -->
            <div class="card admin-panel">
                <h2>🔓 Admin Control Panel</h2>
                <p>Welcome back! You have been automatically authenticated as a local administrator.</p>
                <div class="flag-display">
                    <strong>System Secret Key:</strong><br>
                    <?php echo htmlspecialchars($flag); ?>
                </div>
            </div>
            
            <div class="card">
                <h2>🖨️ Connected Printers</h2>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="value">3</div>
                        <div class="label">Online Printers</div>
                    </div>
                    <div class="status-item">
                        <div class="value">2</div>
                        <div class="label">Active Jobs</div>
                    </div>
                    <div class="status-item">
                        <div class="value">87%</div>
                        <div class="label">Avg. Filament</div>
                    </div>
                    <div class="status-item">
                        <div class="value">23°C</div>
                        <div class="label">Ambient Temp</div>
                    </div>
                </div>
            </div>
            
        <?php else: ?>
            <!-- Guest View -->
            <div class="card login-required">
                <h2>🔒 Authentication Required</h2>
                <p>Access to the PrintHub control panel is restricted to authorized users.</p>
                <p style="color:#666; font-size:14px;">Local network users are automatically authenticated.</p>
            </div>
            
            <div class="card">
                <h2>📋 System Information</h2>
                <div class="info-box">
                    <strong>PrintHub 3D Printer Management System</strong><br>
                    Version: 1.8.2 | Build: 2024.03.15<br><br>
                    This system uses automatic local authentication. Users connecting from the local network 
                    (127.0.0.1, localhost) are granted administrative access without requiring credentials.
                    Remote users must be authenticated through the corporate VPN.
                </div>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="value">Online</div>
                        <div class="label">Server Status</div>
                    </div>
                    <div class="status-item">
                        <div class="value">3</div>
                        <div class="label">Connected Devices</div>
                    </div>
                    <div class="status-item">
                        <div class="value"><?php echo htmlspecialchars($clientIp); ?></div>
                        <div class="label">Your IP Address</div>
                    </div>
                </div>
            </div>
        <?php endif; ?>
    </div>
    
    <footer>
        PrintHub Control Panel v1.8.2 | &copy; 2024 PrintHub Systems
    </footer>
</body>
</html>

