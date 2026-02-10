<?php
session_start();

if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: index.php');
    exit;
}

$conn = new mysqli($_ENV['MYSQL_HOST'] ?? 'localhost', $_ENV['MYSQL_USER'] ?? 'user', $_ENV['MYSQL_PASSWORD'] ?? 'password', $_ENV['MYSQL_DATABASE'] ?? 'blogDB');
if ($conn->connect_error) {
    die("Service temporarily unavailable");
}

$posts = [];
$result = $conn->query("SELECT id, title, category, published, created_at FROM posts ORDER BY created_at DESC");
if ($result) {
    while ($row = $result->fetch_assoc()) {
        $posts[] = $row;
    }
}
$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Posts - Admin Panel</title>
    <link rel="stylesheet" href="../styles.css">
    <style>
        .sidebar { float: left; width: 200px; background: #f4f4f4; padding: 20px; min-height: 400px; }
        .sidebar a { display: block; padding: 10px; margin: 5px 0; text-decoration: none; color: #333; }
        .sidebar a:hover { background: #ddd; }
        .sidebar a.active { background: #333; color: white; }
        .main-content { margin-left: 240px; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #f4f4f4; }
        .status-published { color: green; }
        .status-draft { color: orange; }
    </style>
</head>
<body>
<div class="container">
    <h1>Admin Panel</h1>
    <p>Welcome, <?php echo htmlspecialchars($_SESSION['admin_username']); ?> | <a href="logout.php">Logout</a></p>
    
    <div class="sidebar">
        <a href="dashboard.php">Dashboard</a>
        <a href="posts.php" class="active">Posts</a>
        <a href="translations.php">Translations</a>
        <a href="settings.php">Settings</a>
    </div>
    
    <div class="main-content">
        <h2>Post Management</h2>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($posts as $post): ?>
                <tr>
                    <td><?php echo htmlspecialchars($post['id']); ?></td>
                    <td><?php echo htmlspecialchars($post['title']); ?></td>
                    <td><?php echo htmlspecialchars($post['category']); ?></td>
                    <td class="<?php echo $post['published'] ? 'status-published' : 'status-draft'; ?>">
                        <?php echo $post['published'] ? 'Published' : 'Draft'; ?>
                    </td>
                    <td><?php echo htmlspecialchars($post['created_at']); ?></td>
                    <td><a href="#">Edit</a> | <a href="#">Delete</a></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
    <div style="clear: both;"></div>
</div>
</body>
</html>
