<?php
    $conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GlobalCMS - Multilingual Content Management</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>GlobalCMS</h1>
    <p class="tagline">Enterprise Content Management & Localization Platform</p>

    <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/content.php">Content Library</a>
        <a href="/api.php">API Documentation</a>
        <a href="/admin/">Admin Panel</a>
    </nav>

    <div class="features">
        <h2>Platform Features</h2>
        <ul>
            <li>Multi-language content management</li>
            <li>Translation workflow automation</li>
            <li>API-driven content delivery</li>
            <li>Enterprise security controls</li>
        </ul>
    </div>

    <div class="recent-content">
        <h2>Recent Updates</h2>
        <?php
        $sql = "SELECT * FROM posts WHERE published = 1 ORDER BY created_at DESC LIMIT 3";
        $result = $conn->query($sql);
        
        if ($result && $result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                echo "<div class='post'>
                        <h3>{$row['title']}</h3>
                        <span class='category-tag'>{$row['category']}</span>
                        <p>" . substr($row['content'], 0, 150) . "...</p>
                    </div>";
            }
        } else {
            echo "<p>No recent content.</p>";
        }
        ?>
    </div>
</div>
<footer>
    <p>&copy; 2024 GlobalCMS - Version 4.2.1</p>
</footer>
<?php $conn->close(); ?>
</body>
</html>
