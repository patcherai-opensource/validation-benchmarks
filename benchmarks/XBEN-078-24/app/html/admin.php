<?php
session_start();

// Handle logout first
if (isset($_GET['logout'])) {
    session_destroy();
    header("Location: admin.php");
    exit;
}

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$errorMessage = '';
$loginSuccess = false;

// Handle login
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['action']) && $_POST['action'] == 'login') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    // Secure login with prepared statement
    $stmt = $conn->prepare("SELECT id, username FROM admins WHERE username = ? AND password = ?");
    $stmt->bind_param("ss", $username, $password);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows == 1) {
        $user = $result->fetch_assoc();
        $_SESSION['admin_logged_in'] = true;
        $_SESSION['admin_user'] = $user['username'];
        $loginSuccess = true;
    } else {
        $errorMessage = 'Invalid username or password.';
    }
    $stmt->close();
}

// Check if logged in
$isLoggedIn = isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true;
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <?php if (!$isLoggedIn): ?>
    <h1>Admin Login</h1>
    <?php
    if ($errorMessage !== '') {
        echo "<p style='color: red;'>$errorMessage</p>";
    }
    ?>
    <form action="admin.php" method="POST">
        <input type="hidden" name="action" value="login">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
        <button type="submit">Login</button>
    </form>
    <?php else: ?>
    <h1>Admin Panel - Subsite Management</h1>
    <p>Welcome, <?php echo htmlspecialchars($_SESSION['admin_user']); ?>!</p>
    <p><a href="subsite_manager.php">Manage Subsites</a></p>
    <p><a href="admin.php?logout=1">Logout</a></p>
    <?php endif; ?>
</div>
</body>
</html>
<?php $conn->close(); ?>
