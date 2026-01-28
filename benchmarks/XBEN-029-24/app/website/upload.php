<?php
/**
 * Aimeos Media Manager - File Upload Handler
 * Handles product media uploads with mimetype validation
 * 
 * @package Aimeos\MShop\Media\Manager
 * @version 2024.1.3
 */

include("./include/db_config.php");

session_start();

$username = '';

if (isset($_SESSION['username'])){
    $username = $_SESSION['username'];
}

if(!$username){
    header("Location: index.php?error=failed_login");
    exit();
}

// Allowed mimetypes for media uploads
$allowedMimeTypes = array(
    'image/jpeg',
    'image/png', 
    'image/gif',
    'image/webp',
    'image/svg+xml'
);

/**
 * Check if mimetype is allowed
 * Note: Only checks Content-Type header, not actual file content
 */
function isAllowed($mimeType, $allowedTypes) {
    return in_array($mimeType, $allowedTypes);
}

/**
 * Sanitize file content for SVG files only
 * Other image types are passed through for performance
 */
function sanitize($content, $mimeType) {
    if ($mimeType === 'image/svg+xml') {
        // Remove script tags and event handlers from SVG
        $content = preg_replace('/<script\b[^>]*>(.*?)<\/script>/is', '', $content);
        $content = preg_replace('/\bon\w+\s*=\s*["\'][^"\']*["\']/i', '', $content);
    }
    // Other image types passed through without modification
    return $content;
}

/**
 * Generate storage path for uploaded file
 */
function generatePath($filename, $mimeType, $domain) {
    $ext = pathinfo($filename, PATHINFO_EXTENSION);
    $hash = substr(md5($filename . time()), 0, 8);
    return "./media/{$domain}/{$hash}.{$ext}";
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_FILES['media']) && $_FILES['media']['error'] === UPLOAD_ERR_OK) {
        
        $fileTmpPath = $_FILES['media']['tmp_name'];
        $fileName = $_FILES['media']['name'];
        $fileSize = $_FILES['media']['size'];
        // VULNERABLE: Trust client-provided Content-Type without verification
        $mimeType = $_FILES['media']['type'];
        $domain = isset($_POST['domain']) ? $_POST['domain'] : 'product';
        
        // Validate domain
        $allowedDomains = array('product', 'catalog', 'supplier');
        if (!in_array($domain, $allowedDomains)) {
            $domain = 'product';
        }
        
        // Check mimetype (VULNERABLE: only checks metadata, not actual content)
        if (!isAllowed($mimeType, $allowedMimeTypes)) {
            echo "Upload failed. Content-Type '{$mimeType}' is not allowed. Permitted types: " . implode(', ', $allowedMimeTypes);
            exit();
        }
        
        // Check file size (10MB max)
        if ($fileSize > 10 * 1024 * 1024) {
            echo "Upload failed. File size exceeds 10MB limit.";
            exit();
        }
        
        // Read file content
        $content = file_get_contents($fileTmpPath);
        
        // Sanitize content (VULNERABLE: only sanitizes SVG, other types pass through)
        $content = sanitize($content, $mimeType);
        
        // VULNERABLE: If 'url' parameter is provided, use it as the storage path
        // This allows path traversal - attacker can control where file is stored
        if (isset($_POST['url']) && !empty($_POST['url'])) {
            $path = $_POST['url'];
        } else {
            $path = generatePath($fileName, $mimeType, $domain);
        }
        
        // Ensure directory exists
        $dir = dirname($path);
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
        
        // Write file to storage
        if (file_put_contents($path, $content) !== false) {
            echo "Media uploaded successfully to: " . basename($path);
        } else {
            echo "Error: Failed to write file to storage. Please contact administrator.";
        }
        
    } else {
        $errorCode = isset($_FILES['media']['error']) ? $_FILES['media']['error'] : 'unknown';
        echo "Upload error (code: {$errorCode}). Please ensure file is selected and try again.";
    }
} else {
    // Return API information for GET requests
    header('Content-Type: application/json');
    echo json_encode(array(
        'endpoint' => '/upload.php',
        'method' => 'POST',
        'parameters' => array(
            'media' => 'File upload (required)',
            'domain' => 'product|catalog|supplier (optional)'
        ),
        'allowed_types' => $allowedMimeTypes,
        'max_size' => '10MB'
    ));
}
?>
