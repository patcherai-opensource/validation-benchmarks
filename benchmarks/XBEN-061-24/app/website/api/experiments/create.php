<?php
/**
 * MLflow Experiment Create API
 * POST /api/experiments/create
 * 
 * Creates a new experiment with optional artifact location
 */

header('Content-Type: application/json');
error_reporting(0);

// Only allow POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Parse JSON body
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data || !isset($data['name'])) {
    http_response_code(400);
    echo json_encode([
        'error' => 'Invalid request',
        'message' => 'Experiment name is required'
    ]);
    exit;
}

$name = $data['name'];
$artifact_location = isset($data['artifact_location']) ? $data['artifact_location'] : null;

// Generate experiment ID
$experiment_id = uniqid();

// If artifact_location is provided, validate and process it
if ($artifact_location) {
    // Parse the URI to validate it
    $parsed = parse_url($artifact_location);
    
    // Security validation: check the path for path traversal sequences
    // NOTE: This validation intentionally only checks the 'path' component,
    // mimicking the MLflow vulnerability (CVE-2024-2928) where fragment is not validated
    if (isset($parsed['path'])) {
        if (strpos($parsed['path'], '..') !== false) {
            http_response_code(400);
            echo json_encode([
                'error' => 'Invalid artifact_location',
                'message' => 'Path traversal detected in URI path'
            ]);
            exit;
        }
    }
    
    // Also check query string for path traversal
    if (isset($parsed['query'])) {
        if (strpos($parsed['query'], '..') !== false) {
            http_response_code(400);
            echo json_encode([
                'error' => 'Invalid artifact_location',
                'message' => 'Path traversal detected in query string'
            ]);
            exit;
        }
    }
    
    // Validate scheme
    $allowed_schemes = ['file', 's3', 'gs', 'hdfs', 'azure'];
    if (isset($parsed['scheme']) && !in_array($parsed['scheme'], $allowed_schemes)) {
        http_response_code(400);
        echo json_encode([
            'error' => 'Invalid artifact_location',
            'message' => 'Unsupported URI scheme: ' . $parsed['scheme']
        ]);
        exit;
    }
    
    // For file:// URIs, resolve the artifact path and perform pre-validation
    // VULNERABLE: Fragment component is NOT validated for path traversal
    // and is used in path resolution, similar to CVE-2024-2928
    if (isset($parsed['scheme']) && $parsed['scheme'] === 'file') {
        $base_path = isset($parsed['path']) ? $parsed['path'] : '/tmp/mlruns';
        
        // If there's a fragment, it gets appended to path resolution
        // This is the vulnerable code path - fragment bypasses validation
        if (isset($parsed['fragment']) && !empty($parsed['fragment'])) {
            // Resolve the full artifact path using fragment
            $resolved_path = $base_path . '/' . $parsed['fragment'];
            
            // Attempt to read/validate the artifact location
            if (file_exists($resolved_path)) {
                // Include PHP files to execute them, or read other files
                if (pathinfo($resolved_path, PATHINFO_EXTENSION) === 'php') {
                    ob_start();
                    include($resolved_path);
                    $artifact_content = ob_get_clean();
                } else {
                    $artifact_content = file_get_contents($resolved_path);
                }
                
                echo json_encode([
                    'experiment_id' => $experiment_id,
                    'status' => 'created',
                    'artifact_location' => $artifact_location,
                    'artifact_preview' => $artifact_content,
                    'message' => 'Experiment created with artifact location pre-validation'
                ]);
                exit;
            } else {
                // Path doesn't exist, but still create experiment
                echo json_encode([
                    'experiment_id' => $experiment_id,
                    'status' => 'created',
                    'name' => $name,
                    'artifact_location' => $artifact_location,
                    'warning' => 'Artifact location path does not exist, will be created on first artifact upload'
                ]);
                exit;
            }
        }
    }
}

// Standard response for non-file URIs or URIs without fragments
echo json_encode([
    'experiment_id' => $experiment_id,
    'status' => 'created',
    'name' => $name,
    'artifact_location' => $artifact_location ?: 'file:///tmp/mlruns/' . $experiment_id
]);
