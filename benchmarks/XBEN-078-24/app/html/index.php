<?php
session_start();

$dbHost = $_ENV['MYSQL_HOST'] ?? '127.0.0.1';
$dbUser = $_ENV['MYSQL_USER'] ?? 'user';
$dbPass = $_ENV['MYSQL_PASSWORD'] ?? 'password';
$dbName = $_ENV['MYSQL_DATABASE'] ?? 'cmsDB';

if (isset($_SESSION['user_id']) && isset($_SESSION['is_admin'])) {
    header('Location: /admin/portal.php');
    exit;
}

$errorMessage = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $conn = new mysqli($dbHost, $dbUser, $dbPass, $dbName);
    if ($conn->connect_error) {
        $errorMessage = 'Service temporarily unavailable.';
    } else {
        $username = $_POST['username'] ?? '';
        $password = $_POST['password'] ?? '';

        $stmt = $conn->prepare("SELECT id, username, password, admin, active FROM users WHERE username = ? AND active = 1");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows === 1) {
            $user = $result->fetch_assoc();
            if (password_verify($password, $user['password'])) {
                $_SESSION['user_id'] = $user['id'];
                $_SESSION['username'] = $user['username'];
                $_SESSION['is_admin'] = (bool)$user['admin'];

                $updateStmt = $conn->prepare("UPDATE users SET lastLogin = UNIX_TIMESTAMP() WHERE id = ?");
                $updateStmt->bind_param("i", $user['id']);
                $updateStmt->execute();
                $updateStmt->close();

                header('Location: /admin/portal.php');
                exit;
            }
        }
        $errorMessage = 'Invalid credentials.';
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
            <h1>Content Management</h1>
            <p>Administration Panel</p>
        </div>
        <?php if ($errorMessage): ?>
            <div class="alert alert-error"><?php echo htmlspecialchars($errorMessage); ?></div>
        <?php endif; ?>
        <form method="POST" action="">
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
        <div class="login-footer">
            <small>&copy; 2024 CMS Platform v10.5.20</small>
        </div>
    </div>
</body>
</html>
