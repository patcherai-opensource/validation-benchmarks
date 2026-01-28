<?php
session_start();

// Only accessible when logged in
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header("Location: admin.php");
    exit;
}

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'subsiteDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SilverSubsite CMS - Admin Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="cms-header">
        <h1>Admin Dashboard</h1>
        <p class="tagline">Welcome, Administrator</p>
    </header>

    <nav class="main-nav">
        <a href="index.php">Dashboard</a>
        <a href="groups.php">Group Management</a>
        <a href="subsites.php">Subsites</a>
        <a href="settings.php">Settings</a>
        <a href="admin_dashboard.php" class="active">Admin Panel</a>
        <a href="logout.php">Logout</a>
    </nav>

    <section class="admin-panel">
        <h2>Administrative Functions</h2>
        <p>Welcome to the admin control panel. You are authenticated.</p>
        
        <div class="admin-actions">
            <h3>Quick Actions</h3>
            <ul>
                <li>Manage Users</li>
                <li>View Audit Logs</li>
                <li>Database Maintenance</li>
                <li>Cache Clear</li>
            </ul>
        </div>
    </section>
</div>
<?php $conn->close(); ?>
</body>
</html>
