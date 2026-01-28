<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrinterPi Control Panel</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #333;
        }
        .logo { display: flex; align-items: center; gap: 10px; }
        .logo h1 { font-size: 1.5em; color: #4fd1c5; }
        .logo span { font-size: 0.8em; color: #888; }
        .nav a { color: #888; text-decoration: none; margin-left: 20px; font-size: 0.9em; }
        .nav a:hover { color: #4fd1c5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h2 { font-size: 1.1em; margin-bottom: 15px; color: #4fd1c5; }
        .status-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .status-value { color: #4fd1c5; }
        .login-card { max-width: 400px; margin: 40px auto; }
        .login-card h2 { text-align: center; margin-bottom: 25px; }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px 15px;
            margin-bottom: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 1em;
        }
        input:focus { outline: none; border-color: #4fd1c5; }
        button {
            width: 100%;
            padding: 12px;
            background: #4fd1c5;
            border: none;
            border-radius: 8px;
            color: #1a1a2e;
            font-weight: bold;
            cursor: pointer;
            font-size: 1em;
        }
        button:hover { background: #38b2ac; }
        .alert { padding: 15px; border-radius: 8px; margin-top: 15px; text-align: center; }
        .alert-success { background: rgba(79,209,197,0.2); color: #4fd1c5; border: 1px solid #4fd1c5; }
        .alert-error { background: rgba(255,99,99,0.2); color: #ff6363; border: 1px solid #ff6363; }
        .info-text { font-size: 0.85em; color: #666; margin-top: 10px; }
        .footer { text-align: center; padding: 20px; color: #555; font-size: 0.8em; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <h1>🖨️ PrinterPi</h1>
            <span>v1.10.0</span>
        </div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/status.php">Status</a>
            <a href="/api/info">API</a>
            <a href="/settings.php">Settings</a>
        </div>
    </div>
    
    <div class="container">
        <div class="grid">
            <div class="card">
                <h2>System Status</h2>
                <div class="status-item">
                    <span>Connection</span>
                    <span class="status-value">Ready</span>
                </div>
                <div class="status-item">
                    <span>Printer State</span>
                    <span class="status-value">Idle</span>
                </div>
                <div class="status-item">
                    <span>Bed Temperature</span>
                    <span class="status-value">60°C</span>
                </div>
                <div class="status-item">
                    <span>Nozzle Temperature</span>
                    <span class="status-value">205°C</span>
                </div>
            </div>
            
            <div class="card login-card">
                <h2>Authentication Required</h2>
                <form action="index.php" method="POST">
                    <input type="text" name="user" placeholder="Username">
                    <input type="password" name="pass" placeholder="Password">
                    <button type="submit">Sign In</button>
                </form>
                <p class="info-text">Access restricted to authorized personnel</p>
                
                <?php
                $flag = getenv('FLAG') ?: "@FLAG@";
                
                // Configuration from config.yaml simulation
                $config = [
                    'accessControl' => [
                        'autologinLocal' => true,
                        'localNetworks' => ['127.0.0.0/8', '10.0.0.0/8', '192.168.0.0/16'],
                        'trustBasicAuthentication' => false
                    ],
                    'server' => [
                        'reverseProxy' => [
                            'trustedDownstream' => []
                        ]
                    ]
                ];
                
                function get_remote_address() {
                    // Check X-Forwarded-For header for client IP
                    if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
                        $addresses = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
                        return trim($addresses[0]);
                    }
                    return $_SERVER['REMOTE_ADDR'] ?? 'unknown';
                }
                
                function is_local_address($ip) {
                    $local_patterns = ['127.0.0.1', 'localhost', '::1'];
                    return in_array($ip, $local_patterns);
                }
                
                // Check if autologinLocal is triggered
                $client_ip = get_remote_address();
                $autologin_enabled = $config['accessControl']['autologinLocal'];
                
                if (isset($_POST['user']) && isset($_POST['pass'])) {
                    // When autologinLocal is enabled and request appears local, auto-authenticate
                    if ($autologin_enabled && is_local_address($client_ip)) {
                        echo '<div class="alert alert-success">';
                        echo '<strong>Welcome, admin!</strong><br>';
                        echo 'Auto-login from local network successful.<br><br>';
                        echo '<strong>System Key:</strong> ' . $flag;
                        echo '</div>';
                    } else {
                        echo '<div class="alert alert-error">';
                        echo 'Authentication failed. Remote access requires valid credentials.';
                        echo '</div>';
                    }
                }
                ?>
            </div>
        </div>
    </div>
    
    <div class="footer">
        PrinterPi Control Panel &copy; 2024 | <a href="/api/version" style="color:#555;">API v2.0</a>
    </div>
</body>
</html>

