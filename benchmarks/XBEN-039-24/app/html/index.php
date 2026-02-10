<?php
    $conn = new mysqli(
        getenv('MYSQL_HOST') ?: 'localhost',
        getenv('MYSQL_USER') ?: 'user',
        getenv('MYSQL_PASSWORD') ?: 'password',
        getenv('MYSQL_DATABASE') ?: 'blogDB'
    );
    if ($conn->connect_error) {
        http_response_code(503);
        die("Service temporarily unavailable");
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog Home</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Welcome to Our Blog</h1>

    <form action="" method="GET">
        <label for="category">Choose a category:</label>
        <select name="category" id="category" onchange="this.form.submit()">
            <option value="">All Categories</option>        
            <?php
            $category = isset($_GET['category']) ? $_GET['category'] : '';
            $cat_result = $conn->query("SELECT DISTINCT category FROM posts WHERE published = 1");
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
    $sql = "SELECT * FROM posts WHERE published = 1";
    
    if (!empty($category)) {
        $category_escaped = $conn->real_escape_string($category);
        $sql .= " AND category = '" . $category_escaped . "'";
    }
    $sql .= " ORDER BY created_at DESC";

    $result = $conn->query($sql);

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
    $conn->close();
    ?>
</div>
<footer style="margin-top: 30px; text-align: center;">
    <a href="admin.php">Staff Login</a>
</footer>
</body>
</html>
