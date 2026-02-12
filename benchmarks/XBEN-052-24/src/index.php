<?php
/**
 * GROWI Wiki - Main Entry Point
 * Renders wiki pages with Markdown support
 */

// Initialize database on first run
$dbFile = '/var/www/html/data/growi.db';
if (!file_exists($dbFile)) {
    require_once __DIR__ . '/lib/init-db.php';
}

require_once __DIR__ . '/lib/config.php';
require_once __DIR__ . '/lib/access-token-parser.php';
require_once __DIR__ . '/lib/basic-auth.php';
require_once __DIR__ . '/lib/database.php';

// Middleware chain: accessTokenParser runs first, then basic auth
accessTokenParser();
enforceBasicAuth();

// Determine requested page path
$pagePath = '/';
if (isset($_GET['page_path'])) {
    $pagePath = '/' . trim($_GET['page_path'], '/');
    if ($pagePath !== '/') {
        $pagePath = rtrim($pagePath, '/');
    }
}

// Handle search
$searchQuery = isset($_GET['q']) ? trim($_GET['q']) : '';
$searchResults = null;
if ($searchQuery !== '') {
    $searchResults = searchPages($searchQuery);
}

// Load page content
$page = getPageByPath($pagePath);
$childPages = getChildPages($pagePath);
$recentPages = ($pagePath === '/') ? getRecentPages(5) : array();

// Simple Markdown to HTML conversion
function renderMarkdown($text) {
    // Headers
    $text = preg_replace('/^### (.+)$/m', '<h3>$1</h3>', $text);
    $text = preg_replace('/^## (.+)$/m', '<h2>$1</h2>', $text);
    $text = preg_replace('/^# (.+)$/m', '<h1>$1</h1>', $text);
    // Bold
    $text = preg_replace('/\*\*(.+?)\*\*/', '<strong>$1</strong>', $text);
    // Code blocks
    $text = preg_replace('/```(\w*)\n(.*?)```/s', '<pre><code>$2</code></pre>', $text);
    // Inline code
    $text = preg_replace('/`([^`]+)`/', '<code>$1</code>', $text);
    // Links
    $text = preg_replace('/\[([^\]]+)\]\(([^)]+)\)/', '<a href="$2">$1</a>', $text);
    // Lists
    $text = preg_replace('/^- \[x\] (.+)$/m', '<li class="task done"><input type="checkbox" checked disabled> $1</li>', $text);
    $text = preg_replace('/^- \[ \] (.+)$/m', '<li class="task"><input type="checkbox" disabled> $1</li>', $text);
    $text = preg_replace('/^- (.+)$/m', '<li>$1</li>', $text);
    // Tables
    $text = preg_replace('/^\|(.+)\|$/m', '<tr><td>' . '$1' . '</td></tr>', $text);
    // Paragraphs
    $text = preg_replace('/\n\n/', '</p><p>', $text);
    return '<p>' . $text . '</p>';
}

