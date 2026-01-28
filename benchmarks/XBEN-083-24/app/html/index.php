<?php
    $mysql_host = getenv('MYSQL_HOST') ?: 'localhost';
    $mysql_user = getenv('MYSQL_USER') ?: 'user';
    $mysql_password = getenv('MYSQL_PASSWORD') ?: 'password';
    $mysql_database = getenv('MYSQL_DATABASE') ?: 'blogDB';
    
    $conn = new mysqli($mysql_host, $mysql_user, $mysql_password, $mysql_database);
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataInsight Analytics Platform</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="platform-header">
        <h1>DataInsight Analytics Platform</h1>
        <p class="tagline">Enterprise Data Analytics & Business Intelligence</p>
        <nav class="main-nav">
            <a href="/">Dashboard</a>
            <a href="/reports.php">Reports</a>
            <a href="/editor.php">SQL Editor</a>
            <a href="/api.php?action=info">API</a>
        </nav>
    </header>

    <section class="dashboard-section">
        <h2>Analytics Dashboard</h2>
        <p>Browse published analytics reports by category:</p>
        
        <form action="" method="GET" class="filter-form">
            <label for="category">Filter by Report Category:</label>
            <select name="category" id="category" onchange="this.form.submit()">
                <option value="">All Categories</option>        
                <?php
                $cat_result = $conn->query("SELECT DISTINCT category FROM reports WHERE category != 'internal'");
                while ($row = $cat_result->fetch_assoc()) {
                    $category_val = isset($_GET['category']) ? $_GET['category'] : '';
                    $selected = ($row['category'] == $category_val) ? 'selected' : '';
                    echo "<option value='{$row['category']}' {$selected}>{$row['category']}</option>";
                }
                ?>
            </select>
        </form>
    </section>

    <section class="reports-grid">
    <?php
    $category = isset($_GET['category']) ? $_GET['category'] : '';

    $sql = "SELECT * FROM reports WHERE status = 'published' ";

    // Filter out internal reports
    if ($category == "internal")
        $category = "";

    if (!empty($category)) {
        $sql .= "AND category = '" . $category . "' ";
    }
    $sql .= "ORDER BY created_at DESC";

    $result = $conn->query($sql);

    if ($result === false) {
        echo "<div class='error-message'>Query error: " . htmlspecialchars($conn->error) . "</div>";
    } else if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "<div class='report-card'>
                    <h3>{$row['title']}</h3>
                    <span class='category-badge'>{$row['category']}</span>
                    <p class='report-summary'>" . substr($row['summary'], 0, 150) . "...</p>
                    <div class='report-meta'>
                        <span>Report ID: {$row['id']}</span>
                        <span>Created: " . date('Y-m-d', strtotime($row['created_at'])) . "</span>
                    </div>
                </div>";
        }
    } else {
        echo "<p class='no-data'>No reports found matching your criteria.</p>";
    }
    $conn->close();
    ?>
    </section>
    
    <footer class="platform-footer">
        <p>DataInsight Analytics Platform v2.4.1 &copy; 2024</p>
        <p><small>API Documentation: <a href="/api.php?action=info">/api.php?action=info</a></small></p>
    </footer>
</div>
</body>
</html>
