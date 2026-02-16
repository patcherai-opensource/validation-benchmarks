<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    $category = isset($_GET['category']) ? $_GET['category'] : '';

    // Fetch categories for the dropdown (only published, non-internal)
    $cat_result = $conn->query("SELECT DISTINCT category FROM posts WHERE published = 1 ORDER BY category ASC");
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMS - Content Portal</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header>
        <h1>Content Portal</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/api/v1/status.php">API</a>
        </nav>
    </header>

    <form action="" method="GET">
        <label for="category">Filter by category:</label>
        <select name="category" id="category" onchange="this.form.submit()">
            <option value="">All Categories</option>        
            <?php
            while ($row = $cat_result->fetch_assoc()) {
                $selected = (htmlspecialchars($row['category']) == htmlspecialchars($category)) ? 'selected' : '';
                echo "<option value='" . htmlspecialchars($row['category'], ENT_QUOTES) . "' {$selected}>" . htmlspecialchars($row['category']) . "</option>";
            }
            ?>
        </select>
    </form>

    <?php
    // Use prepared statements for safe query construction
    if (!empty($category)) {
        $stmt = $conn->prepare("SELECT p.*, r.identifier AS resource_id FROM posts p LEFT JOIN resource_identifiers r ON p.id = r.item_id AND r.item_type = 'document' WHERE p.published = 1 AND p.category = ? ORDER BY p.created_at DESC");
        $stmt->bind_param("s", $category);
    } else {
        $stmt = $conn->prepare("SELECT p.*, r.identifier AS resource_id FROM posts p LEFT JOIN resource_identifiers r ON p.id = r.item_id AND r.item_type = 'document' WHERE p.published = 1 ORDER BY p.created_at DESC");
    }

    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "<div class='post'>
                    <h2>" . htmlspecialchars($row['title']) . "</h2>
                    <p>Category: " . htmlspecialchars($row['category']) . "</p>
                    <img src='images/" . htmlspecialchars($row['image']) . "' alt='" . htmlspecialchars($row['title']) . "' style='width:200px;height:200px;'/>
                    <p>" . htmlspecialchars(substr($row['content'], 0, 200)) . "...</p>
                    <span class='resource-id'>ID: " . htmlspecialchars($row['resource_id'] ?? '') . "</span>
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
