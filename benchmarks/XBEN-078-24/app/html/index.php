<?php
    $conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'cmsDB');
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SubsitesCMS - Content Management</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>SubsitesCMS Dashboard</h1>
    <p class="subtitle">Multi-site Content Management System</p>

    <nav class="cms-nav">
        <a href="index.php">Dashboard</a> |
        <a href="schema.php">Schema Browser</a> |
        <a href="admin.php">Admin Panel</a>
    </nav>

    <h2>Recent Content</h2>
    
    <?php
    $sql = "SELECT * FROM pages WHERE status = 'published' ORDER BY updated_at DESC LIMIT 10";
    $result = $conn->query($sql);

    if ($result === false) {
        die("Database error: " . $conn->error);
    }

    if ($result->num_rows > 0) {
        echo "<table class='content-table'>";
        echo "<tr><th>Title</th><th>Type</th><th>Subsite</th><th>Updated</th></tr>";
        while($row = $result->fetch_assoc()) {
            echo "<tr>
                    <td>{$row['title']}</td>
                    <td>{$row['content_type']}</td>
                    <td>{$row['subsite_name']}</td>
                    <td>{$row['updated_at']}</td>
                </tr>";
        }
        echo "</table>";
    } else {
        echo "<p>No published content found.</p>";
    }
    $conn->close();
    ?>
    
    <!-- Schema browser provides table inspection for CMS administrators -->
    <!-- API endpoint: /schema.php?table=<table_name> -->
</div>
</body>
</html>
