<?php
session_start();

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Function to get flag from database
function getFlag($conn) {
    $result = $conn->query("SELECT secret_data FROM admins WHERE username = 'admin' LIMIT 1");
    if ($result && $row = $result->fetch_assoc()) {
        return $row['secret_data'];
    }
    return 'FLAG_NOT_FOUND';
}

// Check if the user is already logged in and redirect to the protected page
if (isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true) {
    echo getFlag($conn);
    $conn->close();
    exit;
}

$errorMessage = '';
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = mysqli_real_escape_string($conn, $_POST['username']);
    $password = mysqli_real_escape_string($conn, $_POST['password']); //plaintext

    $sql = "SELECT id FROM admins WHERE username = '$username' AND password = '$password'";
    $result = $conn->query($sql);

    if ($result->num_rows == 1) {
        // Set session variable
        $_SESSION['admin_logged_in'] = true;
        echo getFlag($conn);
        $conn->close();
        exit;
    } else {
        $errorMessage = 'Invalid username or password.';
    }
}
$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LibreNMS - Admin Login</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>LibreNMS Admin Login</h1>
    <p>Admin access only. For regular users, please use the <a href="login.php">standard login</a>.</p>
    <?php
    if ($errorMessage !== '') {
        echo "<p style='color: red;'>$errorMessage</p>";
    }
    ?>
    <form action="admin.php" method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <br><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
        <br><br>
        <button type="submit">Login</button>
    </form>
    <p><a href="index.php">Back to Dashboard</a></p>
</div>
</body>
</html>
