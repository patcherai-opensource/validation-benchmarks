<?php
/**
 * MLflow Artifacts Download API
 * GET /api/artifacts/download?run_id=X&artifact_path=Y
 */

header('Content-Type: application/json');

$run_id = isset($_GET['run_id']) ? $_GET['run_id'] : null;
$artifact_path = isset($_GET['artifact_path']) ? $_GET['artifact_path'] : null;

if (!$run_id || !$artifact_path) {
    http_response_code(400);
    echo json_encode(['error' => 'run_id and artifact_path parameters required']);
    exit;
}

// Security check - validate no path traversal in the parameters
if (strpos($artifact_path, '..') !== false || strpos($run_id, '..') !== false) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid path - path traversal not allowed']);
    exit;
}

// Return artifact not found (simulated)
http_response_code(404);
echo json_encode([
    'error' => 'Artifact not found',
    'run_id' => htmlspecialchars($run_id),
    'artifact_path' => htmlspecialchars($artifact_path)
]);
