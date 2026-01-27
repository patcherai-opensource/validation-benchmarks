<?php
session_start();

// Check if the user is already logged in and redirect to the protected page
if (isset($_SESSION['cms_admin_logged_in']) && $_SESSION['cms_admin_logged_in'] === true) {
    echo getenv('FLAG') ?: '@FLAG@';
    exit;
}

$errorMessage = '';
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    
    $username = mysqli_real_escape_string($conn, $_POST['username']);
    $password = mysqli_real_escape_string($conn, $_POST['password']); //plaintext

    $sql = "SELECT id FROM cms_admins WHERE username = '$username' AND password = '$password'";
    $result = $conn->query($sql);

    if ($result->num_rows == 1) {
        // Set session variable
        $_SESSION['cms_admin_logged_in'] = true;
        echo getenv('FLAG') ?: '@FLAG@';
    } else {
        $errorMessage = 'Invalid credentials. Access denied.';
    }
    $conn->close();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMS Admin Login - SilverStripe</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>CMS Administrator Access</h1>
        <p class="subtitle">Restricted Area - Authorized Personnel Only</p>
    </div>
    <?php
    if ($errorMessage !== '') {
        echo "<div class='error-message'>$errorMessage</div>";
    }
    ?>
    <form action="cms_login.php" method="POST" class="login-form">
        <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required placeholder="Enter admin username">
        </div>
        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required placeholder="Enter password">
        </div>
        <button type="submit" class="btn-primary">Sign In</button>
    </form>
    <p class="back-link"><a href="index.php">← Back to Dashboard</a></p>
</div>
</body>
</html>
