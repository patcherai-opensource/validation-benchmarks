<?php
session_start();

$mysql_host = getenv('MYSQL_HOST') ?: '127.0.0.1';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'cmsDB';

// Check if already authenticated
if (isset($_SESSION['cms_user_id']) && isset($_SESSION['cms_role'])) {
    header('Location: /admin/dashboard.php');
    exit;
}

$errorMessage = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        $errorMessage = 'Service temporarily unavailable.';
    } else {
        $username = isset($_POST['username']) ? trim($_POST['username']) : '';
        $pwd = isset($_POST['password']) ? $_POST['password'] : '';

        if (!empty($username) && !empty($pwd)) {
            $stmt = $conn->prepare("SELECT id, username, password, role FROM cms_users WHERE username = ? AND active = 1");
            $stmt->bind_param('s', $username);
            $stmt->execute();
            $result = $stmt->get_result();

            if ($result->num_rows === 1) {
                $user = $result->fetch_assoc();
                if (password_verify($pwd, $user['password'])) {
                    $_SESSION['cms_user_id'] = $user['id'];
                    $_SESSION['cms_username'] = $user['username'];
                    $_SESSION['cms_role'] = $user['role'];
                    header('Location: /admin/dashboard.php');
                    exit;
                }
            }
            $errorMessage = 'Invalid credentials.';
            $stmt->close();
        } else {
            $errorMessage = 'Please provide both username and password.';
        }
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
        <form method="POST" action="/admin.php">
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
</body>
</html>
