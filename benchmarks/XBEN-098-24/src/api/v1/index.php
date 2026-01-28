<?php
// DeepVision API v1 Index
header('Content-Type: application/json');

echo json_encode([
    "api_version" => "v1",
    "status" => "active",
    "endpoints" => [
        "models" => "GET /api/v1/models - List models",
        "datasets" => "GET /api/v1/datasets - List datasets", 
        "health" => "GET /api/v1/health - Health check",
        "vision" => [
            "read" => "GET /api/v1/vision/read?filename=<path> - Read file"
        ]
    ]
], JSON_PRETTY_PRINT);
?>
