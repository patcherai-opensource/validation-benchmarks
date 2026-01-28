<?php
// DeepVision API Index
header('Content-Type: application/json');

echo json_encode([
    "service" => "DeepVision ML API",
    "version" => "2.6.0",
    "base_url" => "/api/v1",
    "documentation" => "/docs.php",
    "endpoints" => [
        "GET /api/v1/health" => "Service health check",
        "GET /api/v1/models" => "List available models",
        "GET /api/v1/datasets" => "List available datasets"
    ]
], JSON_PRETTY_PRINT);
?>
