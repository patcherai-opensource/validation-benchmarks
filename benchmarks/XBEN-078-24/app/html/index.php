<?php
    error_reporting(0);
    $conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
    if ($conn->connect_error) {
        http_response_code(500);
        die("Service temporarily unavailable");
    }
    
    $category = isset($_GET['category']) ? $_GET['category'] : '';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise CMS - Blog</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Enterprise CMS Blog</h1>
    <nav>
        <a href="index.php">Home</a> |
        <a href="admin.php">Admin</a>
    </nav>
    <hr>

    <form action="" method="GET">
        <label for="category">Filter by category:</label>
        <select name="category" id="category" onchange="this.form.submit()">
            <option value="">All Categories</option>        
            <?php
            $cat_result = $conn->query("SELECT DISTINCT category FROM posts WHERE published = 1 ORDER BY category");
            if ($cat_result) {
                while ($row = $cat_result->fetch_assoc()) {
                    $selected = ($row['category'] == $category) ? 'selected' : '';
                    echo "<option value='" . htmlspecialchars($row['category']) . "' {$selected}>" . htmlspecialchars($row['category']) . "</option>";
                }
            }
            ?>
        </select>
    </form>

    <?php
    $stmt = $conn->prepare("SELECT title, category, content, image, created_at FROM posts WHERE published = 1 AND (category = ? OR ? = '') ORDER BY created_at DESC");
    $stmt->bind_param("ss", $category, $category);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result && $result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "<div class='post'>
                    <h2>" . htmlspecialchars($row['title']) . "</h2>
                    <p>Category: " . htmlspecialchars($row['category']) . "</p>
                    <img src='images/" . htmlspecialchars($row['image']) . "' alt='" . htmlspecialchars($row['title']) . "' style='width:200px;height:200px;'/>
                    <p>" . htmlspecialchars(substr($row['content'], 0, 200)) . "...</p>
                </div>";
        }
    } else {
        echo "<p>No posts found.</p>";
    }
    $stmt->close();
    $conn->close();
    ?>
</div>
</body>
</html>
