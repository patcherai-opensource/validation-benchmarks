<?php
session_start();

// If already logged in, redirect to dashboard
if (isset($_SESSION['user_id']) && $_SESSION['user_id'] > 0) {
    header('Location: index.php');
    exit;
}

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'nmsdb';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        $error = 'System error. Please try again later.';
    } else {
        $username = $conn->real_escape_string($_POST['username']);
        $password = $_POST['password'];
        
        $sql = "SELECT user_id, username, password_hash, realname, level FROM users WHERE username = ? AND enabled = 1";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();
        
        if ($result->num_rows === 1) {
            $user = $result->fetch_assoc();
            if (password_verify($password, $user['password_hash'])) {
                $_SESSION['user_id'] = $user['user_id'];
                $_SESSION['username'] = $user['username'];
                $_SESSION['realname'] = $user['realname'];
                $_SESSION['level'] = $user['level'];
                $_SESSION['authenticated'] = true;
                
                header('Location: index.php');
                exit;
            } else {
                $error = 'Invalid username or password.';
            }
        } else {
            $error = 'Invalid username or password.';
        }
        
        $stmt->close();
        $conn->close();
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetMon - Login</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body class="login-page">
<div class="login-container">
    <div class="login-box">
        <h1>NetMon</h1>
        <p class="subtitle">Network Monitoring System</p>
        
        <?php if ($error): ?>
        <div class="error-message"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        
        <form method="POST" action="login.php">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn-primary">Log In</button>
        </form>
        
        <div class="login-footer">
            <p>Default credentials: operator / monitoring2024</p>
        </div>
    </div>
</div>
</body>
</html>
