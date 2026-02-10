<?php
session_start();

$flag = "@FLAG@";

$users = [
    'admin' => [
        'password' => 'Spr1ngf13ld_S3cr3t!',
        'totp_secret' => 'JBSWY3DPEHPK3PXP',
        'has_2fa' => true
    ],
    'homer' => [
        'password' => 'donuts123',
        'totp_secret' => null,
        'has_2fa' => false
    ]
];

$remember_me_secret = 'springfield_nuclear_power_plant_2024';

function generateRememberToken($username, $secret) {
    $timestamp = time();
    $data = $username . '|' . $timestamp;
    $signature = hash_hmac('sha256', $data, $secret);
    return base64_encode($data . '|' . $signature);
}

function validateRememberToken($token, $secret) {
    $decoded = base64_decode($token);
    if (!$decoded) return false;
    
    $parts = explode('|', $decoded);
    if (count($parts) !== 3) return false;
    
    $username = $parts[0];
    $timestamp = $parts[1];
    $signature = $parts[2];
    
    $expected_sig = hash_hmac('sha256', $username . '|' . $timestamp, $secret);
    if (!hash_equals($expected_sig, $signature)) return false;
    
    if (time() - intval($timestamp) > 86400 * 30) return false;
    
    return $username;
}

function generateTOTP($secret, $time_offset = 0) {
    $time = floor(time() / 30) + $time_offset;
    $secret_bytes = base32_decode($secret);
    $time_bytes = pack('N*', 0) . pack('N*', $time);
    $hash = hash_hmac('sha1', $time_bytes, $secret_bytes, true);
    $offset = ord($hash[19]) & 0x0F;
    $code = (
        ((ord($hash[$offset]) & 0x7F) << 24) |
        ((ord($hash[$offset+1]) & 0xFF) << 16) |
        ((ord($hash[$offset+2]) & 0xFF) << 8) |
        (ord($hash[$offset+3]) & 0xFF)
    ) % 1000000;
    return str_pad($code, 6, '0', STR_PAD_LEFT);
}

function base32_decode($input) {
    $map = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    $input = strtoupper($input);
    $input = str_replace('=', '', $input);
    $output = '';
    $buffer = 0;
    $bits = 0;
    
    for ($i = 0; $i < strlen($input); $i++) {
        $val = strpos($map, $input[$i]);
        if ($val === false) continue;
        $buffer = ($buffer << 5) | $val;
        $bits += 5;
        if ($bits >= 8) {
            $bits -= 8;
            $output .= chr(($buffer >> $bits) & 0xFF);
        }
    }
    return $output;
}

$page = isset($_GET['page']) ? $_GET['page'] : 'home';

if ($page === 'logout') {
    session_destroy();
    setcookie('REMEMBERME', '', time() - 3600, '/');
    header('Location: index.php');
    exit();
}

if (isset($_COOKIE['REMEMBERME']) && !isset($_SESSION['authenticated'])) {
    $username = validateRememberToken($_COOKIE['REMEMBERME'], $remember_me_secret);
    if ($username && isset($users[$username])) {
        $_SESSION['authenticated'] = true;
        $_SESSION['username'] = $username;
    }
}

