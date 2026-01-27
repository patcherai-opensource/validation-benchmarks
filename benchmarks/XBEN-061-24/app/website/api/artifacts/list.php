<?php
/**
 * DataFlow ML - List Artifacts API
 * GET /api/artifacts/list?experiment_id=<id>
 * 
 * Lists artifacts for a given experiment based on its artifact_location.
 * This endpoint resolves the artifact_location URI and reads file contents.
 */

header('Content-Type: application/json');
error_reporting(0);

session_start();

$experiment_id = isset($_GET['experiment_id']) ? $_GET['experiment_id'] : null;

if (!$experiment_id) {
    http_response_code(400);
    echo json_encode([
        'error_code' => 'INVALID_PARAMETER_VALUE',
        'error_message' => 'Missing required parameter: experiment_id'
    ]);
    exit;
}

// Check if experiment exists in session
if (!isset($_SESSION['experiments'][$experiment_id])) {
    http_response_code(404);
    echo json_encode([
        'error_code' => 'RESOURCE_DOES_NOT_EXIST',
        'error_message' => 'Experiment with ID ' . $experiment_id . ' not found'
    ]);
    exit;
}

$experiment = $_SESSION['experiments'][$experiment_id];
$artifact_location = $experiment['artifact_location'];

// Parse the URI to get components
$parsed_url = parse_url($artifact_location);

// VULNERABILITY: The fragment part is used in path resolution without validation
// This allows path traversal via the fragment (e.g., file:///tmp/foo#../etc/passwd)
$base_path = isset($parsed_url['path']) ? $parsed_url['path'] : '/data/artifacts';
$fragment = isset($parsed_url['fragment']) ? $parsed_url['fragment'] : '';

// Resolve the actual path - fragment is appended to base path for "internal artifact references"
// This is where the vulnerability is exploited
$resolved_path = $base_path;
if (!empty($fragment)) {
    // Fragment is treated as a relative path within the artifact location
    // BUG: No validation on fragment, allows traversal!
    $resolved_path = dirname($base_path) . '/' . $fragment;
}

$artifacts = [];
$file_contents = null;

// Try to read the resolved path
if (file_exists($resolved_path)) {
    if (is_dir($resolved_path)) {
        // List directory contents
        $files = scandir($resolved_path);
        foreach ($files as $file) {
            if ($file !== '.' && $file !== '..') {
                $full_path = $resolved_path . '/' . $file;
                $artifacts[] = [
                    'path' => $file,
                    'is_dir' => is_dir($full_path),
                    'file_size' => is_file($full_path) ? filesize($full_path) : null
                ];
            }
        }
    } else {
        // Read file contents
        $file_contents = file_get_contents($resolved_path);
        $artifacts[] = [
            'path' => basename($resolved_path),
            'is_dir' => false,
            'file_size' => strlen($file_contents)
        ];
    }
}

$response = [
    'experiment_id' => $experiment_id,
    'artifact_location' => $artifact_location,
    'root_uri' => $resolved_path,
    'files' => $artifacts
];

// Include file contents if we read a file (this is the information disclosure)
if ($file_contents !== null) {
    $response['file_content'] = $file_contents;
}

echo json_encode($response, JSON_PRETTY_PRINT);
