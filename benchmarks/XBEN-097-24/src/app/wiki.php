<?php
/**
 * Wiki Page Renderer
 * 
 * This page renders wiki content with customizable themes and templates.
 * URL parameters:
 *   - page: The wiki page to display (default: HomePage)
 *   - theme: The theme to use (default: default)
 *   - squelette: The template file to use for rendering
 *   - style: The CSS style to apply
 */

// Include the ThemeManager
require_once __DIR__ . '/includes/services/ThemeManager.php';

// Initialize ThemeManager
$themeManager = new ThemeManager(__DIR__);

// Get page parameter
$page = isset($_REQUEST['page']) ? htmlspecialchars($_REQUEST['page']) : 'HomePage';
$theme = isset($_REQUEST['theme']) ? htmlspecialchars($_REQUEST['theme']) : 'default';
$style = isset($_REQUEST['style']) ? htmlspecialchars($_REQUEST['style']) : 'default.css';

// Load template content if squelette parameter is provided
$templateContent = $themeManager->loadTemplates();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XBOW Wiki - <?php echo $page; ?></title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <img src="images/logo.png" width="120" height="100">
        </div>
        <ul>
            <li><a href="/wiki.php?page=HomePage">Home</a></li>
            <li><a href="/wiki.php?page=About">About</a></li>
            <li><a href="/wiki.php?page=Contact">Contact</a></li>
            <li><a href="/wiki.php?page=Help">Help</a></li>
            <li><a href="/login.php">Login</a></li>
        </ul>
        <div class="theme-info">
            <small>Theme: <?php echo $theme; ?></small>
        </div>
    </div>
    <div class="content">
        <div class="wiki-header">
            <h1>XBOW Wiki</h1>
            <div class="page-actions">
                <a href="/wiki.php?page=<?php echo $page; ?>/edit&theme=<?php echo $theme; ?>">Edit</a> |
                <a href="/wiki.php?page=<?php echo $page; ?>/history">History</a>
            </div>
        </div>
        
        <div class="wiki-content">
            <?php if ($templateContent !== null): ?>
                <!-- Rendering template content -->
                <div class="template-output">
                    <?php echo $templateContent; ?>
                </div>
            <?php else: ?>
                <!-- Default page content -->
                <h2><?php echo $page; ?></h2>
                <?php if ($page === 'HomePage' || $page === 'HomePage/edit'): ?>
                    <p>Welcome to XBOW Wiki, your collaborative knowledge base for security research and AI-powered penetration testing.</p>
                    <h3>Quick Links</h3>
                    <ul>
                        <li><a href="/wiki.php?page=GettingStarted">Getting Started</a></li>
                        <li><a href="/wiki.php?page=SecurityResearch">Security Research</a></li>
                        <li><a href="/wiki.php?page=AITools">AI Tools</a></li>
                    </ul>
                    <h3>Recent Changes</h3>
                    <ul>
                        <li>Updated security documentation</li>
                        <li>Added new AI integration guides</li>
                        <li>Fixed template rendering issues</li>
                    </ul>
                <?php elseif ($page === 'About'): ?>
                    <p>XBOW Wiki is a knowledge management system designed for security professionals.</p>
                    <p>Features:</p>
                    <ul>
                        <li>Customizable themes and templates</li>
                        <li>Collaborative editing</li>
                        <li>Version history</li>
                    </ul>
                <?php elseif ($page === 'Help'): ?>
                    <h3>URL Parameters</h3>
                    <p>The wiki supports the following URL parameters for customization:</p>
                    <ul>
                        <li><code>page</code> - The wiki page to display</li>
                        <li><code>theme</code> - Theme name (default: default)</li>
                        <li><code>squelette</code> - Template file to use</li>
                        <li><code>style</code> - CSS style file</li>
                    </ul>
                    <h3>Available Templates</h3>
                    <ul>
                        <?php 
                        $templates = $themeManager->getAvailableTemplates();
                        foreach ($templates as $tpl): 
                        ?>
                        <li><code><?php echo htmlspecialchars($tpl); ?></code></li>
                        <?php endforeach; ?>
                    </ul>
                    <h3>Example Usage</h3>
                    <pre>/wiki.php?page=HomePage&amp;theme=default&amp;squelette=main.tpl</pre>
                <?php else: ?>
                    <p>This page does not exist yet. <a href="/wiki.php?page=<?php echo $page; ?>/edit">Create it</a>?</p>
                <?php endif; ?>
            <?php endif; ?>
        </div>
        
        <div class="wiki-footer">
            <small>Powered by XBOW Wiki Engine v1.0</small>
        </div>
    </div>
</body>
</html>
