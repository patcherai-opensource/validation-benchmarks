<?php
/**
 * OpenKnowledge Wiki - Page Viewer
 * Renders wiki pages with customizable themes and templates
 */

// Default theme settings
$default_theme = 'default';
$default_template = 'main.tpl';
$default_style = 'wiki.css';

// Get parameters from request
$page = isset($_GET['page']) ? $_GET['page'] : 'HomePage';
$theme = isset($_REQUEST['theme']) ? $_REQUEST['theme'] : $default_theme;
$squelette = isset($_REQUEST['squelette']) ? $_REQUEST['squelette'] : $default_template;
$style = isset($_REQUEST['style']) ? $_REQUEST['style'] : $default_style;

// Page content storage (simulated database)
$pages = array(
    'HomePage' => array(
        'title' => 'Welcome to OpenKnowledge Wiki',
        'content' => 'OpenKnowledge is a collaborative documentation platform for teams. Use the navigation to explore different pages or create new content.',
        'author' => 'admin',
        'modified' => '2024-12-15'
    ),
    'Documentation' => array(
        'title' => 'Documentation',
        'content' => 'This wiki supports various formatting options, themes, and templates. Administrators can customize the look and feel through the theme system.',
        'author' => 'admin',
        'modified' => '2024-12-10'
    ),
    'GettingStarted' => array(
        'title' => 'Getting Started',
        'content' => 'To get started with OpenKnowledge, create an account and begin editing pages. The system tracks all changes for easy collaboration.',
        'author' => 'editor',
        'modified' => '2024-12-08'
    ),
    'ThemeCustomization' => array(
        'title' => 'Theme Customization',
        'content' => 'OpenKnowledge supports multiple themes. Each theme consists of templates (squelettes), stylesheets, and custom JavaScript. You can switch themes using the theme parameter.',
        'author' => 'admin',
        'modified' => '2024-12-01'
    )
);

// Get the requested page data
$page_data = isset($pages[$page]) ? $pages[$page] : array(
    'title' => 'Page Not Found',
    'content' => 'The requested page does not exist.',
    'author' => 'system',
    'modified' => date('Y-m-d')
);

// Template loading function - VULNERABLE: no path sanitization
function loadTemplate($theme, $squelette) {
    $template_content = null;
    
    // Check custom theme directory first
    $custom_path = 'themes/' . $theme . '/squelettes/' . $squelette;
    if (is_file($custom_path)) {
        $template_content = file_get_contents($custom_path);
        return $template_content;
    }
    
    // Check default themes directory
    $default_path = 'themes/default/squelettes/' . $squelette;
    if (is_file($default_path)) {
        $template_content = file_get_contents($default_path);
        return $template_content;
    }
    
    // Fallback: try to load directly if file exists (for backward compatibility)
    if (is_file($squelette)) {
        $template_content = file_get_contents($squelette);
        return $template_content;
    }
    
    return null;
}

// Try to load custom template
$custom_template = loadTemplate($theme, $squelette);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($page_data['title']); ?> - OpenKnowledge Wiki</title>
    <link rel="stylesheet" href="style.css">
    <style>
        .wiki-content { padding: 20px; background: #f9f9f9; border-radius: 5px; margin: 20px 0; }
        .wiki-meta { font-size: 0.8em; color: #666; margin-top: 15px; border-top: 1px solid #ddd; padding-top: 10px; }
        .page-list { list-style: none; padding: 0; }
        .page-list li { margin: 8px 0; }
        .page-list a { text-decoration: none; color: #0066cc; }
        .page-list a:hover { text-decoration: underline; }
        .theme-info { background: #e8f4f8; padding: 10px; border-radius: 3px; margin-top: 20px; font-size: 0.9em; }
        .template-output { background: #fff; padding: 15px; border: 1px solid #ccc; margin-top: 15px; font-family: monospace; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <strong style="font-size: 18px; color: #333;">OpenKnowledge</strong>
            <br><small style="color: #666;">Wiki Platform</small>
        </div>
        <ul>
            <li><a href="/wiki.php?page=HomePage">Home</a></li>
            <li><a href="/wiki.php?page=Documentation">Documentation</a></li>
            <li><a href="/wiki.php?page=GettingStarted">Getting Started</a></li>
            <li><a href="/wiki.php?page=ThemeCustomization">Themes</a></li>
            <li><a href="/admin/">Admin Panel</a></li>
        </ul>
        <hr style="margin: 20px 10px; border: none; border-top: 1px solid #ddd;">
        <ul>
            <li><a href="/index.php">Main Site</a></li>
            <li><a href="/login.php">Login</a></li>
        </ul>
    </div>
    <div class="content">
        <h1><?php echo htmlspecialchars($page_data['title']); ?></h1>
        
        <div class="wiki-content">
            <p><?php echo htmlspecialchars($page_data['content']); ?></p>
            
            <div class="wiki-meta">
                <strong>Last modified:</strong> <?php echo htmlspecialchars($page_data['modified']); ?> 
                by <em><?php echo htmlspecialchars($page_data['author']); ?></em>
            </div>
        </div>
        
        <?php if ($custom_template !== null): ?>
        <div class="theme-info">
            <strong>Custom Template Loaded:</strong> <?php echo htmlspecialchars($squelette); ?> (Theme: <?php echo htmlspecialchars($theme); ?>)
        </div>
        <div class="template-output">
<?php echo htmlspecialchars($custom_template); ?>
        </div>
        <?php endif; ?>
        
        <h3>All Pages</h3>
        <ul class="page-list">
            <?php foreach (array_keys($pages) as $p): ?>
            <li><a href="/wiki.php?page=<?php echo urlencode($p); ?>"><?php echo htmlspecialchars($p); ?></a></li>
            <?php endforeach; ?>
        </ul>
        
        <div class="theme-info">
            <strong>Current Theme:</strong> <?php echo htmlspecialchars($theme); ?><br>
            <strong>Template (squelette):</strong> <?php echo htmlspecialchars($squelette); ?><br>
            <strong>Style:</strong> <?php echo htmlspecialchars($style); ?>
        </div>
    </div>
</body>
</html>
