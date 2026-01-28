<?php
/**
 * MLflow Artifacts List API
 * GET /api/artifacts/list?run_id=X
 */

header('Content-Type: application/json');

$run_id = isset($_GET['run_id']) ? $_GET['run_id'] : null;

if (!$run_id) {
    http_response_code(400);
    echo json_encode(['error' => 'run_id parameter required']);
    exit;
}

// Simulated artifact listing
echo json_encode([
    'root_uri' => 'file:///tmp/mlruns/artifacts/' . htmlspecialchars($run_id),
    'files' => [
        ['path' => 'model.pkl', 'is_dir' => false, 'file_size' => 15234],
        ['path' => 'metrics', 'is_dir' => true],
        ['path' => 'requirements.txt', 'is_dir' => false, 'file_size' => 128]
    ]
]);
