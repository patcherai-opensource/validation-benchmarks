<?php
// API endpoint for internal use (not vulnerable)
header('Content-Type: application/json');

$action = $_GET['action'] ?? '';

switch ($action) {
    case 'status':
        echo json_encode([
            'status' => 'ok',
            'version' => '3.25.0',
            'service' => 'SecureAuth Portal',
            'timestamp' => date('Y-m-d H:i:s')
        ]);
        break;
    
    case 'health':
        echo json_encode([
            'healthy' => true,
            'uptime' => rand(1000, 9999),
            'sessions_active' => rand(10, 100)
        ]);
        break;
    
    default:
        http_response_code(400);
        echo json_encode([
            'error' => 'Invalid action',
            'available_actions' => ['status', 'health']
        ]);
        break;
}
