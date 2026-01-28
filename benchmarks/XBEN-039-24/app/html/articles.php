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
    <title>ezPortal CMS - Articles</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>ezPortal CMS</h1>
        <p class="tagline">Enterprise Content Management System</p>
    </div>
    
    <nav class="main-nav">
        <a href="index.php">Home</a>
        <a href="articles.php">Articles</a>
        <a href="about.php">About</a>
        <a href="login.php">Staff Login</a>
    </nav>

    <div class="content-area">
        <h2>All Articles</h2>
        
        <?php
        $page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
        $per_page = 5;
        $offset = ($page - 1) * $per_page;
        
        // Safe query with parameterization
        $sql = "SELECT * FROM posts WHERE published = 1 ORDER BY created_at DESC LIMIT ? OFFSET ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ii", $per_page, $offset);
        $stmt->execute();
        $result = $stmt->get_result();
        
        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                echo "<article class='article-item'>
                        <h3>" . htmlspecialchars($row['title']) . "</h3>
                        <span class='category-tag'>" . htmlspecialchars($row['category']) . "</span>
                        <p class='article-date'>Published: " . $row['created_at'] . "</p>
                        <p>" . htmlspecialchars(substr($row['content'], 0, 200)) . "...</p>
                    </article>";
            }
        } else {
            echo "<p>No articles found.</p>";
        }
        
        // Pagination
        $count_result = $conn->query("SELECT COUNT(*) as total FROM posts WHERE published = 1");
        $total = $count_result->fetch_assoc()['total'];
        $total_pages = ceil($total / $per_page);
        
        echo "<div class='pagination'>";
        for ($i = 1; $i <= $total_pages; $i++) {
            $active = ($i == $page) ? 'active' : '';
            echo "<a href='?page=$i' class='$active'>$i</a> ";
        }
        echo "</div>";
        
        $conn->close();
        ?>
    </div>
    
    <footer>
        <p>&copy; 2024 ezPortal CMS. All rights reserved.</p>
    </footer>
</div>
</body>
</html>
