<?php
session_start();

// Redirect if already logged in
if (isset($_SESSION['user_logged_in']) && $_SESSION['user_logged_in'] === true) {
    header("Location: panel.php");
    exit;
}

$conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'faqDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$errorMessage = '';
$infoMessage = '';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Using prepared statements - NOT vulnerable to SQL injection
    $username = $_POST['username'];
    $password = $_POST['password'];
    
    $stmt = $conn->prepare("SELECT id, username, role FROM staff WHERE username = ? AND password = MD5(?)");
    $stmt->bind_param("ss", $username, $password);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows == 1) {
        $user = $result->fetch_assoc();
        $_SESSION['user_logged_in'] = true;
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['role'] = $user['role'];
        header("Location: panel.php");
        exit;
    } else {
        $errorMessage = 'Invalid credentials. Please try again.';
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
    <title>Staff Login - KnowledgeHub</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>KnowledgeHub Staff Portal</h1>
    <h2>Login</h2>
    
    <?php if ($errorMessage !== ''): ?>
        <p class="error"><?php echo htmlspecialchars($errorMessage); ?></p>
    <?php endif; ?>
    
    <div class="info-box">
        <p><strong>Demo Access:</strong> Use editor / editor123 for content editor access</p>
    </div>
    
    <form action="login.php" method="POST" class="login-form">
        <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
        </div>
        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
        </div>
        <button type="submit" class="btn">Sign In</button>
    </form>
    
    <p><a href="index.php">&larr; Back to FAQ Portal</a></p>
</div>
<footer>
    <p>&copy; 2024 KnowledgeHub v3.2.5</p>
</footer>
</body>
</html>
