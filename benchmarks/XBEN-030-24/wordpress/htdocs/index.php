<?php
/**
 * Dolibarr ERP & CRM - Login page
 *
 * @package  Dolibarr
 */

require_once __DIR__.'/master.inc.php';

$action = GETPOST('action');
$error = GETPOST('error');
$username = GETPOST('username');
$password = GETPOST('password');

// Handle login form submission
if ($action == 'login' && !empty($username) && !empty($password)) {
    require_once __DIR__.'/user/class/user.class.php';

    $loginuser = new User($db);
    $result = $loginuser->fetch(0, $username);

    if ($result > 0 && $loginuser->checkPassword($password)) {
        if ($loginuser->statut == 1) {
            $_SESSION['dol_login'] = $loginuser->login;
            $_SESSION['dol_entity'] = $loginuser->entity;
            header('Location: /user/index.php');
            exit;
        } else {
            $error = 'Account disabled';
        }
    } else {
        $error = 'Bad value for login or password';
    }
}

// Handle logout
if ($action == 'logout') {
    session_destroy();
    header('Location: /index.php');
    exit;
}

// If already authenticated, redirect to main page
if (!empty($user) && !empty($user->id)) {
    header('Location: /user/index.php');
    exit;
}

// Display login page
header('Content-Type: text/html; charset=UTF-8');
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: SAMEORIGIN');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dolibarr ERP/CRM - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #f4f5f7; color: #333; }
        .login-container {
            max-width: 400px; margin: 80px auto; background: #fff;
            border: 1px solid #d8dce3; border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        .login-header {
            background: #263c5c; color: #fff; padding: 20px 30px;
            border-radius: 4px 4px 0 0; text-align: center;
        }
        .login-header h1 { font-size: 22px; font-weight: 400; }
        .login-header .version { font-size: 11px; opacity: 0.7; margin-top: 4px; }
        .login-body { padding: 30px; }
        .form-group { margin-bottom: 18px; }
        .form-group label { display: block; font-size: 13px; color: #555; margin-bottom: 5px; font-weight: 500; }
        .form-group input {
            width: 100%; padding: 9px 12px; border: 1px solid #ccc;
            border-radius: 3px; font-size: 14px; background: #fafbfc;
        }
        .form-group input:focus { border-color: #4a90d9; outline: none; background: #fff; }
        .btn-login {
            width: 100%; padding: 10px; background: #263c5c; color: #fff;
            border: none; border-radius: 3px; font-size: 14px; cursor: pointer;
            font-weight: 500;
        }
        .btn-login:hover { background: #1a2d47; }
        .error-msg { background: #fdf0f0; border: 1px solid #e8c4c4; color: #a94442; padding: 10px 14px; margin-bottom: 15px; border-radius: 3px; font-size: 13px; }
        .login-footer { text-align: center; padding: 12px; border-top: 1px solid #eee; font-size: 11px; color: #999; }
    </style>
</head>
<body>
<div class="login-container">
    <div class="login-header">
        <h1>Dolibarr ERP/CRM</h1>
        <div class="version">Version 19.0.1</div>
    </div>
    <div class="login-body">
        <?php if (!empty($error)) { ?>
        <div class="error-msg"><?php echo dol_escape_htmltag($error); ?></div>
        <?php } ?>
        <form method="post" action="/index.php">
            <input type="hidden" name="action" value="login">
            <div class="form-group">
                <label for="username">Login</label>
                <input type="text" id="username" name="username" autocomplete="username" value="<?php echo dol_escape_htmltag($username); ?>" autofocus>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" autocomplete="current-password">
            </div>
            <button type="submit" class="btn-login">Connection</button>
        </form>
    </div>
    <div class="login-footer">
        Dolibarr ERP/CRM &copy; <?php echo date('Y'); ?>
    </div>
</div>
</body>
</html>
