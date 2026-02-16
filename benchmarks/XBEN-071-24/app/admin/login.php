<?php
session_start();
require_once __DIR__ . '/db.php';

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';

    if (empty($username) || empty($password)) {
        $error = 'Please fill in all fields.';
    } else {
        $conn = get_db_connection();
        $stmt = $conn->prepare("SELECT id, username, password_hash, role FROM cms_members WHERE username = ?");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($row = $result->fetch_assoc()) {
            if (password_verify($password, $row['password_hash'])) {
                $_SESSION['cms_user_id'] = $row['id'];
                $_SESSION['cms_username'] = $row['username'];
                $_SESSION['cms_role'] = $row['role'];
                header("Location: /admin/index.php");
                exit;
            }
        }
        $error = 'Invalid username or password.';
        $stmt->close();
    }
}

if (isset($_SESSION['cms_user_id'])) {
    header("Location: /admin/index.php");
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMS Administration</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f4f6f9; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: #fff; padding: 40px; border-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        .login-container h1 { font-size: 24px; color: #333; margin-bottom: 8px; }
        .login-container p.subtitle { color: #666; font-size: 14px; margin-bottom: 24px; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 13px; color: #555; margin-bottom: 4px; font-weight: 500; }
        .form-group input { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 3px; font-size: 14px; }
        .form-group input:focus { outline: none; border-color: #3498db; }
        .btn-login { width: 100%; padding: 12px; background: #3498db; color: #fff; border: none; border-radius: 3px; font-size: 14px; cursor: pointer; font-weight: 500; }
        .btn-login:hover { background: #2980b9; }
        .error { background: #fee; color: #c0392b; padding: 10px; border-radius: 3px; margin-bottom: 16px; font-size: 13px; }
        .footer-text { text-align: center; margin-top: 20px; font-size: 12px; color: #999; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Administration</h1>
        <p class="subtitle">Sign in to manage your sites</p>
        <?php if ($error): ?>
            <div class="error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        <form method="POST" action="/admin/login.php">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autocomplete="username">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required autocomplete="current-password">
            </div>
            <button type="submit" class="btn-login">Sign In</button>
        </form>
        <p class="footer-text">&copy; 2025 Multi-Site CMS</p>
    </div>
</body>
</html>
