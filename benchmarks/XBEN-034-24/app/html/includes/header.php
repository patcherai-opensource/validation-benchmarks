<?php require_once __DIR__ . '/config.php'; ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo APP_NAME; ?> - Plugin Management</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="navbar-brand">
            <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="32" height="32" rx="6" fill="#1a73e8"/>
                <path d="M10 16h12M16 10v12" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
            </svg>
            <span><?php echo APP_NAME; ?></span>
        </a>
        <ul class="navbar-nav">
            <li><a href="/" class="<?php echo ($_SERVER['REQUEST_URI'] == '/' || $_SERVER['REQUEST_URI'] == '/index.php') ? 'active' : ''; ?>">Dashboard</a></li>
            <li><a href="/plugins.php" class="<?php echo strpos($_SERVER['REQUEST_URI'], '/plugins') === 0 ? 'active' : ''; ?>">Plugins</a></li>
            <li><a href="/upload.php" class="<?php echo strpos($_SERVER['REQUEST_URI'], '/upload') === 0 ? 'active' : ''; ?>">Install Plugin</a></li>
            <li><a href="/system.php" class="<?php echo strpos($_SERVER['REQUEST_URI'], '/system') === 0 ? 'active' : ''; ?>">System</a></li>
        </ul>
    </nav>
