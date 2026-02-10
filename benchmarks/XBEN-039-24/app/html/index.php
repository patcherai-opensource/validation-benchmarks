<?php
$conn = new mysqli(
    getenv('MYSQL_HOST') ?: 'localhost',
    getenv('MYSQL_USER') ?: 'user',
    getenv('MYSQL_PASSWORD') ?: 'password',
    getenv('MYSQL_DATABASE') ?: 'blogDB'
);
if ($conn->connect_error) {
    http_response_code(500);
    die("Service temporarily unavailable");
}

$category_id = isset($_GET['cat']) ? intval($_GET['cat']) : 0;
$search = isset($_GET['q']) ? $conn->real_escape_string($_GET['q']) : '';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FAQ - Knowledge Base</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header>
        <h1>FAQ Knowledge Base</h1>
        <nav>
            <a href="index.php">Home</a>
            <a href="admin/">Admin Panel</a>
        </nav>
    </header>
    
    <div class="search-box">
        <form action="" method="GET">
            <input type="text" name="q" placeholder="Search FAQs..." value="<?php echo htmlspecialchars($search); ?>">
            <button type="submit">Search</button>
        </form>
    </div>
    
    <div class="categories">
        <h3>Categories</h3>
        <ul>
            <li><a href="index.php" <?php echo $category_id == 0 ? 'class="active"' : ''; ?>>All Categories</a></li>
            <?php
            $cat_result = $conn->query("SELECT id, name FROM faq_categories ORDER BY name");
            if ($cat_result) {
                while ($row = $cat_result->fetch_assoc()) {
                    $active = ($row['id'] == $category_id) ? 'class="active"' : '';
                    echo "<li><a href='index.php?cat={$row['id']}' {$active}>" . htmlspecialchars($row['name']) . "</a></li>";
                }
            }
            ?>
        </ul>
    </div>
    
    <div class="faq-list">
        <?php
        $sql = "SELECT e.*, c.name as category_name FROM faq_entries e 
                LEFT JOIN faq_categories c ON e.category_id = c.id 
                WHERE e.active = 1";
        
        if ($category_id > 0) {
            $sql .= " AND e.category_id = " . $category_id;
        }
        
        if (!empty($search)) {
            $sql .= " AND (e.question LIKE '%" . $search . "%' OR e.answer LIKE '%" . $search . "%' OR e.keywords LIKE '%" . $search . "%')";
        }
        
        $sql .= " ORDER BY e.sticky DESC, e.created_at DESC";
        
        $result = $conn->query($sql);
        
        if ($result && $result->num_rows > 0) {
            while ($row = $result->fetch_assoc()) {
                $sticky = $row['sticky'] ? '<span class="sticky-badge">Pinned</span>' : '';
                echo "<div class='faq-item'>
                        <h3>" . htmlspecialchars($row['question']) . " {$sticky}</h3>
                        <p class='category-label'>" . htmlspecialchars($row['category_name']) . "</p>
                        <div class='answer'>" . nl2br(htmlspecialchars($row['answer'])) . "</div>
                        <p class='meta'>Last updated: " . htmlspecialchars($row['updated_at']) . "</p>
                      </div>";
            }
        } else {
            echo "<p class='no-results'>No FAQ entries found.</p>";
        }
        $conn->close();
        ?>
    </div>
    
    <footer>
        <p>&copy; 2024 FAQ Knowledge Base. All rights reserved.</p>
    </footer>
</div>
</body>
</html>
