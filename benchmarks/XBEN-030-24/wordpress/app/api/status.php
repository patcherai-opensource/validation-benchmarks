<?php
/**
 * ModuLink - API Status
 */
header('Content-Type: application/json');

$status = [
    'service' => 'ModuLink API',
    'version' => '3.2.1',
    'status' => 'operational',
    'timestamp' => date('c'),
    'endpoints' => [
        '/api/status.php' => 'System status (this endpoint)',
        '/api/plugins/list' => 'List installed plugins',
        '/api/health' => 'Health check',
        '/api/config' => 'Configuration (requires auth)'
    ],
    'server' => [
        'php_version' => phpversion(),
        'os' => php_uname('s')
    ]
];

echo json_encode($status, JSON_PRETTY_PRINT);
