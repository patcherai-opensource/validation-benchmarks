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

$settings = [];
$result = $conn->query("SELECT config_key, config_value FROM site_config ORDER BY config_key");
if ($result) {
    while ($row = $result->fetch_assoc()) {
        $settings[$row['config_key']] = $row['config_value'];
    }
}
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Site Settings - Admin</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Site Settings</h1>
    <p><a href="dashboard.php">&laquo; Back to Dashboard</a></p>

    <form method="POST" action="settings.php">
        <label for="site_name">Site Name:</label>
        <input type="text" id="site_name" name="site_name" value="<?php echo htmlspecialchars($settings['site_name'] ?? ''); ?>" disabled>

        <label for="theme">Theme:</label>
        <input type="text" id="theme" name="theme" value="<?php echo htmlspecialchars($settings['theme'] ?? ''); ?>" disabled>

        <label for="posts_per_page">Posts per Page:</label>
        <input type="number" id="posts_per_page" name="posts_per_page" value="<?php echo htmlspecialchars($settings['posts_per_page'] ?? '10'); ?>" disabled>

        <p><em>Settings modification is currently disabled.</em></p>
    </form>
</div>
</body>
</html>
