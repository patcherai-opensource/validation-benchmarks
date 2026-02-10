<?php
session_start();

$conn = new mysqli(
    getenv('MYSQL_HOST') ?: 'localhost',
    getenv('MYSQL_USER') ?: 'user',
    getenv('MYSQL_PASSWORD') ?: 'password',
    getenv('MYSQL_DATABASE') ?: 'blogDB'
);

if ($conn->connect_error) {
    http_response_code(503);
    die("Service temporarily unavailable");
}

function getEnabledHandlers($conn) {
    $handlers = array();
    $result = $conn->query("SELECT handler_name, handler_type FROM auth_handlers WHERE is_enabled = 1 ORDER BY priority ASC");
    if ($result) {
        while ($row = $result->fetch_assoc()) {
            $handlers[] = $row;
        }
    }
    return $handlers;
}

function loginUser($login, $password, $conn) {
    $login = $conn->real_escape_string($login);
    
    $handlers = getEnabledHandlers($conn);
    $hasLdapOrTextfile = false;
    $hasStandard = false;
    
    foreach ($handlers as $handler) {
        if ($handler['handler_type'] == 'directory' || $handler['handler_name'] == 'textfile') {
            $hasLdapOrTextfile = true;
        }
        if ($handler['handler_name'] == 'standard') {
            $hasStandard = true;
        }
    }
    
    $sql = "SELECT id, username, password_hash, password_hash_type, role FROM users WHERE username = '$login' AND is_active = 1";
    $result = $conn->query($sql);
    
    if ($result && $result->num_rows > 0) {
        $user = $result->fetch_assoc();
        
        if ($hasStandard && $hasLdapOrTextfile) {
            if ($user['password_hash_type'] == 0) {
                return $user;
            }
        }
        
        if (!empty($password)) {
            $valid = false;
            switch ($user['password_hash_type']) {
                case 1:
                    $valid = (md5($password) === $user['password_hash']);
                    break;
                case 2:
                    $valid = (hash('sha256', $password) === $user['password_hash']);
                    break;
            }
            
            if ($valid) {
                return $user;
            }
        }
    }
    
    return false;
}

if (isset($_SESSION['user_id']) && isset($_SESSION['role'])) {
    header("Location: dashboard.php");
    exit;
}

$errorMessage = '';
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = isset($_POST['username']) ? trim($_POST['username']) : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';
    
    if (empty($username)) {
        $errorMessage = 'Please enter your username.';
    } else {
        $user = loginUser($username, $password, $conn);
        
        if ($user !== false) {
            $_SESSION['user_id'] = $user['id'];
            $_SESSION['username'] = $user['username'];
            $_SESSION['role'] = $user['role'];
            
            header("Location: dashboard.php");
            exit;
        } else {
            $errorMessage = 'Invalid credentials.';
        }
    }
}
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Staff Login - Blog CMS</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Staff Portal</h1>
    <p>Please sign in to access the management dashboard.</p>
    <?php if (!empty($errorMessage)): ?>
        <p class="error-message"><?php echo htmlspecialchars($errorMessage); ?></p>
    <?php endif; ?>
    <form action="admin.php" method="POST">
        <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" autocomplete="username">
        </div>
        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" autocomplete="current-password">
        </div>
        <button type="submit">Sign In</button>
    </form>
    <p class="back-link"><a href="index.php">&larr; Back to Blog</a></p>
</div>
</body>
</html>
