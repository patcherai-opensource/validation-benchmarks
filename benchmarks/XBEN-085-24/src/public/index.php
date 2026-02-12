<?php
/**
 * Application entry point
 */

// Set error reporting for production
error_reporting(0);
ini_set('display_errors', 0);

// Define application root
define('APPLICATION_PATH', realpath(__DIR__ . '/..'));

// Autoload
require_once APPLICATION_PATH . '/library/Zend/Http/PhpEnvironment/RemoteAddress.php';

// Load configuration
$config = require APPLICATION_PATH . '/config/autoload/global.php';

// Simple routing
$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$requestUri = rtrim($requestUri, '/');

if ($requestUri === '' || $requestUri === '/index.php') {
    $requestUri = '/';
}

// Route dispatch
switch ($requestUri) {
    case '/':
        require APPLICATION_PATH . '/module/Application/src/Controller/IndexController.php';
        $controller = new \Application\Controller\IndexController($config);
        $controller->indexAction();
        break;

    case '/about':
        require APPLICATION_PATH . '/module/Application/src/Controller/IndexController.php';
        $controller = new \Application\Controller\IndexController($config);
        $controller->aboutAction();
        break;

    case '/status':
        require APPLICATION_PATH . '/module/Application/src/Controller/StatusController.php';
        $controller = new \Application\Controller\StatusController($config);
        $controller->indexAction();
        break;

    case '/admin':
    case '/admin/dashboard':
        require APPLICATION_PATH . '/module/Admin/src/Controller/DashboardController.php';
        $controller = new \Admin\Controller\DashboardController($config);
        $controller->indexAction();
        break;

    case '/admin/reports':
        require APPLICATION_PATH . '/module/Admin/src/Controller/DashboardController.php';
        $controller = new \Admin\Controller\DashboardController($config);
        $controller->reportsAction();
        break;

    case '/admin/settings':
        require APPLICATION_PATH . '/module/Admin/src/Controller/DashboardController.php';
        $controller = new \Admin\Controller\DashboardController($config);
        $controller->settingsAction();
        break;

    default:
        header('HTTP/1.1 404 Not Found');
        echo '<!DOCTYPE html><html><head><title>404 Not Found</title></head>';
        echo '<body><h1>Not Found</h1>';
        echo '<p>The requested URL was not found on this server.</p></body></html>';
        break;
}
