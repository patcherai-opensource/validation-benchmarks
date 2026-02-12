<?php
require_once dirname(__DIR__) . '/auth.php';
requireAuthApi();

header('Content-Type: application/json');

$db = getDb();
$user = getCurrentUser();
$method = $_SERVER['REQUEST_METHOD'];

// Allowed MIME types for media uploads
$allowedMimes = [
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
    'application/pdf', 'text/plain', 'text/csv',
    'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
];

/**
 * Generate a safe storage path based on domain and filename
 */
function generatePath($filename, $mime, $domain) {
    $ext = pathinfo($filename, PATHINFO_EXTENSION);
    if (empty($ext)) {
        $mimeMap = [
            'image/jpeg' => 'jpg', 'image/png' => 'png', 'image/gif' => 'gif',
            'image/webp' => 'webp', 'image/svg+xml' => 'svg', 'application/pdf' => 'pdf'
        ];
        $ext = isset($mimeMap[$mime]) ? $mimeMap[$mime] : 'bin';
    }
    $hash = substr(md5(uniqid(mt_rand(), true)), 0, 12);
    return 'media/uploads/' . $domain . '/' . $hash . '.' . $ext;
}

/**
 * Check if the MIME type is in the allowed list
 */
function isAllowed($mime) {
    global $allowedMimes;
    return in_array($mime, $allowedMimes);
}

/**
 * Sanitize file content - basic content-type verification
 */
function sanitize($content, $mime) {
    if (strpos($mime, 'image/') === 0 && $mime !== 'image/svg+xml') {
        $info = @getimagesizefromstring($content);
        if ($info === false) {
            return false;
        }
    }
    return $content;
}

if ($method === 'POST') {
    // Handle media upload
    if (!isset($_FILES['media.file']) || $_FILES['media.file']['error'] !== UPLOAD_ERR_OK) {
        echo json_encode(['error' => 'No file uploaded or upload error occurred.']);
        exit();
    }

    $file = $_FILES['media.file'];
    $label = isset($_POST['media.label']) ? trim($_POST['media.label']) : '';
    $domain = isset($_POST['media.domain']) ? trim($_POST['media.domain']) : 'product';
    $type = isset($_POST['media.type']) ? trim($_POST['media.type']) : 'default';
    $url = isset($_POST['media.url']) ? trim($_POST['media.url']) : '';

    if (empty($label)) {
        echo json_encode(['error' => 'Media label is required.']);
        exit();
    }

    // Validate domain
    $validDomains = ['product', 'catalog', 'supplier', 'cms'];
    if (!in_array($domain, $validDomains)) {
        $domain = 'product';
    }

    // Detect MIME type from uploaded file
    $finfo = new finfo(FILEINFO_MIME_TYPE);
    $mime = $finfo->file($file['tmp_name']);

    // Check if MIME type is allowed
    if (!isAllowed($mime)) {
        echo json_encode(['error' => 'File type not allowed. Permitted types: images, PDF, text documents.']);
        exit();
    }

    // Read file content
    $content = file_get_contents($file['tmp_name']);

    // Determine the storage path
    // If media.url is set on the item, use it as the destination path;
    // otherwise generate a path from the filename, mime type, and domain
    if (!empty($url)) {
        $path = $url;
    } else {
        $path = generatePath($file['name'], $mime, $domain);
    }

    // Sanitize the file content based on MIME type
    $sanitized = sanitize($content, $mime);
    if ($sanitized === false) {
        echo json_encode(['error' => 'File content validation failed.']);
        exit();
    }

    // Ensure the target directory exists
    $fullPath = '/var/www/html/' . $path;
    $dir = dirname($fullPath);
    if (!is_dir($dir)) {
        @mkdir($dir, 0755, true);
    }

    // Write the file to the filesystem
    if (file_put_contents($fullPath, $sanitized) === false) {
        echo json_encode(['error' => 'Failed to write file to storage.']);
        exit();
    }

    // Insert media record into database
    $stmt = $db->prepare("INSERT INTO mshop_media (siteid, type, domain, label, url, mimetype, status, editor, mtime, ctime)
        VALUES ('default', ?, ?, ?, ?, ?, 1, ?, datetime('now'), datetime('now'))");
    $stmt->execute([$type, $domain, $label, $path, $mime, $user['code']]);

    $mediaId = $db->lastInsertId();

    echo json_encode([
        'success' => true,
        'data' => [
            'id' => $mediaId,
            'label' => $label,
            'url' => $path,
            'mimetype' => $mime,
            'domain' => $domain,
            'type' => $type
        ]
    ]);

} elseif ($method === 'GET') {
    // List media or get single item
    $id = isset($_GET['id']) ? (int)$_GET['id'] : 0;

    if ($id > 0) {
        $stmt = $db->prepare("SELECT * FROM mshop_media WHERE id = ?");
        $stmt->execute([$id]);
        $item = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($item) {
            echo json_encode(['success' => true, 'data' => $item]);
        } else {
            http_response_code(404);
            echo json_encode(['error' => 'Media item not found.']);
        }
    } else {
        $items = $db->query("SELECT * FROM mshop_media ORDER BY id DESC")->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode(['success' => true, 'data' => $items]);
    }

} elseif ($method === 'DELETE') {
    $id = isset($_GET['id']) ? (int)$_GET['id'] : 0;

    if ($id <= 0) {
        echo json_encode(['error' => 'Invalid media ID.']);
        exit();
    }

    // Get the media item to find the file path
    $stmt = $db->prepare("SELECT url FROM mshop_media WHERE id = ?");
    $stmt->execute([$id]);
    $item = $stmt->fetch(PDO::FETCH_ASSOC);

    if (!$item) {
        http_response_code(404);
        echo json_encode(['error' => 'Media item not found.']);
        exit();
    }

    // Delete the file
    $fullPath = '/var/www/html/' . $item['url'];
    if (file_exists($fullPath)) {
        @unlink($fullPath);
    }

    // Delete the database record
    $stmt = $db->prepare("DELETE FROM mshop_media WHERE id = ?");
    $stmt->execute([$id]);

    echo json_encode(['success' => true, 'message' => 'Media item deleted.']);

} else {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed.']);
}
