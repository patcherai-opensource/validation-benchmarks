<?php
session_start();
require_once __DIR__ . '/../includes/db.php';
require_once __DIR__ . '/../includes/auth.php';

$current_user = get_current_user_info();
$page_path = isset($_GET['page']) ? trim($_GET['page'], '/') : 'Main/WebHome';

// Convert URL path to dot notation (Main/WebHome -> Main.WebHome)
$fullname = str_replace('/', '.', $page_path);
if (strpos($fullname, '.') === false) {
    $fullname = $fullname . '.WebHome';
}

$conn = get_db_connection();
$stmt = $conn->prepare("SELECT XWD_FULLNAME, XWD_TITLE, XWD_CONTENT, XWD_AUTHOR, XWD_DATE, XWD_HIDDEN FROM xwikidoc WHERE XWD_FULLNAME = ?");
$stmt->bind_param('s', $fullname);
$stmt->execute();
$result = $stmt->get_result();
$page = $result->fetch_assoc();
$stmt->close();

// Check if page exists and is accessible
$page_exists = ($page !== null);
$is_hidden = $page_exists && $page['XWD_HIDDEN'];

if ($is_hidden && (!$current_user || !has_right($current_user, 'EDIT'))) {
    $page_exists = false;
}

// Get space pages for sidebar
$space = explode('.', $fullname)[0];
$stmt2 = $conn->prepare("SELECT XWD_FULLNAME, XWD_TITLE FROM xwikidoc WHERE XWD_FULLNAME LIKE ? AND XWD_HIDDEN = 0 ORDER BY XWD_TITLE");
$space_pattern = $space . '.%';
$stmt2->bind_param('s', $space_pattern);
$stmt2->execute();
$space_pages = $stmt2->get_result();
$stmt2->close();
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XWiki - <?php echo $page_exists ? htmlspecialchars($page['XWD_TITLE']) : 'Page Not Found'; ?></title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div id="xwikimaincontainer">
    <div id="xwikiheader">
        <div class="navbar">
            <a href="/" class="brand">XWiki Platform</a>
            <div class="nav-links">
                <a href="/bin/view/Main/">Wiki</a>
                <a href="/bin/view/Blog/">Blog</a>
                <a href="/bin/view/Sandbox/">Sandbox</a>
                <?php if ($current_user): ?>
                    <a href="/bin/view/XWiki/ScriptConsole">Script Console</a>
                    <span class="user-info"><?php echo htmlspecialchars($current_user['XWU_USERNAME']); ?></span>
                    <a href="/bin/logout">Logout</a>
                <?php else: ?>
                    <a href="/bin/login">Login</a>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <div class="page-layout">
        <div class="sidebar">
            <h3><?php echo htmlspecialchars($space); ?></h3>
            <ul>
                <?php while ($sp = $space_pages->fetch_assoc()): ?>
                <li><a href="/bin/view/<?php echo htmlspecialchars(str_replace('.', '/', $sp['XWD_FULLNAME'])); ?>"><?php echo htmlspecialchars($sp['XWD_TITLE']); ?></a></li>
                <?php endwhile; ?>
            </ul>
        </div>

        <div id="xwikicontent" class="main-content">
            <?php if ($page_exists): ?>
                <div class="page-header">
                    <h1><?php echo htmlspecialchars($page['XWD_TITLE']); ?></h1>
                    <div class="page-meta">
                        <span>Author: <?php echo htmlspecialchars($page['XWD_AUTHOR']); ?></span>
                        <span>Last modified: <?php echo htmlspecialchars($page['XWD_DATE']); ?></span>
                        <span>Location: <?php echo htmlspecialchars($page['XWD_FULLNAME']); ?></span>
                    </div>
                </div>
                <div class="page-body">
                    <?php echo nl2br(htmlspecialchars($page['XWD_CONTENT'])); ?>
                </div>
            <?php else: ?>
                <h1>Page Not Found</h1>
                <p>The page <strong><?php echo htmlspecialchars($fullname); ?></strong> does not exist.</p>
                <p><a href="/">Return to home page</a></p>
            <?php endif; ?>
        </div>
    </div>

    <div id="xwikifooter">
        <p>Powered by <a href="#">XWiki Platform</a> 16.4.5</p>
    </div>
</div>
</body>
</html>