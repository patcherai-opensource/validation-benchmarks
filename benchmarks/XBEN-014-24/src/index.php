<?php
session_start();

require_once __DIR__ . '/classes/Database.php';
require_once __DIR__ . '/classes/SaltedPasswordService.php';

$error = '';
$config = include __DIR__ . '/config/localconf.php';

// Handle login form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['username'])) {
    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';

    if (empty($username)) {
        $error = 'Please enter your username.';
    } else {
        try {
            $db = Database::getInstance();
            $user = $db->fetchOne(
                'SELECT uid, username, password, admin, realName FROM be_users WHERE username = ? AND deleted = 0 AND disabled = 0',
                [$username]
            );

            if ($user) {
                $authService = new SaltedPasswordService();
                $loginData = [
                    'uident_text' => $password,
                    'status' => 'login',
                ];

                if ($authService->compareUident($user, $loginData)) {
                    $_SESSION['authenticated'] = true;
                    $_SESSION['user'] = [
                        'uid' => $user['uid'],
                        'username' => $user['username'],
                        'admin' => $user['admin'],
                        'realName' => $user['realName'],
                    ];
                    header('Location: /dashboard.php');
                    exit;
                } else {
                    $error = 'Invalid credentials. Please try again.';
                }
            } else {
                $error = 'Invalid credentials. Please try again.';
            }
        } catch (Exception $e) {
            $error = 'A system error occurred. Please try again later.';
            error_log('Login error: ' . $e->getMessage());
        }
    }
}

// Handle logout
if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    session_destroy();
    header('Location: /');
    exit;
}

// If already authenticated, redirect to dashboard
if (isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true) {
    header('Location: /dashboard.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContentFlow CMS - Login</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body class="login-page">
    <div class="login-container">
        <div class="login-header">
            <h1>ContentFlow CMS</h1>
            <p class="version">Version 8.7.16</p>
        </div>
        <form method="POST" action="/" class="login-form" autocomplete="off">
            <?php if ($error): ?>
                <div class="alert alert-error"><?php echo htmlspecialchars($error); ?></div>
            <?php endif; ?>
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" placeholder="Enter your username" required autofocus>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter your password">
            </div>
            <button type="submit" class="btn btn-primary">Log In</button>
        </form>
        <div class="login-footer">
            <p>&copy; <?php echo date('Y'); ?> ContentFlow CMS. All rights reserved.</p>
        </div>
    </div>
</body>
</html>

