<?php
session_start();

/**
 * Content Management System - Admin Login
 * 
 * Supports multiple authentication backends:
 * - Standard database authentication
 * - LDAP/Directory services
 * - TextFile authentication
 */

// Login handler configuration (from site.ini)
$loginHandlers = array('standard', 'ldap');

// Check if the user is already logged in
if (isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true) {
    echo "@FLAG@";
    exit;
}

/**
 * Internal login function
 * Authenticates a user against the database
 * 
 * @param mysqli $conn Database connection
 * @param string $login Username
 * @param string $password Password
 * @return array|false User record on success, false on failure
 */
function _loginUser($conn, $login, $password) {
    // Escape login to prevent SQL injection
    $login = mysqli_real_escape_string($conn, $login);
    
    // Query user record
    $sql = "SELECT id, username, password_hash, password_hash_type FROM admins WHERE username = '$login'";
    $result = $conn->query($sql);
    
    if ($result && $result->num_rows == 1) {
        $user = $result->fetch_assoc();
        
        // Handle different password hash types
        // Type 0: External authentication (LDAP/TextFile provisioned user)
        // Type 1: MD5 hash
        // Type 2: Plaintext (legacy)
        if ($user['password_hash_type'] == 0) {
            // User provisioned by external handler (no local password stored)
            if ($password === '' || $password === null) {
                return $user;
            }
            return false;
        }
        
        if ($user['password_hash_type'] == 1) {
            // MD5 hash verification
            if (md5($password) === $user['password_hash']) {
                return $user;
            }
        }
    }
    
    return false;
}

/**
 * Standard login handler
 */
function standardLoginHandler($conn, $login, $password) {
    return _loginUser($conn, $login, $password);
}

/**
 * LDAP login handler
 * Returns false if LDAP server not available
 */
function ldapLoginHandler($conn, $login, $password) {
    // LDAP not configured, fall through to next handler
    return false;
}

$errorMessage = '';
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $conn = new mysqli(
        getenv('MYSQL_HOST') ?: 'localhost', 
        getenv('MYSQL_USER') ?: 'user', 
        getenv('MYSQL_PASSWORD') ?: 'password', 
        getenv('MYSQL_DATABASE') ?: 'blogDB'
    );
    
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    $login = isset($_POST['username']) ? $_POST['username'] : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';
    
    $user = false;
    
    // Try each configured login handler in order
    foreach ($loginHandlers as $handler) {
        if ($handler === 'ldap') {
            $user = ldapLoginHandler($conn, $login, $password);
        } elseif ($handler === 'standard') {
            $user = standardLoginHandler($conn, $login, $password);
        }
        
        if ($user !== false) {
            break;
        }
    }
    
    if ($user !== false) {
        // Authentication successful
        $_SESSION['admin_logged_in'] = true;
        $_SESSION['username'] = $user['username'];
        echo "@FLAG@";
        $conn->close();
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
    <title>Admin Login - Content Management System</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Admin Login</h1>
    <p class="info">Content Management System v4.7</p>
    <?php
    if ($errorMessage !== '') {
        echo "<p style='color: red;'>$errorMessage</p>";
    }
    ?>
    <form action="admin.php" method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username">
        <label for="password">Password:</label>
        <input type="password" id="password" name="password">
        <button type="submit">Login</button>
    </form>
</div>
</body>
</html>
