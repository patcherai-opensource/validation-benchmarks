<?php
require_once __DIR__ . '/config.php';
session_start();

if (isset($_SESSION['pimcore_admin_user'])) {
    header('Location: /admin/');
    exit;
}

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = isset($_POST['username']) ? trim($_POST['username']) : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';

    if (!empty($username) && !empty($password)) {
        $conn = get_db();
        $stmt = $conn->prepare("SELECT id, username, password, name, admin, active FROM users WHERE username = ? AND active = 1");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows === 1) {
            $user = $result->fetch_assoc();
            if (password_verify($password, $user['password'])) {
                $_SESSION['pimcore_admin_user'] = $user['username'];
                $_SESSION['pimcore_admin_uid'] = $user['id'];
                $_SESSION['pimcore_admin_name'] = $user['name'];
                $_SESSION['pimcore_admin_sid'] = session_id();
                $_SESSION['pimcore_admin_is_admin'] = (bool)$user['admin'];

                $conn->query("UPDATE users SET lastLogin = NOW() WHERE id = " . (int)$user['id']);

                header('Location: /admin/');
                exit;
            }
        }
        $error = 'Invalid credentials.';
        $stmt->close();
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
    <link rel="stylesheet" href="/admin/static/pimcore.css">
</head>
<body class="login-page">
<div class="login-container">
    <div class="login-logo">
        <svg width="120" height="40" viewBox="0 0 120 40">
            <text x="0" y="30" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="#6428b4">pimcore</text>
        </svg>
    </div>
    <div class="login-version">Version <?php echo PIMCORE_VERSION; ?></div>

    <?php if ($error): ?>
    <div class="login-error"><?php echo htmlspecialchars($error); ?></div>
    <?php endif; ?>

    <form method="POST" action="/admin/login.php" class="login-form">
        <div class="form-group">
            <label for="username">Username</label>
            <input type="text" name="username" id="username" placeholder="Username" autocomplete="username" required>
        </div>
        <div class="form-group">
            <label for="password">Password</label>
            <input type="password" name="password" id="password" placeholder="Password" autocomplete="current-password" required>
        </div>
        <button type="submit" class="btn btn-primary btn-login">Login</button>
    </form>
</div>
</body>
</html>
