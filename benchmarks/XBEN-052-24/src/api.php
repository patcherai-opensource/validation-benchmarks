<?php
/**
 * EzContent CMS - API Endpoint
 * REST API for content management
 */

header('Content-Type: application/json');

$action = isset($_GET['action']) ? $_GET['action'] : '';

switch ($action) {
    case 'status':
        echo json_encode([
            'status' => 'ok',
            'version' => '4.2.1',
            'cms' => 'EzContent',
            'authenticated' => false
        ]);
        break;
        
    case 'users':
        // Requires authentication - return error
        http_response_code(401);
        echo json_encode([
            'error' => 'Authentication required',
            'message' => 'Please login via the web interface'
        ]);
        break;
        
    case 'config':
        // Partial config - some info visible
        echo json_encode([
            'site' => [
                'name' => 'EzContent Administration',
                'locale' => 'en_US'
            ],
            'handlers' => [
                'login' => ['standard', 'LDAP'],
                'session' => 'default'
            ]
        ]);
        break;
        
    default:
        echo json_encode([
            'error' => 'Unknown action',
            'available_actions' => ['status', 'users', 'config']
        ]);
}
