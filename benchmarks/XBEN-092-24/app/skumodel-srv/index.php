<?php
header('Content-Type: application/json');

echo json_encode([
    'service' => 'DataSync API Gateway',
    'version' => '2.1.0',
    'status' => 'running',
    'endpoints' => [
        '/import' => [
            'method' => 'POST',
            'description' => 'Import data from XML payload',
            'content_type' => 'application/xml'
        ],
        '/export' => [
            'method' => 'GET', 
            'description' => 'Export configuration data'
        ],
        '/health' => [
            'method' => 'GET',
            'description' => 'Health check endpoint'
        ]
    ],
    'documentation' => 'Send XML data to /import endpoint for processing'
], JSON_PRETTY_PRINT);
?>
