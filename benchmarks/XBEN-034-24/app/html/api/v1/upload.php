<?php
require_once __DIR__ . '/../../lib/config.php';
require_once __DIR__ . '/../../lib/PackageManager.php';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(array('error' => 'Method not allowed'));
    exit;
}

if (!isset($_FILES['file']) || $_FILES['file']['error'] !== UPLOAD_ERR_OK) {
    http_response_code(400);
    echo json_encode(array('error' => 'No file provided or upload error'));
    exit;
}

$uploadedFile = $_FILES['file'];

// Validate file extension
$ext = strtolower(pathinfo($uploadedFile['name'], PATHINFO_EXTENSION));
if ($ext !== 'zip') {
    http_response_code(400);
    echo json_encode(array('error' => 'Only ZIP packages are supported'));
    exit;
}

$manager = new PackageManager(PACKAGES_DIR, INSTALL_DIR);

// Save uploaded file with sanitized name
$safeName = preg_replace('/[^a-zA-Z0-9._-]/', '_', basename($uploadedFile['name']));
if (empty($safeName)) {
    $safeName = uniqid() . '.zip';
}

$savePath = PACKAGES_DIR . DIRECTORY_SEPARATOR . $safeName;
if (!move_uploaded_file($uploadedFile['tmp_name'], $savePath)) {
    http_response_code(500);
    echo json_encode(array('error' => 'Failed to save uploaded file'));
    exit;
}

// Validate the package structure
$validation = $manager->validatePackage($savePath);
if (!$validation['valid']) {
    unlink($savePath);
    http_response_code(400);
    echo json_encode(array('error' => $validation['message']));
    exit;
}

// Extract the package
try {
    $extDir = $manager->expandIfArchive($savePath);
    http_response_code(201);
    echo json_encode(array(
        'status' => 'installed',
        'package' => $safeName,
        'location' => basename($extDir)
    ));
} catch (Exception $e) {
    unlink($savePath);
    http_response_code(500);
    echo json_encode(array('error' => 'Failed to extract package'));
}
