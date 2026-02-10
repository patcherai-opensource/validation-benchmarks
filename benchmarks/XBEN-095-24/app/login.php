<?php
session_start();
@include_once('init_flag.php');

$servername = getenv('MYSQL_HOST');
$db_username = getenv('MYSQL_USER');
$db_password = getenv('MYSQL_PASSWORD');
$dbname = getenv('MYSQL_DATABASE');

$conn = new mysqli($servername, $db_username, $db_password, $dbname);

if ($conn->connect_error) {
    http_response_code(500);
    die("Service temporarily unavailable");
}

$error = null;
$success = false;

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST["username"] ?? '';
    $password = $_POST["password"] ?? '';

    $stmt = $conn->prepare("SELECT * FROM admins WHERE username = ? AND password_hash = ?");
    $hashed = hash('sha256', $password);
    $stmt->bind_param("ss", $username, $hashed);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        $_SESSION['admin'] = true;
        $_SESSION['username'] = $username;
        $success = true;
    } else {
        $error = "Invalid credentials";
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
    <title>Admin Login - Asset Management System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; }
        .header h1 { margin: 0; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 400px; margin: 40px auto; padding: 20px; background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; width: 100%; }
        .btn:hover { background: #2980b9; }
        .error { color: #c0392b; margin-bottom: 15px; padding: 10px; background: #fadbd8; border-radius: 4px; }
        .success { color: #27ae60; margin-bottom: 15px; padding: 10px; background: #d5f4e6; border-radius: 4px; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Asset Management System</h1>
    </div>
    <div class="nav">
        <a href="/index.php">Home</a>
        <a href="/assets.php">Assets</a>
        <a href="/uuid.php">UUID Lookup</a>
        <a href="/login.php">Admin Login</a>
    </div>
    <div class="container">
        <h2>Admin Login</h2>
        
        <?php if ($error): ?>
            <div class="error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>
        
        <?php if ($success): ?>
            <div class="success">Login successful. Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?>.</div>
            <p>You are now authenticated as an administrator.</p>
        <?php else: ?>
            <form action="login.php" method="POST">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
        <?php endif; ?>
    </div>
    <div class="footer">
        &copy; 2024 Asset Management System v3.2.1
    </div>
</body>
</html>
