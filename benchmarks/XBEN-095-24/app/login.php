<?php
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/db.php';

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

$error = '';
$success = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    if (empty($username) || empty($password)) {
        $error = 'Please provide both username and password.';
    } else {
        $conn = get_db_connection();
        if ($conn) {
            $stmt = $conn->prepare("SELECT user_id, username, password_hash, display_name, user_role FROM wiki_users WHERE username = ? AND active = 1");
            $stmt->bind_param("s", $username);
            $stmt->execute();
            $result = $stmt->get_result();
            
            if ($result->num_rows === 1) {
                $user = $result->fetch_assoc();
                if (password_verify($password, $user['password_hash'])) {
                    $_SESSION['user_id'] = $user['user_id'];
                    $_SESSION['username'] = $user['username'];
                    $_SESSION['role'] = $user['user_role'];
                    $_SESSION['display_name'] = $user['display_name'];
                    
                    header('Location: /');
                    exit;
                } else {
                    $error = 'Invalid credentials.';
                }
            } else {
                $error = 'Invalid credentials.';
            }
            
            $stmt->close();
            $conn->close();
        } else {
            $error = 'Service temporarily unavailable.';
        }
    }
}

if (check_session()) {
    header('Location: /');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - WikiEngine</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">WikiEngine</a>
            <span class="version">v3.8.2</span>
        </div>
        <div class="nav-links">
            <a href="/browse.php">Browse</a>
            <a href="/spaces.php">Spaces</a>
            <a href="/login.php">Login</a>
        </div>
    </nav>

    <div class="container">
        <div class="login-form">
            <h2>Sign In</h2>
            <?php if ($error): ?>
            <div class="alert alert-error"><?php echo htmlspecialchars($error); ?></div>
            <?php endif; ?>
            <form method="POST" action="/login.php">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required autocomplete="username">
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required autocomplete="current-password">
                </div>
                <button type="submit" class="btn btn-primary">Login</button>
            </form>
        </div>
    </div>

    <footer class="footer">
        <p>WikiEngine Platform v3.8.2 &copy; 2024</p>
    </footer>
</body>
</html>
