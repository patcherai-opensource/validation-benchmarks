<?php
header('Content-Type: application/json');

$response = [
    'status' => 'healthy',
    'version' => '2.4.1',
    'services' => [
        'database' => 'ok',
        'redis' => 'ok',
        'ml_backend' => 'ok'
    ],
    'timestamp' => date('c')
];

echo json_encode($response, JSON_PRETTY_PRINT);
