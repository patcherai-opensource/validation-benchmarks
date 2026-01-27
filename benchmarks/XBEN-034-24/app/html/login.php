<?php
/**
 * DataSheet Pro - Login Page
 */
session_start();

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    // Demo credentials (not relevant to the challenge)
    if ($username === 'admin' && $password === 'demo123') {
        $_SESSION['user'] = $username;
        header('Location: /');
        exit;
    } else {
        $error = 'Invalid credentials';
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - DataSheet Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; min-height: 100vh; display: flex; flex-direction: column; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem 2rem; color: white; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 1.5rem; }
        .navbar nav a { color: white; text-decoration: none; margin-left: 2rem; }
        .login-container { flex: 1; display: flex; justify-content: center; align-items: center; padding: 2rem; }
        .login-box { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        .login-box h2 { color: #667eea; margin-bottom: 1.5rem; text-align: center; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; color: #666; }
        .form-group input { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; }
        .form-group input:focus { outline: none; border-color: #667eea; }
        .btn { width: 100%; padding: 0.75rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; }
        .btn:hover { opacity: 0.9; }
        .error { color: #dc3545; margin-bottom: 1rem; text-align: center; }
        .info { color: #666; font-size: 0.9rem; text-align: center; margin-top: 1rem; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>📊 DataSheet Pro</h1>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/exports.php">Exports</a>
            <a href="/docs.php">Documentation</a>
            <a href="/login.php">Login</a>
        </nav>
    </div>

    <div class="login-container">
        <div class="login-box">
            <h2>Sign In</h2>
            <?php if ($error): ?>
                <div class="error"><?php echo htmlspecialchars($error); ?></div>
            <?php endif; ?>
            <form method="POST">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">Sign In</button>
            </form>
            <p class="info">Contact your administrator for access credentials.</p>
        </div>
    </div>
</body>
</html>
