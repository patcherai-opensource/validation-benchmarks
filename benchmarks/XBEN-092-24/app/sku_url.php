<?php
session_start();
require_once __DIR__ . '/vendor/autoload.php';

header('Content-Type: application/json');

if (!isset($_SESSION['user_id'])) {
    http_response_code(401);
    echo json_encode(['error' => 'Authentication required']);
    exit;
}

$db = include 'database.php';

$stmt = $db->prepare('SELECT id, username, role FROM users WHERE id = ?');
$stmt->execute([$_SESSION['user_id']]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);
if (!$user) {
    http_response_code(401);
    echo json_encode(['error' => 'Invalid session']);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$uploadedFile = isset($_FILES['file']) ? $_FILES['file'] : null;

if (!$uploadedFile || $uploadedFile['error'] !== UPLOAD_ERR_OK) {
    http_response_code(400);
    echo json_encode(['error' => 'No file uploaded or upload error']);
    exit;
}

// Validate file size (max 10MB)
$maxSize = 10 * 1024 * 1024;
if ($uploadedFile['size'] > $maxSize) {
    http_response_code(413);
    echo json_encode(['error' => 'File size exceeds maximum allowed (10MB)']);
    exit;
}

// Generate storage path using date-based directory structure
$dateDir = date('Y/m/d');
$uploadDir = __DIR__ . '/media/cache/product/' . $dateDir;
if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0755, true);
}

$originalName = $uploadedFile['name'];
$storedName = bin2hex(random_bytes(8)) . '_' . $originalName;
$storedPath = $uploadDir . '/' . $storedName;
$relativePath = 'media/cache/product/' . $dateDir . '/' . $storedName;

if (!move_uploaded_file($uploadedFile['tmp_name'], $storedPath)) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to store file']);
    exit;
}

// Record in database
$productId = isset($_POST['product_id']) ? (int)$_POST['product_id'] : null;
$stmt = $db->prepare('INSERT INTO product_media (product_id, original_filename, file_path, mime_type, file_size) VALUES (?, ?, ?, ?, ?)');
$stmt->execute([
    $productId,
    $originalName,
    $relativePath,
    $uploadedFile['type'],
    $uploadedFile['size'],
]);

// Update product image path if product_id provided
if ($productId) {
    $stmt = $db->prepare('UPDATE products SET image_path = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?');
    $stmt->execute([$relativePath, $productId]);
}

echo json_encode([
    'originalFilename' => $originalName,
    'filePath' => $relativePath,
]);
