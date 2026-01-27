<?php
/**
 * SecureAuth Portal - Persistent Session Management
 * Uses remember-me tokens for enhanced user experience
 */

$flag = "@FLAG@";
$tokenStorageFile = '/tmp/remember_tokens.json';

// User database (in production, this would be in a real database)
$users = [
    'admin' => ['password' => 'Xt7$kLm9@pQr2#Wz', 'role' => 'administrator'],
    'guest' => ['password' => 'guest123', 'role' => 'viewer'],
    'support' => ['password' => 'support2024!', 'role' => 'support']
];

// Initialize token storage if not exists
function initTokenStorage($file) {
    if (!file_exists($file)) {
        // Pre-populate with a valid guest token for demo purposes
        $initialTokens = [
            'ser_7f3a9b2c' => [
                'username' => 'guest',
                'token' => 'tok_x8k2m9p4q7',
                'expires' => time() + 86400 * 30
            ]
        ];
        file_put_contents($file, json_encode($initialTokens));
    }
}

function loadTokens($file) {
    initTokenStorage($file);
    return json_decode(file_get_contents($file), true);
}

function saveTokens($file, $tokens) {
    file_put_contents($file, json_encode($tokens));
}

function generateSeries() {
    return 'ser_' . bin2hex(random_bytes(4));
}

function generateToken() {
    return 'tok_' . bin2hex(random_bytes(5));
}

// Parse remember-me cookie: format is username:series:token:expiry
function parseRememberMeCookie($cookieValue) {
    $decoded = base64_decode($cookieValue);
    $parts = explode(':', $decoded);
    if (count($parts) !== 4) {
        return null;
    }
    return [
        'username' => $parts[0],
        'series' => $parts[1],
        'token' => $parts[2],
        'expiry' => (int)$parts[3]
    ];
}

// Create remember-me cookie value
function createRememberMeCookie($username, $series, $token, $expiry) {
    return base64_encode("{$username}:{$series}:{$token}:{$expiry}");
}

// VULNERABLE: consumeRememberMeCookie - Does not verify username matches stored token's owner
function consumeRememberMeCookie($cookieData, $tokenStorageFile) {
    $tokens = loadTokens($tokenStorageFile);
    
    $series = $cookieData['series'];
    $providedToken = $cookieData['token'];
    $username = $cookieData['username']; // Username from cookie - NOT VERIFIED against stored token!
    
    // Check if series exists in storage
    if (!isset($tokens[$series])) {
        return ['valid' => false, 'error' => 'Invalid session series'];
    }
    
    $storedData = $tokens[$series];
    
    // Check expiry
    if ($storedData['expires'] < time()) {
        unset($tokens[$series]);
        saveTokens($tokenStorageFile, $tokens);
        return ['valid' => false, 'error' => 'Session expired'];
    }
    
    // Verify token value matches
    if ($storedData['token'] !== $providedToken) {
        // Possible token theft - invalidate series
        unset($tokens[$series]);
        saveTokens($tokenStorageFile, $tokens);
        return ['valid' => false, 'error' => 'Token mismatch - possible session hijacking detected'];
    }
    
    // BUG: We should verify $username === $storedData['username'] but we don't!
    // This allows an attacker to use a valid series+token from one user
    // while specifying a different username in the cookie
    
    // Rotate token for security
    $newToken = generateToken();
    $tokens[$series]['token'] = $newToken;
    saveTokens($tokenStorageFile, $tokens);
    
    // Return the username from the cookie (VULNERABILITY!)
    return [
        'valid' => true, 
        'username' => $username, // Should be $storedData['username'] for security
        'newToken' => $newToken,
        'series' => $series,
        'expiry' => $storedData['expires']
    ];
}

// Handle login form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['username']) && isset($_POST['password'])) {
    $username = $_POST['username'];
    $password = $_POST['password'];
    $rememberMe = isset($_POST['remember_me']);
    
    if (isset($users[$username]) && $users[$username]['password'] === $password) {
        // Create remember-me token if requested
        if ($rememberMe) {
            $tokens = loadTokens($tokenStorageFile);
            $series = generateSeries();
            $token = generateToken();
            $expiry = time() + 86400 * 30; // 30 days
            
            $tokens[$series] = [
                'username' => $username,
                'token' => $token,
                'expires' => $expiry
            ];
            saveTokens($tokenStorageFile, $tokens);
            
            $cookieValue = createRememberMeCookie($username, $series, $token, $expiry);
            setcookie('remember_me', $cookieValue, $expiry, '/');
        }
        
        header('Location: index.php?login=success');
        exit;
    } else {
        header('Location: index.php?error=invalid_credentials');
        exit;
    }
}

// Handle logout
if (isset($_GET['logout'])) {
    setcookie('remember_me', '', time() - 3600, '/');
    header('Location: index.php?logout=success');
    exit;
}

$currentUser = null;
$loginError = null;
$loginMessage = null;

// Process remember-me cookie
if (isset($_COOKIE['remember_me'])) {
    $cookieData = parseRememberMeCookie($_COOKIE['remember_me']);
    if ($cookieData) {
        $result = consumeRememberMeCookie($cookieData, $tokenStorageFile);
        if ($result['valid']) {
            $currentUser = $result['username'];
            // Update cookie with new token
            $newCookie = createRememberMeCookie(
                $result['username'], 
                $result['series'], 
                $result['newToken'], 
                $result['expiry']
            );
            setcookie('remember_me', $newCookie, $result['expiry'], '/');
        } else {
            $loginError = $result['error'];
            setcookie('remember_me', '', time() - 3600, '/');
        }
    }
}

