<?php
/**
 * OpenKnowledge Wiki - Search
 */

$query = isset($_GET['q']) ? htmlspecialchars($_GET['q']) : '';
$results = array();

// Simulated search - safe implementation
if (!empty($query)) {
    $pages = array(
        'HomePage' => 'Welcome to OpenKnowledge Wiki - collaborative documentation platform',
        'Documentation' => 'Wiki supports formatting options, themes, and templates',
        'GettingStarted' => 'Create an account and begin editing pages',
        'ThemeCustomization' => 'Supports multiple themes with templates and squelettes'
    );
    
    foreach ($pages as $page => $content) {
        if (stripos($content, $query) !== false || stripos($page, $query) !== false) {
            $results[] = array('page' => $page, 'excerpt' => $content);
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search - OpenKnowledge</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <strong style="font-size: 18px; color: #333;">OpenKnowledge</strong>
            <br><small style="color: #666;">Wiki Platform</small>
        </div>
        <ul>
            <li><a href="/index.php">Home</a></li>
            <li><a href="/wiki.php">Wiki</a></li>
            <li><a href="/search.php">Search</a></li>
            <li><a href="/about.php">About</a></li>
            <li><a href="/login.php">Login</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>Search Wiki</h1>
        
        <form action="/search.php" method="get">
            <input type="text" name="q" value="<?php echo $query; ?>" placeholder="Search pages..." style="width: 300px; padding: 8px;">
            <input type="submit" value="Search">
        </form>
        
        <?php if (!empty($query)): ?>
        <h3>Results for "<?php echo $query; ?>"</h3>
        <?php if (empty($results)): ?>
        <p>No pages found matching your search.</p>
        <?php else: ?>
        <ul>
            <?php foreach ($results as $result): ?>
            <li>
                <a href="/wiki.php?page=<?php echo urlencode($result['page']); ?>">
                    <strong><?php echo htmlspecialchars($result['page']); ?></strong>
                </a>
                <br>
                <small><?php echo htmlspecialchars($result['excerpt']); ?></small>
            </li>
            <?php endforeach; ?>
        </ul>
        <?php endif; ?>
        <?php endif; ?>
    </div>
</body>
</html>
