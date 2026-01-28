<?php
header('Content-Type: application/json');

$run_id = isset($_GET['run_id']) ? $_GET['run_id'] : null;
$path = isset($_GET['path']) ? $_GET['path'] : '';

if (!$run_id) {
    http_response_code(400);
    echo json_encode([
        'error' => 'INVALID_PARAMETER_VALUE',
        'message' => 'Missing required parameter: run_id'
    ]);
    exit;
}

// Return mock artifact listing
$response = [
    'root_uri' => "file:///var/mltrack/artifacts/$run_id",
    'files' => [
        [
            'path' => 'model.pkl',
            'is_dir' => false,
            'file_size' => 15678432
        ],
        [
            'path' => 'metrics.json',
            'is_dir' => false,
            'file_size' => 1024
        ],
        [
            'path' => 'params.yaml',
            'is_dir' => false,
            'file_size' => 512
        ],
        [
            'path' => 'checkpoints',
            'is_dir' => true,
            'file_size' => null
        ]
    ]
];

echo json_encode($response, JSON_PRETTY_PRINT);
?>