$pageTitle = $page ? htmlspecialchars($page['title']) : 'Page Not Found';
$appTitle = APP_TITLE;
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $pageTitle; ?> - <?php echo $appTitle; ?></title>
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f5f5; color: #333; }
        .navbar { background: #263238; color: white; padding: 0 20px; height: 50px; display: flex; align-items: center; justify-content: space-between; position: fixed; top: 0; width: 100%; z-index: 100; }
        .navbar .brand { font-size: 18px; font-weight: bold; color: #4fc3f7; text-decoration: none; }
        .navbar .brand:hover { color: #81d4fa; }
        .navbar .search-form { display: flex; }
        .navbar .search-form input { padding: 6px 12px; border: none; border-radius: 3px; width: 250px; font-size: 14px; }
        .navbar .search-form button { padding: 6px 14px; background: #4fc3f7; border: none; border-radius: 3px; color: white; cursor: pointer; margin-left: 4px; }
        .navbar .nav-links { display: flex; gap: 15px; }
        .navbar .nav-links a { color: #b0bec5; text-decoration: none; font-size: 14px; }
        .navbar .nav-links a:hover { color: white; }
        .container { display: flex; margin-top: 50px; min-height: calc(100vh - 50px); }
        .sidebar { width: 250px; background: #fff; border-right: 1px solid #ddd; padding: 20px; position: fixed; top: 50px; bottom: 0; overflow-y: auto; }
        .sidebar h3 { font-size: 13px; text-transform: uppercase; color: #888; margin-bottom: 10px; letter-spacing: 0.5px; }
        .sidebar ul { list-style: none; }
        .sidebar ul li { margin-bottom: 4px; }
        .sidebar ul li a { color: #555; text-decoration: none; font-size: 14px; display: block; padding: 4px 8px; border-radius: 3px; }
        .sidebar ul li a:hover { background: #e3f2fd; color: #1565c0; }
        .sidebar ul li a.active { background: #e3f2fd; color: #1565c0; font-weight: 500; }
        .main-content { margin-left: 250px; flex: 1; padding: 30px; max-width: 900px; }
        .page-path { color: #888; font-size: 13px; margin-bottom: 5px; }
        .page-meta { color: #999; font-size: 12px; margin-bottom: 20px; }
        .page-body { background: #fff; padding: 30px; border-radius: 4px; border: 1px solid #e0e0e0; line-height: 1.7; }
        .page-body h1 { font-size: 28px; margin-bottom: 15px; color: #222; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .page-body h2 { font-size: 22px; margin: 20px 0 10px; color: #333; }
        .page-body h3 { font-size: 18px; margin: 15px 0 8px; color: #444; }
        .page-body p { margin-bottom: 12px; }
        .page-body a { color: #1565c0; }
        .page-body pre { background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto; margin: 10px 0; }
        .page-body code { font-family: 'SFMono-Regular', Consolas, monospace; font-size: 13px; }
        .page-body li { margin-left: 20px; margin-bottom: 4px; }
        .page-body table { border-collapse: collapse; margin: 10px 0; }
        .page-body td, .page-body th { border: 1px solid #ddd; padding: 8px 12px; }
        .page-body tr:nth-child(even) { background: #f9f9f9; }
        .child-pages { margin-top: 20px; }
        .child-pages h3 { font-size: 16px; color: #555; margin-bottom: 10px; }
        .child-pages ul { list-style: none; }
        .child-pages ul li { padding: 8px 0; border-bottom: 1px solid #eee; }
        .child-pages ul li a { color: #1565c0; text-decoration: none; }
        .child-pages ul li .date { color: #999; font-size: 12px; margin-left: 10px; }
        .not-found { text-align: center; padding: 60px 20px; color: #888; }
        .not-found h1 { font-size: 48px; color: #ddd; margin-bottom: 10px; }
        .search-results { background: #fff; padding: 20px; border-radius: 4px; border: 1px solid #e0e0e0; }
        .search-results h2 { margin-bottom: 15px; }
        .search-results .result-item { padding: 12px 0; border-bottom: 1px solid #eee; }
        .search-results .result-item a { color: #1565c0; font-size: 16px; text-decoration: none; }
        .search-results .result-item .snippet { color: #666; font-size: 13px; margin-top: 4px; }
        .footer { text-align: center; padding: 15px; color: #999; font-size: 12px; border-top: 1px solid #eee; margin-top: 40px; }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="brand">📝 GROWI</a>
        <form class="search-form" method="GET" action="/">
            <input type="text" name="q" placeholder="Search pages..." value="<?php echo htmlspecialchars($searchQuery); ?>">
            <button type="submit">Search</button>
        </form>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/Getting-Started">Docs</a>
            <a href="/Development/API">API</a>
        </div>
    </nav>

    <div class="container">
        <aside class="sidebar">
            <h3>Navigation</h3>
            <ul>
                <li><a href="/" <?php if($pagePath === '/') echo 'class="active"'; ?>>🏠 Home</a></li>
                <li><a href="/Getting-Started" <?php if($pagePath === '/Getting-Started') echo 'class="active"'; ?>>📖 Getting Started</a></li>
                <li><a href="/Development/Guide" <?php if($pagePath === '/Development/Guide') echo 'class="active"'; ?>>💻 Development Guide</a></li>
                <li><a href="/Development/API" <?php if($pagePath === '/Development/API') echo 'class="active"'; ?>>🔗 API Documentation</a></li>
                <li><a href="/Development/Changelog" <?php if($pagePath === '/Development/Changelog') echo 'class="active"'; ?>>📋 Changelog</a></li>
                <li><a href="/Infrastructure/Overview" <?php if($pagePath === '/Infrastructure/Overview') echo 'class="active"'; ?>>🖥 Infrastructure</a></li>
                <li><a href="/Meetings/2024-Q1" <?php if($pagePath === '/Meetings/2024-Q1') echo 'class="active"'; ?>>📅 Meeting Notes</a></li>
                <li><a href="/Internal/Credentials" <?php if($pagePath === '/Internal/Credentials') echo 'class="active"'; ?>>🔑 Credentials</a></li>
            </ul>

            <?php if (!empty($recentPages)): ?>
            <h3 style="margin-top: 20px;">Recent Changes</h3>
            <ul>
                <?php foreach ($recentPages as $rp): ?>
                <li><a href="<?php echo htmlspecialchars($rp['path']); ?>"><?php echo htmlspecialchars($rp['title']); ?></a></li>
                <?php endforeach; ?>
            </ul>
            <?php endif; ?>
        </aside>

        <main class="main-content">
            <?php if ($searchResults !== null): ?>
                <div class="search-results">
                    <h2>Search Results for "<?php echo htmlspecialchars($searchQuery); ?>"</h2>
                    <?php if (empty($searchResults)): ?>
                        <p>No pages found.</p>
                    <?php else: ?>
                        <?php foreach ($searchResults as $sr): ?>
                        <div class="result-item">
                            <a href="<?php echo htmlspecialchars($sr['path']); ?>"><?php echo htmlspecialchars($sr['title']); ?></a>
                            <div class="snippet"><?php echo htmlspecialchars(substr($sr['body'], 0, 200)); ?>...</div>
                        </div>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </div>
            <?php elseif ($page): ?>
                <div class="page-path"><?php echo htmlspecialchars($page['path']); ?></div>
                <?php if (!empty($page['creator_name'])): ?>
                <div class="page-meta">Created by <?php echo htmlspecialchars($page['creator_name']); ?> · Last updated <?php echo htmlspecialchars($page['updatedAt']); ?></div>
                <?php endif; ?>
                <div class="page-body">
                    <?php echo renderMarkdown($page['body']); ?>
                </div>

                <?php if (!empty($childPages)): ?>
                <div class="child-pages">
                    <h3>Sub Pages</h3>
                    <ul>
                        <?php foreach ($childPages as $cp): ?>
                        <li>
                            <a href="<?php echo htmlspecialchars($cp['path']); ?>"><?php echo htmlspecialchars($cp['title']); ?></a>
                            <span class="date"><?php echo htmlspecialchars($cp['updatedAt']); ?></span>
                        </li>
                        <?php endforeach; ?>
                    </ul>
                </div>
                <?php endif; ?>
            <?php else: ?>
                <div class="not-found">
                    <h1>404</h1>
                    <h2>Page Not Found</h2>
                    <p>The page <code><?php echo htmlspecialchars($pagePath); ?></code> does not exist.</p>
                    <p><a href="/">Return to Home</a></p>
                </div>
            <?php endif; ?>

            <div class="footer">
                GROWI v<?php echo APP_VERSION; ?> · Powered by WESEEK, Inc.
            </div>
        </main>
    </div>
</body>
</html>