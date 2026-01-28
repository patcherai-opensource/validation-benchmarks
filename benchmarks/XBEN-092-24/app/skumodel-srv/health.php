<?php
header('Content-Type: application/json');

$response = [
    'status' => 'healthy',
    'service' => 'ImageOptimizer Backend',
    'version' => '1.2.3',
    'uptime' => rand(1000, 100000),
    'memory_usage' => memory_get_usage(true),
    'timestamp' => date('Y-m-d H:i:s')
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
