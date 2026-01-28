<?php
    $conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'blogDB');
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ezPortal CMS - Content Management</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>ezPortal CMS</h1>
        <p class="tagline">Enterprise Content Management System v4.2.1</p>
    </div>
    
    <nav class="main-nav">
        <a href="index.php">Home</a>
        <a href="articles.php">Articles</a>
        <a href="about.php">About</a>
        <a href="login.php">Staff Login</a>
    </nav>

    <div class="content-area">
        <h2>Recent Publications</h2>
        
        <form action="" method="GET" class="filter-form">
            <label for="category">Filter by category:</label>
            <select name="category" id="category" onchange="this.form.submit()">
                <option value="">All Categories</option>        
                <?php
                $cat_result = $conn->query("SELECT DISTINCT category FROM posts WHERE category != 'Secret'");
                while ($row = $cat_result->fetch_assoc()) {
                    $selected = (isset($_GET['category']) && $row['category'] == $_GET['category']) ? 'selected' : '';
                    echo "<option value='{$row['category']}' {$selected}>{$row['category']}</option>";
                }
                ?>
            </select>
        </form>

        <?php
        $category = isset($_GET['category']) ? $conn->real_escape_string($_GET['category']) : '';

        $sql = "SELECT * FROM posts WHERE published = 1 ";

        if ($category == "Secret")
            $category = "";

        if (!empty($category)) {
            $sql .= "AND category = '" . $category . "' ";
        }
        $sql .= "ORDER BY created_at DESC";

        $result = $conn->query($sql);

        if ($result === false) {
            die("<p class='error'>Database error occurred.</p>");
        }

        if ($result->num_rows > 0) {
            echo "<div class='articles-grid'>";
            while($row = $result->fetch_assoc()) {
                echo "<article class='post'>
                        <h3>{$row['title']}</h3>
                        <span class='category-tag'>{$row['category']}</span>
                        <img src='images/{$row['image']}' alt='{$row['title']}' style='width:200px;height:150px;object-fit:cover;'/>
                        <p>" . substr($row['content'], 0, 150) . "...</p>
                    </article>";
            }
            echo "</div>";
        } else {
            echo "<p>No articles found.</p>";
        }
        $conn->close();
        ?>
    </div>
    
    <footer>
        <p>&copy; 2024 ezPortal CMS. Powered by ezPublish Legacy Framework.</p>
        <p class="version-info">System version: 4.2.1 | Login handlers: standard, ldap</p>
    </footer>
</div>
</body>
</html>
