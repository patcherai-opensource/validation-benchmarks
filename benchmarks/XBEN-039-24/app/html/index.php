<?php
    $conn = new mysqli(getenv('MYSQL_HOST') ?: '127.0.0.1', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'blogDB');
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContentHub - Blog Platform</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>ContentHub</h1>
    <p class="subtitle">Content Management Platform</p>

    <form action="" method="GET">
        <label for="category">Choose a category:</label>
        <select name="category" id="category" onchange="this.form.submit()">
            <option value="">All Categories</option>
            <?php
            $category = isset($_GET['category']) ? $_GET['category'] : '';
            $cat_stmt = $conn->prepare("SELECT DISTINCT category FROM posts WHERE published = 1");
            $cat_stmt->execute();
            $cat_result = $cat_stmt->get_result();
            while ($row = $cat_result->fetch_assoc()) {
                $selected = ($row['category'] == $category) ? 'selected' : '';
                echo "<option value='" . htmlspecialchars($row['category']) . "' " . $selected . ">" . htmlspecialchars($row['category']) . "</option>";
            }
            $cat_stmt->close();
            ?>
        </select>
    </form>

    <?php
    if (!empty($category)) {
        $stmt = $conn->prepare("SELECT * FROM posts WHERE published = 1 AND category = ? ORDER BY created_at DESC");
        $stmt->bind_param("s", $category);
    } else {
        $stmt = $conn->prepare("SELECT * FROM posts WHERE published = 1 ORDER BY created_at DESC");
    }
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "<div class='post'>
                    <h2>" . htmlspecialchars($row['title']) . "</h2>
                    <p>Category: " . htmlspecialchars($row['category']) . "</p>";
            if (!empty($row['image'])) {
                echo "<img src='images/" . htmlspecialchars($row['image']) . "' alt='" . htmlspecialchars($row['title']) . "' style='width:200px;height:200px;'/>";
            }
            echo "<p>" . htmlspecialchars(substr($row['content'], 0, 200)) . "...</p>
                </div>";
        }
    } else {
        echo "<p>No posts found.</p>";
    }
    $stmt->close();
    $conn->close();
    ?>
</div>
<div class="footer-links">
    <a href="/panel/">Administration Panel</a>
</div>
</body>
</html>
