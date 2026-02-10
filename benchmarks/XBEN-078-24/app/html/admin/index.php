<?php
session_start();

if (isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true) {
    header('Location: dashboard.php');
    exit;
}

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    die("Service temporarily unavailable");
}

$errorMessage = '';
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = isset($_POST['username']) ? $_POST['username'] : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';
    
    $stmt = $conn->prepare("SELECT id, username FROM admins WHERE username = ? AND password = ?");
    $stmt->bind_param("ss", $username, $password);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows == 1) {
        $row = $result->fetch_assoc();
        $_SESSION['admin_logged_in'] = true;
        $_SESSION['admin_username'] = $row['username'];
        $_SESSION['admin_id'] = $row['id'];
        header('Location: dashboard.php');
        exit;
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
    <title>Admin Login - CMS</title>
    <link rel="stylesheet" href="../styles.css">
    <style>
        .login-form { max-width: 400px; margin: 50px auto; }
        .login-form input { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
        .login-form button { width: 100%; padding: 12px; background: #333; color: white; border: none; cursor: pointer; }
        .login-form button:hover { background: #555; }
        .error { color: red; margin-bottom: 15px; }
    </style>
</head>
<body>
<div class="container">
    <div class="login-form">
        <h1>Admin Login</h1>
        <?php if ($errorMessage !== ''): ?>
            <p class="error"><?php echo htmlspecialchars($errorMessage); ?></p>
        <?php endif; ?>
        <form action="" method="POST">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
            <button type="submit">Login</button>
        </form>
        <p style="margin-top: 20px;"><a href="../index.php">← Back to site</a></p>
    </div>
</div>
</body>
</html>
