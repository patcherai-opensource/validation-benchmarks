<?php
/**
 * ModuLink - Login Page
 */

session_start();

// Hardcoded credentials for CTF
$valid_users = [
    'admin' => ['password' => 'modlink2024!', 'role' => 'admin', 'id' => 1],
    'viewer' => ['password' => 'viewonly123', 'role' => 'viewer', 'id' => 2],
    'developer' => ['password' => 'dev@321', 'role' => 'developer', 'id' => 3]
];

$error = '';
$message = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    // Check credentials
    if (isset($valid_users[$username]) && $valid_users[$username]['password'] === $password) {
        $_SESSION['user_id'] = $valid_users[$username]['id'];
        $_SESSION['username'] = $username;
        $_SESSION['role'] = $valid_users[$username]['role'];
        
        // Log successful login
        $log_file = __DIR__ . '/logs/auth.log';
        file_put_contents($log_file, date('Y-m-d H:i:s') . " - Login success: $username\n", FILE_APPEND);
        
        header('Location: /dashboard.php');
        exit;
    } else {
        $error = 'Invalid username or password';
        // Log failed attempt
        $log_file = __DIR__ . '/logs/auth.log';
        file_put_contents($log_file, date('Y-m-d H:i:s') . " - Login failed: $username\n", FILE_APPEND);
    }
}

// Check for redirect message
if (isset($_GET['msg'])) {
    switch ($_GET['msg']) {
        case 'unauthorized':
            $message = 'Please log in to access that page.';
            break;
        case 'admin_required':
            $message = 'Administrator access required.';
            break;
        case 'logged_out':
            $message = 'You have been logged out successfully.';
            break;
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - ModuLink</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-box { background: #1e293b; padding: 40px; border-radius: 10px; width: 100%; max-width: 400px; border: 1px solid #334155; }
        .logo { text-align: center; font-size: 1.8rem; font-weight: bold; color: #38bdf8; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #94a3b8; }
        .form-group input { width: 100%; padding: 12px; background: #0f172a; border: 1px solid #334155; border-radius: 5px; color: #e2e8f0; font-size: 16px; }
        .form-group input:focus { outline: none; border-color: #3b82f6; }
        .btn { width: 100%; padding: 12px; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #2563eb; }
        .error { background: #991b1b; border: 1px solid #ef4444; padding: 12px; border-radius: 5px; margin-bottom: 20px; }
        .info { background: #1e40af; border: 1px solid #3b82f6; padding: 12px; border-radius: 5px; margin-bottom: 20px; }
        .back-link { text-align: center; margin-top: 20px; }
        .back-link a { color: #94a3b8; text-decoration: none; }
        .back-link a:hover { color: #f8fafc; }
    </style>
</head>
<body>
    <div class="login-box">
        <div class="logo">ModuLink</div>
        
        <?php if ($error): ?>
            <div class="error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        
        <?php if ($message): ?>
            <div class="info"><?php echo htmlspecialchars($message); ?></div>
        <?php endif; ?>
        
        <form method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Sign In</button>
        </form>
        
        <div class="back-link">
            <a href="/">&larr; Back to Home</a>
        </div>
    </div>
</body>
</html>
