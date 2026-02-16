<?php
session_start();

if (isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true) {
    header('Location: /admin/dashboard.php');
    exit;
}

$errorMessage = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $conn = new mysqli(
        $_ENV['MYSQL_HOST'] ?? '127.0.0.1',
        $_ENV['MYSQL_USER'] ?? 'user',
        $_ENV['MYSQL_PASSWORD'] ?? 'password',
        $_ENV['MYSQL_DATABASE'] ?? 'cmfDB'
    );
    if ($conn->connect_error) {
        $errorMessage = 'Service temporarily unavailable.';
    } else {
        $username = $_POST['username'] ?? '';
        $password = $_POST['password'] ?? '';

        $stmt = $conn->prepare("SELECT id, username, password_hash, role FROM admins WHERE username = ? AND active = 1");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows === 1) {
            $admin = $result->fetch_assoc();
            if (password_verify($password, $admin['password_hash'])) {
                $_SESSION['admin_logged_in'] = true;
                $_SESSION['admin_user'] = $admin['username'];
                $_SESSION['admin_role'] = $admin['role'];
                $_SESSION['admin_id'] = $admin['id'];
                header('Location: /admin/dashboard.php');
                exit;
            }
        }
        $errorMessage = 'Invalid username or password.';
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
    <title>CMF Admin - Login</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="login-wrapper">
    <div class="login-container">
        <div class="login-header">
            <h1>Customer Management Framework</h1>
            <p class="subtitle">Administration Panel</p>
        </div>
        <?php if ($errorMessage): ?>
            <div class="alert alert-error"><?php echo htmlspecialchars($errorMessage); ?></div>
        <?php endif; ?>
        <form action="" method="POST" class="login-form">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autocomplete="username">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required autocomplete="current-password">
            </div>
            <button type="submit" class="btn btn-primary">Sign In</button>
        </form>
    </div>
</div>
</body>
</html>
