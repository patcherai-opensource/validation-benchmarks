<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pimcore - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1d2332; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .login-container { background: #fff; border-radius: 4px; padding: 40px; width: 380px; box-shadow: 0 2px 20px rgba(0,0,0,0.3); }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { font-size: 28px; color: #4a148c; font-weight: 300; letter-spacing: 2px; }
        .logo span { color: #999; font-size: 12px; display: block; margin-top: 5px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; font-size: 13px; color: #666; margin-bottom: 6px; }
        .form-group input { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 3px; font-size: 14px; outline: none; transition: border-color 0.2s; }
        .form-group input:focus { border-color: #4a148c; }
        .btn-login { width: 100%; padding: 12px; background: #4a148c; color: #fff; border: none; border-radius: 3px; font-size: 14px; cursor: pointer; transition: background 0.2s; }
        .btn-login:hover { background: #6a1b9a; }
        .error { background: #fde8e8; color: #c62828; padding: 10px; border-radius: 3px; margin-bottom: 15px; font-size: 13px; display: none; }
        .footer { text-align: center; margin-top: 20px; color: #999; font-size: 11px; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>pimcore</h1>
            <span>Administration Panel</span>
        </div>
        <div class="error" id="error">Invalid credentials</div>
        <form method="POST" action="/admin/login.php">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" autocomplete="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" autocomplete="current-password" required>
            </div>
            <button type="submit" class="btn-login">Login</button>
        </form>
        <div class="footer">&copy; 2023 pimcore GmbH</div>
    </div>
<?php
session_start();
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Simple admin authentication
    $user = $_POST['username'] ?? '';
    $pass = $_POST['password'] ?? '';
    
    // This is a placeholder login - credentials are managed via the users table
    require_once __DIR__ . '/../lib/db.php';
    try {
        $conn = \Pimcore\Db::getConnection();
        $stmt = $conn->prepare("SELECT id, name, password FROM users WHERE name = ? AND active = 1 AND admin = 1");
        $stmt->bind_param("s", $user);
        $stmt->execute();
        $result = $stmt->get_result();
        $row = $result->fetch_assoc();
        $stmt->close();
        
        if ($row && password_verify($pass, $row['password'])) {
            $_SESSION['admin_authenticated'] = true;
            $_SESSION['admin_user'] = $row['name'];
            header('Location: /admin/dashboard.php');
            exit;
        } else {
            echo '<script>document.getElementById("error").style.display="block";</script>';
        }
    } catch (Exception $e) {
        echo '<script>document.getElementById("error").style.display="block";</script>';
    }
}
?>
</body>
</html>
