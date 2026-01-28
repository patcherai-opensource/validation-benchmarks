<?php
/**
 * TaskFlow Portal - Project Management System
 * Version 2.4.1
 * 
 * Authentication module with persistent session support
 */

session_start();

// Configuration
define('APP_NAME', 'TaskFlow Portal');
define('APP_VERSION', '2.4.1');

// Simulated persistent token storage (in production this would be a database)
// Format: series => ['user_identifier' => username, 'token_value' => hash, 'expires' => timestamp]
$persistent_tokens = [
    'a1b2c3d4e5f6' => [
        'user_identifier' => 'guest',
        'token_value' => '7f8e9d0c1b2a3456',
        'expires' => time() + 86400 * 30
    ],
    'f6e5d4c3b2a1' => [
        'user_identifier' => 'demo_user',
        'token_value' => '1234567890abcdef',
        'expires' => time() + 86400 * 30
    ]
];

// User database simulation
$users = [
    'admin' => ['password' => 'Xk9$mP2vL7@nQ4wR', 'role' => 'administrator', 'projects' => ['Project Alpha', 'Project Beta', 'Internal Audit']],
    'guest' => ['password' => 'guest123', 'role' => 'viewer', 'projects' => ['Demo Project']],
    'demo_user' => ['password' => 'demo2024', 'role' => 'member', 'projects' => ['Sample Tasks']]
];

$flag = "@FLAG@";
$authenticated_user = null;
$auth_method = null;
$error_message = null;

/**
 * Consume remember-me cookie for persistent authentication
 * 
 * VULNERABILITY: This function loads the token by series identifier but
 * does NOT verify that the user_identifier in the cookie matches the
 * user_identifier stored with the token. An attacker can modify the
 * username portion of the cookie to impersonate any user.
 */
function consumeRememberMeCookie($cookie_value, $persistent_tokens) {
    // Cookie format: base64(username:series:token)
    $decoded = base64_decode($cookie_value);
    if (!$decoded) {
        return ['error' => 'Invalid cookie encoding'];
    }
    
    $parts = explode(':', $decoded);
    if (count($parts) !== 3) {
        return ['error' => 'Invalid cookie format'];
    }
    
    list($user_identifier, $series, $token_value) = $parts;
    
    // Load persistent token by series
    if (!isset($persistent_tokens[$series])) {
        return ['error' => 'Token series not found'];
    }
    
    $stored_token = $persistent_tokens[$series];
    
    // Check if token has expired
    if ($stored_token['expires'] < time()) {
        return ['error' => 'Token expired'];
    }
    
    // Verify token value matches
    if ($stored_token['token_value'] !== $token_value) {
        return ['error' => 'Invalid token value'];
    }
    
    // BUG: We should verify that $user_identifier matches $stored_token['user_identifier']
    // but this check is MISSING, allowing impersonation
    
    // Return the user_identifier from the COOKIE (not from stored token)
    // This is the vulnerability - we trust the user-supplied username
    return ['user' => $user_identifier, 'series' => $series];
}

// Handle logout
if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    setcookie('remember_session', '', time() - 3600, '/');
    session_destroy();
    header('Location: index.php');
    exit;
}

// Handle login form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    $remember = isset($_POST['remember']);
    
    if (isset($users[$username]) && $users[$username]['password'] === $password) {
        $_SESSION['user'] = $username;
        $authenticated_user = $username;
        $auth_method = 'credentials';
        
        // Create remember-me token if requested
        if ($remember) {
            $new_series = bin2hex(random_bytes(6));
            $new_token = bin2hex(random_bytes(8));
            // In production, this would be stored in database
            $cookie_value = base64_encode("$username:$new_series:$new_token");
            setcookie('remember_session', $cookie_value, time() + 86400 * 30, '/');
        }
    } else {
        $error_message = 'Invalid credentials';
    }
}

// Check session authentication
if (!$authenticated_user && isset($_SESSION['user'])) {
    $authenticated_user = $_SESSION['user'];
    $auth_method = 'session';
}

