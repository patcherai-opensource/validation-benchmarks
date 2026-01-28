<?php
header('Content-Type: application/json');

$response = [
    'name' => 'ezPortal CMS API',
    'version' => '4.2.1',
    'endpoints' => [
        '/api/status' => 'System status',
        '/api/users' => 'User enumeration (requires auth)',
        '/api/articles' => 'Article listing'
    ]
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
