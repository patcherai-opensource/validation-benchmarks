<?php
session_start();

if (!isset($_SESSION['user_id'])) {
    header("Location: index.php");
    exit;
}

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
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Categories - FAQ Admin</title>
    <link rel="stylesheet" href="../styles.css">
</head>
<body>
<div class="container admin-panel">
    <header class="admin-header">
        <h1>FAQ Administration</h1>
        <div class="user-info">
            Welcome, <?php echo htmlspecialchars($_SESSION['display_name']); ?> 
            (<?php echo htmlspecialchars($_SESSION['role']); ?>)
            | <a href="logout.php">Logout</a>
        </div>
    </header>
    
    <nav class="admin-nav">
        <a href="dashboard.php">FAQ Entries</a>
        <a href="dashboard.php?action=insertentry">Add New Entry</a>
        <a href="categories.php" class="active">Categories</a>
        <a href="../index.php" target="_blank">View Site</a>
    </nav>
    
    <main class="admin-content">
        <h2>FAQ Categories</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Entries</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $sql = "SELECT c.*, COUNT(e.id) as entry_count 
                        FROM faq_categories c 
                        LEFT JOIN faq_entries e ON c.id = e.category_id 
                        GROUP BY c.id 
                        ORDER BY c.name";
                $result = $conn->query($sql);
                if ($result && $result->num_rows > 0) {
                    while ($row = $result->fetch_assoc()) {
                        echo "<tr>
                                <td>{$row['id']}</td>
                                <td>" . htmlspecialchars($row['name']) . "</td>
                                <td>" . htmlspecialchars($row['description']) . "</td>
                                <td>{$row['entry_count']}</td>
                              </tr>";
                    }
                } else {
                    echo "<tr><td colspan='4'>No categories found.</td></tr>";
                }
                ?>
            </tbody>
        </table>
    </main>
</div>
</body>
</html>
<?php $conn->close(); ?>
