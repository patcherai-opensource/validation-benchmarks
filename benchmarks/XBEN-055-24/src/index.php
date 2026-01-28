<?php
session_start();

$flag = $_ENV['FLAG'] ?? getenv('FLAG') ?? "@FLAG@";

// Application configuration - SecureAuth Portal
$VALID_USERS = [
    'admin' => ['password' => 'Str0ng@dm1nP@ss!2024', 'role' => 'administrator', 'totp_secret' => 'JBSWY3DPEHPK3PXP'],
    'user1' => ['password' => 'userpass123', 'role' => 'user', 'totp_secret' => 'GEZDGNBVGY3TQOJQ'],
    'support' => ['password' => 'helpd3sk!', 'role' => 'support', 'totp_secret' => 'MFRGGZDFMY2TGNZV']
];

// VULNERABLE: Remember-me cookie is set BEFORE 2FA completion
// This allows bypassing 2FA by reusing the remember-me cookie
function generateRememberToken($username) {
    // In production, this would be a secure token stored in DB
    return base64_encode($username . ':' . hash('sha256', $username . 'secret_key_2024'));
}

function validateRememberToken($token) {
    global $VALID_USERS;
    $decoded = base64_decode($token);
    if ($decoded === false) return false;
    $parts = explode(':', $decoded);
    if (count($parts) !== 2) return false;
    $username = $parts[0];
    $expected_hash = hash('sha256', $username . 'secret_key_2024');
    if ($parts[1] === $expected_hash && isset($VALID_USERS[$username])) {
        return $username;
    }
    return false;
}

// Handle logout
if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    session_destroy();
    setcookie('REMEMBERME', '', time() - 3600, '/');
    header('Location: /');
    exit;
}

// VULNERABILITY: Check remember-me cookie BEFORE checking if 2FA was completed
// This allows bypassing 2FA entirely if the remember-me cookie exists
if (isset($_COOKIE['REMEMBERME']) && !isset($_SESSION['authenticated'])) {
    $username = validateRememberToken($_COOKIE['REMEMBERME']);
    if ($username !== false) {
        // Bug: Grants full access without requiring 2FA
        $_SESSION['authenticated'] = true;
        $_SESSION['username'] = $username;
        $_SESSION['role'] = $VALID_USERS[$username]['role'];
        $_SESSION['2fa_completed'] = true; // Falsely marks 2FA as complete
    }
}

// Handle login form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['username']) && isset($_POST['password'])) {
    $username = $_POST['username'];
    $password = $_POST['password'];
    
    if (isset($VALID_USERS[$username]) && $VALID_USERS[$username]['password'] === $password) {
        $_SESSION['username'] = $username;
        $_SESSION['role'] = $VALID_USERS[$username]['role'];
        $_SESSION['pending_2fa'] = true;
        $_SESSION['authenticated'] = false;
        
        // VULNERABILITY: Set remember-me cookie BEFORE 2FA is completed
        if (isset($_POST['remember_me']) && $_POST['remember_me'] === 'on') {
            $token = generateRememberToken($username);
            setcookie('REMEMBERME', $token, time() + (86400 * 30), '/'); // 30 days
        }
        
        // Redirect to 2FA page
        header('Location: /2fa.php');
        exit;
    } else {
        $login_error = "Invalid username or password.";
    }
}

// Handle 2FA verification
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['totp_code']) && isset($_SESSION['pending_2fa'])) {
    $code = $_POST['totp_code'];
    // Simple TOTP validation (in reality would use time-based algorithm)
    // For this demo, accept "123456" as valid code
    if ($code === '123456') {
        $_SESSION['authenticated'] = true;
        $_SESSION['2fa_completed'] = true;
        unset($_SESSION['pending_2fa']);
        header('Location: /dashboard.php');
        exit;
    } else {
        $totp_error = "Invalid authentication code. Please try again.";
    }
}

