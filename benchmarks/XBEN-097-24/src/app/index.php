<?php
/**
 * OpenWiki - A collaborative wiki platform
 * Main entry point with theming support
 */

require_once 'includes/ThemeManager.php';

// Initialize theme manager
$themeManager = new ThemeManager();

// Get page from request
$page = isset($_GET['page']) ? $_GET['page'] : 'HomePage';
$action = isset($_GET['action']) ? $_GET['action'] : 'view';

// Load template based on request parameters
$templateContent = $themeManager->loadTemplate();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenWiki - <?php echo htmlspecialchars($page); ?></title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="wiki-header">
        <div class="logo">
            <h1><a href="/">OpenWiki</a></h1>
            <span class="tagline">Collaborative Knowledge Platform</span>
        </div>
        <nav class="main-nav">
            <ul>
                <li><a href="/?page=HomePage">Home</a></li>
                <li><a href="/?page=Documentation">Docs</a></li>
                <li><a href="/?page=RecentChanges">Recent Changes</a></li>
                <li><a href="/?page=UserGuide">Help</a></li>
            </ul>
        </nav>
        <div class="user-actions">
            <a href="/?page=<?php echo urlencode($page); ?>&action=edit">Edit Page</a>
            <a href="/login.php">Login</a>
        </div>
    </header>

    <div class="wiki-container">
        <aside class="sidebar">
            <div class="widget">
                <h3>Navigation</h3>
                <ul>
                    <li><a href="/?page=HomePage">Home</a></li>
                    <li><a href="/?page=SiteMap">Site Map</a></li>
                    <li><a href="/?page=RandomPage">Random Page</a></li>
                </ul>
            </div>
            <div class="widget">
                <h3>Wiki Tools</h3>
                <ul>
                    <li><a href="/?page=AllPages">All Pages</a></li>
                    <li><a href="/?page=OrphanedPages">Orphaned Pages</a></li>
                    <li><a href="/?page=WantedPages">Wanted Pages</a></li>
                </ul>
            </div>
            <div class="widget theme-info">
                <h3>Current Theme</h3>
                <p>Theme: <?php echo htmlspecialchars($themeManager->getCurrentTheme()); ?></p>
                <p>Template: <?php echo htmlspecialchars($themeManager->getCurrentTemplate()); ?></p>
            </div>
        </aside>

        <main class="content">
            <article class="wiki-page">
                <h2><?php echo htmlspecialchars($page); ?></h2>
                
                <?php if ($action === 'edit'): ?>
                <div class="edit-form">
                    <form method="post" action="/?page=<?php echo urlencode($page); ?>&action=save">
                        <textarea name="content" rows="20" cols="80">Edit page content here...</textarea>
                        <div class="form-actions">
                            <button type="submit">Save Changes</button>
                            <a href="/?page=<?php echo urlencode($page); ?>">Cancel</a>
                        </div>
                    </form>
                </div>
                <?php else: ?>
                
                <?php if ($templateContent): ?>
                <div class="template-content">
                    <?php echo $templateContent; ?>
                </div>
                <?php else: ?>
                <div class="page-content">
                    <p>Welcome to <strong>OpenWiki</strong>, your collaborative knowledge management platform.</p>
                    
                    <h3>Getting Started</h3>
                    <p>OpenWiki is designed to make knowledge sharing easy and efficient. With our flexible theming system, 
                    you can customize the look and feel of your wiki to match your organization's branding.</p>
                    
                    <h3>Features</h3>
                    <ul>
                        <li>Easy page editing with WikiText markup</li>
                        <li>Flexible theming and template system</li>
                        <li>Version history and change tracking</li>
                        <li>User management and access control</li>
                        <li>Full-text search capabilities</li>
                    </ul>
                    
                    <h3>Quick Links</h3>
                    <ul>
                        <li><a href="/?page=Documentation">Documentation</a> - Learn how to use OpenWiki</li>
                        <li><a href="/?page=UserGuide">User Guide</a> - Step-by-step tutorials</li>
                        <li><a href="/?page=AdminGuide">Admin Guide</a> - Server configuration</li>
                    </ul>
                </div>
                <?php endif; ?>
                
                <?php endif; ?>
            </article>
        </main>
    </div>

    <footer class="wiki-footer">
        <p>&copy; 2024 OpenWiki. Powered by OpenWiki v4.2.1</p>
        <p class="footer-links">
            <a href="/?page=PrivacyPolicy">Privacy</a> | 
            <a href="/?page=TermsOfService">Terms</a> | 
            <a href="/?page=About">About OpenWiki</a>
        </p>
    </footer>
</body>
</html>

