<?php
// DeepVision Health Check API
header('Content-Type: application/json');

echo json_encode([
    "status" => "healthy",
    "version" => "2.6.0",
    "service" => "deepvision-api",
    "timestamp" => date('c'),
    "endpoints" => [
        "/api/v1/models",
        "/api/v1/datasets",
        "/api/v1/vision/read"
    ]
], JSON_PRETTY_PRINT);
?>
