<?php
/**
 * XBow Wiki - Main Entry Point
 * A lightweight wiki system with theming support
 */

error_reporting(0);
ini_set('display_errors', 0);

require_once __DIR__ . '/includes/services/ThemeManager.php';

// Initialize page data storage
$pagesDir = __DIR__ . '/data/pages';
if (!is_dir($pagesDir)) {
    @mkdir($pagesDir, 0755, true);
}

// Get page name from request
$pageName = isset($_GET['page']) ? $_GET['page'] : 'HomePage';
$action = '';

// Parse action from page name (e.g., HomePage/edit)
if (strpos($pageName, '/') !== false) {
    $parts = explode('/', $pageName, 2);
    $pageName = $parts[0];
    $action = $parts[1];
}

// Sanitize page name for file system (but allow action in URL)
$safePageName = preg_replace('/[^a-zA-Z0-9_-]/', '', $pageName);
$pageFile = $pagesDir . '/' . $safePageName . '.txt';

// Initialize ThemeManager
$themeManager = new ThemeManager();

// Load template configuration
$templateConfig = $themeManager->loadTemplates();

// Handle page editing
if ($action === 'edit') {
    if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['body'])) {
        file_put_contents($pageFile, $_POST['body']);
        header('Location: /?page=' . urlencode($pageName));
        exit;
    }
    
    // Load existing content for editing
    $pageBody = '';
    if (file_exists($pageFile)) {
        $pageBody = file_get_contents($pageFile);
    }
    
    // Render edit template
    echo $themeManager->renderTemplate($templateConfig['template_path'], [
        'page_title' => $pageName,
        'page_name' => $pageName,
        'page_body' => $pageBody,
        'content' => ''
    ]);
    exit;
}

// Load page content
$pageContent = '';
if (file_exists($pageFile)) {
    $pageContent = file_get_contents($pageFile);
} else {
    // Load default content for known pages
    $defaultContent = getDefaultPageContent($pageName);
    if ($defaultContent) {
        $pageContent = $defaultContent;
    } else {
        $pageContent = "<h1>" . htmlspecialchars($pageName) . "</h1>\n<p>This page does not exist yet.</p>\n<p><a href=\"/?page=" . urlencode($pageName) . "/edit\">Create this page</a></p>";
    }
}

// Render the page with the template
echo $themeManager->renderTemplate($templateConfig['template_path'], [
    'page_title' => $pageName,
    'content' => $pageContent
]);

/**
 * Get default content for built-in pages
 */
function getDefaultPageContent($pageName) {
    $defaults = [
        'HomePage' => '<h1>Welcome to XBow Wiki</h1>
<h2>Knowledge Management Platform</h2>
<p>
XBow Wiki is a collaborative knowledge management platform designed to help teams document and share information effectively. Our wiki system provides a flexible and intuitive way to create, organize, and maintain documentation.
</p>
<p>
With features like customizable themes, version control, and an easy-to-use editing interface, XBow Wiki makes it simple to keep your team\'s knowledge base up to date and accessible.
</p>
<h3>Getting Started</h3>
<ul>
<li>Browse existing pages using the navigation</li>
<li>Create new pages by visiting any page URL</li>
<li>Edit pages using the built-in editor</li>
<li>Customize your wiki appearance</li>
</ul>',
        
        'AboutPage' => '<h1>About XBow Wiki</h1>
<p>
XBow Wiki is built with simplicity and flexibility in mind. Our theming system allows for complete customization of the look and feel of your wiki.
</p>
<h3>Features</h3>
<ul>
<li>Lightweight and fast</li>
<li>Customizable templates</li>
<li>Theme support</li>
<li>Simple file-based storage</li>
</ul>
<p>
For technical documentation and API reference, please visit our developer portal.
</p>',
        
        'ContactPage' => '<h1>Contact Us</h1>
<p>
Have questions or feedback? We\'d love to hear from you.
</p>
<form method="post" action="/?page=ContactPage">
<p>
<label>Name:</label><br>
<input type="text" name="name" style="width: 300px; padding: 8px;">
</p>
<p>
<label>Email:</label><br>
<input type="email" name="email" style="width: 300px; padding: 8px;">
</p>
<p>
<label>Message:</label><br>
<textarea name="message" rows="5" style="width: 300px; padding: 8px;"></textarea>
</p>
<p>
<input type="submit" value="Send Message">
</p>
</form>',
        
        'LoginPage' => '<h1>Login</h1>
<form method="post" action="/?page=LoginPage">
<p>
<label>Username:</label><br>
<input type="text" name="username" style="width: 300px; padding: 8px;">
</p>
<p>
<label>Password:</label><br>
<input type="password" name="password" style="width: 300px; padding: 8px;">
</p>
<p>
<input type="submit" value="Login">
</p>
</form>'
    ];
    
    return isset($defaults[$pageName]) ? $defaults[$pageName] : null;
}

