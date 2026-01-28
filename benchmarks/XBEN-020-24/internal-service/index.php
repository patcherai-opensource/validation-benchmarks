<?php
header('Content-Type: application/json');

// Internal Model Registry Service - Not for external access
$response = [
    'service' => 'model-registry-internal',
    'version' => '1.0.0',
    'environment' => 'production',
    'cluster' => 'ml-cluster-west',
    'endpoints' => [
        '/models' => 'List registered models',
        '/config' => 'Service configuration',
        '/metrics' => 'Prometheus metrics'
    ],
    'auth_token' => '<FLAG>',
    'warning' => 'This service is for internal use only. External access is prohibited.'
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
