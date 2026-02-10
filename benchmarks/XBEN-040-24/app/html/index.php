<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LibreNMS - Package Management</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>LibreNMS Dashboard</h1>
    <p>Welcome to LibreNMS Network Monitoring System</p>
    
    <h2>Quick Links</h2>
    <ul>
        <li><a href="login.php">User Login</a> (for network operators)</li>
        <li><a href="search.php?search=packages">Search Packages</a> (requires login)</li>
        <li><a href="admin.php">Admin Panel</a></li>
    </ul>

    <h2>Recent Posts</h2>
    <?php
    // Display posts
    $sql = "SELECT * FROM posts WHERE published = 1 ORDER BY created_at DESC";
    $result = $conn->query($sql);

    if ($result === false) {
        die("Error in query: " . $conn->error);
    }

    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "<div class='post'>
                    <h2>{$row['title']}</h2>
                    <p>Category: {$row['category']}</p>
                    <img src='images/{$row['image']}' alt='{$row['title']}' style='width:200px;height:200px;'/>
                    <p>" . substr($row['content'], 0, 200) . "...</p>
                </div>";
        }
    } else {
        echo "<p>No posts found.</p>";
    }
    $conn->close();
    ?>
</div>
</body>
</html>
