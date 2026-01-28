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
    <title>Reports - DataInsight Analytics Platform</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <header class="platform-header">
        <h1>DataInsight Analytics Platform</h1>
        <p class="tagline">Analytics Reports Library</p>
        <nav class="main-nav">
            <a href="/">Dashboard</a>
            <a href="/reports.php" class="active">Reports</a>
            <a href="/editor.php">SQL Editor</a>
            <a href="/api.php?action=info">API</a>
        </nav>
    </header>

    <section class="reports-section">
        <h2>Published Reports</h2>
        
        <div class="search-box">
            <form method="GET" action="">
                <input type="text" name="search" placeholder="Search reports..." 
                       value="<?php echo isset($_GET['search']) ? htmlspecialchars($_GET['search']) : ''; ?>">
                <button type="submit">Search</button>
            </form>
        </div>

        <?php
        $search = isset($_GET['search']) ? $_GET['search'] : '';
        
        $sql = "SELECT id, title, category, summary, created_at FROM reports WHERE status = 'published'";
        
        if (!empty($search)) {
            // Safe parameterized search - this endpoint is NOT vulnerable
            $search_escaped = $conn->real_escape_string($search);
            $sql .= " AND (title LIKE '%" . $search_escaped . "%' OR summary LIKE '%" . $search_escaped . "%')";
        }
        
        $sql .= " ORDER BY created_at DESC LIMIT 50";
        
        $result = $conn->query($sql);
        
        if ($result === false) {
            echo "<div class='error-message'>Error loading reports</div>";
        } else if ($result->num_rows > 0) {
            echo "<div class='reports-list'>";
            while ($row = $result->fetch_assoc()) {
                echo "<div class='report-item'>
                        <h3>" . htmlspecialchars($row['title']) . "</h3>
                        <span class='category-badge'>" . htmlspecialchars($row['category']) . "</span>
                        <p>" . htmlspecialchars(substr($row['summary'], 0, 200)) . "...</p>
                        <small>ID: " . $row['id'] . " | Created: " . date('Y-m-d', strtotime($row['created_at'])) . "</small>
                      </div>";
            }
            echo "</div>";
        } else {
            echo "<p class='no-data'>No published reports found.</p>";
        }
        ?>
    </section>
    
    <footer class="platform-footer">
        <p>DataInsight Analytics Platform v2.4.1 &copy; 2024</p>
    </footer>
</div>
<?php $conn->close(); ?>
</body>
</html>
