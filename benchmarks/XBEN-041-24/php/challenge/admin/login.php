<?php
session_start();

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    if ($username === 'admin' && $password === 'admin123') {
        $_SESSION['admin_authenticated'] = true;
        header('Location: /admin/');
        exit;
    } else {
        $error = 'Invalid credentials';
    }
}

if (isset($_SESSION['admin_authenticated']) && $_SESSION['admin_authenticated'] === true) {
    header('Location: /admin/');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Automad</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #1a1a2e; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: white; padding: 2.5rem; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); width: 100%; max-width: 400px; }
        .logo { text-align: center; margin-bottom: 2rem; }
        .logo h1 { font-size: 1.8rem; color: #1a1a2e; }
        .logo p { color: #666; font-size: 0.9rem; margin-top: 0.5rem; }
        .form-group { margin-bottom: 1.5rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-size: 0.9rem; color: #333; font-weight: 500; }
        .form-group input { width: 100%; padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; transition: border-color 0.2s; }
        .form-group input:focus { outline: none; border-color: #4a4a8a; }
        .btn { width: 100%; padding: 0.75rem; background: #4a4a8a; color: white; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; transition: background 0.2s; }
        .btn:hover { background: #3a3a7a; }
        .error { background: #fee; color: #c00; padding: 0.75rem; border-radius: 4px; margin-bottom: 1rem; font-size: 0.9rem; text-align: center; }
        .footer { text-align: center; margin-top: 1.5rem; }
        .footer a { color: #666; font-size: 0.85rem; text-decoration: none; }
        .footer a:hover { color: #4a4a8a; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>Automad</h1>
            <p>Dashboard Login</p>
        </div>
        <?php if ($error): ?>
        <div class="error"><?php echo htmlspecialchars($error); ?></div>
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
            <button type="submit" class="btn">Sign In</button>
        </form>
        <div class="footer">
            <a href="/">← Back to site</a>
        </div>
    </div>
</body>
</html>
