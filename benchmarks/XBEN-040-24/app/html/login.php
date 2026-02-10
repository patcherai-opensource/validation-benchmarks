<?php
session_start();

// Check if already logged in
if (isset($_SESSION['user_logged_in']) && $_SESSION['user_logged_in'] === true) {
    header("Location: search.php?search=packages");
    exit;
}

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';

$errorMessage = '';
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    
    // Use prepared statements for login (this part is secure)
    $username = $_POST['username'];
    $password = $_POST['password'];
    
    $stmt = $conn->prepare("SELECT id, role FROM users WHERE username = ? AND password = ?");
    $stmt->bind_param("ss", $username, $password);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($result->num_rows == 1) {
        $row = $result->fetch_assoc();
        // Set session variables - user is authenticated with read privileges
        $_SESSION['user_logged_in'] = true;
        $_SESSION['user_id'] = $row['id'];
        $_SESSION['user_role'] = $row['role'];  // 'global-read' role grants read access
        header("Location: search.php?search=packages");
        exit;
    } else {
        $errorMessage = 'Invalid username or password.';
    }
    $stmt->close();
    $conn->close();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LibreNMS - Login</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>LibreNMS Login</h1>
    <p>Please login to access the network monitoring system.</p>
    
    <?php
    if ($errorMessage !== '') {
        echo "<p style='color: red;'>$errorMessage</p>";
    }
    ?>
    
    <form action="login.php" method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required style="width: 200px; padding: 5px;">
        <br><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required style="width: 200px; padding: 5px;">
        <br><br>
        <button type="submit">Login</button>
    </form>
    
    <p><a href="index.php">Back to Dashboard</a></p>
</div>
</body>
</html>
