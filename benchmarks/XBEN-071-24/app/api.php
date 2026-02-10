<?php
/**
 * API Documentation and Status Page
 * Lists available API endpoints
 */
header('Content-Type: application/json');

$endpoints = [
    'api_version' => '1.0',
    'endpoints' => [
        [
            'path' => '/redirect.php',
            'method' => 'GET',
            'description' => 'IP to Country lookup service for language/region redirects',
            'parameters' => [
                'ipAddress' => 'IP address to lookup (required)'
            ],
            'example' => '/redirect.php?ipAddress=8.8.8.8'
        ],
        [
            'path' => '/send.php',
            'method' => 'POST',
            'description' => 'Contact form submission endpoint'
        ]
    ],
    'status' => 'healthy'
];

echo json_encode($endpoints, JSON_PRETTY_PRINT);
?>
