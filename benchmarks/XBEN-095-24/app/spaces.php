<?php
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/db.php';

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

$user = get_session_user();
$conn = get_db_connection();

$spaces = [];
if ($conn) {
    $result = $conn->query("SELECT s.space_name, s.space_description, COUNT(d.doc_id) as doc_count FROM wiki_spaces s LEFT JOIN wiki_documents d ON s.space_name = d.doc_space AND d.doc_hidden = 0 WHERE s.space_hidden = 0 GROUP BY s.space_id ORDER BY s.space_name");
    if ($result) {
        while ($row = $result->fetch_assoc()) {
            $spaces[] = $row;
        }
    }
    $conn->close();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spaces - WikiEngine</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">WikiEngine</a>
            <span class="version">v3.8.2</span>
        </div>
        <div class="nav-links">
            <a href="/browse.php">Browse</a>
            <a href="/spaces.php" class="active">Spaces</a>
            <?php if ($user && ($user['role'] === 'editor' || $user['role'] === 'admin')): ?>
            <a href="/api/search_content.php">Content Query</a>
            <?php endif; ?>
            <?php if ($user): ?>
            <span class="nav-user"><?php echo htmlspecialchars($user['display_name']); ?></span>
            <a href="/logout.php">Logout</a>
            <?php else: ?>
            <a href="/login.php">Login</a>
            <?php endif; ?>
        </div>
    </nav>

    <div class="container">
        <h2>Wiki Spaces</h2>
        
        <?php if (count($spaces) > 0): ?>
        <div class="space-list">
            <?php foreach ($spaces as $space): ?>
            <div class="space-card">
                <h3><a href="/browse.php?space=<?php echo urlencode($space['space_name']); ?>"><?php echo htmlspecialchars($space['space_name']); ?></a></h3>
                <p><?php echo htmlspecialchars($space['space_description'] ?? ''); ?></p>
                <span class="badge"><?php echo (int)$space['doc_count']; ?> documents</span>
            </div>
            <?php endforeach; ?>
        </div>
        <?php else: ?>
        <p>No spaces found.</p>
        <?php endif; ?>
    </div>

    <footer class="footer">
        <p>WikiEngine Platform v3.8.2 &copy; 2024</p>
    </footer>
</body>
</html>
