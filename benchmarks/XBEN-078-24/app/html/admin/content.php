<?php
session_start();

if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: /admin/');
    exit;
}

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Management - GlobalCMS</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<div class="admin-container">
    <h1>Content Management</h1>
    <nav class="admin-nav">
        <a href="/admin/">Dashboard</a>
        <a href="/admin/content.php" class="active">Content Management</a>
        <a href="/admin/translations.php">Translations</a>
        <a href="/admin/users.php">User Management</a>
        <a href="/admin/settings.php">Settings</a>
        <a href="/admin/?logout=1" class="logout">Logout</a>
    </nav>
    
    <div class="content-panel">
        <h2>Content Items</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Published</th>
                    <th>Created</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $result = $conn->query("SELECT id, title, category, published, created_at FROM posts ORDER BY created_at DESC");
                if ($result && $result->num_rows > 0) {
                    while($row = $result->fetch_assoc()) {
                        $status = $row['published'] ? 'Yes' : 'No';
                        echo "<tr>
                            <td>" . htmlspecialchars($row['id']) . "</td>
                            <td>" . htmlspecialchars($row['title']) . "</td>
                            <td>" . htmlspecialchars($row['category']) . "</td>
                            <td>{$status}</td>
                            <td>" . htmlspecialchars($row['created_at']) . "</td>
                        </tr>";
                    }
                }
                ?>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
<?php $conn->close(); ?>
