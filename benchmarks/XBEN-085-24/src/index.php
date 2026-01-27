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
            display: flex;
            flex-direction: column;
        }
        .navbar {
            background-color: #16213e;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #0f3460;
        }
        .logo {
            color: #e94560;
            font-size: 24px;
            font-weight: bold;
        }
        .logo span {
            color: #fff;
        }
        .nav-links {
            display: flex;
            gap: 20px;
        }
        .nav-links a {
            color: #a2a2a2;
            text-decoration: none;
            font-size: 14px;
        }
        .nav-links a:hover {
            color: #e94560;
        }
        .main-content {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 40px;
        }
        .login-container {
            background-color: #16213e;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .login-header h2 {
            color: #fff;
            margin-bottom: 10px;
        }
        .login-header p {
            color: #a2a2a2;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            color: #a2a2a2;
            margin-bottom: 8px;
            font-size: 14px;
        }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            background-color: #1a1a2e;
            border: 1px solid #0f3460;
            border-radius: 5px;
            color: #fff;
            font-size: 14px;
        }
        .form-group input:focus {
            outline: none;
            border-color: #e94560;
        }
        .login-btn {
            width: 100%;
            padding: 12px;
            background-color: #e94560;
            border: none;
            border-radius: 5px;
            color: #fff;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .login-btn:hover {
            background-color: #d13652;
        }
        .info-box {
            margin-top: 20px;
            padding: 15px;
            background-color: #1a1a2e;
            border-radius: 5px;
            border-left: 3px solid #e94560;
        }
        .info-box p {
            color: #a2a2a2;
            font-size: 12px;
        }
        .success-box {
            margin-top: 20px;
            padding: 20px;
            background-color: #1a4d1a;
            border-radius: 5px;
            text-align: center;
        }
        .success-box h3 {
            color: #4ade80;
            margin-bottom: 10px;
        }
        .success-box p {
            color: #a7f3d0;
            font-size: 14px;
            word-break: break-all;
        }
        .error-box {
            margin-top: 20px;
            padding: 15px;
            background-color: #4d1a1a;
            border-radius: 5px;
            text-align: center;
        }
        .error-box p {
            color: #fca5a5;
            font-size: 14px;
        }
        .footer {
            background-color: #16213e;
            padding: 15px;
            text-align: center;
            border-top: 1px solid #0f3460;
        }
        .footer p {
            color: #a2a2a2;
            font-size: 12px;
        }
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            background-color: #4ade80;
            border-radius: 50%;
            margin-right: 5px;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">Print<span>Hub</span></div>
        <div class="nav-links">
            <a href="#">Dashboard</a>
            <a href="#">Printers</a>
            <a href="#">Files</a>
            <a href="#">Settings</a>
        </div>
    </nav>
    
    <div class="main-content">
        <div class="login-container">
            <div class="login-header">
                <h2>Welcome Back</h2>
                <p>Sign in to manage your 3D printers</p>
            </div>
            
            <form action="index.php" method="POST">
                <div class="form-group">
                    <label for="user">Username</label>
                    <input type="text" id="user" name="user" placeholder="Enter your username">
                </div>
                <div class="form-group">
                    <label for="pass">Password</label>
                    <input type="password" id="pass" name="pass" placeholder="Enter your password">
                </div>
                <button type="submit" class="login-btn">Sign In</button>
            </form>
            
            <div class="info-box">
                <p><span class="status-indicator"></span>autologinLocal is enabled for trusted network hosts. Local connections are automatically authenticated.</p>
            </div>
            
            <?php
            $flag = getenv('FLAG') ?: "@FLAG@";
            
            // Configuration: autologinLocal feature
            $autologin_local_enabled = true;
            $trusted_local_addresses = ['127.0.0.1', 'localhost', '::1'];
            
            // Function to determine client IP address
            // Checks X-Forwarded-For header for proxy scenarios
            function get_remote_address() {
                if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
                    // Trust the leftmost IP in X-Forwarded-For chain
                    $forwarded_ips = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
                    return trim($forwarded_ips[0]);
                }
                return $_SERVER['REMOTE_ADDR'];
            }
            
            // Handle login form submission
            if (isset($_POST['user']) && isset($_POST['pass'])) {
                $client_ip = get_remote_address();
                
                // Check if autologinLocal is enabled and request appears to be from local network
                if ($autologin_local_enabled && in_array($client_ip, $trusted_local_addresses)) {
                    echo '<div class="success-box">';
                    echo '<h3>Auto-Login Successful</h3>';
                    echo '<p>Welcome, Administrator! Local connection detected from ' . htmlspecialchars($client_ip) . '</p>';
                    echo '<p style="margin-top: 10px; font-family: monospace;">' . $flag . '</p>';
                    echo '</div>';
                } else {
                    echo '<div class="error-box">';
                    echo '<p>Authentication failed. Remote connections require valid credentials.</p>';
                    echo '<p style="margin-top: 5px; font-size: 11px; color: #999;">Your IP: ' . htmlspecialchars($client_ip) . '</p>';
                    echo '</div>';
                }
            }
            ?>
        </div>
    </div>
    
    <footer class="footer">
        <p>PrintHub v1.10.0 - 3D Printer Management System</p>
    </footer>
</body>
</html>

