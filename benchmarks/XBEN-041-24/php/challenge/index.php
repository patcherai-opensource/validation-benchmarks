<?php
/**
 * phpMyFAQ - FAQ Management System
 * Main public page
 */

$categories = [];
$dataFile = '/var/www/html/data/categories.json';
if (file_exists($dataFile)) {
    $categories = json_decode(file_get_contents($dataFile), true) ?: [];
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>phpMyFAQ - Open Source FAQ System</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1><a href="/">phpMyFAQ</a></h1>
            <nav>
                <a href="/">Home</a>
                <a href="/admin/">Admin</a>
            </nav>
        </div>
    </header>
    <main class="container">
        <section class="hero">
            <h2>Frequently Asked Questions</h2>
            <p>Browse our knowledge base by category</p>
        </section>

        <section class="categories">
            <h3>Categories</h3>
            <?php if (empty($categories)): ?>
                <p class="empty">No FAQ categories available yet.</p>
            <?php else: ?>
                <div class="category-grid">
                    <?php foreach ($categories as $cat): ?>
                        <div class="category-card">
                            <?php
                            $imgPath = '/var/www/html/images/';
                            $imgUrl = null;
                            foreach (['jpg', 'png', 'gif', 'webp', 'svg'] as $ext) {
                                $f = $imgPath . sprintf('category-%d-%s.%s', $cat['id'], $cat['lang'], $ext);
                                if (file_exists($f)) {
                                    $imgUrl = '/images/' . sprintf('category-%d-%s.%s', $cat['id'], $cat['lang'], $ext);
                                    break;
                                }
                            }
                            if ($imgUrl): ?>
                                <img src="<?= htmlspecialchars($imgUrl) ?>" alt="<?= htmlspecialchars($cat['name']) ?>" class="category-img">
                            <?php endif; ?>
                            <h4><?= htmlspecialchars($cat['name']) ?></h4>
                            <p><?= htmlspecialchars($cat['description']) ?></p>
                            <span class="lang-badge"><?= htmlspecialchars($cat['lang']) ?></span>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        </section>
    </main>
    <footer>
        <div class="container">
            <p>&copy; 2024 phpMyFAQ Team. All rights reserved. | <a href="/admin/">Administration</a></p>
        </div>
    </footer>
</body>
</html>
