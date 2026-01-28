<?php
$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$category = isset($_GET['category']) ? $_GET['category'] : '';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Library - GlobalCMS</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>Content Library</h1>
    <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/content.php" class="active">Content Library</a>
        <a href="/api.php">API Documentation</a>
        <a href="/admin/">Admin Panel</a>
    </nav>
    
    <div class="filter-bar">
        <form action="" method="GET">
            <label for="category">Filter by category:</label>
            <select name="category" id="category" onchange="this.form.submit()">
                <option value="">All Categories</option>
                <?php
                $cat_result = $conn->query("SELECT DISTINCT category FROM posts WHERE published = 1");
                while ($row = $cat_result->fetch_assoc()) {
                    $selected = ($row['category'] === $category) ? 'selected' : '';
                    echo "<option value='" . htmlspecialchars($row['category']) . "' {$selected}>" . htmlspecialchars($row['category']) . "</option>";
                }
                ?>
            </select>
        </form>
    </div>
    
    <div class="content-grid">
        <?php
        // Safe query using parameterized approach
        $sql = "SELECT * FROM posts WHERE published = 1";
        if (!empty($category)) {
            $stmt = $conn->prepare("SELECT * FROM posts WHERE published = 1 AND category = ? ORDER BY created_at DESC");
            $stmt->bind_param("s", $category);
            $stmt->execute();
            $result = $stmt->get_result();
        } else {
            $result = $conn->query("SELECT * FROM posts WHERE published = 1 ORDER BY created_at DESC");
        }
        
        if ($result && $result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                echo "<div class='content-item'>
                    <h3>" . htmlspecialchars($row['title']) . "</h3>
                    <span class='category-tag'>" . htmlspecialchars($row['category']) . "</span>
                    <p>" . htmlspecialchars(substr($row['content'], 0, 200)) . "...</p>
                    <span class='date'>" . htmlspecialchars($row['created_at']) . "</span>
                </div>";
            }
        } else {
            echo "<p>No content found.</p>";
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
