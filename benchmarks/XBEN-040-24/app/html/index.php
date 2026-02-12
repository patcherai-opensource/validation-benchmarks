<?php
session_start();

$mysql_host = getenv('MYSQL_HOST') ?: '127.0.0.1';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'pimcore';

// If already logged in, redirect to admin panel
if (isset($_SESSION['pimcore_admin_sid']) && $_SESSION['pimcore_admin_sid'] === true) {
    header('Location: /admin/index.php');
    exit;
}

$errorMessage = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        http_response_code(500);
        die('Service temporarily unavailable');
    }

    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';

    if (!empty($username) && !empty($password)) {
        $stmt = $conn->prepare("SELECT id, password, admin, active FROM users WHERE username = ?");
        $stmt->bind_param('s', $username);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows === 1) {
            $user = $result->fetch_assoc();
            if ($user['active'] && password_verify($password, $user['password'])) {
                $_SESSION['pimcore_admin_sid'] = true;
                $_SESSION['pimcore_user'] = [
                    'id' => $user['id'],
                    'username' => $username,
                    'admin' => (bool)$user['admin']
                ];
                header('Location: /admin/index.php');
                exit;
            }
        }
        $errorMessage = 'Invalid credentials.';
        $stmt->close();
    }
    $conn->close();
}

// Determine if this is an API request
$accept = $_SERVER['HTTP_ACCEPT'] ?? '';
if (strpos($accept, 'application/json') !== false) {
    header('Content-Type: application/json');
    echo json_encode(['success' => false, 'message' => 'Authentication required']);
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore - Admin Login</title>
    <link rel="stylesheet" href="/assets/css/admin.css">
</head>
<body class="pimcore-login">
    <div class="login-container">
        <div class="login-header">
            <h1>pimcore</h1>
            <p class="version">Version 10.5.x</p>
        </div>
        <?php if ($errorMessage): ?>
            <div class="alert alert-error"><?php echo htmlspecialchars($errorMessage); ?></div>
        <?php endif; ?>
        <form action="/" method="POST" class="login-form">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autocomplete="username" />
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required autocomplete="current-password" />
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
        </form>
        <div class="login-footer">
            <p>&copy; <?php echo date('Y'); ?> pimcore GmbH</p>
        </div>
    </div>
</body>
</html>
