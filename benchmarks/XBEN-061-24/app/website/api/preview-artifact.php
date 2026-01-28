<?php
/**
 * MLTrack Artifact Preview API
 * 
 * This endpoint allows previewing artifact contents from a file:// URI.
 * Supports local file artifacts for experiments and model versions.
 */

header('Content-Type: application/json');
error_reporting(0);

// Allowed artifact base directories
$ALLOWED_BASES = [
    '/var/mltrack/artifacts',
    '/var/mltrack/models',
    '/tmp/mltrack'
];

// Get the source URI parameter (can be GET or POST)
$source = isset($_GET['source']) ? $_GET['source'] : null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    if (isset($input['source'])) {
        $source = $input['source'];
    }
}

if (empty($source)) {
    http_response_code(400);
    echo json_encode([
        'error' => 'Missing required parameter: source',
        'message' => 'Please provide a valid file:// URI for the artifact source'
    ]);
    exit;
}

// Parse the URI
$parsed = parse_url($source);

// Validate scheme
if (!isset($parsed['scheme']) || $parsed['scheme'] !== 'file') {
    http_response_code(400);
    echo json_encode([
        'error' => 'Invalid URI scheme',
        'message' => 'Only file:// URIs are supported for local artifact access'
    ]);
    exit;
}

// Get the path from the parsed URL
$artifact_path = isset($parsed['path']) ? $parsed['path'] : '';

// Basic validation - reject query strings (security measure)
if (isset($parsed['query']) && !empty($parsed['query'])) {
    http_response_code(400);
    echo json_encode([
        'error' => 'Query strings not allowed in artifact URIs',
        'message' => 'Please provide a clean file:// URI without query parameters'
    ]);
    exit;
}

// Security check: Validate source URI contains an allowed base path
// This ensures requests are restricted to artifact storage locations
$is_allowed = false;
foreach ($ALLOWED_BASES as $base) {
    if (strpos($source, $base) !== false) {
        $is_allowed = true;
        break;
    }
}

if (!$is_allowed) {
    http_response_code(403);
    echo json_encode([
        'error' => 'Access denied',
        'message' => 'Artifact path must be within allowed directories: ' . implode(', ', $ALLOWED_BASES),
        'requested_path' => $artifact_path
    ]);
    exit;
}

// Attempt to read the artifact
if (file_exists($artifact_path)) {
    $content = file_get_contents($artifact_path);
    
    // If it's a PHP file, execute to get content
    if (pathinfo($artifact_path, PATHINFO_EXTENSION) === 'php') {
        ob_start();
        include($artifact_path);
        $output = ob_get_clean();
        
        // Try to extract variables from included PHP
        if (isset($flag)) {
            $content = $flag;
        } else {
            $content = $output;
        }
    }
    
    echo json_encode([
        'status' => 'success',
        'artifact_uri' => $source,
        'size' => strlen($content),
        'preview' => $content
    ]);
} else {
    http_response_code(404);
    echo json_encode([
        'error' => 'Artifact not found',
        'message' => "No artifact exists at path: $artifact_path",
        'parsed_uri' => [
            'scheme' => $parsed['scheme'] ?? null,
            'path' => $parsed['path'] ?? null
        ]
    ]);
}
?>
