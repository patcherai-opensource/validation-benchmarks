<?php
session_start();

// Redirect if already logged in
if (isset($_SESSION['user_id'])) {
    if ($_SESSION['is_admin']) {
        header("Location: admin.php");
    } else {
        header("Location: index.php");
    }
    exit;
}

$errorMessage = '';
$conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'libraryDB');

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = trim($_POST['username']);
    $password = $_POST['password'];
    
    // Proper parameterized query - no SQL injection here
    $stmt = $conn->prepare("SELECT id, username, password, is_admin FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($result->num_rows == 1) {
        $user = $result->fetch_assoc();
        // Use password_verify for secure comparison
        if (password_verify($password, $user['password'])) {
            $_SESSION['user_id'] = $user['id'];
            $_SESSION['username'] = $user['username'];
            $_SESSION['is_admin'] = (bool)$user['is_admin'];
            
            if ($user['is_admin']) {
                header("Location: admin.php");
            } else {
                header("Location: index.php");
            }
            exit;
        } else {
            $errorMessage = 'Invalid username or password.';
        }
    } else {
        $errorMessage = 'Invalid username or password.';
    }
    $stmt->close();
}
$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Calibre-Web</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>📚 Calibre-Web Login</h1>
    
    <?php if ($errorMessage !== ''): ?>
        <p class="error"><?php echo htmlspecialchars($errorMessage); ?></p>
    <?php endif; ?>
    
    <form action="login.php" method="POST" class="auth-form">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
        
        <button type="submit">Login</button>
    </form>
    
    <p class="auth-link">Don't have an account? <a href="register.php">Register here</a></p>
    <p class="auth-link"><a href="index.php">← Back to Library</a></p>
</div>
<footer>
    <p>Calibre-Web v0.6.19</p>
</footer>
</body>
</html>
