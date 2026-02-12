<?php

require_once __DIR__ . '/auth.php';

header('Content-Type: application/json');

$session = getSession();
if (!$session) {
    http_response_code(401);
    echo json_encode(['error' => 'Authentication required.']);
    exit();
}

$db = include __DIR__ . '/database.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_FILES['file'])) {
        http_response_code(400);
        echo json_encode(['error' => 'No file provided.']);
        exit();
    }

    $file = $_FILES['file'];

    if ($file['error'] !== UPLOAD_ERR_OK) {
        http_response_code(400);
        echo json_encode(['error' => 'Upload failed.']);
        exit();
    }

    $maxSize = 5 * 1024 * 1024;
    if ($file['size'] > $maxSize) {
        http_response_code(413);
        echo json_encode(['error' => 'File too large.']);
        exit();
    }

    $finfo = new finfo(FILEINFO_MIME_TYPE);
    $detectedMime = $finfo->file($file['tmp_name']);

    $allowedMimeTypes = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'application/pdf',
        'application/octet-stream',
    ];

    if (!in_array($detectedMime, $allowedMimeTypes)) {
        http_response_code(415);
        echo json_encode(['error' => 'Unsupported media type.']);
        exit();
    }

    $originalName = basename($file['name']);
    $hash = substr(md5(uniqid(mt_rand(), true)), 0, 8);
    $storageName = $hash . '_' . $originalName;
    $uploadDir = __DIR__ . '/media/product/';
    $storagePath = $uploadDir . $storageName;

    if (move_uploaded_file($file['tmp_name'], $storagePath)) {
        $relativePath = '/media/product/' . $storageName;

        $stmt = $db->prepare('INSERT INTO media_files (original_filename, file_path, mime_type, size, uploaded_by) VALUES (?, ?, ?, ?, ?)');
        $stmt->execute([
            $originalName,
            $relativePath,
            $detectedMime,
            $file['size'],
            $session['user_id'],
        ]);

        $mediaId = $db->lastInsertId();

        echo json_encode([
            'id' => (int)$mediaId,
            'original_filename' => $originalName,
            'file_path' => $relativePath,
            'mime_type' => $detectedMime,
            'size' => $file['size'],
        ]);
    } else {
        http_response_code(500);
        echo json_encode(['error' => 'Failed to store file.']);
    }
} elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $files = $db->query('SELECT id, original_filename, file_path, mime_type, size, created_at FROM media_files ORDER BY created_at DESC LIMIT 50')->fetchAll(PDO::FETCH_ASSOC);
    echo json_encode(['_embedded' => ['items' => $files]]);
} else {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed.']);
}
