<?php
/**
 * CatalogHub PIM - Product Information Management
 * Front controller
 */

session_start();

require_once __DIR__ . '/includes/config.php';
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/database.php';

$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Route mapping
$routes = [
    '/'                         => 'dashboard',
    '/login'                    => 'login',
    '/logout'                   => 'logout',
    '/catalog/products'         => 'products',
    '/catalog/products/create'  => 'product_create',
    '/catalog/categories'       => 'categories',
    '/catalog/attributes'       => 'attributes',
    '/enrich/media/upload'      => 'media_upload',
    '/api/internal/asset/store' => 'api_asset_store',
    '/system/health'            => 'health',
];

$action = $routes[$requestUri] ?? 'not_found';

// Health endpoint (no auth)
if ($action === 'health') {
    header('Content-Type: application/json');
    echo json_encode(['status' => 'ok']);
    exit;
}

// Login/logout don't require auth
if ($action === 'login') {
    handleLogin();
    exit;
}

if ($action === 'logout') {
    handleLogout();
    exit;
}

// All other routes require authentication
if (!isAuthenticated()) {
    header('Location: /login');
    exit;
}

switch ($action) {
    case 'dashboard':
        renderDashboard();
        break;
    case 'products':
        renderProducts();
        break;
    case 'product_create':
        renderProductCreate();
        break;
    case 'categories':
        renderCategories();
        break;
    case 'attributes':
        renderAttributes();
        break;
    case 'media_upload':
        handleMediaUpload();
        break;
    case 'api_asset_store':
        handleAssetStore();
        break;
    default:
        http_response_code(404);
        renderTemplate('404');
        break;
}
