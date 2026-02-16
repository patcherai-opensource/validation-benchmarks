<?php
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/db.php';

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

$user = get_session_user();
$conn = get_db_connection();

$space_filter = $_GET['space'] ?? '';
$documents = [];

if ($conn) {
    if (!empty($space_filter)) {
        $stmt = $conn->prepare("SELECT doc_fullname, doc_title, doc_space, doc_author, doc_modified FROM wiki_documents WHERE doc_hidden = 0 AND doc_space = ? ORDER BY doc_title");
        $stmt->bind_param("s", $space_filter);
        $stmt->execute();
        $result = $stmt->get_result();
    } else {
        $result = $conn->query("SELECT doc_fullname, doc_title, doc_space, doc_author, doc_modified FROM wiki_documents WHERE doc_hidden = 0 ORDER BY doc_space, doc_title");
    }
    
    if ($result) {
        while ($row = $result->fetch_assoc()) {
            $documents[] = $row;
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
    <title>Browse Documents - WikiEngine</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">WikiEngine</a>
            <span class="version">v3.8.2</span>
        </div>
        <div class="nav-links">
            <a href="/browse.php" class="active">Browse</a>
            <a href="/spaces.php">Spaces</a>
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
        <h2>Browse Documents<?php if ($space_filter): ?> in <?php echo htmlspecialchars($space_filter); ?><?php endif; ?></h2>
        
        <?php if (count($documents) > 0): ?>
        <table class="doc-table">
            <thead>
                <tr>
                    <th>Document</th>
                    <th>Space</th>
                    <th>Author</th>
                    <th>Last Modified</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($documents as $doc): ?>
                <tr>
                    <td><a href="/view.php?page=<?php echo urlencode($doc['doc_fullname']); ?>"><?php echo htmlspecialchars($doc['doc_title']); ?></a></td>
                    <td><a href="/browse.php?space=<?php echo urlencode($doc['doc_space']); ?>"><?php echo htmlspecialchars($doc['doc_space']); ?></a></td>
                    <td><?php echo htmlspecialchars($doc['doc_author']); ?></td>
                    <td><?php echo htmlspecialchars($doc['doc_modified']); ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <?php else: ?>
        <p>No documents found.</p>
        <?php endif; ?>
    </div>

    <footer class="footer">
        <p>WikiEngine Platform v3.8.2 &copy; 2024</p>
    </footer>
</body>
</html>
