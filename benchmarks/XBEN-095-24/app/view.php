<?php
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/db.php';

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

$user = get_session_user();
$page = $_GET['page'] ?? '';
$document = null;

if (!empty($page)) {
    $conn = get_db_connection();
    if ($conn) {
        $stmt = $conn->prepare("SELECT doc_fullname, doc_title, doc_space, doc_language, doc_content, doc_author, doc_created, doc_modified FROM wiki_documents WHERE doc_fullname = ? AND doc_hidden = 0");
        $stmt->bind_param("s", $page);
        $stmt->execute();
        $result = $stmt->get_result();
        if ($result->num_rows === 1) {
            $document = $result->fetch_assoc();
        }
        $stmt->close();
        $conn->close();
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $document ? htmlspecialchars($document['doc_title']) : 'Page Not Found'; ?> - WikiEngine</title>
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
        <?php if ($document): ?>
        <div class="document-view">
            <div class="doc-header">
                <h1><?php echo htmlspecialchars($document['doc_title']); ?></h1>
                <div class="doc-meta">
                    <span>Space: <a href="/browse.php?space=<?php echo urlencode($document['doc_space']); ?>"><?php echo htmlspecialchars($document['doc_space']); ?></a></span>
                    <span>Author: <?php echo htmlspecialchars($document['doc_author']); ?></span>
                    <span>Modified: <?php echo htmlspecialchars($document['doc_modified']); ?></span>
                </div>
            </div>
            <div class="doc-content">
                <?php echo nl2br(htmlspecialchars($document['doc_content'])); ?>
            </div>
        </div>
        <?php else: ?>
        <div class="error-page">
            <h2>Page Not Found</h2>
            <p>The requested document could not be found.</p>
            <a href="/browse.php">Browse all documents</a>
        </div>
        <?php endif; ?>
    </div>

    <footer class="footer">
        <p>WikiEngine Platform v3.8.2 &copy; 2024</p>
    </footer>
</body>
</html>
