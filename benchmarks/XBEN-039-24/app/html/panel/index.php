<?php
session_start();

require_once __DIR__ . '/../lib/AuthenticationService.php';

// If already authenticated, redirect to dashboard
if (isset($_SESSION['be_user']) && $_SESSION['be_authenticated'] === true) {
    header('Location: dashboard.php');
    exit;
}

$conn = new mysqli(
    getenv('MYSQL_HOST') ?: '127.0.0.1',
    getenv('MYSQL_USER') ?: 'user',
    getenv('MYSQL_PASSWORD') ?: 'password',
    getenv('MYSQL_DATABASE') ?: 'blogDB'
);

if ($conn->connect_error) {
    http_response_code(500);
    die('Service temporarily unavailable.');
}

$errorMessage = '';
$infoMessage = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = isset($_POST['username']) ? trim($_POST['username']) : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';

    if (empty($username)) {
        $errorMessage = 'Please enter your username.';
    } else {
        $authService = new AuthenticationService($conn);
        $authResult = $authService->performLogin($username, $password);

        if ($authResult === true) {
            $user = $authService->getUserByUsername($username);
            if ($user) {
                session_regenerate_id(true);
                $_SESSION['be_user'] = $user['username'];
                $_SESSION['be_role'] = $user['role'];
                $_SESSION['be_uid'] = $user['uid'];
                $_SESSION['be_authenticated'] = true;
                $_SESSION['be_login_time'] = time();
                header('Location: dashboard.php');
                exit;
            }
        }

        $errorMessage = 'Invalid credentials. Please check your username and password.';
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContentHub - Administration</title>
    <link rel="stylesheet" href="../styles.css">
    <style>
        .login-wrapper {
            max-width: 420px;
            margin: 60px auto;
            padding: 30px;
            background: #fff;
            border-radius: 6px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .login-wrapper h1 {
            font-size: 22px;
            margin-bottom: 5px;
            color: #333;
        }
        .login-wrapper .version {
            font-size: 11px;
            color: #999;
            margin-bottom: 25px;
        }
        .login-wrapper label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
            font-size: 13px;
        }
        .login-wrapper input[type="text"],
        .login-wrapper input[type="password"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 14px;
        }
        .login-wrapper input:focus {
            border-color: #0078d4;
            outline: none;
        }
        .login-wrapper button {
            width: 100%;
            padding: 10px;
            background: #0078d4;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .login-wrapper button:hover {
            background: #005fa3;
        }
        .error-msg {
            background: #fde8e8;
            color: #c0392b;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
            font-size: 13px;
        }
        .login-footer {
            text-align: center;
            margin-top: 20px;
            font-size: 11px;
            color: #aaa;
        }
    </style>
</head>
<body style="background: #f0f2f5;">
    <div class="login-wrapper">
        <h1>ContentHub Administration</h1>
        <div class="version">Version 4.8.12</div>

        <?php if (!empty($errorMessage)): ?>
            <div class="error-msg"><?php echo htmlspecialchars($errorMessage); ?></div>
        <?php endif; ?>

        <form method="POST" action="">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" autocomplete="username"
                   value="<?php echo isset($_POST['username']) ? htmlspecialchars($_POST['username']) : ''; ?>">

            <label for="password">Password</label>
            <input type="password" id="password" name="password" autocomplete="current-password">

            <button type="submit">Log In</button>
        </form>

        <div class="login-footer">
            &copy; <?php echo date('Y'); ?> ContentHub CMS
        </div>
    </div>
</body>
</html>
