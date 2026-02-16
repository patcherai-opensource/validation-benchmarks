<?php
/**
 * SecurePortal - Enterprise Authentication Gateway
 * Session and authentication routing
 */

session_start();

// Route configuration
$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Route handling
switch ($request_uri) {
    case '/':
    case '/index.php':
        require __DIR__ . '/controllers/home.php';
        break;
    case '/auth/signin':
        require __DIR__ . '/controllers/signin.php';
        break;
    case '/auth/verify':
        require __DIR__ . '/controllers/verify.php';
        break;
    case '/auth/signout':
        require __DIR__ . '/controllers/signout.php';
        break;
    case '/dashboard':
        require __DIR__ . '/controllers/dashboard.php';
        break;
    case '/account/profile':
        require __DIR__ . '/controllers/profile.php';
        break;
    case '/account/settings':
        require __DIR__ . '/controllers/settings.php';
        break;
    case '/help':
        require __DIR__ . '/controllers/help.php';
        break;
    case '/ping':
        header('Content-Type: text/plain');
        echo 'OK';
        break;
    default:
        http_response_code(404);
        require __DIR__ . '/views/404.php';
        break;
}
