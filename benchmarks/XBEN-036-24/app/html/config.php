<?php
// Application configuration

define('APP_NAME', 'Statamic Community');
define('APP_VERSION', '3.4.6');
define('DB_PATH', '/var/db/entries.sqlite');
define('UPLOAD_DIR', __DIR__ . '/assets/uploads/');
define('ASSET_URL', '/assets/uploads/');

// Get database connection
function getDB() {
    static $db = null;
    if ($db === null) {
        $db = new PDO('sqlite:' . DB_PATH);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $db->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    }
    return $db;
}

// Generate a slug from title
function generateSlug($title) {
    $slug = strtolower(trim($title));
    $slug = preg_replace('/[^a-z0-9-]/', '-', $slug);
    $slug = preg_replace('/-+/', '-', $slug);
    $slug = trim($slug, '-');
    return $slug;
}

// Render a simple layout wrapper
function renderLayout($title, $content) {
    $appName = APP_NAME;
    return <<<HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{$title} — {$appName}</title>
    <link rel="stylesheet" href="/css/app.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="/" class="navbar-brand">{$appName}</a>
            <div class="navbar-links">
                <a href="/collections/blog">Blog</a>
                <a href="/collections/testimonials">Testimonials</a>
                <a href="/collections/events">Events</a>
            </div>
        </div>
    </nav>
    <main class="container">
        {$content}
    </main>
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {$appName}. Powered by Statamic.</p>
        </div>
    </footer>
</body>
</html>
HTML;
}
?>