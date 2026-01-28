<?php
// API Router
header("Content-Type: application/json");

$request_uri = $_SERVER['REQUEST_URI'];

// Handle different API routes
if (preg_match('/^\/api\/media/', $request_uri)) {
    include __DIR__ . '/media.php';
} elseif (preg_match('/^\/api\/products/', $request_uri)) {
    echo json_encode([
        "status" => "error",
        "message" => "Products API is under maintenance"
    ]);
} elseif (preg_match('/^\/api\/orders/', $request_uri)) {
    echo json_encode([
        "status" => "error", 
        "message" => "Orders API requires enterprise license"
    ]);
} else {
    echo json_encode([
        "status" => "error",
        "message" => "Unknown API endpoint",
        "available_endpoints" => [
            "/api/media" => "Media management API",
            "/api/products" => "Products API (maintenance)",
            "/api/orders" => "Orders API (enterprise only)"
        ]
    ]);
}
