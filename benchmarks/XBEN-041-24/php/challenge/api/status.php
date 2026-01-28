<?php
header('Content-Type: application/json');

$status = [
    'status' => 'online',
    'version' => '2.1.3',
    'server_time' => date('Y-m-d H:i:s'),
    'php_version' => PHP_VERSION,
    'uptime' => '3 days, 14 hours'
];

echo json_encode($status, JSON_PRETTY_PRINT);
