<?php
session_start();
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header("Location: login.php");
    exit;
}

$conn = new mysqli(getenv('MYSQL_HOST') ?: 'localhost', getenv('MYSQL_USER') ?: 'user', getenv('MYSQL_PASSWORD') ?: 'password', getenv('MYSQL_DATABASE') ?: 'blogDB');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ezPortal CMS - Manage Articles</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>Article Management</h1>
    </div>
    
    <nav class="admin-nav">
        <a href="admin.php">Dashboard</a>
        <a href="manage_articles.php">Manage Articles</a>
        <a href="manage_users.php">Manage Users</a>
        <a href="settings.php">Settings</a>
        <a href="logout.php">Logout</a>
    </nav>

    <div class="admin-content">
        <h2>All Articles</h2>
        <table class="data-table">
            <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Category</th>
                <th>Published</th>
                <th>Created</th>
            </tr>
            <?php
            $result = $conn->query("SELECT id, title, category, published, created_at FROM posts ORDER BY created_at DESC");
            while ($row = $result->fetch_assoc()) {
                $published = $row['published'] ? 'Yes' : 'No';
                echo "<tr>
                    <td>{$row['id']}</td>
                    <td>" . htmlspecialchars($row['title']) . "</td>
                    <td>{$row['category']}</td>
                    <td>{$published}</td>
                    <td>{$row['created_at']}</td>
                </tr>";
            }
            ?>
        </table>
    </div>
</div>
</body>
</html>
<?php $conn->close(); ?>
