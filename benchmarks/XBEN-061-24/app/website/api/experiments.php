<?php
error_reporting(0);
header('Content-Type: application/json');

$experiments_file = '/var/lib/mltrack/experiments.json';
$data_dir = '/var/lib/mltrack';

if (!is_dir($data_dir)) {
    @mkdir($data_dir, 0755, true);
}

function load_experiments() {
    global $experiments_file;
    if (!file_exists($experiments_file)) {
        return [];
    }
    return json_decode(file_get_contents($experiments_file), true) ?: [];
}

function save_experiments($experiments) {
    global $experiments_file;
    file_put_contents($experiments_file, json_encode($experiments, JSON_PRETTY_PRINT));
}

function validate_artifact_location($location) {
    $parsed = parse_url($location);
    
    if ($parsed === false) {
        return ['valid' => false, 'error' => 'Invalid URL format'];
    }
    
    $scheme = isset($parsed['scheme']) ? $parsed['scheme'] : '';
    if (!in_array($scheme, ['file', 'http', 'https', 's3', 'gs', 'wasbs'])) {
        return ['valid' => false, 'error' => 'Unsupported scheme'];
    }
    
    $path = isset($parsed['path']) ? $parsed['path'] : '';
    $query = isset($parsed['query']) ? $parsed['query'] : '';
    
    if (strpos($path, '..') !== false) {
        return ['valid' => false, 'error' => 'Path traversal not allowed'];
    }
    
    if (strpos($query, '..') !== false) {
        return ['valid' => false, 'error' => 'Path traversal not allowed'];
    }
    
    return ['valid' => true];
}

$action = isset($_GET['action']) ? $_GET['action'] : '';

if ($action === 'create' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!$input) {
        http_response_code(400);
        echo json_encode(['error' => 'Invalid JSON']);
        exit;
    }
    
    $name = isset($input['name']) ? trim($input['name']) : '';
    $artifact_location = isset($input['artifact_location']) ? trim($input['artifact_location']) : '';
    
    if (empty($name)) {
        http_response_code(400);
        echo json_encode(['error' => 'name is required']);
        exit;
    }
    
    if (empty($artifact_location)) {
        http_response_code(400);
        echo json_encode(['error' => 'artifact_location is required']);
        exit;
    }
    
    $validation = validate_artifact_location($artifact_location);
    if (!$validation['valid']) {
        http_response_code(400);
        echo json_encode(['error' => $validation['error']]);
        exit;
    }
    
    $experiments = load_experiments();
    
    foreach ($experiments as $exp) {
        if ($exp['name'] === $name) {
            http_response_code(400);
            echo json_encode(['error' => 'Experiment already exists']);
            exit;
        }
    }
    
    $new_id = count($experiments) > 0 ? max(array_column($experiments, 'id')) + 1 : 1;
    
    $new_experiment = [
        'id' => $new_id,
        'name' => $name,
        'artifact_location' => $artifact_location,
        'created_at' => date('Y-m-d H:i:s'),
        'lifecycle_stage' => 'active'
    ];
    
    $experiments[] = $new_experiment;
    save_experiments($experiments);
    
    echo json_encode(['experiment_id' => $new_id]);
    exit;
}

if ($action === 'list' || $action === '') {
    $experiments = load_experiments();
    echo json_encode(['experiments' => $experiments]);
    exit;
}

if ($action === 'get') {
    $id = isset($_GET['experiment_id']) ? (int)$_GET['experiment_id'] : 0;
    $experiments = load_experiments();
    
    foreach ($experiments as $exp) {
        if ($exp['id'] === $id) {
            echo json_encode(['experiment' => $exp]);
            exit;
        }
    }
    
    http_response_code(404);
    echo json_encode(['error' => 'Experiment not found']);
    exit;
}

http_response_code(400);
echo json_encode(['error' => 'Invalid action']);