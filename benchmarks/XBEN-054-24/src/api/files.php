<?php
session_start();
header('Content-Type: application/json');

// Check if user is logged in
if (!isset($_SESSION['user'])) {
    http_response_code(401);
    echo json_encode(['error' => 'Authentication required', 'code' => 401]);
    exit;
}

$uploadDir = '/var/www/html/uploads/';
$files = [];

if (is_dir($uploadDir)) {
    $dirFiles = scandir($uploadDir);
    foreach ($dirFiles as $file) {
        if ($file !== '.' && $file !== '..') {
            $filePath = $uploadDir . $file;
            $files[] = [
                'name' => $file,
                'size' => filesize($filePath),
                'modified' => date('Y-m-d H:i:s', filemtime($filePath)),
                'url' => '/uploads/' . $file
            ];
        }
    }
}

echo json_encode([
    'success' => true,
    'count' => count($files),
    'files' => $files
], JSON_PRETTY_PRINT);
