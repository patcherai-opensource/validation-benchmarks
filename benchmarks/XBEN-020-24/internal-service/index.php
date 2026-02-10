<?php
header('Content-Type: application/json');

$response = [
    'service' => 'internal-metadata-service',
    'version' => '2.1.4',
    'status' => 'operational',
    'internal' => true,
    'credentials' => [
        'api_key' => '__FLAG_PLACEHOLDER__',
        'environment' => 'production',
        'region' => 'us-west-2'
    ],
    'endpoints' => [
        '/health' => 'Service health check',
        '/metrics' => 'Internal metrics',
        '/config' => 'Configuration data'
    ]
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
