<?php
session_start();
require_once __DIR__ . '/../includes/db.php';
require_once __DIR__ . '/../includes/auth.php';

$error = '';
$success = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = isset($_POST['j_username']) ? trim($_POST['j_username']) : '';
    $password = isset($_POST['j_password']) ? trim($_POST['j_password']) : '';

    if (empty($username) || empty($password)) {
        $error = 'Please provide both username and password.';
    } else {
        $conn = get_db_connection();
        $stmt = $conn->prepare("SELECT XWU_ID, XWU_USERNAME, XWU_PASSWORD, XWU_RIGHTS, XWU_ACTIVE FROM xwikiusers WHERE XWU_USERNAME = ? AND XWU_ACTIVE = 1");
        $stmt->bind_param('s', $username);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows === 1) {
            $user = $result->fetch_assoc();
            // Verify password (plain text comparison for legacy accounts)
            if ($password === $user['XWU_PASSWORD']) {
                $_SESSION['xwiki_user'] = $user;
                $success = 'Login successful.';
                header('Location: /');
                exit();
            } else {
                $error = 'Invalid credentials.';
            }
        } else {
            $error = 'Invalid credentials.';
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
    <title>XWiki - Log in</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div id="xwikimaincontainer">
    <div id="xwikiheader">
        <div class="navbar">
            <a href="/" class="brand">XWiki Platform</a>
            <div class="nav-links">
                <a href="/bin/view/Main/">Wiki</a>
                <a href="/bin/login">Login</a>
            </div>
        </div>
    </div>

    <div id="xwikicontent" class="main-content">
        <h1>Log in</h1>

        <?php if ($error): ?>
            <div class="message error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>

        <form action="/bin/login" method="POST" class="login-form">
            <div class="form-group">
                <label for="j_username">Username:</label>
                <input type="text" id="j_username" name="j_username" required autocomplete="username">
            </div>
            <div class="form-group">
                <label for="j_password">Password:</label>
                <input type="password" id="j_password" name="j_password" required autocomplete="current-password">
            </div>
            <button type="submit" class="btn btn-primary">Log in</button>
        </form>

        <div class="login-info">
            <p>You need an account to access wiki features. Contact the administrator if you need access.</p>
        </div>
    </div>

    <div id="xwikifooter">
        <p>Powered by <a href="#">XWiki Platform</a> 16.4.5</p>
    </div>
</div>
</body>
</html>