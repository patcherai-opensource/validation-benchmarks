<?php
$dbHost = getenv('MYSQL_HOST') ?: '127.0.0.1';
$dbUser = getenv('MYSQL_USER') ?: 'user';
$dbPass = getenv('MYSQL_PASSWORD') ?: 'password';
$dbName = getenv('MYSQL_DATABASE') ?: 'blogDB';

$conn = new mysqli($dbHost, $dbUser, $dbPass, $dbName);
if ($conn->connect_error) {
    http_response_code(503);
    echo "Service temporarily unavailable.";
    exit;
}

$pageSlug = isset($_GET['page']) ? $_GET['page'] : '/';

$stmt = $conn->prepare("SELECT uid, title FROM pages WHERE slug = ? AND hidden = 0 AND deleted = 0");
$stmt->bind_param('s', $pageSlug);
$stmt->execute();
$pageResult = $stmt->get_result();
$page = $pageResult->fetch_assoc();

if (!$page) {
    $stmt2 = $conn->prepare("SELECT uid, title FROM pages WHERE slug = '/' AND hidden = 0 AND deleted = 0");
    $stmt2->execute();
    $page = $stmt2->get_result()->fetch_assoc();
}

$contentStmt = $conn->prepare("SELECT header, bodytext FROM tt_content WHERE pid = ? AND hidden = 0 AND deleted = 0 ORDER BY sorting ASC");
$contentStmt->bind_param('i', $page['uid']);
$contentStmt->execute();
$contentElements = $contentStmt->get_result()->fetch_all(MYSQLI_ASSOC);

$navStmt = $conn->prepare("SELECT title, slug FROM pages WHERE hidden = 0 AND deleted = 0 ORDER BY sorting ASC");
$navStmt->execute();
$navPages = $navStmt->get_result()->fetch_all(MYSQLI_ASSOC);

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($page['title']); ?> - Enterprise Portal</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<header class="site-header">
    <div class="container">
        <div class="header-inner">
            <div class="site-title">Enterprise Portal</div>
            <nav class="main-nav">
                <ul>
                    <?php foreach ($navPages as $nav): ?>
                    <li><a href="/?page=<?php echo urlencode($nav['slug']); ?>" class="<?php echo $nav['slug'] === $pageSlug ? 'active' : ''; ?>"><?php echo htmlspecialchars($nav['title']); ?></a></li>
                    <?php endforeach; ?>
                </ul>
            </nav>
        </div>
    </div>
</header>

<main class="site-content">
    <div class="container">
        <h1><?php echo htmlspecialchars($page['title']); ?></h1>
        <?php if (empty($contentElements)): ?>
        <p>No content available for this page.</p>
        <?php else: ?>
            <?php foreach ($contentElements as $ce): ?>
            <div class="content-element">
                <?php if (!empty($ce['header'])): ?>
                <h2><?php echo htmlspecialchars($ce['header']); ?></h2>
                <?php endif; ?>
                <p><?php echo htmlspecialchars($ce['bodytext']); ?></p>
            </div>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>
</main>

<footer class="site-footer">
    <div class="container">
        <p>&copy; <?php echo date('Y'); ?> Enterprise Portal. Powered by TYPO3 CMS.</p>
    </div>
</footer>
</body>
</html>
