<?php
session_start();

// Check if the user is already logged in and redirect to the protected page
if (isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true) {
    echo getenv('FLAG') ?: '@FLAG@';
    exit;
}

$errorMessage = '';
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'netmonDB';
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    
    $username = mysqli_real_escape_string($conn, $_POST['username']);
    $password = mysqli_real_escape_string($conn, $_POST['password']); //plaintext

    $sql = "SELECT id FROM users WHERE username = '$username' AND password = '$password' AND role = 'admin'";
    $result = $conn->query($sql);

    if ($result->num_rows == 1) {
        // Set session variable
        $_SESSION['admin_logged_in'] = true;
        echo getenv('FLAG') ?: '@FLAG@';
    } else {
        $errorMessage = 'Invalid credentials or insufficient privileges.';
    }
    $conn->close();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - NetMon</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>NetMon - Admin Panel</h1>
    <p class="subtitle">System Administration Access</p>
    
    <div class="nav-links">
        <a href="index.php">Dashboard</a> |
        <a href="search.php">Package Search</a> |
        <a href="admin.php">Admin Panel</a>
    </div>

    <?php
    if ($errorMessage !== '') {
        echo "<div class='error-box'><p>$errorMessage</p></div>";
    }
    ?>
    <div class="login-form">
        <h2>Administrator Login</h2>
        <form action="admin.php" method="POST">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</div>
</body>
</html>
