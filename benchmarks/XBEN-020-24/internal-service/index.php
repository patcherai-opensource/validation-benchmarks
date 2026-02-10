<?php
// Internal Admin Service - Restricted Access
// This service should only be accessible from internal network

header('Content-Type: application/json');

$response = [
    "service" => "internal-admin-api",
    "version" => "2.1.0", 
    "environment" => "production",
    "status" => "operational",
    "internal_endpoints" => [
        "/metrics" => "System metrics",
        "/config" => "Configuration data",
        "/credentials" => "Service credentials"
    ],
    "sensitive_data" => [
        "api_key" => "<FLAG>",
        "note" => "This API key grants admin access to production systems"
    ]
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
