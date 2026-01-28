<?php
/**
 * TaskFlow Portal - Health Check Endpoint
 */
header('Content-Type: application/json');

echo json_encode([
    'status' => 'healthy',
    'uptime' => time() - $_SERVER['REQUEST_TIME'],
    'php_version' => phpversion()
]);
