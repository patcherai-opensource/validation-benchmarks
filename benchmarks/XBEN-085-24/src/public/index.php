<?php
/**
 * CodeIgniter Application Entry Point
 *
 * This file serves as the front controller for the application,
 * routing all requests to the appropriate controller.
 *
 * @package    CodeIgniter
 */

// Suppress error display in production
error_reporting(0);
ini_set('display_errors', '0');
ini_set('log_errors', '1');

// Define paths
define('APPPATH', dirname(__DIR__) . '/app/');
define('SYSTEMPATH', dirname(__DIR__) . '/system/');

// Load framework components
require_once SYSTEMPATH . 'HTTP/IncomingRequest.php';
require_once APPPATH . 'Config/App.php';
require_once APPPATH . 'Config/Database.php';

// Initialize configuration
$config = new AppConfig();

// Initialize request with proxy configuration
$request = new IncomingRequest([
    'proxyIPs' => $config->proxyIPs,
]);

// Load controllers
require_once APPPATH . 'Controllers/Home.php';
require_once APPPATH . 'Controllers/Admin.php';

// Simple router
$path = $request->getPath();
$path = rtrim($path, '/') ?: '/';

// Remove query string
if (($pos = strpos($path, '?')) !== false) {
    $path = substr($path, 0, $pos);
}

// Route mapping
$homeController = new HomeController($request);
$adminController = new AdminController($request, $config);

switch ($path) {
    case '/':
        echo $homeController->index();
        break;

    case '/login':
        echo $homeController->login();
        break;

    case '/logout':
        $homeController->logout();
        break;

    case '/dashboard':
        echo $homeController->dashboard();
        break;

    case '/about':
        echo $homeController->about();
        break;

    case '/health':
    case '/api/health':
        $homeController->health();
        break;

    case '/admin':
        echo $adminController->index();
        break;

    case '/admin/config':
        echo $adminController->config();
        break;

    case '/admin/report':
        echo $adminController->report();
        break;

    default:
        http_response_code(404);
        $ip = '';
        ob_start();
        include APPPATH . 'Views/errors/notfound.php';
        echo ob_get_clean();
        break;
}
