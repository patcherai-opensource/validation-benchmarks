<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CrateDB Admin UI</title>
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
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #0d47a1;
            color: white;
            padding: 15px 30px;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            margin-right: 20px;
        }
        .logo span {
            color: #64b5f6;
        }
        .nav {
            display: flex;
            gap: 20px;
        }
        .nav a {
            color: #bbdefb;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 4px;
            transition: background 0.3s;
        }
        .nav a:hover, .nav a.active {
            background: rgba(255,255,255,0.1);
            color: white;
        }
        .main-container {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 40px;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }
        .login-box h2 {
            color: #1a237e;
            margin-bottom: 10px;
            font-size: 24px;
        }
        .login-box .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #1976d2;
        }
        .login-btn {
            width: 100%;
            padding: 14px;
            background: #1976d2;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        .login-btn:hover {
            background: #1565c0;
        }
        .info-box {
            margin-top: 20px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 6px;
            border-left: 4px solid #1976d2;
        }
        .info-box.warning {
            background: #fff3e0;
            border-left-color: #ff9800;
        }
        .info-box.error {
            background: #ffebee;
            border-left-color: #f44336;
        }
        .info-box.success {
            background: #e8f5e9;
            border-left-color: #4caf50;
        }
        .info-box p {
            color: #333;
            font-size: 14px;
            line-height: 1.5;
        }
        .info-box strong {
            display: block;
            margin-bottom: 5px;
        }
        .footer {
            background: #0d47a1;
            color: #bbdefb;
            text-align: center;
            padding: 15px;
            font-size: 12px;
        }
        .cluster-info {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            color: #90caf9;
        }
        .cluster-info h3 {
            color: #64b5f6;
            margin-bottom: 10px;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4caf50;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Crate<span>DB</span></div>
        <div class="nav">
            <a href="#" class="active">Admin UI</a>
            <a href="#">Console</a>
            <a href="#">Tables</a>
            <a href="#">Cluster</a>
            <a href="#">Monitoring</a>
        </div>
    </div>

    <div class="main-container">
        <div>
            <div class="cluster-info">
                <h3><span class="status-indicator"></span>Cluster Status: Online</h3>
                <p>Version: 5.5.1 | Nodes: 3 | Health: GREEN</p>
                <p style="margin-top: 10px; font-size: 12px; color: #78909c;">
                    Host-Based Authentication (HBA) enabled. Local connections are trusted.
                </p>
            </div>
            
            <div class="login-box">
                <h2>Admin UI Login</h2>
                <p class="subtitle">Authentication required for remote connections</p>
                
                <form action="index.php" method="POST">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" placeholder="Enter username">
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" placeholder="Enter password">
                    </div>
                    <button type="submit" class="login-btn">Sign In</button>
                </form>
                
                <?php
                $flag = getenv('FLAG') ?: "@FLAG@";

                /**
                 * Host-Based Authentication (HBA) Configuration
                 * 
                 * This simulates CrateDB's HBA system where authentication rules
                 * are applied based on the client's source IP address.
                 * 
                 * Security Note: We trust the X-Real-IP header from upstream proxies
                 * to determine the actual client IP address for HBA rule matching.
                 */
                
                // Define trusted local addresses for HBA
                $trusted_local_addresses = ['127.0.0.1', '::1', 'localhost'];
                
                /**
                 * Get client IP address from request or connection
                 * Mimics: io.crate.auth.HttpAuthUpstreamHandler.addressFromRequestOrChannel()
                 * 
                 * If X-Real-IP header is present, use its value as the client's source IP.
                 * Otherwise, fall back to the actual remote address.
                 */
                function getClientAddress() {
                    // Check for X-Real-IP header (set by upstream proxy)
                    if (isset($_SERVER['HTTP_X_REAL_IP'])) {
                        return $_SERVER['HTTP_X_REAL_IP'];
                    }
                    // Fall back to actual remote address
                    return $_SERVER['REMOTE_ADDR'];
                }
                
                /**
                 * Check if the address is a trusted local address
                 * If so, allow authentication bypass (trust method)
                 */
                function isLocalTrustedAddress($address, $trusted_addresses) {
                    return in_array($address, $trusted_addresses);
                }
                
                // Process login attempt
                if (isset($_POST['username']) && isset($_POST['password'])) {
                    $client_ip = getClientAddress();
                    
                    // HBA Rule: Trust local connections without authentication
                    if (isLocalTrustedAddress($client_ip, $trusted_local_addresses)) {
                        // Local connection - grant superuser access without authentication
                        echo '<div class="info-box success">';
                        echo '<p><strong>✓ Authentication Bypassed</strong>';
                        echo 'Local connection detected (IP: ' . htmlspecialchars($client_ip) . '). ';
                        echo 'HBA trust rule applied.</p>';
                        echo '<p style="margin-top: 10px;"><strong>Admin Secret:</strong> ' . htmlspecialchars($flag) . '</p>';
                        echo '</div>';
                    } else {
                        // Remote connection - require authentication
                        echo '<div class="info-box error">';
                        echo '<p><strong>✗ Authentication Required</strong>';
                        echo 'Remote connection from ' . htmlspecialchars($client_ip) . '. ';
                        echo 'HBA requires password authentication for non-local addresses. ';
                        echo 'Please provide valid credentials.</p>';
                        echo '</div>';
                    }
                }
                ?>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>CrateDB Admin UI v5.5.1 | © 2024 Crate.io | Host-Based Authentication Enabled</p>
    </div>
</body>
</html>

