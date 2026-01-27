<?php
header('Content-Type: application/json');

// DataFlow ML Tracking Server - Model Version Creation API
// POST /api/model-versions/create
// Accepts JSON body with model version configuration

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
if (!isset($data['name']) || !isset($data['source'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing required fields: name, source']);
    exit;
}

$name = $data['name'];
$source = $data['source'];
$description = isset($data['description']) ? $data['description'] : '';

// Parse the source URI
$parsed = parse_url($source);

// VULNERABILITY: We validate certain parts but not fragment component
// This mirrors the MLflow CVE
if (isset($parsed['query'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Query parameters not allowed in source URI']);
    exit;
}

// Handle file:// URIs  
if (isset($parsed['scheme']) && $parsed['scheme'] === 'file') {
    $file_path = $parsed['path'];
    
    // The fragment (#...) is parsed separately and ignored in validation
    // but the file path itself is used directly
    
    if (file_exists($file_path)) {
        $content = file_get_contents($file_path);
        $version = rand(1, 100);
        echo json_encode([
            'name' => $name,
            'version' => $version,
            'source' => $source,
            'source_content' => $content,
            'description' => $description,
            'status' => 'READY'
        ]);
        exit;
    } else {
        http_response_code(404);
        echo json_encode(['error' => 'Source path does not exist: ' . $file_path]);
        exit;
    }
}

// Default response for other URI schemes
$version = rand(1, 100);
echo json_encode([
    'name' => $name,
    'version' => $version,
    'source' => $source,
    'description' => $description,
    'status' => 'PENDING_REGISTRATION'
]);
