<?php
session_start();

if (isset($_SESSION['pimcore_admin']) && $_SESSION['pimcore_admin'] === true) {
    header('Location: /admin/dashboard.php');
    exit;
}

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';

    if (!empty($username) && !empty($password)) {
        $conn = new mysqli(
            $_ENV['MYSQL_HOST'] ?? '127.0.0.1',
            $_ENV['MYSQL_USER'] ?? 'user',
            $_ENV['MYSQL_PASSWORD'] ?? 'password',
            $_ENV['MYSQL_DATABASE'] ?? 'pimcore'
        );

        if ($conn->connect_error) {
            $error = 'Service temporarily unavailable.';
        } else {
            $stmt = $conn->prepare("SELECT id, username, password, admin FROM users WHERE username = ? AND active = 1");
            $stmt->bind_param("s", $username);
            $stmt->execute();
            $result = $stmt->get_result();

            if ($result->num_rows === 1) {
                $user = $result->fetch_assoc();
                if (password_verify($password, $user['password']) && $user['admin'] == 1) {
                    $_SESSION['pimcore_admin'] = true;
                    $_SESSION['pimcore_user'] = $user['username'];
                    $_SESSION['pimcore_user_id'] = $user['id'];
                    header('Location: /admin/dashboard.php');
                    exit;
                }
            }
            $error = 'Invalid credentials.';
            $stmt->close();
            $conn->close();
        }
    } else {
        $error = 'Please enter username and password.';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore - Login</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body class="login-page">
    <div class="login-container">
        <div class="login-header">
            <h1>pimcore</h1>
            <p class="version">Platform Version 10.6.8</p>
        </div>
        <form method="POST" action="/">
            <?php if ($error): ?>
                <div class="error-message"><?php echo htmlspecialchars($error); ?></div>
            <?php endif; ?>
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" autocomplete="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" autocomplete="current-password" required>
            </div>
            <button type="submit" class="btn-login">Login</button>
        </form>
        <div class="login-footer">
            <p>&copy; <?php echo date('Y'); ?> pimcore GmbH. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
