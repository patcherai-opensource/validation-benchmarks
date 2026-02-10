<?php
error_reporting(0);
ini_set('display_errors', 0);

$db_path = '/var/lib/app/tokens.db';

function init_database() {
    global $db_path;
    
    $db_dir = dirname($db_path);
    if (!is_dir($db_dir)) {
        mkdir($db_dir, 0755, true);
    }
    
    $db = new SQLite3($db_path);
    
    $db->exec('CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )');
    
    $db->exec('CREATE TABLE IF NOT EXISTS remember_tokens (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        series TEXT UNIQUE NOT NULL,
        token TEXT NOT NULL,
        expires INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )');
    
    $result = $db->querySingle("SELECT COUNT(*) FROM users");
    if ($result == 0) {
        $db->exec("INSERT INTO users (username, password, is_admin) VALUES ('admin', '" . password_hash('S3cur3Adm1nP@ssw0rd!', PASSWORD_DEFAULT) . "', 1)");
        $db->exec("INSERT INTO users (username, password, is_admin) VALUES ('homer', '" . password_hash('donuts123', PASSWORD_DEFAULT) . "', 0)");
        $db->exec("INSERT INTO users (username, password, is_admin) VALUES ('marge', '" . password_hash('blueHair456', PASSWORD_DEFAULT) . "', 0)");
        $db->exec("INSERT INTO users (username, password, is_admin) VALUES ('bart', '" . password_hash('eatMyShorts789', PASSWORD_DEFAULT) . "', 0)");
        
        $series = bin2hex(random_bytes(32));
        $token_value = bin2hex(random_bytes(32));
        $expires = time() + (86400 * 30);
        $db->exec("INSERT INTO remember_tokens (user_id, username, series, token, expires) VALUES (2, 'homer', '$series', '$token_value', $expires)");
    }
    
    return $db;
}

function generate_remember_cookie($db, $user_id, $username) {
    $series = bin2hex(random_bytes(32));
    $token_value = bin2hex(random_bytes(32));
    $expires = time() + (86400 * 30);
    
    $stmt = $db->prepare("INSERT INTO remember_tokens (user_id, username, series, token, expires) VALUES (:user_id, :username, :series, :token, :expires)");
    $stmt->bindValue(':user_id', $user_id, SQLITE3_INTEGER);
    $stmt->bindValue(':username', $username, SQLITE3_TEXT);
    $stmt->bindValue(':series', $series, SQLITE3_TEXT);
    $stmt->bindValue(':token', $token_value, SQLITE3_TEXT);
    $stmt->bindValue(':expires', $expires, SQLITE3_INTEGER);
    $stmt->execute();
    
    $cookie_value = base64_encode("$username:$series:$token_value:$expires");
    return $cookie_value;
}

function consume_remember_cookie($db, $cookie_value) {
    $decoded = base64_decode($cookie_value);
    if ($decoded === false) {
        return null;
    }
    
    $parts = explode(':', $decoded);
    if (count($parts) !== 4) {
        return null;
    }
    
    list($username, $series, $token, $expires) = $parts;
    
    $stmt = $db->prepare("SELECT * FROM remember_tokens WHERE series = :series");
    $stmt->bindValue(':series', $series, SQLITE3_TEXT);
    $result = $stmt->execute();
    $stored_token = $result->fetchArray(SQLITE3_ASSOC);
    
    if (!$stored_token) {
        return null;
    }
    
    if ($stored_token['token'] !== $token) {
        return null;
    }
    
    if (time() > $stored_token['expires']) {
        return null;
    }
    
    $new_token = bin2hex(random_bytes(32));
    $new_expires = time() + (86400 * 30);
    
    $update_stmt = $db->prepare("UPDATE remember_tokens SET token = :token, expires = :expires WHERE series = :series");
    $update_stmt->bindValue(':token', $new_token, SQLITE3_TEXT);
    $update_stmt->bindValue(':expires', $new_expires, SQLITE3_INTEGER);
    $update_stmt->bindValue(':series', $series, SQLITE3_TEXT);
    $update_stmt->execute();
    
    $cookie_value = base64_encode("$username:$series:$new_token:$new_expires");
    setcookie('remember_me', $cookie_value, $new_expires, '/', '', false, true);
    
    $user_stmt = $db->prepare("SELECT * FROM users WHERE username = :username");
    $user_stmt->bindValue(':username', $username, SQLITE3_TEXT);
    $user_result = $user_stmt->execute();
    $user = $user_result->fetchArray(SQLITE3_ASSOC);
    
    return $user;
}

