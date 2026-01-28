<?php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed. Use POST.']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);

if (!isset($input['name']) || !isset($input['source'])) {
    http_response_code(400);
    echo json_encode([
        'error' => 'INVALID_PARAMETER_VALUE',
        'message' => 'Missing required parameters: name, source'
    ]);
    exit;
}

// Parse the source URI
$parsed = parse_url($input['source']);

// Validate scheme
if (!isset($parsed['scheme']) || $parsed['scheme'] !== 'file') {
    http_response_code(400);
    echo json_encode([
        'error' => 'INVALID_PARAMETER_VALUE',
        'message' => 'Source must be a valid file:// URI'
    ]);
    exit;
}

$response = [
    'model_version' => [
        'name' => $input['name'],
        'version' => '1',
        'creation_timestamp' => time() * 1000,
        'last_updated_timestamp' => time() * 1000,
        'current_stage' => 'None',
        'source' => $input['source'],
        'status' => 'READY'
    ]
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
