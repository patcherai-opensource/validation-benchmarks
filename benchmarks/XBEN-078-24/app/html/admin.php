<?php
session_start();
error_reporting(0);

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    http_response_code(500);
    die("Service temporarily unavailable");
}

$errorMessage = '';
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['username']) && isset($_POST['password'])) {
    $username = mysqli_real_escape_string($conn, $_POST['username']);
    $password = mysqli_real_escape_string($conn, $_POST['password']);

    $sql = "SELECT id FROM admins WHERE username = '$username' AND password = '$password'";
    $result = $conn->query($sql);

    if ($result && $result->num_rows == 1) {
        $_SESSION['admin_logged_in'] = true;
        header("Location: admin.php");
        exit;
    } else {
        $errorMessage = 'Invalid username or password.';
    }
}

$isLoggedIn = isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true;
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - Enterprise CMS</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <?php if (!$isLoggedIn): ?>
    <h1>Admin Login</h1>
    <?php if ($errorMessage !== ''): ?>
        <p style='color: red;'><?php echo htmlspecialchars($errorMessage); ?></p>
    <?php endif; ?>
    <form action="admin.php" method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
        <button type="submit">Login</button>
    </form>
    <?php else: ?>
    <h1>Enterprise CMS - Admin Dashboard</h1>
    <nav>
        <a href="admin.php">Dashboard</a> |
        <a href="subsites.php">Manage Subsites</a> |
        <a href="admin.php?logout=1">Logout</a>
    </nav>
    <hr>
    <h2>Welcome, Administrator</h2>
    <p>Use the navigation above to manage your subsites and content.</p>
    
    <h3>Quick Stats</h3>
    <?php
    $postCount = $conn->query("SELECT COUNT(*) as cnt FROM posts")->fetch_assoc()['cnt'];
    $subsiteCount = $conn->query("SELECT COUNT(*) as cnt FROM subsites")->fetch_assoc()['cnt'];
    ?>
    <ul>
        <li>Total Posts: <?php echo $postCount; ?></li>
        <li>Active Subsites: <?php echo $subsiteCount; ?></li>
    </ul>
    <?php endif; ?>
</div>
</body>
</html>
<?php
if (isset($_GET['logout'])) {
    session_destroy();
    header("Location: admin.php");
    exit;
}
$conn->close();
?>