if ($page === 'dashboard') {
    if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
        header('Location: index.php');
        exit();
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if ($page === 'login' && isset($_POST['username']) && isset($_POST['password'])) {
        $username = $_POST['username'];
        $password = $_POST['password'];
        
        if (isset($users[$username]) && $users[$username]['password'] === $password) {
            $_SESSION['username'] = $username;
            $_SESSION['login_verified'] = true;
            
            if (isset($_POST['remember_me']) && $_POST['remember_me'] === 'on') {
                $token = generateRememberToken($username, $remember_me_secret);
                setcookie('REMEMBERME', $token, time() + 86400 * 30, '/');
            }
            
            if ($users[$username]['has_2fa']) {
                $_SESSION['pending_2fa'] = true;
                header('Location: index.php?page=verify2fa');
                exit();
            } else {
                $_SESSION['authenticated'] = true;
                header('Location: index.php?page=dashboard');
                exit();
            }
        } else {
            $login_error = 'Invalid credentials';
        }
    }
    
    if ($page === 'verify2fa' && isset($_POST['totp_code'])) {
        if (isset($_SESSION['pending_2fa']) && $_SESSION['pending_2fa'] === true) {
            $username = $_SESSION['username'];
            $submitted_code = $_POST['totp_code'];
            
            $valid = false;
            for ($offset = -1; $offset <= 1; $offset++) {
                $expected = generateTOTP($users[$username]['totp_secret'], $offset);
                if ($submitted_code === $expected) {
                    $valid = true;
                    break;
                }
            }
            
            if ($valid) {
                $_SESSION['authenticated'] = true;
                unset($_SESSION['pending_2fa']);
                header('Location: index.php?page=dashboard');
                exit();
            } else {
                $totp_error = 'Invalid verification code';
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Springfield Power - Employee Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: rgba(255,255,255,0.1);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
        }
        .logo {
            color: #4ecca3;
            font-size: 1.5em;
            font-weight: bold;
        }
        .nav a {
            color: #fff;
            text-decoration: none;
            margin-left: 20px;
            padding: 8px 16px;
            border-radius: 5px;
            transition: background 0.3s;
        }
        .nav a:hover { background: rgba(255,255,255,0.1); }
        .container {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 40px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        }
        .card h2 {
            color: #1a1a2e;
            margin-bottom: 25px;
            text-align: center;
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
        .form-group input[type="text"],
        .form-group input[type="password"] {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #4ecca3;
        }
        .checkbox-group {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        .checkbox-group input {
            margin-right: 10px;
        }
        .checkbox-group label {
            color: #666;
            font-size: 14px;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: #4ecca3;
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        .btn:hover { background: #3db892; }
        .error {
            background: #ff6b6b;
            color: #fff;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        .info-box {
            background: #e8f5e9;
            border-left: 4px solid #4ecca3;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 0 8px 8px 0;
        }
        .info-box p {
            color: #2e7d32;
            font-size: 14px;
        }
        .dashboard-card {
            max-width: 600px;
        }
        .welcome-msg {
            text-align: center;
            margin-bottom: 30px;
        }
        .welcome-msg h1 {
            color: #1a1a2e;
            margin-bottom: 10px;
        }
        .welcome-msg p {
            color: #666;
        }
        .data-section {
            background: #f5f5f5;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        .data-section h3 {
            color: #1a1a2e;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #4ecca3;
        }
        .data-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        .data-item:last-child { border-bottom: none; }
        .data-label { color: #666; }
        .data-value { color: #1a1a2e; font-weight: 500; }
        .flag-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            text-align: center;
        }
        .flag-section h3 { margin-bottom: 10px; }
        .flag-value {
            font-family: 'Courier New', monospace;
            background: rgba(255,255,255,0.2);
            padding: 10px;
            border-radius: 5px;
            word-break: break-all;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: rgba(255,255,255,0.5);
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">⚛️ Springfield Nuclear Power</div>
        <div class="nav">
            <a href="index.php">Home</a>
            <?php if (isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true): ?>
                <a href="index.php?page=dashboard">Dashboard</a>
                <a href="index.php?page=logout">Logout</a>
            <?php else: ?>
                <a href="index.php?page=login">Login</a>
            <?php endif; ?>
        </div>
    </div>

    <div class="container">
        <?php if ($page === 'login'): ?>
            <div class="card">
                <h2>Employee Login</h2>
                <?php if (isset($login_error)): ?>
                    <div class="error"><?php echo htmlspecialchars($login_error); ?></div>
                <?php endif; ?>
                <form method="POST" action="index.php?page=login">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="remember_me" name="remember_me">
                        <label for="remember_me">Remember me on this device</label>
                    </div>
                    <button type="submit" class="btn">Sign In</button>
                </form>
            </div>

        <?php elseif ($page === 'verify2fa'): ?>
            <?php if (!isset($_SESSION['pending_2fa']) || $_SESSION['pending_2fa'] !== true): ?>
                <?php header('Location: index.php?page=login'); exit(); ?>
            <?php endif; ?>
            <div class="card">
                <h2>Two-Factor Authentication</h2>
                <?php if (isset($totp_error)): ?>
                    <div class="error"><?php echo htmlspecialchars($totp_error); ?></div>
                <?php endif; ?>
                <div class="info-box">
                    <p>Enter the 6-digit code from your authenticator app to continue.</p>
                </div>
                <form method="POST" action="index.php?page=verify2fa">
                    <div class="form-group">
                        <label for="totp_code">Verification Code</label>
                        <input type="text" id="totp_code" name="totp_code" 
                               pattern="[0-9]{6}" maxlength="6" 
                               placeholder="000000" required 
                               autocomplete="off">
                    </div>
                    <button type="submit" class="btn">Verify</button>
                </form>
            </div>

        <?php elseif ($page === 'dashboard'): ?>
            <div class="card dashboard-card">
                <div class="welcome-msg">
                    <h1>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h1>
                    <p>Springfield Nuclear Power Plant - Sector 7-G</p>
                </div>
                
                <div class="data-section">
                    <h3>System Information</h3>
                    <div class="data-item">
                        <span class="data-label">Reactor Status</span>
                        <span class="data-value">Online - Normal Operation</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">Core Temperature</span>
                        <span class="data-value">285°C</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">Power Output</span>
                        <span class="data-value">2,000 MW</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">Safety Rating</span>
                        <span class="data-value">Grade B+</span>
                    </div>
                </div>

                <?php if ($_SESSION['username'] === 'admin'): ?>
                <div class="flag-section">
                    <h3>🔐 Administrator Access Granted</h3>
                    <p style="margin-bottom: 10px;">Classified System Key:</p>
                    <div class="flag-value"><?php echo htmlspecialchars($flag); ?></div>
                </div>
                <?php endif; ?>
            </div>

        <?php else: ?>
            <div class="card">
                <h2>Welcome to Springfield Nuclear</h2>
                <div class="info-box">
                    <p>Secure employee portal for Springfield Nuclear Power Plant personnel.</p>
                </div>
                <p style="text-align: center; margin-top: 20px; color: #666;">
                    Please <a href="index.php?page=login" style="color: #4ecca3;">sign in</a> to access the system.
                </p>
            </div>
        <?php endif; ?>
    </div>

    <div class="footer">
        &copy; 2024 Springfield Nuclear Power Plant - All Rights Reserved
    </div>
</body>
</html>
