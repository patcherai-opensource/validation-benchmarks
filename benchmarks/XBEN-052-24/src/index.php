<?php
session_start();

$users = array(
    array(
        'user_id' => 1,
        'login' => 'homer',
        'password_hash' => '$2y$10$8K1p/a0dL1LXMIgoEDFrwOfMQkLgHxj5pYjqQVKv9L.4pYvN6Xn2m',
        'password_hash_type' => 5,
        'role' => 'user'
    ),
    array(
        'user_id' => 2,
        'login' => 'marge',
        'password_hash' => '$2y$10$YK8fV6gPjvQKfT/kL9MxJOKdZ4QrFZJI1xQz.m8hY3KxV8GxN1LXm',
        'password_hash_type' => 5,
        'role' => 'user'
    ),
    array(
        'user_id' => 3,
        'login' => 'admin',
        'password_hash' => '',
        'password_hash_type' => 0,
        'role' => 'administrator'
    ),
    array(
        'user_id' => 4,
        'login' => 'bart',
        'password_hash' => '$2y$10$J1p2K3L4M5n6O7p8Q9r0stU1v2W3x4Y5z6A7B8C9D0E1F2G3H4I5J6',
        'password_hash_type' => 5,
        'role' => 'user'
    )
);

$ldap_handler_enabled = true;
$standard_handler_enabled = true;

function _loginUser($login, $password) {
    global $users;
    
    foreach ($users as $user) {
        if ($user['login'] === $login) {
            if ($user['password_hash_type'] == 0) {
                return $user;
            }
            
            if ($user['password_hash_type'] == 5 && password_verify($password, $user['password_hash'])) {
                return $user;
            }
        }
    }
    return false;
}

function checkUserStandardHandler($login, $password) {
    return _loginUser($login, $password);
}

function checkUserLdapHandler($login, $password) {
    return false;
}

function authenticateUser($login, $password) {
    global $ldap_handler_enabled, $standard_handler_enabled;
    
    $user = false;
    
    if ($ldap_handler_enabled) {
        $user = checkUserLdapHandler($login, $password);
    }
    
    if (!$user && $standard_handler_enabled) {
        $user = checkUserStandardHandler($login, $password);
    }
    
    return $user;
}

function getAdminContent() {
    $flag_file = '/var/www/html/.flag';
    $flag = file_exists($flag_file) ? trim(file_get_contents($flag_file)) : 'FLAG_NOT_SET';
    
    return '
    <div class="admin-panel">
        <h2>Administration Panel</h2>
        <div class="admin-section">
            <h3>System Status</h3>
            <p>All services running normally</p>
        </div>
        <div class="admin-section">
            <h3>User Management</h3>
            <p>4 users registered</p>
        </div>
        <div class="admin-section">
            <h3>System Configuration</h3>
            <p>Configuration token: ' . htmlspecialchars($flag) . '</p>
        </div>
    </div>';
}

$error_message = '';
$login_success = false;
$current_user = null;

if (isset($_SESSION['user'])) {
    $current_user = $_SESSION['user'];
    $login_success = true;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['action']) && $_POST['action'] === 'logout') {
        session_destroy();
        header('Location: index.php');
        exit;
    }
    
    if (isset($_POST['login'])) {
        $login = $_POST['login'];
        $password = isset($_POST['password']) ? $_POST['password'] : '';
        
        $user = authenticateUser($login, $password);
        
        if ($user) {
            $_SESSION['user'] = $user;
            $current_user = $user;
            $login_success = true;
        } else {
            $error_message = 'Invalid username or password';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Springfield CMS - Login</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #fff;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            margin-bottom: 5px;
        }
        .header p {
            color: rgba(255,255,255,0.8);
            font-size: 1.1em;
        }
        .container {
            background: #fff;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        .container h2 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e1e1e1;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 5px;
            color: #fff;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .error {
            background: #fee;
            color: #c00;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .success-container {
            max-width: 600px;
        }
        .welcome-msg {
            text-align: center;
            margin-bottom: 30px;
        }
        .welcome-msg h2 {
            color: #333;
        }
        .welcome-msg p {
            color: #666;
        }
        .admin-panel {
            margin-top: 20px;
        }
        .admin-section {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .admin-section h3 {
            margin: 0 0 10px 0;
            color: #333;
            font-size: 1.1em;
        }
        .admin-section p {
            margin: 0;
            color: #666;
        }
        .logout-form {
            margin-top: 30px;
            text-align: center;
        }
        .btn-logout {
            background: #dc3545;
            padding: 10px 30px;
            width: auto;
        }
        .btn-logout:hover {
            box-shadow: 0 5px 20px rgba(220, 53, 69, 0.4);
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: rgba(255,255,255,0.7);
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Springfield CMS</h1>
        <p>Content Management System v4.2.1</p>
    </div>

    <?php if ($login_success && $current_user): ?>
    <div class="container success-container">
        <div class="welcome-msg">
            <h2>Welcome, <?php echo htmlspecialchars($current_user['login']); ?>!</h2>
            <p>Role: <?php echo htmlspecialchars($current_user['role']); ?></p>
        </div>
        
        <?php if ($current_user['role'] === 'administrator'): ?>
            <?php echo getAdminContent(); ?>
        <?php else: ?>
            <div class="admin-section">
                <h3>User Dashboard</h3>
                <p>Welcome to your dashboard. Contact an administrator for elevated privileges.</p>
            </div>
        <?php endif; ?>
        
        <form method="POST" class="logout-form">
            <input type="hidden" name="action" value="logout">
            <button type="submit" class="btn btn-logout">Logout</button>
        </form>
    </div>
    <?php else: ?>
    <div class="container">
        <h2>Sign In</h2>
        
        <?php if ($error_message): ?>
        <div class="error"><?php echo htmlspecialchars($error_message); ?></div>
        <?php endif; ?>
        
        <form method="POST" action="index.php">
            <div class="form-group">
                <label for="login">Username</label>
                <input type="text" id="login" name="login" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password">
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
    </div>
    <?php endif; ?>
    
    <div class="footer">
        <p>&copy; 2024 Springfield CMS. All rights reserved.</p>
    </div>
</body>
</html>
