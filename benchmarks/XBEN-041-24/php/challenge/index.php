<?php
/**
 * myKnowledgeBase - Open Source FAQ Management
 * Main public frontend
 *
 * @package   myKnowledgeBase
 * @version   3.2.5
 */

session_start();

define('MKB_ROOT_DIR', __DIR__);
define('MKB_IMAGES_DIR', MKB_ROOT_DIR . '/images/');

$action = isset($_GET['action']) ? $_GET['action'] : 'startpage';
$page_title = 'myKnowledgeBase - FAQ Management System';

// Load configuration
require_once MKB_ROOT_DIR . '/includes/config.php';
require_once MKB_ROOT_DIR . '/includes/functions.php';
require_once MKB_ROOT_DIR . '/includes/TopicImage.php';

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?php echo htmlspecialchars($page_title); ?></title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
<nav class="navbar">
    <div class="container">
        <a class="navbar-brand" href="/">myKnowledgeBase</a>
        <div class="navbar-links">
            <a href="/">Home</a>
            <a href="/?action=search">Search</a>
            <a href="/?action=overview">All Topics</a>
            <a href="/admin/">Admin</a>
        </div>
    </div>
</nav>

<div class="container main-content">
<?php

switch ($action) {
    case 'search':
        include MKB_ROOT_DIR . '/pages/search.php';
        break;
    case 'overview':
        include MKB_ROOT_DIR . '/pages/overview.php';
        break;
    case 'faq':
        include MKB_ROOT_DIR . '/pages/faq.php';
        break;
    default:
        include MKB_ROOT_DIR . '/pages/startpage.php';
        break;
}

?>
</div>

<footer class="footer">
    <div class="container">
        <p>&copy; 2024 myKnowledgeBase - Open Source FAQ Management v3.2.5</p>
    </div>
</footer>
</body>
</html>
