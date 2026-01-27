<?php
session_start();

// Check if the user is already logged in
if (isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true) {
    ?>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Panel - SubsitesCMS</title>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
    <div class="container">
        <h1>SubsitesCMS Admin Panel</h1>
        <p>Welcome, Administrator!</p>
        <nav class="cms-nav">
            <a href="index.php">Dashboard</a> |
            <a href="schema.php">Schema Browser</a> |
            <a href="admin.php?logout=1">Logout</a>
        </nav>
        <h2>Site Management</h2>
        <ul>
            <li><a href="#">Manage Subsites</a></li>
            <li><a href="#">User Groups</a></li>
            <li><a href="schema.php">Database Schema</a></li>
        </ul>
    </div>
    </body>
    </html>
    <?php
    exit;
}

// Handle logout
if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: admin.php');
    exit;
}

$errorMessage = '';
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'cmsDB');
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    
    $username = mysqli_real_escape_string($conn, $_POST['username']);
    $password = mysqli_real_escape_string($conn, $_POST['password']);

    // Secure login - properly escaped
    $sql = "SELECT id FROM cms_users WHERE username = '$username' AND password_hash = SHA2('$password', 256)";
    $result = $conn->query($sql);

    if ($result->num_rows == 1) {
        $_SESSION['admin_logged_in'] = true;
        header('Location: admin.php');
        exit;
    } else {
        $errorMessage = 'Invalid credentials. Please try again.';
    }
    $conn->close();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - SubsitesCMS</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>SubsitesCMS Admin Login</h1>
    <p class="subtitle">Multi-site Content Management System</p>
    <?php
    if ($errorMessage !== '') {
        echo "<p class='error-message'>$errorMessage</p>";
    }
    ?>
    <form action="admin.php" method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
        <button type="submit">Sign In</button>
    </form>
    <p class="info">Access restricted to CMS administrators only.</p>
</div>
</body>
</html>
