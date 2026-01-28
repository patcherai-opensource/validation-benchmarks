<?php
header('Content-Type: application/json');

$response = [
    'name' => 'DataLabel Studio API',
    'version' => '2.4.1',
    'endpoints' => [
        '/api/v1/projects' => 'List all projects',
        '/api/v1/projects/{id}' => 'Get project details',
        '/api/v1/projects/{id}/tasks' => 'List tasks in project',
        '/api/v1/projects/{id}/export' => 'Export annotations',
        '/api/v1/users/me' => 'Current user info',
        '/api/v1/health' => 'Health check'
    ],
    'documentation' => '/api/docs.php'
];

echo json_encode($response, JSON_PRETTY_PRINT);
