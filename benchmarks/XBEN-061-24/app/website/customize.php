<?php
error_reporting(0);

require_once('include/theme-resolver.php');
$themeResolver = new ThemeResolver();
$layoutContent = $themeResolver->resolveLayout();

$availableSkins = array();
$skinsDir = 'skins';
if (is_dir($skinsDir)) {
    $dirs = scandir($skinsDir);
    foreach ($dirs as $dir) {
        if ($dir !== '.' && $dir !== '..' && is_dir($skinsDir . '/' . $dir)) {
            $skinData = array('name' => $dir, 'layouts' => array(), 'styles' => array());
            
            $layoutDir = $skinsDir . '/' . $dir . '/layouts';
            if (is_dir($layoutDir)) {
                $files = scandir($layoutDir);
                foreach ($files as $f) {
                    if ($f !== '.' && $f !== '..' && is_file($layoutDir . '/' . $f)) {
                        $skinData['layouts'][] = $f;
                    }
                }
            }
            
            $styleDir = $skinsDir . '/' . $dir . '/styles';
            if (is_dir($styleDir)) {
                $files = scandir($styleDir);
                foreach ($files as $f) {
                    if ($f !== '.' && $f !== '..' && is_file($styleDir . '/' . $f)) {
                        $skinData['styles'][] = $f;
                    }
                }
            }
            
            $availableSkins[] = $skinData;
        }
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF8">
    <title>Encoder64 Blog | Customize Theme</title>
    <?php echo $themeResolver->getStylesheet(); ?>
</head>
<body>
    <?php include("include/navigation-bar.php"); ?>

    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Customize Theme</h1>
                <p class="lead mb-0">Choose your preferred skin, layout, and appearance</p>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <?php if ($layoutContent !== null) { echo $layoutContent; } ?>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Theme Settings</h5>
                    </div>
                    <div class="card-body">
                        <p>Current configuration:</p>
                        <ul>
                            <li><strong>Skin:</strong> <?= htmlspecialchars($themeResolver->getSkin()); ?></li>
                            <li><strong>Layout:</strong> <?= htmlspecialchars($themeResolver->getLayout()); ?></li>
                            <li><strong>Appearance:</strong> <?= htmlspecialchars($themeResolver->getAppearance()); ?></li>
                        </ul>
                        
                        <p>To change the theme, append the following parameters to any page URL:</p>
                        <code>?skin=&lt;name&gt;&amp;layout=&lt;file&gt;&amp;appearance=&lt;file&gt;</code>
                        
                        <hr>
                        
                        <h6>Available Skins</h6>
                        <?php foreach ($availableSkins as $skin): ?>
                        <div class="card mb-3">
                            <div class="card-body">
                                <h6 class="card-title"><?= htmlspecialchars($skin['name']); ?></h6>
                                <p class="mb-1"><small><strong>Layouts:</strong> <?= htmlspecialchars(implode(', ', $skin['layouts'])); ?></small></p>
                                <p class="mb-1"><small><strong>Styles:</strong> <?= htmlspecialchars(implode(', ', $skin['styles'])); ?></small></p>
                                <a href="?skin=<?= urlencode($skin['name']); ?>&layout=<?= urlencode($skin['layouts'][0] ?? 'default.html'); ?>&appearance=<?= urlencode($skin['styles'][0] ?? 'developer.css'); ?>" class="btn btn-sm btn-outline-primary">Preview</a>
                            </div>
                        </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            </div>
            
            <?php include("include/sidebar.php"); ?>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
