<?php
/**
 * MLflow Runs Create API
 * POST /api/runs/create
 */

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data || !isset($data['experiment_id'])) {
    http_response_code(400);
    echo json_encode(['error' => 'experiment_id is required']);
    exit;
}

$run_id = bin2hex(random_bytes(16));
$run_name = isset($data['run_name']) ? $data['run_name'] : 'run-' . substr($run_id, 0, 8);

echo json_encode([
    'run' => [
        'info' => [
            'run_id' => $run_id,
            'run_name' => $run_name,
            'experiment_id' => $data['experiment_id'],
            'status' => 'RUNNING',
            'start_time' => time() * 1000,
            'artifact_uri' => 'file:///tmp/mlruns/artifacts/' . $run_id
        ]
    ]
]);
