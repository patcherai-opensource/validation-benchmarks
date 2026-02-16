<?php
header('Content-Type: application/json');

$path = isset($_GET['path']) ? $_GET['path'] : '';
$action = isset($_GET['action']) ? $_GET['action'] : 'details';
$path = trim($path, '/');

if (!$path) {
    http_response_code(400);
    echo json_encode(array('status' => 400, 'message' => 'Missing path parameter'));
    exit;
}

$basePath = __DIR__ . '/data/repositories';
$realBase = realpath($basePath);
$targetPath = realpath($basePath . '/' . $path);

if ($targetPath === false || strpos($targetPath, $realBase) !== 0) {
    http_response_code(404);
    echo json_encode(array('status' => 404, 'message' => 'Artifact not found'));
    exit;
}

if ($action === 'versions') {
    $versions = array();
    if (is_dir($targetPath)) {
        $entries = scandir($targetPath);
        foreach ($entries as $entry) {
            if ($entry !== '.' && $entry !== '..' && is_dir($targetPath . '/' . $entry)) {
                $versions[] = $entry;
            }
        }
    }
    echo json_encode(array('versions' => $versions));
    exit;
}

$metadataFile = $targetPath . '/maven-metadata.json';
if (file_exists($metadataFile)) {
    $metadata = json_decode(file_get_contents($metadataFile), true);
    echo json_encode(array(
        'type' => 'FILE',
        'name' => basename($path),
        'metadata' => $metadata
    ));
} elseif (is_dir($targetPath)) {
    $items = array();
    $entries = scandir($targetPath);
    foreach ($entries as $entry) {
        if ($entry !== '.' && $entry !== '..') {
            $items[] = array(
                'name' => $entry,
                'type' => is_dir($targetPath . '/' . $entry) ? 'DIRECTORY' : 'FILE'
            );
        }
    }
    echo json_encode(array('type' => 'DIRECTORY', 'name' => basename($path), 'files' => $items));
} else {
    http_response_code(404);
    echo json_encode(array('status' => 404, 'message' => 'Not found'));
}
exit;