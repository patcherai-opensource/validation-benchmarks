<?php
session_start();

// Simple admin authentication
$errorMessage = '';
$isLoggedIn = isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true;

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['action']) && $_POST['action'] == 'login') {
    $conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    
    $username = mysqli_real_escape_string($conn, $_POST['username'] ?? '');
    $password = mysqli_real_escape_string($conn, $_POST['password'] ?? '');

    $sql = "SELECT id, role FROM admins WHERE username = '$username' AND password = '$password'";
    $result = $conn->query($sql);

    if ($result && $result->num_rows == 1) {
        $row = $result->fetch_assoc();
        $_SESSION['admin_logged_in'] = true;
        $_SESSION['admin_role'] = $row['role'];
        $_SESSION['admin_id'] = $row['id'];
        $isLoggedIn = true;
    } else {
        $errorMessage = 'Authentication failed. Invalid credentials.';
    }
    $conn->close();
}

if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: /admin/');
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GlobalCMS Admin Panel</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="admin-container">
    <h1>GlobalCMS Administration</h1>
    
    <?php if (!$isLoggedIn): ?>
    <div class="login-form">
        <h2>Administrator Login</h2>
        <?php if ($errorMessage !== ''): ?>
            <p class="error"><?php echo htmlspecialchars($errorMessage); ?></p>
        <?php endif; ?>
        <form action="/admin/" method="POST">
            <input type="hidden" name="action" value="login">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn-primary">Sign In</button>
        </form>
    </div>
    <?php else: ?>
    <div class="admin-dashboard">
        <nav class="admin-nav">
            <a href="/admin/">Dashboard</a>
            <a href="/admin/content.php">Content Management</a>
            <a href="/admin/translations.php">Translations</a>
            <a href="/admin/users.php">User Management</a>
            <a href="/admin/settings.php">Settings</a>
            <a href="/admin/?logout=1" class="logout">Logout</a>
        </nav>
        
        <div class="dashboard-content">
            <h2>Dashboard Overview</h2>
            <p>Welcome to the GlobalCMS administration panel.</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Content Items</h3>
                    <span class="stat-number">156</span>
                </div>
                <div class="stat-card">
                    <h3>Translations</h3>
                    <span class="stat-number">1,247</span>
                </div>
                <div class="stat-card">
                    <h3>Languages</h3>
                    <span class="stat-number">12</span>
                </div>
                <div class="stat-card">
                    <h3>Active Users</h3>
                    <span class="stat-number">8</span>
                </div>
            </div>
            
            <div class="quick-actions">
                <h3>Quick Actions</h3>
                <ul>
                    <li><a href="/admin/translations.php">Manage Translation Strings</a></li>
                    <li><a href="/admin/content.php">Edit Content</a></li>
                    <li><a href="/admin/api-docs.php">API Documentation</a></li>
                </ul>
            </div>
        </div>
    </div>
    <?php endif; ?>
</div>
<footer>
    <p>&copy; 2024 GlobalCMS - Admin Panel v4.2.1</p>
</footer>
</body>
</html>
