<?php
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/db.php';

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

$user = get_session_user();
$conn = get_db_connection();

$recent_docs = [];
if ($conn) {
    $result = $conn->query("SELECT doc_fullname, doc_title, doc_space, doc_modified FROM wiki_documents WHERE doc_hidden = 0 ORDER BY doc_modified DESC LIMIT 5");
    if ($result) {
        while ($row = $result->fetch_assoc()) {
            $recent_docs[] = $row;
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
    <title>WikiEngine - Collaborative Wiki Platform</title>
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
            <span class="nav-user"><?php echo htmlspecialchars($user['display_name']); ?> (<?php echo htmlspecialchars($user['role']); ?>)</span>
            <a href="/logout.php">Logout</a>
            <?php else: ?>
            <a href="/login.php">Login</a>
            <?php endif; ?>
        </div>
    </nav>

    <div class="container">
        <div class="welcome-section">
            <h1>Welcome to WikiEngine</h1>
            <p>A collaborative wiki platform for your team. Browse documents, manage spaces, and query content.</p>
        </div>

        <div class="content-section">
            <h2>Recently Modified Documents</h2>
            <?php if (count($recent_docs) > 0): ?>
            <table class="doc-table">
                <thead>
                    <tr>
                        <th>Document</th>
                        <th>Space</th>
                        <th>Last Modified</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($recent_docs as $doc): ?>
                    <tr>
                        <td><a href="/view.php?page=<?php echo urlencode($doc['doc_fullname']); ?>"><?php echo htmlspecialchars($doc['doc_title']); ?></a></td>
                        <td><?php echo htmlspecialchars($doc['doc_space']); ?></td>
                        <td><?php echo htmlspecialchars($doc['doc_modified']); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <?php else: ?>
            <p>No documents found.</p>
            <?php endif; ?>
        </div>
    </div>

    <footer class="footer">
        <p>WikiEngine Platform v3.8.2 &copy; 2024</p>
    </footer>
</body>
</html>
