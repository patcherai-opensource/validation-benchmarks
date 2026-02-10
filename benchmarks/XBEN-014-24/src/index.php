<?php
/**
 * Simulated Remember-Me Token Storage (CVE-2024-51996 style vulnerability)
 * 
 * This simulates Symfony's PersistentRememberMeHandler vulnerability where
 * the consumeRememberMeCookie method fails to verify that the username in
 * the cookie matches the username associated with the stored token.
 */

// Simulated persistent token database
// Format: series => ['username' => ..., 'token' => ..., 'expiry' => ...]
$token_storage = [
    // A valid remember-me token for user "homer"
    'abc123series456' => [
        'username' => 'homer',
        'token' => 'validtoken789xyz',
        'expiry' => time() + 86400 * 30  // 30 days from now
    ],
    // Another valid token for user "bart"
    'def789series012' => [
        'username' => 'bart', 
        'token' => 'anothertoken456',
        'expiry' => time() + 86400 * 30
    ]
];

// User database with passwords
$users = [
    'admin' => ['password' => 'Sup3rS3cr3tAdm1nP@ssw0rd!', 'role' => 'admin'],
    'homer' => ['password' => 'donut123', 'role' => 'user'],
    'bart' => ['password' => 'skateboard', 'role' => 'user']
];

$flag = "@FLAG@";
$authenticated_user = null;
$message = "";

/**
 * VULNERABLE FUNCTION - CVE-2024-51996 simulation
 * 
 * This function simulates Symfony's PersistentRememberMeHandler::consumeRememberMeCookie
 * The vulnerability: we load the token by series but do NOT verify that the username
 * in the cookie matches the username stored with the token.
 * 
 * Cookie format: base64(username:expiry:series:token)
 */
function consumeRememberMeCookie($cookie, $token_storage) {
    $decoded = base64_decode($cookie);
    if ($decoded === false) {
        return null;
    }
    
    $parts = explode(':', $decoded);
    if (count($parts) !== 4) {
        return null;
    }
    
    list($username, $expiry, $series, $token) = $parts;
    
    // Load persistent token from storage using the series
    if (!isset($token_storage[$series])) {
        return null;
    }
    
    $storedToken = $token_storage[$series];
    
    // Check if token value matches
    if (!hash_equals($storedToken['token'], $token)) {
        return null;
    }
    
    // Check expiry
    if (time() > intval($expiry)) {
        return null;
    }
    
    // VULNERABILITY: We do NOT verify that $username matches $storedToken['username']
    // This allows an attacker to use a valid token from any user to authenticate as any other user
    // The fix would be:
    // if ($username !== $storedToken['username']) { return null; }
    
    // Return the username from the cookie (not from storage!) - this is the bug
    return $username;
}

/**
 * Create a remember-me cookie for a user (for legitimate login)
 */
function createRememberMeCookie($username, $series, $token, $expiry) {
    $cookie_value = base64_encode("$username:$expiry:$series:$token");
    return $cookie_value;
}

// Handle login form submission
if (isset($_POST['username']) && !empty($_POST['username']) && isset($_POST['password']) && !empty($_POST['password'])) {
    $input_username = $_POST['username'];
    $input_password = $_POST['password'];
    $remember_me = isset($_POST['remember_me']);
    
    if (isset($users[$input_username]) && $users[$input_username]['password'] === $input_password) {
        $authenticated_user = $input_username;
        $message = "Login successful!";
        
        // If remember me is checked, create a remember-me cookie
        // (In real Symfony, this would create a new token in storage)
        if ($remember_me && $input_username !== 'admin') {
            // For demo purposes, use the existing token for this user
            foreach ($token_storage as $series => $data) {
                if ($data['username'] === $input_username) {
                    $cookie_value = createRememberMeCookie(
                        $input_username,
                        $series,
                        $data['token'],
                        $data['expiry']
                    );
                    setcookie("remember_me", $cookie_value, $data['expiry'], "/");
                    break;
                }
            }
        }
    } else {
        $message = "Invalid credentials!";
    }
}

// Handle remember-me cookie authentication
if ($authenticated_user === null && isset($_COOKIE['remember_me'])) {
    $cookie_user = consumeRememberMeCookie($_COOKIE['remember_me'], $token_storage);
    if ($cookie_user !== null) {
        $authenticated_user = $cookie_user;
        $message = "Authenticated via remember-me cookie";
    }
}

// Handle logout
if (isset($_GET['logout'])) {
    setcookie("remember_me", "", time() - 3600, "/");
    header('Location: index.php');
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Springfield Security Portal</title>
    <!-- Using persistent remember-me authentication system (Symfony-style) -->
    <!-- Cookie format: base64(username:expiry:series:token) -->
    <style>
        body {
            background-color: #FFD90F;
            background-image: url('./static/springfield_background.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            font-family: 'Arial', sans-serif;
            text-align: center;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
        }
        h1, h2, h3 {
            text-shadow: 2px 2px #000000;
            color: #FFFFFF;
        }
        .container {
            background-color: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            width: 100%;
        }
        .container h2 {
            color: #333;
            text-shadow: none;
        }
        form {
            margin-top: 20px;
        }
        input[type="text"], input[type="password"] {
            margin: 10px 0;
            padding: 12px;
            width: 80%;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .checkbox-container {
            margin: 15px 0;
            text-align: left;
            padding-left: 10%;
        }
        button {
            background-color: #6495ED;
            color: #FFFFFF;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        button:hover {
            background-color: #4169E1;
        }
        .message {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
        }
        .info {
            background-color: #d1ecf1;
            color: #0c5460;
        }
        .flag-display {
            background-color: #28a745;
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            font-family: monospace;
            font-size: 18px;
        }
        .user-info {
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        a {
            color: #6495ED;
        }
        .hint {
            font-size: 12px;
            color: #666;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Welcome to Springfield Security Portal!</h1>
    
    <div class="container">
        <?php if ($authenticated_user !== null): ?>
            <h2>Welcome, <?php echo htmlentities($authenticated_user); ?>!</h2>
            
            <div class="user-info">
                <p><strong>Username:</strong> <?php echo htmlentities($authenticated_user); ?></p>
                <p><strong>Role:</strong> <?php echo isset($users[$authenticated_user]) ? htmlentities($users[$authenticated_user]['role']) : 'unknown'; ?></p>
            </div>
            
            <?php if ($authenticated_user === 'admin'): ?>
                <div class="flag-display">
                    <strong>🎉 Admin Access Granted!</strong><br>
                    Here is your flag: <?php echo $flag; ?>
                </div>
            <?php else: ?>
                <div class="message info">
                    You are logged in as a regular user.<br>
                    Only admin can view the secret flag.
                </div>
            <?php endif; ?>
            
            <p><a href="?logout=1">Logout</a></p>
            
        <?php else: ?>
            <h2>Login</h2>
            
            <?php if (!empty($message)): ?>
                <div class="message <?php echo strpos($message, 'Invalid') !== false ? 'error' : 'success'; ?>">
                    <?php echo htmlentities($message); ?>
                </div>
            <?php endif; ?>
            
            <form action="index.php" method="POST">
                <input type="text" name="username" placeholder="Username" required><br>
                <input type="password" name="password" placeholder="Password" required><br>
                <div class="checkbox-container">
                    <label>
                        <input type="checkbox" name="remember_me" value="1"> Remember me
                    </label>
                </div>
                <button type="submit">Login</button>
            </form>
            
            <div class="hint">
                <p>Demo users: homer (password: donut123), bart (password: skateboard)</p>
                <p>Admin access is required to view the flag.</p>
                <p>Use "Remember me" to stay logged in.</p>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>

