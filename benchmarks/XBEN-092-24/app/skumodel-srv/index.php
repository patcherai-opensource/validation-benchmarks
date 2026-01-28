<?php
header('Content-Type: application/json');

$response = [
    'service' => 'ImageOptimizer Backend v1.2.3',
    'status' => 'operational',
    'endpoints' => [
        [
            'name' => 'health',
            'path' => '/health',
            'method' => 'POST',
            'description' => 'Health check endpoint'
        ],
        [
            'name' => 'stats',
            'path' => '/stats',
            'method' => 'POST',
            'description' => 'Service statistics'
        ],
        [
            'name' => 'upload',
            'path' => '/upload',
            'method' => 'POST',
            'params' => ['data' => 'base64 encoded image'],
            'description' => 'Upload image for optimization'
        ],
        [
            'name' => 'optimize',
            'path' => '/optimize',
            'method' => 'POST',
            'params' => ['image_path' => 'path to uploaded image'],
            'description' => 'Run optimization on uploaded image'
        ]
    ],
    'timestamp' => date('Y-m-d H:i:s')
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
