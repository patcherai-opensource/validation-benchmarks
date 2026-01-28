<?php
header('Content-Type: application/json');

$status = [
    'status' => 'operational',
    'version' => '2.4.1',
    'uptime' => rand(10000, 999999),
    'storage_used' => '45.2 GB',
    'storage_available' => '154.8 GB',
    'api_endpoints' => [
        '/api/status.php' => 'System status information',
        '/api/files.php' => 'File listing (authentication required)',
        '/api/upload.php' => 'File upload endpoint (authentication required)'
    ],
    'documentation' => '/api/docs'
];

echo json_encode($status, JSON_PRETTY_PRINT);
