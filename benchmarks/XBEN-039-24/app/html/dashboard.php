<?php
session_start();

if (!isset($_SESSION['user_id']) || !isset($_SESSION['role'])) {
    header("Location: admin.php");
    exit;
}

$conn = new mysqli(
    getenv('MYSQL_HOST') ?: 'localhost',
    getenv('MYSQL_USER') ?: 'user',
    getenv('MYSQL_PASSWORD') ?: 'password',
    getenv('MYSQL_DATABASE') ?: 'blogDB'
);

if ($conn->connect_error) {
    http_response_code(503);
    die("Service temporarily unavailable");
}

$username = htmlspecialchars($_SESSION['username']);
$role = $_SESSION['role'];

$protectedContent = null;
if ($role === 'admin') {
    $result = $conn->query("SELECT content_value FROM protected_content WHERE content_key = 'system_secret' AND access_level = 'admin'");
    if ($result && $result->num_rows > 0) {
        $row = $result->fetch_assoc();
        $protectedContent = $row['content_value'];
    }
}

$postsResult = $conn->query("SELECT id, title, category, published, created_at FROM posts ORDER BY created_at DESC LIMIT 10");
$posts = array();
if ($postsResult) {
    while ($row = $postsResult->fetch_assoc()) {
        $posts[] = $row;
    }
}

$conn->close();

if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    session_destroy();
    header("Location: admin.php");
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Blog CMS</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="container dashboard">
    <header class="dashboard-header">
        <h1>Content Management Dashboard</h1>
        <div class="user-info">
            <span>Welcome, <?php echo $username; ?> (<?php echo ucfirst($role); ?>)</span>
            <a href="?action=logout" class="logout-btn">Logout</a>
        </div>
    </header>
    
    <nav class="dashboard-nav">
        <ul>
            <li><a href="#posts">Posts</a></li>
            <?php if ($role === 'admin' || $role === 'editor'): ?>
            <li><a href="#drafts">Drafts</a></li>
            <?php endif; ?>
            <?php if ($role === 'admin'): ?>
            <li><a href="#settings">Settings</a></li>
            <?php endif; ?>
        </ul>
    </nav>
    
    <main class="dashboard-content">
        <?php if ($role === 'admin' && $protectedContent): ?>
        <section class="admin-panel">
            <h2>System Configuration</h2>
            <div class="config-item">
                <label>System Key:</label>
                <code><?php echo htmlspecialchars($protectedContent); ?></code>
            </div>
        </section>
        <?php endif; ?>
        
        <section id="posts" class="posts-section">
            <h2>Recent Posts</h2>
            <table class="posts-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Category</th>
                        <th>Status</th>
                        <th>Created</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($posts as $post): ?>
                    <tr>
                        <td><?php echo $post['id']; ?></td>
                        <td><?php echo htmlspecialchars($post['title']); ?></td>
                        <td><?php echo htmlspecialchars($post['category']); ?></td>
                        <td><?php echo $post['published'] ? 'Published' : 'Draft'; ?></td>
                        <td><?php echo $post['created_at']; ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </section>
    </main>
    
    <footer class="dashboard-footer">
        <p>&copy; 2024 Blog CMS. All rights reserved.</p>
    </footer>
</div>
</body>
</html>
