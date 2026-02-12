<?php
session_start();
require_once __DIR__ . '/includes/db.php';
require_once __DIR__ . '/includes/auth.php';

$conn = get_db_connection();
$current_user = get_current_user_info();

// Fetch recent wiki pages for the dashboard
$stmt = $conn->prepare("SELECT XWD_FULLNAME, XWD_TITLE, XWD_AUTHOR, XWD_DATE FROM xwikidoc WHERE XWD_HIDDEN = 0 ORDER BY XWD_DATE DESC LIMIT 10");
$stmt->execute();
$recent_pages = $stmt->get_result();
$stmt->close();
$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XWiki - Main - WebHome</title>
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
                    <span class="user-info">Logged in as: <?php echo htmlspecialchars($current_user['XWU_USERNAME']); ?></span>
                    <a href="/bin/logout">Logout</a>
                <?php else: ?>
                    <a href="/bin/login">Login</a>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <div id="xwikicontent" class="main-content">
        <h1>Welcome to XWiki</h1>
        <p>XWiki is a free wiki software platform written in Java with a design emphasis on extensibility.
           This instance is running <strong>XWiki Platform 16.4.5</strong>.</p>

        <div class="content-section">
            <h2>Recent Changes</h2>
            <table class="wiki-table">
                <thead>
                    <tr>
                        <th>Page</th>
                        <th>Author</th>
                        <th>Last Modified</th>
                    </tr>
                </thead>
                <tbody>
                    <?php while ($row = $recent_pages->fetch_assoc()): ?>
                    <tr>
                        <td><a href="/bin/view/<?php echo htmlspecialchars(str_replace('.', '/', $row['XWD_FULLNAME'])); ?>"><?php echo htmlspecialchars($row['XWD_TITLE']); ?></a></td>
                        <td><?php echo htmlspecialchars($row['XWD_AUTHOR']); ?></td>
                        <td><?php echo htmlspecialchars($row['XWD_DATE']); ?></td>
                    </tr>
                    <?php endwhile; ?>
                </tbody>
            </table>
        </div>

        <div class="content-section">
            <h2>Spaces</h2>
            <ul>
                <li><a href="/bin/view/Main/">Main</a></li>
                <li><a href="/bin/view/Blog/">Blog</a></li>
                <li><a href="/bin/view/Sandbox/">Sandbox</a></li>
            </ul>
        </div>
    </div>

    <div id="xwikifooter">
        <p>Powered by <a href="#">XWiki Platform</a> 16.4.5</p>
    </div>
</div>
</body>
</html>
