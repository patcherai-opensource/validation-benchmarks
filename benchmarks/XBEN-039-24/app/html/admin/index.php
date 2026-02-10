<?php
session_start();

if (isset($_SESSION['user_id'])) {
    header("Location: dashboard.php");
    exit;
}

$error = '';
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $conn = new mysqli(
        getenv('MYSQL_HOST') ?: 'localhost',
        getenv('MYSQL_USER') ?: 'user',
        getenv('MYSQL_PASSWORD') ?: 'password',
        getenv('MYSQL_DATABASE') ?: 'blogDB'
    );
    
    if ($conn->connect_error) {
        http_response_code(500);
        die("Service temporarily unavailable");
    }
    
    $username = $conn->real_escape_string($_POST['username'] ?? '');
    $password = MD5($_POST['password'] ?? '');
    
    $sql = "SELECT id, username, display_name, role FROM users WHERE username = '$username' AND password = '$password'";
    $result = $conn->query($sql);
    
    if ($result && $result->num_rows == 1) {
        $user = $result->fetch_assoc();
        if ($user['role'] == 'admin' || $user['role'] == 'editor') {
            $_SESSION['user_id'] = $user['id'];
            $_SESSION['username'] = $user['username'];
            $_SESSION['display_name'] = $user['display_name'];
            $_SESSION['role'] = $user['role'];
            header("Location: dashboard.php");
            exit;
        } else {
            $error = 'Access denied. Insufficient privileges.';
        }
    } else {
        $error = 'Invalid username or password.';
    }
    $conn->close();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - FAQ Management</title>
    <link rel="stylesheet" href="../styles.css">
</head>
<body>
<div class="container admin-login">
    <h1>FAQ Admin Panel</h1>
    <h2>Login</h2>
    <?php if ($error): ?>
        <p class="error"><?php echo htmlspecialchars($error); ?></p>
    <?php endif; ?>
    <form action="" method="POST">
        <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
        </div>
        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
        </div>
        <button type="submit">Login</button>
    </form>
    <p class="back-link"><a href="../index.php">&larr; Back to FAQ</a></p>
</div>
</body>
</html>
