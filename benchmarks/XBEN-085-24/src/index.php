<?php
/**
 * Application Entry Point
 * 
 * Front controller that handles all incoming requests
 * and routes them to the appropriate controller.
 */

// Suppress PHP version info
header_remove('X-Powered-By');

// Load core components
require_once __DIR__ . '/core/Request.php';
require_once __DIR__ . '/core/Response.php';
require_once __DIR__ . '/core/Router.php';

// Load controllers
require_once __DIR__ . '/controllers/DashboardController.php';
require_once __DIR__ . '/controllers/AuthController.php';
require_once __DIR__ . '/controllers/AdminController.php';

// Initialize request and response
$request = new Request();
$response = new Response();

// Initialize controllers
$dashboard = new DashboardController($request, $response);
$auth = new AuthController($request, $response);
$admin = new AdminController($request, $response);

// Initialize router
$router = new Router();

// Register routes
$router->get('/', [$dashboard, 'index']);
$router->get('/login', [$auth, 'showLogin']);
$router->post('/login', [$auth, 'processLogin']);
$router->get('/logout', [$auth, 'logout']);
$router->get('/panel', [$admin, 'panel']);
$router->get('/panel/diagnostics', [$admin, 'diagnostics']);
$router->get('/api/status', [$dashboard, 'status']);
$router->get('/health', [$dashboard, 'health']);

// Dispatch the request
$router->dispatch($request->getMethod(), $request->getPath());
