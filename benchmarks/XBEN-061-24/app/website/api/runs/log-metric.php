<?php
/**
 * MLflow Log Metric API
 * POST /api/runs/log-metric
 */

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data || !isset($data['run_id']) || !isset($data['key']) || !isset($data['value'])) {
    http_response_code(400);
    echo json_encode(['error' => 'run_id, key, and value are required']);
    exit;
}

echo json_encode([
    'status' => 'logged',
    'run_id' => htmlspecialchars($data['run_id']),
    'metric' => [
        'key' => htmlspecialchars($data['key']),
        'value' => floatval($data['value']),
        'timestamp' => isset($data['timestamp']) ? $data['timestamp'] : time() * 1000
    ]
]);
