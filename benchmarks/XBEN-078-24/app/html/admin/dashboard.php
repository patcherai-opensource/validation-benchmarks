<?php
session_start();

if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: index.php');
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - CMS</title>
    <link rel="stylesheet" href="../styles.css">
    <style>
        .sidebar { float: left; width: 200px; background: #f4f4f4; padding: 20px; min-height: 400px; }
        .sidebar a { display: block; padding: 10px; margin: 5px 0; text-decoration: none; color: #333; }
        .sidebar a:hover { background: #ddd; }
        .sidebar a.active { background: #333; color: white; }
        .main-content { margin-left: 240px; padding: 20px; }
        .stats { display: flex; gap: 20px; margin-bottom: 30px; }
        .stat-box { background: #f9f9f9; padding: 20px; border-radius: 5px; flex: 1; text-align: center; }
        .stat-box h3 { margin: 0 0 10px 0; color: #666; font-size: 14px; }
        .stat-box .number { font-size: 32px; font-weight: bold; color: #333; }
    </style>
</head>
<body>
<div class="container">
    <h1>Admin Panel</h1>
    <p>Welcome, <?php echo htmlspecialchars($_SESSION['admin_username']); ?> | <a href="logout.php">Logout</a></p>
    
    <div class="sidebar">
        <a href="dashboard.php" class="active">Dashboard</a>
        <a href="posts.php">Posts</a>
        <a href="translations.php">Translations</a>
        <a href="settings.php">Settings</a>
    </div>
    
    <div class="main-content">
        <h2>Dashboard Overview</h2>
        
        <?php
        $conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
        if (!$conn->connect_error) {
            $posts_count = $conn->query("SELECT COUNT(*) as cnt FROM posts")->fetch_assoc()['cnt'];
            $translations_count = $conn->query("SELECT COUNT(*) as cnt FROM translations")->fetch_assoc()['cnt'];
            $conn->close();
        } else {
            $posts_count = 0;
            $translations_count = 0;
        }
        ?>
        
        <div class="stats">
            <div class="stat-box">
                <h3>Total Posts</h3>
                <div class="number"><?php echo $posts_count; ?></div>
            </div>
            <div class="stat-box">
                <h3>Translation Entries</h3>
                <div class="number"><?php echo $translations_count; ?></div>
            </div>
        </div>
        
        <h3>Quick Actions</h3>
        <ul>
            <li><a href="posts.php">Manage Posts</a></li>
            <li><a href="translations.php">Manage Translations</a></li>
        </ul>
    </div>
    <div style="clear: both;"></div>
</div>
</body>
</html>
