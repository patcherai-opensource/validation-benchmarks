<?php
$authenticated = false;
$showError = false;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $token = isset($_POST['token']) ? $_POST['token'] : '';
    $alias = isset($_POST['alias']) ? $_POST['alias'] : '';
    if ($alias && $token) {
        $showError = true;
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reposilite - Dashboard</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="header-bar">
        <div class="header-inner">
            <a href="/" class="header-brand">Reposilite</a>
            <nav class="header-nav">
                <a href="/browse">Browse</a>
                <a href="/dashboard">Dashboard</a>
            </nav>
        </div>
    </div>
    <div class="main-content">
        <?php if (!$authenticated): ?>
        <div class="login-container">
            <h2>Authentication</h2>
            <p style="text-align:center; color:#666; margin-bottom:1.5rem; font-size:0.9rem;">
                Sign in with your access token to manage repositories
            </p>
            <form action="/dashboard" method="post">
                <div class="form-group">
                    <label for="alias">Alias</label>
                    <input type="text" id="alias" name="alias" required placeholder="admin">
                </div>
                <div class="form-group">
                    <label for="token">Access Token</label>
                    <input type="password" id="token" name="token" required placeholder="secret-token">
                </div>
                <button type="submit" class="btn">Sign In</button>
            </form>
            <?php if ($showError): ?>
                <p class="error-msg">Invalid credentials</p>
            <?php endif; ?>
        </div>
        <?php endif; ?>
    </div>
</body>
</html>