$db = init_database();
$flag = "@FLAG@";
$logged_in_user = null;
$message = '';
$message_type = '';

if (isset($_GET['logout'])) {
    if (isset($_COOKIE['remember_me'])) {
        $decoded = base64_decode($_COOKIE['remember_me']);
        if ($decoded !== false) {
            $parts = explode(':', $decoded);
            if (count($parts) === 4) {
                $series = $parts[1];
                $stmt = $db->prepare("DELETE FROM remember_tokens WHERE series = :series");
                $stmt->bindValue(':series', $series, SQLITE3_TEXT);
                $stmt->execute();
            }
        }
        setcookie('remember_me', '', time() - 3600, '/');
    }
    header('Location: index.php');
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['username']) && isset($_POST['password'])) {
    $username = $_POST['username'];
    $password = $_POST['password'];
    $remember = isset($_POST['remember']);
    
    $stmt = $db->prepare("SELECT * FROM users WHERE username = :username");
    $stmt->bindValue(':username', $username, SQLITE3_TEXT);
    $result = $stmt->execute();
    $user = $result->fetchArray(SQLITE3_ASSOC);
    
    if ($user && password_verify($password, $user['password'])) {
        $logged_in_user = $user;
        if ($remember) {
            $cookie_value = generate_remember_cookie($db, $user['id'], $user['username']);
            setcookie('remember_me', $cookie_value, time() + (86400 * 30), '/', '', false, true);
        }
        $message = "Login successful!";
        $message_type = 'success';
    } else {
        $message = "Invalid username or password.";
        $message_type = 'error';
    }
}

if (!$logged_in_user && isset($_COOKIE['remember_me'])) {
    $logged_in_user = consume_remember_cookie($db, $_COOKIE['remember_me']);
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Springfield Community Portal</title>
    <style>
        body {
            background-color: #FFD90F;
            background-image: url('./static/springfield_background.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            font-family: 'Arial', sans-serif;
            text-align: center;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
        }
        h1, h2, h3 {
            text-shadow: 2px 2px #000000;
            color: #FFFFFF;
        }
        .container {
            background-color: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px #000000;
            max-width: 400px;
            width: 100%;
        }
        .form-group {
            margin: 15px 0;
            text-align: left;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], input[type="password"] {
            padding: 10px;
            width: 100%;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        .remember-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        input[type="checkbox"] {
            width: auto;
        }
        button {
            background-color: #6495ED;
            color: #FFFFFF;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
            margin-top: 10px;
        }
        button:hover {
            background-color: #4169E1;
        }
        .message {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .user-panel {
            background-color: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px #000000;
            max-width: 500px;
            width: 100%;
        }
        .admin-section {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
            border: 2px solid #28a745;
        }
        .logout-link {
            display: inline-block;
            margin-top: 15px;
            color: #dc3545;
            text-decoration: none;
        }
        .logout-link:hover {
            text-decoration: underline;
        }
        .flag-display {
            font-family: monospace;
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <h1>Welcome to Springfield Community Portal</h1>
    
    <?php if ($logged_in_user): ?>
        <div class="user-panel">
            <h2>Welcome, <?php echo htmlspecialchars($logged_in_user['username']); ?>!</h2>
            <p>You are logged in to the Springfield Community Portal.</p>
            
            <?php if ($logged_in_user['is_admin']): ?>
                <div class="admin-section">
                    <h3>Admin Dashboard</h3>
                    <p>System Configuration Key:</p>
                    <div class="flag-display"><?php echo $flag; ?></div>
                </div>
            <?php else: ?>
                <p>You have access to standard community features.</p>
                <p>Contact an administrator if you need elevated privileges.</p>
            <?php endif; ?>
            
            <a href="?logout=1" class="logout-link">Logout</a>
        </div>
    <?php else: ?>
        <div class="container">
            <h2>Login</h2>
            
            <?php if ($message): ?>
                <div class="message <?php echo $message_type; ?>">
                    <?php echo htmlspecialchars($message); ?>
                </div>
            <?php endif; ?>
            
            <form action="index.php" method="POST">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" name="username" id="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" name="password" id="password" required>
                </div>
                <div class="form-group remember-group">
                    <input type="checkbox" name="remember" id="remember">
                    <label for="remember" style="display: inline; font-weight: normal;">Remember me</label>
                </div>
                <button type="submit">Login</button>
            </form>
        </div>
    <?php endif; ?>
</body>
</html>

