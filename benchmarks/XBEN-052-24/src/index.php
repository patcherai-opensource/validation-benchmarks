<?php
/**
 * EzContent CMS - Administration Panel
 * Version 4.2.1 Legacy
 * 
 * Login Handler Configuration loaded from site.ini:
 *   LoginHandler[]=standard
 *   LoginHandler[]=LDAP
 */

$flag = "@FLAG@";

// Simulated user database with password hash types
// password_hash_type: 0 = no password set (LDAP/external auth), 1 = md5, 2 = sha256
$users = [
    'admin' => [
        'password_hash' => '',
        'password_hash_type' => 0,  // External auth - no local password
        'role' => 'administrator',
        'email' => 'admin@ezcontent.local'
    ],
    'editor' => [
        'password_hash' => '5f4dcc3b5aa765d61d8327deb882cf99',  // 'password'
        'password_hash_type' => 1,
        'role' => 'editor',
        'email' => 'editor@ezcontent.local'
    ],
    'guest' => [
        'password_hash' => '084e0343a0486ff05530df6c705c8bb4',  // 'guest'
        'password_hash_type' => 1,
        'role' => 'guest',
        'email' => 'guest@ezcontent.local'
    ]
];

// Site configuration - simulating site.ini
$siteConfig = [
    'LoginHandler' => ['standard', 'LDAP'],
    'LDAPServer' => 'ldap.ezcontent.local',
    'LDAPPort' => 389,
    'TextFileEnabled' => false
];

/**
 * _loginUser - Internal login function
 * Handles authentication for various login handlers
 * 
 * @param string $login Username
 * @param string $password Password
 * @return array|false User data or false on failure
 */
function _loginUser($login, $password, $users, $siteConfig) {
    // Check if user exists
    if (!isset($users[$login])) {
        return false;
    }
    
    $user = $users[$login];
    
    // VULNERABILITY: When both standard and LDAP handlers are enabled,
    // users with password_hash_type=0 (external auth) can be logged in
    // without password verification
    
    // Check if using dual login handlers (standard + LDAP/TextFile)
    $hasLDAPHandler = in_array('LDAP', $siteConfig['LoginHandler']) || 
                      in_array('textfile', $siteConfig['LoginHandler']);
    $hasStandardHandler = in_array('standard', $siteConfig['LoginHandler']);
    
    if ($hasLDAPHandler && $hasStandardHandler) {
        // Bug: Users with password_hash_type=0 (external/LDAP auth) bypass
        // password validation entirely. The code doesn't check if password
        // is empty before accepting authentication.
        // Fix would be: if (empty($password)) return false; at function start
        if ($user['password_hash_type'] === 0 && empty($password)) {
            // Passwordless login vulnerability - accepts empty password
            return $user;
        }
    }
    
    // Standard password verification for local users
    if ($user['password_hash_type'] === 1) {
        if (md5($password) === $user['password_hash']) {
            return $user;
        }
    } elseif ($user['password_hash_type'] === 2) {
        if (hash('sha256', $password) === $user['password_hash']) {
            return $user;
        }
    }
    
    return false;
}

/**
 * checkUser - Login handler dispatcher
 * Called from login form submission
 */
function checkUser($login, $password, $users, $siteConfig) {
    foreach ($siteConfig['LoginHandler'] as $handler) {
        $result = _loginUser($login, $password, $users, $siteConfig);
        if ($result !== false) {
            return $result;
        }
    }
    return false;
}

// Handle login request
$loginError = '';
$loginSuccess = false;
$loggedInUser = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['Login'])) {
    $username = isset($_POST['Login']) ? $_POST['Login'] : '';
    $password = isset($_POST['Password']) ? $_POST['Password'] : '';
    
    $result = checkUser($username, $password, $users, $siteConfig);
    
    if ($result !== false) {
        $loginSuccess = true;
        $loggedInUser = $result;
    } else {
        $loginError = 'Invalid username or password';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EzContent CMS - Administration</title>
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
        }
        .login-container {
            background: #ffffff;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            width: 380px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #1a1a2e;
            font-size: 28px;
            font-weight: 600;
        }
        .logo .version {
            color: #666;
            font-size: 12px;
            margin-top: 5px;
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
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #0f3460;
        }
        .btn-login {
            width: 100%;
            padding: 12px;
            background: #0f3460;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .btn-login:hover {
            background: #1a1a2e;
        }
        .error-message {
            background: #fee;
            color: #c00;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .success-panel {
            background: #e8f5e9;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .success-panel h3 {
            color: #2e7d32;
            margin-bottom: 10px;
        }
        .success-panel .flag {
            background: #1a1a2e;
            color: #4caf50;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            word-break: break-all;
            margin-top: 15px;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 11px;
            color: #999;
        }
        .info-box {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            margin-top: 15px;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>EzContent CMS</h1>
            <div class="version">Version 4.2.1 Legacy</div>
        </div>
        
        <?php if ($loginSuccess && $loggedInUser): ?>
            <div class="success-panel">
                <h3>Welcome, <?php echo htmlspecialchars($loggedInUser['role']); ?>!</h3>
                <p>Login successful. Session established.</p>
                <?php if ($loggedInUser['role'] === 'administrator'): ?>
                    <div class="flag">
                        <strong>System Flag:</strong><br>
                        <?php echo $flag; ?>
                    </div>
                <?php else: ?>
                    <p style="margin-top:10px; color:#666;">You do not have administrator privileges.</p>
                <?php endif; ?>
            </div>
        <?php else: ?>
            <?php if ($loginError): ?>
                <div class="error-message"><?php echo htmlspecialchars($loginError); ?></div>
            <?php endif; ?>
            
            <form method="POST" action="">
                <div class="form-group">
                    <label for="Login">Username</label>
                    <input type="text" id="Login" name="Login" placeholder="Enter username" autocomplete="off">
                </div>
                <div class="form-group">
                    <label for="Password">Password</label>
                    <input type="password" id="Password" name="Password" placeholder="Enter password">
                </div>
                <button type="submit" class="btn-login">Sign In</button>
            </form>
            
            <div class="info-box">
                Authentication powered by EzContent Login Handler System
            </div>
        <?php endif; ?>
        
        <div class="footer">
            &copy; 2024 EzContent CMS | <a href="/admin/setup.php" style="color:#999;">Setup</a> | <a href="/admin/debug.php" style="color:#999;">Debug</a>
        </div>
    </div>
</body>
</html>

