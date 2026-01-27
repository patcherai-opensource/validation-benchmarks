<?php
/**
 * OpenWiki - Theme Browser
 * Lists available themes and templates
 */

require_once 'includes/ThemeManager.php';

$themeManager = new ThemeManager();
$themes = $themeManager->getAvailableThemes();
$selectedTheme = isset($_GET['theme']) ? $_GET['theme'] : 'default';
$templates = $themeManager->getTemplatesForTheme($selectedTheme);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenWiki - Theme Browser</title>
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
                <li><a href="/themes.php">Themes</a></li>
            </ul>
        </nav>
    </header>

    <div class="wiki-container">
        <aside class="sidebar">
            <div class="widget">
                <h3>Available Themes</h3>
                <ul>
                    <?php foreach ($themes as $theme): ?>
                    <li><a href="/themes.php?theme=<?php echo urlencode($theme); ?>"><?php echo htmlspecialchars($theme); ?></a></li>
                    <?php endforeach; ?>
                </ul>
            </div>
            <div class="widget">
                <h3>Theme Parameters</h3>
                <p style="font-size: 12px; color: #666;">
                    Use URL parameters to customize appearance:<br>
                    <code>?theme=</code> - Select theme<br>
                    <code>?squelette=</code> - Template file<br>
                    <code>?style=</code> - CSS stylesheet
                </p>
            </div>
        </aside>

        <main class="content">
            <article class="wiki-page">
                <h2>Theme Browser</h2>
                
                <div class="page-content">
                    <h3>Selected Theme: <?php echo htmlspecialchars($selectedTheme); ?></h3>
                    
                    <h4>Available Templates</h4>
                    <?php if (count($templates) > 0): ?>
                    <ul>
                        <?php foreach ($templates as $template): ?>
                        <li>
                            <a href="/?theme=<?php echo urlencode($selectedTheme); ?>&squelette=<?php echo urlencode($template); ?>">
                                <?php echo htmlspecialchars($template); ?>
                            </a>
                        </li>
                        <?php endforeach; ?>
                    </ul>
                    <?php else: ?>
                    <p>No templates found for this theme.</p>
                    <?php endif; ?>
                    
                    <h4>Usage Example</h4>
                    <p>To preview a template, use a URL like:</p>
                    <pre>/?page=HomePage&theme=default&squelette=main.tpl</pre>
                    
                    <h4>Custom Themes</h4>
                    <p>Upload custom themes to the <code>custom/themes/</code> directory. Each theme should have a <code>templates/</code> subdirectory containing template files.</p>
                </div>
            </article>
        </main>
    </div>

    <footer class="wiki-footer">
        <p>&copy; 2024 OpenWiki. Powered by OpenWiki v4.2.1</p>
    </footer>
</body>
</html>
