<?php
/**
 * Login page
 */

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';

    if (auth_login($username, $password)) {
        gp_redirect('/index.php');
    } else {
        $error = 'Invalid credentials. Please check your username and password.';
    }
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo APP_NAME; ?> - Login</title>
    <link rel="stylesheet" href="/public/css/style.css">
</head>
<body class="login-page">
<div class="login-container">
    <div class="login-header">
        <h1><?php echo APP_NAME; ?></h1>
        <p class="login-subtitle">Enterprise Resource Planning</p>
        <p class="login-version">Version <?php echo APP_VERSION; ?></p>
    </div>
    <?php if ($error): ?>
    <div class="gp-msg gp-msg-error"><?php echo gp_escape_html($error); ?></div>
    <?php endif; ?>
    <form method="post" action="/index.php?module=login" class="login-form">
        <div class="form-group">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" required autofocus>
        </div>
        <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" name="password" required>
        </div>
        <div class="form-group">
            <button type="submit" class="btn btn-primary">Login</button>
        </div>
    </form>
    <div class="login-footer">
        <p>&copy; <?php echo date('Y'); ?> <?php echo APP_NAME; ?></p>
    </div>
</div>
</body>
</html>
