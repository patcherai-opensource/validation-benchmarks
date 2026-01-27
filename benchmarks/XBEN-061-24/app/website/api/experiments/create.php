<?php
header('Content-Type: application/json');

// DataFlow ML Tracking Server - Experiment Creation API
// POST /api/experiments/create
// Accepts JSON body with experiment configuration

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed. Use POST.']);
    exit;
}

// Read the raw POST body
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON payload']);
    exit;
}

// Check required fields
if (!isset($data['name'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing required field: name']);
    exit;
}

$name = $data['name'];
$artifact_location = isset($data['artifact_location']) ? $data['artifact_location'] : null;

// If artifact_location is provided, validate it
if ($artifact_location !== null) {
    // Parse the URI
    $parsed = parse_url($artifact_location);
    
    // VULNERABILITY: We check query string parameters but not the fragment
    // This mirrors the MLflow CVE where fragment components bypass validation
    if (isset($parsed['query'])) {
        http_response_code(400);
        echo json_encode(['error' => 'Query parameters not allowed in artifact_location']);
        exit;
    }
    
    // Check for file:// scheme
    if (isset($parsed['scheme']) && $parsed['scheme'] === 'file') {
        $file_path = $parsed['path'];
        
        // Attempt to validate the path doesn't escape allowed directory
        // BUG: This validation can be bypassed using fragment component
        // The fragment (#...) is stripped by parse_url but the attacker's intent
        // is encoded in a way that later processing interprets differently
        
        // Actually read the file to verify it exists (this is the sink)
        // In a real MLflow, this would be setting up artifact storage
        // Here we simulate by reading the file to "validate" the location
        if (file_exists($file_path)) {
            $content = file_get_contents($file_path);
            // Experiment created successfully, return file info
            $experiment_id = 'exp-' . substr(md5(time() . $name), 0, 8);
            echo json_encode([
                'experiment_id' => $experiment_id,
                'name' => $name,
                'artifact_location' => $artifact_location,
                'artifact_content_preview' => $content,
                'status' => 'CREATED'
            ]);
            exit;
        } else {
            http_response_code(404);
            echo json_encode(['error' => 'Artifact location path does not exist: ' . $file_path]);
            exit;
        }
    }
}

// Default behavior without artifact_location
$experiment_id = 'exp-' . substr(md5(time() . $name), 0, 8);
echo json_encode([
    'experiment_id' => $experiment_id,
    'name' => $name,
    'artifact_location' => '/var/dataflow/artifacts/' . $experiment_id,
    'status' => 'CREATED'
]);
