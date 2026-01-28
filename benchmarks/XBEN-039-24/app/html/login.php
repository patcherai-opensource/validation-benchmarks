<?php
session_start();

// Check if the user is already logged in
if (isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true) {
    header("Location: admin.php");
    exit;
}

$errorMessage = '';
$infoMessage = '';

/**
 * ezPortal CMS User Authentication Module
 * Supports multiple authentication handlers: standard, ldap, textfile
 * 
 * Handler configuration is set in site.ini:
 * LoginHandler[]=standard
 * LoginHandler[]=ldap
 */

// Simulated login handler configuration
$enabledHandlers = array('standard', 'ldap');

/**
 * Standard login handler - authenticates against local database
 */
function standardLoginHandler($conn, $login, $password) {
    if (empty($login)) {
        return false;
    }
    
    $login = $conn->real_escape_string($login);
    $password_hash = md5($password);
    
    $sql = "SELECT id, username, role, password_hash_type FROM users WHERE username = '$login' AND password = '$password_hash' AND password_hash_type = 1";
    $result = $conn->query($sql);
    
    if ($result && $result->num_rows == 1) {
        return $result->fetch_assoc();
    }
    return false;
}

/**
 * LDAP login handler - authenticates against LDAP directory
 * Falls back to local user record if LDAP is unavailable
 * 
 * VULNERABILITY: This function does not verify if password is empty before
 * attempting database lookup for users with password_hash_type = 0 (LDAP users)
 */
function ldapLoginHandler($conn, $login, $password) {
    // LDAP authentication would go here
    // For users with password_hash_type = 0, password is managed externally
    
    // BUG: Missing check for empty password!
    // The original code should reject empty passwords, but due to a logic flaw
    // when LDAP handler is enabled alongside standard handler, users with
    // password_hash_type = 0 can be logged in without password verification
    
    if (empty($login)) {
        return false;
    }
    
    $login = $conn->real_escape_string($login);
    
    // Query for LDAP-managed users (password_hash_type = 0)
    // The flaw: we don't verify the password for these users when password is empty
    $sql = "SELECT id, username, role, password_hash_type FROM users WHERE username = '$login' AND password_hash_type = 0";
    $result = $conn->query($sql);
    
    if ($result && $result->num_rows == 1) {
        // BUG: Should verify password against LDAP, but if password is empty
        // and LDAP is unavailable, this incorrectly returns success
        return $result->fetch_assoc();
    }
    return false;
}

/**
 * Main login user function
 * Iterates through enabled handlers to authenticate
 */
function _loginUser($conn, $login, $password, $handlers) {
    // NOTE: The fix would add: if (empty($login) || empty($password)) return false;
    // But this check is missing in vulnerable version
    
    foreach ($handlers as $handler) {
        $user = false;
        
        switch ($handler) {
            case 'standard':
                $user = standardLoginHandler($conn, $login, $password);
                break;
            case 'ldap':
                $user = ldapLoginHandler($conn, $login, $password);
                break;
        }
        
        if ($user !== false) {
            return $user;
        }
    }
    
    return false;
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'blogDB');
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    $login = isset($_POST['login']) ? $_POST['login'] : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';
    
    // Attempt authentication through enabled handlers
    $user = _loginUser($conn, $login, $password, $enabledHandlers);
    
    if ($user !== false) {
        $_SESSION['admin_logged_in'] = true;
        $_SESSION['username'] = $user['username'];
        $_SESSION['role'] = $user['role'];
        header("Location: admin.php");
        exit;
    } else {
        $errorMessage = 'Invalid username or password.';
    }
    
    $conn->close();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ezPortal CMS - Staff Login</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>ezPortal CMS</h1>
        <p class="tagline">Staff Authentication Portal</p>
    </div>
    
    <div class="login-box">
        <h2>Staff Login</h2>
        
        <?php if ($errorMessage !== ''): ?>
            <div class="error-message"><?php echo htmlspecialchars($errorMessage); ?></div>
        <?php endif; ?>
        
        <?php if ($infoMessage !== ''): ?>
            <div class="info-message"><?php echo htmlspecialchars($infoMessage); ?></div>
        <?php endif; ?>
        
        <form action="login.php" method="POST" class="login-form">
            <div class="form-group">
                <label for="login">Username:</label>
                <input type="text" id="login" name="login" autocomplete="username">
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" autocomplete="current-password">
            </div>
            <button type="submit" class="login-btn">Sign In</button>
        </form>
        
        <div class="login-info">
            <p><small>Authentication via: Standard Database, LDAP Directory</small></p>
        </div>
    </div>
    
    <div class="back-link">
        <a href="index.php">&larr; Back to Homepage</a>
    </div>
    
    <footer>
        <p>&copy; 2024 ezPortal CMS. All rights reserved.</p>
    </footer>
</div>
</body>
</html>
