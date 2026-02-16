<?php
/**
 * System Status API
 */

header('Content-Type: application/json');

echo json_encode([
    'status' => 'healthy',
    'version' => '10.5.18',
    'endpoints' => [
        '/api/v1/status.php' => 'System health and version information',
        '/api/v1/list.php' => 'List registered resource identifiers',
        '/api/v1/resolve.php' => 'Resolve a resource identifier to its content reference',
        '/api/v1/settings.php' => 'Retrieve public system configuration'
    ]
]);
