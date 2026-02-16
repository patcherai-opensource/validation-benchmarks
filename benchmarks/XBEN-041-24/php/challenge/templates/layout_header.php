<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= APP_NAME ?> - <?= $pageTitle ?? 'Dashboard' ?></title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <nav class="sidebar">
        <div class="sidebar-header">
            <h2><?= APP_NAME ?></h2>
        </div>
        <ul class="nav-menu">
            <li><a href="/" class="<?= $requestUri === '/' ? 'active' : '' ?>">Dashboard</a></li>
            <li class="nav-section">Catalog</li>
            <li><a href="/catalog/products" class="<?= strpos($requestUri, '/catalog/products') === 0 ? 'active' : '' ?>">Products</a></li>
            <li><a href="/catalog/categories" class="<?= $requestUri === '/catalog/categories' ? 'active' : '' ?>">Categories</a></li>
            <li><a href="/catalog/attributes" class="<?= $requestUri === '/catalog/attributes' ? 'active' : '' ?>">Attributes</a></li>
            <li class="nav-section">Enrichment</li>
            <li><a href="/enrich/media/upload" class="<?= $requestUri === '/enrich/media/upload' ? 'active' : '' ?>">Asset Manager</a></li>
        </ul>
        <div class="sidebar-footer">
            <span><?= htmlspecialchars($user['username'] ?? '', ENT_QUOTES, 'UTF-8') ?></span>
            <a href="/logout" class="logout-link">Sign out</a>
        </div>
    </nav>
    <main class="content">