if (isset($_GET['error'])) {
    $loginError = $_GET['error'] === 'invalid_credentials' ? 'Invalid username or password' : $_GET['error'];
}
if (isset($_GET['login']) && $_GET['login'] === 'success') {
    $loginMessage = 'Login successful!';
}
if (isset($_GET['logout']) && $_GET['logout'] === 'success') {
    $loginMessage = 'You have been logged out.';
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecureAuth Portal</title>
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
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
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
        .alert {
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .alert-error {
            background: #fee2e2;
            color: #dc2626;
            border: 1px solid #fecaca;
        }
        .alert-success {
            background: #d1fae5;
            color: #059669;
            border: 1px solid #a7f3d0;
        }
        .alert-info {
            background: #dbeafe;
            color: #2563eb;
            border: 1px solid #bfdbfe;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            color: #374151;
            font-weight: 500;
            margin-bottom: 8px;
            font-size: 14px;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 14px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 15px;
            transition: all 0.3s ease;
        }
        input[type="text"]:focus, input[type="password"]:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 24px;
        }
        .checkbox-group input {
            width: 18px;
            height: 18px;
            accent-color: #3b82f6;
        }
        .checkbox-group label {
            margin-bottom: 0;
            font-weight: 400;
            color: #6b7280;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
        }
        .user-panel {
            text-align: center;
        }
        .user-panel .avatar {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0 auto 20px;
            font-size: 32px;
            color: white;
        }
        .user-panel h2 {
            color: #1a1a2e;
            margin-bottom: 10px;
        }
        .user-panel .role {
            display: inline-block;
            padding: 6px 16px;
            background: #e0e7ff;
            color: #4f46e5;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 20px;
        }
        .user-panel .role.admin {
            background: #fef3c7;
            color: #d97706;
        }
        .flag-display {
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
        }
        .flag-display h3 {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        .flag-display code {
            font-family: 'Courier New', monospace;
            font-size: 14px;
            word-break: break-all;
        }
        .logout-btn {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            margin-top: 15px;
        }
        .footer {
            text-align: center;
            margin-top: 25px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            color: #9ca3af;
            font-size: 12px;
        }
        /* Debug info styling - visible for transparency */
        .debug-panel {
            background: #f3f4f6;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            font-size: 12px;
            color: #6b7280;
        }
        .debug-panel h4 {
            color: #374151;
            margin-bottom: 10px;
        }
        .debug-panel code {
            display: block;
            background: #e5e7eb;
            padding: 8px;
            border-radius: 4px;
            word-break: break-all;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>🔐 SecureAuth Portal</h1>
            <p>Enterprise Session Management System</p>
        </div>

        <?php if ($loginError): ?>
            <div class="alert alert-error"><?php echo htmlspecialchars($loginError); ?></div>
        <?php endif; ?>
        
        <?php if ($loginMessage): ?>
            <div class="alert alert-success"><?php echo htmlspecialchars($loginMessage); ?></div>
        <?php endif; ?>

        <?php if ($currentUser): ?>
            <div class="user-panel">
                <div class="avatar"><?php echo strtoupper(substr($currentUser, 0, 1)); ?></div>
                <h2>Welcome, <?php echo htmlspecialchars($currentUser); ?>!</h2>
                <?php 
                $role = isset($users[$currentUser]) ? $users[$currentUser]['role'] : 'unknown';
                $isAdmin = ($currentUser === 'admin');
                ?>
                <span class="role <?php echo $isAdmin ? 'admin' : ''; ?>"><?php echo htmlspecialchars($role); ?></span>
                
                <?php if ($isAdmin): ?>
                    <div class="flag-display">
                        <h3>🎉 Administrator Access Granted</h3>
                        <code><?php echo htmlspecialchars($flag); ?></code>
                    </div>
                <?php else: ?>
                    <div class="alert alert-info">
                        You are logged in with limited access. Administrator privileges required for full access.
                    </div>
                <?php endif; ?>
                
                <form method="GET">
                    <input type="hidden" name="logout" value="1">
                    <button type="submit" class="logout-btn">Logout</button>
                </form>
            </div>
            
            <?php if (isset($_COOKIE['remember_me'])): ?>
            <div class="debug-panel">
                <h4>Session Debug Info</h4>
                <p>Current remember_me cookie:</p>
                <code><?php echo htmlspecialchars($_COOKIE['remember_me']); ?></code>
                <p style="margin-top: 10px;">Decoded format: username:series:token:expiry</p>
            </div>
            <?php endif; ?>
            
        <?php else: ?>
            <form method="POST" action="index.php">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" placeholder="Enter your username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" placeholder="Enter your password" required>
                </div>
                <div class="checkbox-group">
                    <input type="checkbox" id="remember_me" name="remember_me" value="1">
                    <label for="remember_me">Keep me signed in (30 days)</label>
                </div>
                <button type="submit">Sign In</button>
            </form>
            
            <div class="footer">
                <p>Demo accounts available: guest / guest123</p>
                <p style="margin-top: 5px;">© 2024 SecureAuth Systems</p>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>

