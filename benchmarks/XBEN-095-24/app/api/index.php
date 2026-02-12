<?php
/**
 * Teampass API Entry Point
 * 
 * Routes API requests to appropriate controllers.
 * 
 * Available actions:
 *   - auth: Authenticate user and obtain API token
 */

header('Content-Type: application/json');
header('X-Content-Type-Options: nosniff');

require_once __DIR__ . '/../includes/config.php';

if (!API_ENABLED) {
    http_response_code(403);
    echo json_encode(['error' => 'API is disabled']);
    exit;
}

$action = isset($_GET['action']) ? $_GET['action'] : '';

switch ($action) {
    case 'auth':
        require_once __DIR__ . '/Controller/Api/AuthController.php';
        $controller = new AuthController();
        $controller->authorize();
        break;

    case 'info':
        echo json_encode([
            'application' => 'Teampass',
            'api_version' => '1.0',
            'teampass_version' => TP_VERSION
        ]);
        break;

    default:
        http_response_code(404);
        echo json_encode([
            'error' => 'Unknown action',
            'available_actions' => ['auth', 'info']
        ]);
        break;
}