<?php
error_reporting(0);

require_once 'includes/services/ThemeManager.php';

// Get the requested page
$page = isset($_GET['page']) ? $_GET['page'] : 'HomePage';

// Sanitize page name - only allow alphanumeric and basic characters
$page = preg_replace('/[^a-zA-Z0-9_-]/', '', $page);

// Determine the action (view or edit)
$pathInfo = isset($_SERVER['PATH_INFO']) ? $_SERVER['PATH_INFO'] : '';
$action = 'view';
if (preg_match('#/edit$#', $pathInfo) || (isset($_GET['action']) && $_GET['action'] === 'edit')) {
    $action = 'edit';
}

// Load the page content
$pageFile = 'pages/' . $page . '.txt';
$pageContent = '';
$pageTitle = $page;

if (file_exists($pageFile)) {
    $pageContent = file_get_contents($pageFile);
} else {
    $pageContent = '<div class="alert alert-warning">Page "' . htmlspecialchars($page) . '" does not exist yet.</div>';
}

// Initialize the theme manager
$themeManager = new ThemeManager();

// Set page-specific metadata
$metadata = [
    'theme' => 'margot',
    'style' => 'margot.css',
    'squelette' => ($action === 'edit') ? 'edit.html' : 'default.html'
];

// Load templates (this is where request parameters can override)
$themeManager->loadTemplates($metadata);

// For edit action, wrap content in an edit form
if ($action === 'edit') {
    $editContent = '<form method="post" action="/wiki.php?page=' . htmlspecialchars($page) . '">';
    $editContent .= '<div class="mb-3">';
    $editContent .= '<textarea class="form-control edit-form" name="content" rows="15">' . htmlspecialchars($pageContent) . '</textarea>';
    $editContent .= '</div>';
    $editContent .= '<button type="submit" class="btn btn-primary">Save Changes</button>';
    $editContent .= ' <a href="/wiki.php?page=' . htmlspecialchars($page) . '" class="btn btn-secondary">Cancel</a>';
    $editContent .= '</form>';
    $pageContent = $editContent;
}

// Render the page through the theme
$output = $themeManager->render($pageContent, $pageTitle);

echo $output;
