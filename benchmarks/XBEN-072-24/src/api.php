<?php
header('Content-Type: application/json');

$action = isset($_GET['action']) ? $_GET['action'] : '';

switch ($action) {
    case 'status':
        echo json_encode([
            'status' => 'online',
            'version' => '2.1.1',
            'endpoints' => [
                '/api.php?action=status',
                '/api.php?action=health'
            ]
        ]);
        break;
    
    case 'health':
        echo json_encode([
            'healthy' => true,
            'database' => 'connected',
            'cache' => 'operational',
            'timestamp' => date('c')
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
?>