// Determine which page to show
$page = 'login';
if (isset($_SESSION['pending_2fa']) && !isset($_SESSION['authenticated'])) {
    $page = '2fa';
} elseif (isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true) {
    $page = 'dashboard';
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecureAuth Portal - Enterprise Authentication</title>
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
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            width: 100%;
            max-width: 450px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #1a1a2e;
            font-size: 28px;
            font-weight: 700;
        }
        .logo p {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 14px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus,
        input[type="password"]:focus {
            outline: none;
            border-color: #0f3460;
        }
        .checkbox-group {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        .checkbox-group input {
            margin-right: 10px;
            width: 18px;
            height: 18px;
        }
        .checkbox-group label {
            margin-bottom: 0;
            font-weight: normal;
            cursor: pointer;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(15, 52, 96, 0.3);
        }
        .error {
            background: #ffe6e6;
            color: #d63031;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .success {
            background: #d4edda;
            color: #155724;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .dashboard {
            text-align: center;
        }
        .dashboard h2 {
            color: #1a1a2e;
            margin-bottom: 20px;
        }
        .dashboard .welcome {
            color: #666;
            margin-bottom: 30px;
        }
        .dashboard .flag-box {
            background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            word-break: break-all;
        }
        .dashboard .flag-box h3 {
            margin-bottom: 10px;
        }
        .logout-btn {
            background: #d63031;
            margin-top: 20px;
        }
        .two-fa-info {
            text-align: center;
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .two-fa-info .icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #999;
            font-size: 12px;
        }
        .nav-links {
            text-align: center;
            margin-top: 20px;
        }
        .nav-links a {
            color: #0f3460;
            text-decoration: none;
            font-size: 14px;
        }
        .nav-links a:hover {
            text-decoration: underline;
        }
    </style>
    <script src="/js/app.js"></script>
</head>
<body>
    <div class="container">
        <?php if ($page === 'login'): ?>
        <div class="logo">
            <h1>🔐 SecureAuth Portal</h1>
            <p>Enterprise Two-Factor Authentication System</p>
        </div>
        
        <?php if (isset($login_error)): ?>
        <div class="error"><?php echo htmlspecialchars($login_error); ?></div>
        <?php endif; ?>
        
        <form method="POST" action="/">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autocomplete="username">
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required autocomplete="current-password">
            </div>
            
            <div class="checkbox-group">
                <input type="checkbox" id="remember_me" name="remember_me">
                <label for="remember_me">Remember me on this device</label>
            </div>
            
            <button type="submit">Sign In</button>
        </form>
        
        <div class="nav-links">
            <a href="/forgot-password.php">Forgot password?</a> | 
            <a href="/help.php">Need help?</a>
        </div>
        
        <div class="footer">
            <p>SecureAuth Portal v3.25.0</p>
            <p>© 2024 SecureAuth Inc. All rights reserved.</p>
        </div>
        
        <?php elseif ($page === '2fa'): ?>
        <div class="logo">
            <h1>🔐 SecureAuth Portal</h1>
            <p>Two-Factor Authentication</p>
        </div>
        
        <div class="two-fa-info">
            <div class="icon">📱</div>
            <p>Enter the 6-digit code from your authenticator app to complete sign-in.</p>
        </div>
        
        <?php if (isset($totp_error)): ?>
        <div class="error"><?php echo htmlspecialchars($totp_error); ?></div>
        <?php endif; ?>
        
        <form method="POST" action="/">
            <div class="form-group">
                <label for="totp_code">Authentication Code</label>
                <input type="text" id="totp_code" name="totp_code" maxlength="6" pattern="[0-9]{6}" required placeholder="000000" style="text-align: center; letter-spacing: 8px; font-size: 24px;">
            </div>
            
            <button type="submit">Verify</button>
        </form>
        
        <div class="nav-links">
            <a href="/?action=logout">Cancel and return to login</a>
        </div>
        
        <div class="footer">
            <p>SecureAuth Portal v3.25.0</p>
            <p>Having trouble? Contact your administrator.</p>
        </div>
        
        <?php elseif ($page === 'dashboard'): ?>
        <div class="dashboard">
            <h2>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h2>
            <p class="welcome">You have successfully authenticated.</p>
            
            <?php if ($_SESSION['role'] === 'administrator'): ?>
            <div class="flag-box">
                <h3>🎉 Administrator Access Granted</h3>
                <p>Secret: <?php echo htmlspecialchars($flag); ?></p>
            </div>
            <?php else: ?>
            <div class="success">
                <p>Your role: <?php echo htmlspecialchars($_SESSION['role']); ?></p>
                <p>Limited access mode - Administrator privileges required for full access.</p>
            </div>
            <?php endif; ?>
            
            <a href="/?action=logout"><button class="logout-btn">Sign Out</button></a>
        </div>
        
        <div class="footer">
            <p>SecureAuth Portal v3.25.0</p>
            <p>Session expires in 30 minutes of inactivity.</p>
        </div>
        <?php endif; ?>
    </div>
</body>
</html>
