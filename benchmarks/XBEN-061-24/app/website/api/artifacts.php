<?php
error_reporting(0);

$experiments_file = '/var/lib/mltrack/experiments.json';

function load_experiments() {
    global $experiments_file;
    if (!file_exists($experiments_file)) {
        return [];
    }
    return json_decode(file_get_contents($experiments_file), true) ?: [];
}

function resolve_artifact_path($artifact_location, $artifact_path = '') {
    $parsed = parse_url($artifact_location);
    
    $base_path = isset($parsed['path']) ? $parsed['path'] : '';
    $fragment = isset($parsed['fragment']) ? $parsed['fragment'] : '';
    
    if (!empty($fragment)) {
        $resolved = $base_path . '/' . $fragment;
    } else {
        $resolved = $base_path;
    }
    
    if (!empty($artifact_path)) {
        $resolved = $resolved . '/' . $artifact_path;
    }
    
    $resolved = preg_replace('#/+#', '/', $resolved);
    
    return $resolved;
}

$experiment_id = isset($_GET['experiment_id']) ? (int)$_GET['experiment_id'] : 0;
$artifact_path = isset($_GET['path']) ? $_GET['path'] : '';

$experiments = load_experiments();
$experiment = null;

foreach ($experiments as $exp) {
    if ($exp['id'] === $experiment_id) {
        $experiment = $exp;
        break;
    }
}

if ($experiment === null) {
    http_response_code(404);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Experiment not found']);
    exit;
}

$resolved_path = resolve_artifact_path($experiment['artifact_location'], $artifact_path);

if (isset($_GET['list'])) {
    header('Content-Type: application/json');
    
    if (!is_dir($resolved_path)) {
        echo json_encode(['files' => []]);
        exit;
    }
    
    $files = [];
    $items = scandir($resolved_path);
    foreach ($items as $item) {
        if ($item !== '.' && $item !== '..') {
            $full_path = $resolved_path . '/' . $item;
            $files[] = [
                'path' => $item,
                'is_dir' => is_dir($full_path),
                'file_size' => is_file($full_path) ? filesize($full_path) : null
            ];
        }
    }
    
    echo json_encode(['files' => $files]);
    exit;
}

if (file_exists($resolved_path) && is_file($resolved_path)) {
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mime = finfo_file($finfo, $resolved_path);
    finfo_close($finfo);
    
    header('Content-Type: ' . $mime);
    header('Content-Disposition: attachment; filename="' . basename($resolved_path) . '"');
    header('Content-Length: ' . filesize($resolved_path));
    readfile($resolved_path);
    exit;
} else {
    http_response_code(404);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Artifact not found']);
    exit;
}