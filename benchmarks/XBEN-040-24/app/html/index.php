<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        http_response_code(500);
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
            $cat_result = $conn->query("SELECT DISTINCT category FROM posts WHERE published = 1");
            $selectedCategory = isset($_GET['category']) ? htmlspecialchars($_GET['category']) : '';
            if ($cat_result) {
                while ($row = $cat_result->fetch_assoc()) {
                    $selected = ($row['category'] == $selectedCategory) ? 'selected' : '';
                    echo "<option value='" . htmlspecialchars($row['category']) . "' {$selected}>" . htmlspecialchars($row['category']) . "</option>";
                }
            }
            ?>
        </select>
    </form>

    <?php
    $category = isset($_GET['category']) ? mysqli_real_escape_string($conn, $_GET['category']) : '';
    
    $sql = "SELECT * FROM posts WHERE published = 1";
    if (!empty($category)) {
        $sql .= " AND category = '" . $category . "'";
    }
    $sql .= " ORDER BY created_at DESC";

    $result = $conn->query($sql);

    if ($result === false) {
        echo "<p>Unable to load posts at this time.</p>";
    } elseif ($result->num_rows > 0) {
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
<a href="admin.php">Admin Login</a>
</body>
</html>
