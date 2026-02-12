<?php
/**
 * phpMyFAQ Admin Panel - Login / Dashboard
 */

require_once '/var/www/html/src/Session.php';

use phpMyFAQ\Session;

Session::init();

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'login') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';

    if (Session::login($username, $password)) {
        header('Location: /admin/');
        exit;
    } else {
        $error = 'Invalid credentials. Please try again.';
    }
}

if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    Session::logout();
    header('Location: /admin/');
    exit;
}

$isAuthenticated = Session::isAuthenticated();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>phpMyFAQ - Administration</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <header class="admin-header">
        <div class="container">
            <h1><a href="/admin/">phpMyFAQ Admin</a></h1>
            <nav>
                <?php if ($isAuthenticated): ?>
                    <a href="/admin/">Dashboard</a>
                    <a href="/admin/category.main.php">Categories</a>
                    <a href="/admin/user.php">Users</a>
                    <a href="/admin/config.php">Configuration</a>
                    <a href="/admin/?action=logout">Logout (<?= htmlspecialchars(Session::getUser()) ?>)</a>
                <?php else: ?>
                    <a href="/">Back to FAQ</a>
                <?php endif; ?>
            </nav>
        </div>
    </header>

    <main class="container admin-main">
        <?php if (!$isAuthenticated): ?>
            <div class="login-form">
                <h2>Administration Login</h2>
                <?php if ($error): ?>
                    <div class="alert alert-error"><?= htmlspecialchars($error) ?></div>
                <?php endif; ?>
                <form method="POST" action="/admin/">
                    <input type="hidden" name="action" value="login">
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" required autocomplete="username">
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required autocomplete="current-password">
                    </div>
                    <button type="submit" class="btn btn-primary">Login</button>
                </form>
            </div>
        <?php else: ?>
            <h2>Dashboard</h2>
            <div class="dashboard-grid">
                <div class="dashboard-card">
                    <h3>Categories</h3>
                    <p>Manage FAQ categories and their images</p>
                    <a href="/admin/category.main.php" class="btn">Manage Categories</a>
                </div>
                <div class="dashboard-card">
                    <h3>Users</h3>
                    <p>Manage admin users and permissions</p>
                    <a href="/admin/user.php" class="btn">Manage Users</a>
                </div>
                <div class="dashboard-card">
                    <h3>Configuration</h3>
                    <p>System settings and configuration</p>
                    <a href="/admin/config.php" class="btn">Configuration</a>
                </div>
                <div class="dashboard-card">
                    <h3>System Information</h3>
                    <p>phpMyFAQ 3.2.5</p>
                    <p>PHP <?= PHP_VERSION ?></p>
                </div>
            </div>
        <?php endif; ?>
    </main>
    <footer>
        <div class="container">
            <p>&copy; 2024 phpMyFAQ Team. Administration Panel</p>
        </div>
    </footer>
</body>
</html>
