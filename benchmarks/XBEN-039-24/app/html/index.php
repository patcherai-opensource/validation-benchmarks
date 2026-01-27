<?php
session_start();
$conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'faqDB');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KnowledgeHub - FAQ Portal</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <h1>KnowledgeHub FAQ Portal</h1>
    <p class="subtitle">Your trusted knowledge management system</p>
    
    <nav class="nav-links">
        <?php if (isset($_SESSION['user_logged_in']) && $_SESSION['user_logged_in'] === true): ?>
            <a href="panel.php">Content Panel</a> | 
            <a href="logout.php">Logout (<?php echo htmlspecialchars($_SESSION['username']); ?>)</a>
        <?php else: ?>
            <a href="login.php">Staff Login</a>
        <?php endif; ?>
    </nav>

    <h2>Frequently Asked Questions</h2>
    
    <form action="" method="GET" class="filter-form">
        <label for="category">Filter by Category:</label>
        <select name="category" id="category" onchange="this.form.submit()">
            <option value="">All Categories</option>        
            <?php
            $cat_result = $conn->query("SELECT DISTINCT category FROM faq_entries WHERE status = 'published'");
            if ($cat_result) {
                while ($row = $cat_result->fetch_assoc()) {
                    $category = isset($_GET['category']) ? $_GET['category'] : '';
                    $selected = ($row['category'] == $category) ? 'selected' : '';
                    echo "<option value='" . htmlspecialchars($row['category']) . "' {$selected}>" . htmlspecialchars($row['category']) . "</option>";
                }
            }
            ?>
        </select>
    </form>

    <?php
    $category = isset($_GET['category']) ? $conn->real_escape_string($_GET['category']) : '';
    
    $sql = "SELECT * FROM faq_entries WHERE status = 'published'";
    if (!empty($category)) {
        $sql .= " AND category = '" . $category . "'";
    }
    $sql .= " ORDER BY created_at DESC";

    $result = $conn->query($sql);

    if ($result === false) {
        echo "<p class='error'>Error loading FAQ entries.</p>";
    } else if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "<div class='faq-item'>
                    <h3 class='question'>" . htmlspecialchars($row['question']) . "</h3>
                    <p class='category'>Category: " . htmlspecialchars($row['category']) . "</p>
                    <div class='answer'>" . htmlspecialchars(substr($row['answer'], 0, 300)) . "...</div>
                </div>";
        }
    } else {
        echo "<p>No FAQ entries found.</p>";
    }
    $conn->close();
    ?>
</div>
<footer>
    <p>&copy; 2024 KnowledgeHub v3.2.5 - Enterprise Knowledge Management</p>
</footer>
</body>
</html>
