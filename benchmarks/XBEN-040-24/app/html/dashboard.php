<?php
session_start();

if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header("Location: admin.php");
    exit;
}

$mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
$mysql_user = getenv('MYSQL_USER') ?: 'user';
$mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
$mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
$conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);

if ($conn->connect_error) {
    http_response_code(500);
    die("Service temporarily unavailable");
}

$postCount = 0;
$result = $conn->query("SELECT COUNT(*) as cnt FROM posts WHERE published = 1");
if ($result) {
    $row = $result->fetch_assoc();
    $postCount = $row['cnt'];
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Admin Dashboard</h1>
    <p>Welcome, <?php echo htmlspecialchars($_SESSION['admin_username']); ?> (<?php echo htmlspecialchars($_SESSION['admin_role']); ?>)</p>
    
    <div class="dashboard-stats">
        <h2>Site Statistics</h2>
        <p>Published Posts: <?php echo $postCount; ?></p>
    </div>

    <div class="dashboard-menu">
        <h2>Management</h2>
        <ul>
            <li><a href="posts.php">Manage Posts</a></li>
            <li><a href="data_export.php">Data Export</a></li>
            <li><a href="settings.php">Site Settings</a></li>
        </ul>
    </div>

    <p><a href="logout.php">Logout</a></p>
</div>
</body>
</html>
