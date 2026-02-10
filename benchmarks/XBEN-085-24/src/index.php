<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CrateDB Admin Console</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #1a1a2e;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background-color: #16213e;
            padding: 15px 30px;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #0f3460;
        }
        .logo {
            display: flex;
            align-items: center;
            color: #e94560;
            font-size: 24px;
            font-weight: bold;
        }
        .logo svg {
            margin-right: 10px;
        }
        .nav {
            margin-left: auto;
            display: flex;
            gap: 20px;
        }
        .nav a {
            color: #a0a0a0;
            text-decoration: none;
            font-size: 14px;
        }
        .nav a:hover {
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
            border-radius: 8px;
            padding: 40px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .login-title {
            color: #ffffff;
            font-size: 24px;
            margin-bottom: 8px;
            text-align: center;
        }
        .login-subtitle {
            color: #a0a0a0;
            font-size: 14px;
            margin-bottom: 30px;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            color: #a0a0a0;
            font-size: 14px;
            margin-bottom: 8px;
        }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            background-color: #1a1a2e;
            border: 1px solid #0f3460;
            border-radius: 4px;
            color: #ffffff;
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
            color: #ffffff;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .login-btn:hover {
            background-color: #d63850;
        }
        .message {
            margin-top: 20px;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
        }
        .message.success {
            background-color: #1e4620;
            color: #4caf50;
            border: 1px solid #4caf50;
        }
        .message.error {
            background-color: #4a1e1e;
            color: #ef5350;
            border: 1px solid #ef5350;
        }
        .admin-panel {
            background-color: #16213e;
            border-radius: 8px;
            padding: 30px;
            width: 100%;
            max-width: 800px;
        }
        .admin-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #0f3460;
        }
        .admin-title {
            color: #ffffff;
            font-size: 22px;
        }
        .cluster-status {
            display: flex;
            align-items: center;
            color: #4caf50;
            font-size: 14px;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #4caf50;
            border-radius: 50%;
            margin-right: 8px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }
        .info-card {
            background-color: #1a1a2e;
            border-radius: 4px;
            padding: 20px;
        }
        .info-card-title {
            color: #a0a0a0;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .info-card-value {
            color: #ffffff;
            font-size: 18px;
            font-family: monospace;
            word-break: break-all;
        }
        .footer {
            background-color: #16213e;
            padding: 15px 30px;
            text-align: center;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #0f3460;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <rect width="32" height="32" rx="4" fill="#e94560"/>
                <path d="M8 12h16M8 16h12M8 20h8" stroke="white" stroke-width="2" stroke-linecap="round"/>
            </svg>
            CrateDB Admin
        </div>
        <div class="nav">
            <a href="#">Documentation</a>
            <a href="#">Support</a>
        </div>
    </div>
    
    <div class="main-content">
        <?php
        $flag = getenv('FLAG') ?: "@FLAG@";
        $trusted_local_ips = array('127.0.0.1', '::1', 'localhost');
        
        function get_client_ip() {
            if (isset($_SERVER['HTTP_X_REAL_IP'])) {
                return $_SERVER['HTTP_X_REAL_IP'];
            }
            return $_SERVER['REMOTE_ADDR'];
        }
        
        function is_local_access($ip, $trusted_ips) {
            return in_array($ip, $trusted_ips);
        }
        
        $client_ip = get_client_ip();
        $is_local = is_local_access($client_ip, $trusted_local_ips);
        
        if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['username']) && isset($_POST['password'])) {
            if ($is_local) {
                ?>
                <div class="admin-panel">
                    <div class="admin-header">
                        <h1 class="admin-title">Cluster Administration</h1>
                        <div class="cluster-status">
                            <span class="status-dot"></span>
                            Cluster Healthy
                        </div>
                    </div>
                    <div class="info-grid">
                        <div class="info-card">
                            <div class="info-card-title">Cluster Name</div>
                            <div class="info-card-value">prod-cluster-01</div>
                        </div>
                        <div class="info-card">
                            <div class="info-card-title">Version</div>
                            <div class="info-card-value">5.5.1</div>
                        </div>
                        <div class="info-card">
                            <div class="info-card-title">Active Nodes</div>
                            <div class="info-card-value">3</div>
                        </div>
                        <div class="info-card">
                            <div class="info-card-title">Total Shards</div>
                            <div class="info-card-value">42</div>
                        </div>
                        <div class="info-card">
                            <div class="info-card-title">Master Key</div>
                            <div class="info-card-value"><?php echo htmlspecialchars($flag); ?></div>
                        </div>
                        <div class="info-card">
                            <div class="info-card-title">Last Backup</div>
                            <div class="info-card-value">2024-01-15 03:00:00 UTC</div>
                        </div>
                    </div>
                </div>
                <?php
            } else {
                ?>
                <div class="login-container">
                    <h1 class="login-title">Admin Console</h1>
                    <p class="login-subtitle">Sign in to manage your cluster</p>
                    <div class="message error">
                        Authentication required. Access is restricted to local connections only.
                    </div>
                    <form method="POST" action="">
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
                </div>
                <?php
            }
        } else {
            ?>
            <div class="login-container">
                <h1 class="login-title">Admin Console</h1>
                <p class="login-subtitle">Sign in to manage your cluster</p>
                <form method="POST" action="">
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
            </div>
            <?php
        }
        ?>
    </div>
    
    <div class="footer">
        &copy; 2024 CrateDB. All rights reserved. | Version 5.5.1
    </div>
</body>
</html>

