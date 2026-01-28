<?php
/**
 * TaskFlow Portal - API Status Endpoint
 */
header('Content-Type: application/json');

$status = [
    'application' => 'TaskFlow Portal',
    'version' => '2.4.1',
    'status' => 'operational',
    'timestamp' => date('c'),
    'features' => [
        'persistent_sessions' => true,
        'remember_me_enabled' => true,
        'session_storage' => 'memory',
        'token_format' => 'series:value'
    ],
    'active_sessions' => [
        'count' => 2,
        'types' => ['guest', 'demo_user']
    ]
];

echo json_encode($status, JSON_PRETTY_PRINT);
