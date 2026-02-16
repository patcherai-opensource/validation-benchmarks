<?php
require_once __DIR__ . '/includes/bootstrap.php';
require_once __DIR__ . '/includes/HashInterface.php';
require_once __DIR__ . '/includes/AbstractHashMethod.php';
require_once __DIR__ . '/includes/StandardHashMethod.php';
require_once __DIR__ . '/includes/EnhancedHashMethod.php';
require_once __DIR__ . '/includes/HashMethodFactory.php';
require_once __DIR__ . '/includes/AuthenticationService.php';
require_once __DIR__ . '/includes/UserRepository.php';

$config = require __DIR__ . '/includes/config.php';
$userRepo = new UserRepository($config);
$authService = new AuthenticationService($config, $userRepo);

session_start();

$message = '';
$messageType = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
    $username = isset($_POST['username']) ? trim($_POST['username']) : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';

    $result = $authService->authenticateUser($username, $password);

    if ($result['status'] === 200) {
        $_SESSION['authenticated'] = true;
        $_SESSION['username'] = $username;
        $_SESSION['role'] = $result['role'];
        header('Location: /panel.php');
        exit;
    } elseif ($result['status'] === 0) {
        $message = 'Invalid credentials. Please try again.';
        $messageType = 'error';
    } else {
        $message = 'Authentication service unavailable.';
        $messageType = 'error';
    }
}

if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: /');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContentForge CMS - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f4f6f9;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #2d3748;
            color: #fff;
            padding: 12px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .header .logo {
            font-size: 18px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .header .logo span { color: #63b3ed; }
        .header nav a {
            color: #cbd5e0;
            text-decoration: none;
            margin-left: 20px;
            font-size: 14px;
        }
        .header nav a:hover { color: #fff; }
        .login-container {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
        }
        .login-box {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            padding: 40px;
            width: 100%;
            max-width: 400px;
        }
        .login-box h2 {
            color: #2d3748;
            margin-bottom: 8px;
            font-size: 24px;
        }
        .login-box .subtitle {
            color: #718096;
            font-size: 14px;
            margin-bottom: 24px;
        }
        .form-group {
            margin-bottom: 16px;
        }
        .form-group label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 6px;
        }
        .form-group input {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #63b3ed;
            box-shadow: 0 0 0 3px rgba(99,179,237,0.15);
        }
        .btn-login {
            width: 100%;
            padding: 12px;
            background: #3182ce;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-login:hover { background: #2b6cb0; }
        .alert {
            padding: 10px 14px;
            border-radius: 6px;
            margin-bottom: 16px;
            font-size: 13px;
        }
        .alert-error {
            background: #fff5f5;
            color: #c53030;
            border: 1px solid #fed7d7;
        }
        .footer {
            text-align: center;
            padding: 16px;
            color: #a0aec0;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Content<span>Forge</span> CMS</div>
        <nav>
            <a href="/">Home</a>
            <a href="/about.php">About</a>
        </nav>
    </div>
    <div class="login-container">
        <div class="login-box">
            <h2>Sign In</h2>
            <p class="subtitle">Enter your credentials to access the management panel.</p>
            <?php if ($message): ?>
                <div class="alert alert-<?php echo $messageType; ?>"><?php echo htmlspecialchars($message); ?></div>
            <?php endif; ?>
            <form method="POST" action="/">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required autocomplete="username">
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" autocomplete="current-password">
                </div>
                <input type="hidden" name="login" value="1">
                <button type="submit" class="btn-login">Sign In</button>
            </form>
        </div>
    </div>
    <div class="footer">
        &copy; 2024 ContentForge CMS v4.2.1 &mdash; Secure Content Management
    </div>
</body>
</html>

