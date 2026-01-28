<?php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

echo json_encode([
    'error' => 'Batch processing is not available in demo mode',
    'code' => 403,
    'upgrade_url' => 'https://predictml.io/enterprise'
]);
?>
