<?php
session_start();

if (isset($_SESSION['admin_user_id']) && isset($_SESSION['admin_role'])) {
    header("Location: /panel/");
    exit;
}

$errorMessage = '';
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $conn = new mysqli(getenv('MYSQL_HOST') ?: '127.0.0.1', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'cmsDB');
    if ($conn->connect_error) {
        $errorMessage = 'Service temporarily unavailable.';
    } else {
        $username = isset($_POST['username']) ? $_POST['username'] : '';
        $password = isset($_POST['password']) ? $_POST['password'] : '';

        // Use parameterized query for login
        $stmt = $conn->prepare("SELECT id, username, password, display_name, role, active FROM users WHERE username = ? AND active = 1");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows == 1) {
            $user = $result->fetch_assoc();
            if (password_verify($password, $user['password'])) {
                $_SESSION['admin_user_id'] = $user['id'];
                $_SESSION['admin_username'] = $user['username'];
                $_SESSION['admin_display_name'] = $user['display_name'];
                $_SESSION['admin_role'] = $user['role'];

                // Update last login
                $updateStmt = $conn->prepare("UPDATE users SET last_login = NOW() WHERE id = ?");
                $updateStmt->bind_param("i", $user['id']);
                $updateStmt->execute();
                $updateStmt->close();

                header("Location: /panel/");
                exit;
            } else {
                $errorMessage = 'Invalid credentials.';
            }
        } else {
            $errorMessage = 'Invalid credentials.';
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
    <title>Administration - Login</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body class="login-page">
<div class="login-container">
    <div class="login-header">
        <h1>Administration</h1>
        <p>Content Management System</p>
    </div>
    <?php if ($errorMessage): ?>
    <div class="error-message"><?php echo htmlspecialchars($errorMessage); ?></div>
    <?php endif; ?>
    <form action="/admin/" method="POST" class="login-form">
        <div class="form-group">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" required autocomplete="username">
        </div>
        <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" name="password" required autocomplete="current-password">
        </div>
        <button type="submit" class="btn-login">Sign In</button>
    </form>
</div>
</body>
</html>
