<?php
/**
 * Dolibar ERP - Login Page
 * Version 12.0.3
 */

session_start();

$error = '';

// Check if form submitted
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = isset($_POST['username']) ? trim($_POST['username']) : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';
    
    // Simple authentication - admin:admin123 or operator:backup2024
    if (($username === 'admin' && $password === 'admin123') ||
        ($username === 'operator' && $password === 'backup2024')) {
        $_SESSION['logged_in'] = true;
        $_SESSION['username'] = $username;
        $_SESSION['role'] = ($username === 'admin') ? 'administrator' : 'operator';
        header("Location: /admin/index.php");
        exit;
    } else {
        $error = 'Invalid credentials. Please check username and password.';
    }
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dolibar ERP - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: #fff; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); padding: 40px; width: 100%; max-width: 400px; }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { color: #1a1a2e; font-size: 28px; }
        .logo span { color: #e94560; }
        .logo p { color: #666; font-size: 12px; margin-top: 5px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        input:focus { outline: none; border-color: #e94560; }
        button { width: 100%; padding: 12px; background: #e94560; color: #fff; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; }
        button:hover { background: #d63350; }
        .error { background: #ffebee; color: #c62828; padding: 10px; border-radius: 4px; margin-bottom: 20px; font-size: 14px; }
        .version { text-align: center; margin-top: 20px; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>Doli<span>bar</span></h1>
            <p>Enterprise Resource Planning</p>
        </div>
        
        <?php if ($error): ?>
        <div class="error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        
        <form method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autocomplete="username">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required autocomplete="current-password">
            </div>
            <button type="submit">Sign In</button>
        </form>
        
        <div class="version">Dolibar ERP v12.0.3</div>
    </div>
</body>
</html>
