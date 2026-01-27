<?php
/**
 * eZContent Legacy CMS - Administration Panel
 * Version: 4.7.2
 * 
 * Login handler supporting multiple authentication backends:
 * - Standard database authentication
 * - LDAP authentication  
 * - TextFile authentication
 * 
 * Configuration: site.ini [UserSettings] LoginHandler[]=standard,LDAP
 */

$flag = "@FLAG@";

// Simulated user database with different password hash types
// password_hash_type: 0 = plaintext/none, 1 = md5, 2 = password_hash
$users = array(
    'admin' => array(
        'login' => 'admin',
        'email' => 'admin@ezcontent.local',
        'password_hash' => '', // Empty - created via LDAP sync
        'password_hash_type' => 0, // Type 0 = no password set (LDAP/external auth)
        'role' => 'Administrator',
        'is_enabled' => true
    ),
    'editor' => array(
        'login' => 'editor',
        'email' => 'editor@ezcontent.local', 
        'password_hash' => '5f4dcc3b5aa765d61d8327deb882cf99', // "password"
        'password_hash_type' => 1, // MD5
        'role' => 'Editor',
        'is_enabled' => true
    ),
    'guest' => array(
        'login' => 'guest',
        'email' => 'guest@ezcontent.local',
        'password_hash' => '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', // "password"
        'password_hash_type' => 2, // password_hash
        'role' => 'Guest',
        'is_enabled' => true
    )
);

/**
 * Authenticates a user - VULNERABLE VERSION
 * Bug: Does not properly check for empty passwords when password_hash_type = 0
 * 
 * This mimics the vulnerability in eZ Publish Legacy kernel/classes/datatypes/ezuser/ezuser.php
 * in the _loginUser() function
 */
function _loginUser($login, $password, $users) {
    // VULNERABILITY: Missing check for empty login or password
    // The fix should include:
    // if (empty($login) || empty($password)) { return false; }
    
    if (!isset($users[$login])) {
        return false;
    }
    
    $user = $users[$login];
    
    if (!$user['is_enabled']) {
        return false;
    }
    
    // VULNERABILITY: When password_hash_type is 0, we accept ANY password including empty
    // This simulates users synced from LDAP that have no local password set
    switch ($user['password_hash_type']) {
        case 0:
            // BUG: Should require password validation via LDAP/external auth
            // Instead, we're accepting the login without proper verification
            // This is the core vulnerability - empty password hash matches empty password
            return $user;
            
        case 1: // MD5 hash
            if (md5($password) === $user['password_hash']) {
                return $user;
            }
            break;
            
        case 2: // password_hash
            if (password_verify($password, $user['password_hash'])) {
                return $user;
            }
            break;
    }
    
    return false;
}

$login_error = '';
$authenticated_user = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['Login']) && isset($_POST['Password'])) {
    $login = $_POST['Login'];
    $password = $_POST['Password'];
    
    // Attempt authentication through the login handler chain
    $authenticated_user = _loginUser($login, $password, $users);
    
    if ($authenticated_user === false) {
        $login_error = 'Invalid username or password. Please check your credentials.';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eZContent Legacy CMS - Administration</title>
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
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            width: 400px;
            overflow: hidden;
        }
        .login-header {
            background: #2c3e50;
            color: white;
            padding: 25px;
            text-align: center;
        }
        .login-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        .login-header .version {
            font-size: 12px;
            opacity: 0.7;
        }
        .login-form {
            padding: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #34495e;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #3498db;
        }
        .btn-login {
            width: 100%;
            padding: 14px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .btn-login:hover {
            background: #2980b9;
        }
        .error-message {
            background: #fee;
            border: 1px solid #fcc;
            color: #c00;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .success-panel {
            background: #e8f5e9;
            border: 1px solid #a5d6a7;
            padding: 20px;
            border-radius: 4px;
            text-align: center;
        }
        .success-panel h2 {
            color: #2e7d32;
            margin-bottom: 10px;
        }
        .success-panel .role {
            color: #388e3c;
            font-size: 14px;
            margin-bottom: 15px;
        }
        .success-panel .flag {
            background: #1b5e20;
            color: #fff;
            padding: 15px;
            border-radius: 4px;
            font-family: monospace;
            word-break: break-all;
        }
        .login-footer {
            padding: 15px;
            background: #f8f9fa;
            text-align: center;
            font-size: 12px;
            color: #7f8c8d;
            border-top: 1px solid #eee;
        }
        .info-note {
            font-size: 11px;
            color: #95a5a6;
            margin-top: 15px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>eZContent Legacy CMS</h1>
            <div class="version">Administration Panel v4.7.2</div>
        </div>
        
        <div class="login-form">
            <?php if ($authenticated_user): ?>
                <div class="success-panel">
                    <h2>Welcome, <?php echo htmlspecialchars($authenticated_user['login']); ?>!</h2>
                    <div class="role">Role: <?php echo htmlspecialchars($authenticated_user['role']); ?></div>
                    
                    <?php if ($authenticated_user['role'] === 'Administrator'): ?>
                        <p style="margin-bottom: 10px; color: #2e7d32;">Access granted to system configuration:</p>
                        <div class="flag"><?php echo htmlspecialchars($flag); ?></div>
                    <?php else: ?>
                        <p style="color: #666;">You do not have administrator privileges.</p>
                        <p style="color: #999; font-size: 12px; margin-top: 10px;">Contact your system administrator for elevated access.</p>
                    <?php endif; ?>
                </div>
            <?php else: ?>
                <?php if ($login_error): ?>
                    <div class="error-message"><?php echo htmlspecialchars($login_error); ?></div>
                <?php endif; ?>
                
                <form method="POST" action="">
                    <div class="form-group">
                        <label for="Login">Username</label>
                        <input type="text" id="Login" name="Login" placeholder="Enter your username" autocomplete="username">
                    </div>
                    
                    <div class="form-group">
                        <label for="Password">Password</label>
                        <input type="password" id="Password" name="Password" placeholder="Enter your password" autocomplete="current-password">
                    </div>
                    
                    <button type="submit" class="btn-login">Sign In</button>
                </form>
                
                <p class="info-note">Authentication: Standard + LDAP handlers enabled</p>
            <?php endif; ?>
        </div>
        
        <div class="login-footer">
            &copy; 2024 eZContent Systems | Powered by eZ Publish Legacy
        </div>
    </div>
</body>
</html>

