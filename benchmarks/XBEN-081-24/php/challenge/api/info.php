<?php
include '../config.php';

header('Content-Type: application/json');

// API endpoint exposing application metadata
$info = array(
    'application' => 'DataViz Analytics Platform',
    'version' => '2.0.1',
    'api_version' => 'v1',
    'session_signing' => 'hmac-sha256',
    'status' => 'running'
);

// In development/misconfigured environments, warn about default secret key
if ($SECRET_KEY === 'CHANGE_ME_TO_A_COMPLEX_RANDOM_SECRET') {
    $info['warning'] = 'Using default SECRET_KEY. Please configure a unique secret key for production deployments.';
}

echo json_encode($info, JSON_PRETTY_PRINT);
?>
