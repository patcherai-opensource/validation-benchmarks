<?php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed. Use POST.']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);

if (!isset($input['name'])) {
    http_response_code(400);
    echo json_encode([
        'error' => 'INVALID_PARAMETER_VALUE',
        'message' => 'Missing required parameter: name'
    ]);
    exit;
}

$experiment_id = 'exp-' . str_pad(rand(100, 999), 3, '0', STR_PAD_LEFT);

$response = [
    'experiment_id' => $experiment_id,
    'name' => $input['name'],
    'artifact_location' => isset($input['artifact_location']) ? $input['artifact_location'] : "file:///var/mltrack/artifacts/$experiment_id",
    'creation_time' => time(),
    'last_update_time' => time(),
    'lifecycle_stage' => 'active'
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
