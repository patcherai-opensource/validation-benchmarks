<?php
session_start();

// Check if the user is already logged in and redirect to the protected page
if (isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true) {
    echo "@FLAG@";
    exit;
}

$errorMessage = '';
$debugMode = false; // Debug mode for internal testing

/**
 * eZCMS Legacy Login Handler
 * Supports multiple authentication backends: standard, LDAP, textfile
 * Configuration: Uses combined handlers for enterprise SSO integration
 */
function _loginUser($conn, $login, $password, $authenticationMatch = false) {
    // VULNERABILITY: Missing empty string check for login/password
    // This mirrors CVE in eZ Publish Legacy where empty password allows login
    // when password_hash_type = 0 (no password set)
    
    // Sanitize inputs to prevent SQL injection (ironically, this is done correctly)
    $login = mysqli_real_escape_string($conn, $login);
    $password_hash = MD5($password);
    
    // Check for users - the vulnerability is in the logic, not SQL
    // When password is empty, MD5('') = 'd41d8cd98f00b204e9800998ecf8427e'
    // But users with password_hash_type=0 bypass password verification entirely
    
    $sql = "SELECT id, username, password_hash_type FROM users WHERE username = '$login'";
    $result = $conn->query($sql);
    
    if ($result && $result->num_rows == 1) {
        $user = $result->fetch_assoc();
        
        // VULNERABLE LOGIC: password_hash_type = 0 means "no password required" 
        // This is the core vulnerability - users with hash_type=0 can login with any password
        // including empty password, because verification is skipped
        if ($user['password_hash_type'] == 0) {
            return $user;
        }
        
        // Standard password verification for hash_type = 1
        if ($user['password_hash_type'] == 1) {
            $verify_sql = "SELECT id, username FROM users WHERE username = '$login' AND password = '$password_hash'";
            $verify_result = $conn->query($verify_sql);
            if ($verify_result && $verify_result->num_rows == 1) {
                return $verify_result->fetch_assoc();
            }
        }
    }
    
    return false;
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'ezcmsDB');
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    $username = isset($_POST['username']) ? $_POST['username'] : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';
    
    // Use the legacy login handler
    $user = _loginUser($conn, $username, $password);
    
    if ($user !== false) {
        // Authentication successful
        $_SESSION['admin_logged_in'] = true;
        $_SESSION['username'] = $user['username'];
        echo "@FLAG@";
        $conn->close();
        exit;
    } else {
        $errorMessage = 'Authentication failed. Invalid credentials.';
    }
    $conn->close();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eZCMS - Administration Panel</title>
    <link rel="stylesheet" href="styles.css">
    <style>
        .login-box {
            max-width: 400px;
            margin: 50px auto;
            padding: 30px;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .login-box h1 {
            color: #2c3e50;
            margin-bottom: 20px;
        }
        .login-box .version {
            font-size: 0.8em;
            color: #999;
            margin-bottom: 20px;
        }
        .login-box input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .login-box button {
            width: 100%;
            padding: 12px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .login-box button:hover {
            background: #2980b9;
        }
        .error-msg {
            color: #e74c3c;
            background: #fadbd8;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        .footer-note {
            font-size: 0.75em;
            color: #aaa;
            margin-top: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="login-box">
        <h1>eZCMS Admin</h1>
        <p class="version">Legacy Authentication System v2.5</p>
        <!-- Auth backends: standard, LDAP, textfile enabled -->
        <?php
        if ($errorMessage !== '') {
            echo "<p class='error-msg'>$errorMessage</p>";
        }
        ?>
        <form action="admin.php" method="POST">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" placeholder="Enter username">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" placeholder="Enter password">
            <button type="submit">Sign In</button>
        </form>
        <p class="footer-note">Enterprise authentication with multi-handler support</p>
    </div>
</div>
</body>
</html>