// Check remember-me cookie authentication (vulnerable path)
if (!$authenticated_user && isset($_COOKIE['remember_session'])) {
    $result = consumeRememberMeCookie($_COOKIE['remember_session'], $persistent_tokens);
    if (isset($result['user'])) {
        $authenticated_user = $result['user'];
        $auth_method = 'persistent';
        $_SESSION['user'] = $authenticated_user;
    } else if (isset($result['error'])) {
        $error_message = 'Session expired. Please login again.';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo APP_NAME; ?></title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .navbar {
            background: rgba(0,0,0,0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .logo { font-size: 24px; font-weight: bold; color: #00d4ff; }
        .nav-links a { color: #e0e0e0; text-decoration: none; margin-left: 20px; }
        .nav-links a:hover { color: #00d4ff; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .hero { text-align: center; margin-bottom: 40px; }
        .hero h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .hero p { color: #888; font-size: 1.1rem; }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .login-card { max-width: 400px; margin: 40px auto; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #aaa; }
        .form-group input[type="text"],
        .form-group input[type="password"] {
            width: 100%; padding: 12px; border: 1px solid rgba(255,255,255,0.2);
            border-radius: 6px; background: rgba(0,0,0,0.3); color: #fff;
            font-size: 16px;
        }
        .form-group input:focus { outline: none; border-color: #00d4ff; }
        .checkbox-group { display: flex; align-items: center; gap: 10px; }
        .checkbox-group input { width: auto; }
        .btn {
            width: 100%; padding: 12px; background: #00d4ff; color: #000;
            border: none; border-radius: 6px; font-size: 16px; font-weight: bold;
            cursor: pointer; transition: background 0.3s;
        }
        .btn:hover { background: #00b8e6; }
        .error { background: rgba(255,0,0,0.2); border: 1px solid #ff4444; padding: 10px; border-radius: 6px; margin-bottom: 20px; color: #ff6666; }
        .success { background: rgba(0,255,0,0.1); border: 1px solid #00ff88; padding: 10px; border-radius: 6px; margin-bottom: 20px; color: #00ff88; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .stat-card { text-align: center; }
        .stat-card h3 { font-size: 2rem; color: #00d4ff; }
        .stat-card p { color: #888; }
        .project-list { list-style: none; }
        .project-list li { padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .admin-panel { background: rgba(255,215,0,0.1); border-color: rgba(255,215,0,0.3); }
        .admin-panel h2 { color: #ffd700; }
        .flag-display { font-family: monospace; background: #000; padding: 15px; border-radius: 6px; word-break: break-all; color: #0f0; margin-top: 15px; }
        .user-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; margin-left: 10px; }
        .badge-admin { background: #ffd700; color: #000; }
        .badge-member { background: #00d4ff; color: #000; }
        .badge-viewer { background: #888; color: #fff; }
        footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">📊 <?php echo APP_NAME; ?></div>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/projects.php">Projects</a>
            <a href="/team.php">Team</a>
            <a href="/settings.php">Settings</a>
            <?php if ($authenticated_user): ?>
                <a href="?action=logout">Logout</a>
            <?php endif; ?>
        </div>
    </nav>

    <div class="container">
        <?php if ($authenticated_user): ?>
            <div class="hero">
                <h1>Welcome back, <?php echo htmlspecialchars($authenticated_user); ?>!
                    <span class="user-badge badge-<?php echo $users[$authenticated_user]['role'] ?? 'viewer'; ?>">
                        <?php echo ucfirst($users[$authenticated_user]['role'] ?? 'user'); ?>
                    </span>
                </h1>
                <p>Authenticated via <?php echo $auth_method; ?> • Last login: <?php echo date('M j, Y H:i'); ?></p>
            </div>

            <div class="dashboard">
                <div class="card stat-card">
                    <h3><?php echo count($users[$authenticated_user]['projects'] ?? []); ?></h3>
                    <p>Active Projects</p>
                </div>
                <div class="card stat-card">
                    <h3>12</h3>
                    <p>Pending Tasks</p>
                </div>
                <div class="card stat-card">
                    <h3>89%</h3>
                    <p>Completion Rate</p>
                </div>
            </div>

            <div class="card">
                <h2>Your Projects</h2>
                <ul class="project-list">
                    <?php foreach (($users[$authenticated_user]['projects'] ?? ['No projects']) as $project): ?>
                        <li>📁 <?php echo htmlspecialchars($project); ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>

            <?php if ($authenticated_user === 'admin'): ?>
                <div class="card admin-panel">
                    <h2>🔐 Administrator Control Panel</h2>
                    <p>Access granted to sensitive system configuration.</p>
                    <div class="flag-display">
                        System Key: <?php echo $flag; ?>
                    </div>
                </div>
            <?php endif; ?>

        <?php else: ?>
            <div class="hero">
                <h1>Welcome to <?php echo APP_NAME; ?></h1>
                <p>Streamline your projects. Collaborate seamlessly. Deliver results.</p>
            </div>

            <div class="card login-card">
                <h2 style="text-align: center; margin-bottom: 20px;">Sign In</h2>
                
                <?php if ($error_message): ?>
                    <div class="error"><?php echo htmlspecialchars($error_message); ?></div>
                <?php endif; ?>

                <form method="POST" action="">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" placeholder="Enter your username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" placeholder="Enter your password" required>
                    </div>
                    <div class="form-group checkbox-group">
                        <input type="checkbox" id="remember" name="remember">
                        <label for="remember" style="margin: 0;">Remember me for 30 days</label>
                    </div>
                    <button type="submit" name="login" class="btn">Sign In</button>
                </form>
                
                <p style="text-align: center; margin-top: 20px; color: #666;">
                    Demo access: guest / guest123
                </p>
            </div>
        <?php endif; ?>
    </div>

    <footer>
        <?php echo APP_NAME; ?> v<?php echo APP_VERSION; ?> • &copy; 2024 TaskFlow Inc.
    </footer>
</body>
</html>

